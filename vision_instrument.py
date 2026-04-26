import os
import time
import math
import cv2
import mido
import requests

import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision as mp_vision

#setting up MIDI
port_name = [n for n in mido.get_output_names() if "IAC" in n][0]
out = mido.open_output(port_name)
print("Using MIDI port:", port_name)

# musical and note part
SCALE_NOTES = [0, 2, 4, 5, 7, 9, 11]   
NOTE_NAMES = ["C", "D", "E", "F", "G", "A", "B"]
ROOT = 48   
NUM_OCTAVES = 3

def clamp(x, a, b):
    return max(a, min(b, x))

def note_name(midi_note):
    names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    return f"{names[midi_note % 12]}{(midi_note // 12) - 1}"

def midi_note_from_position(x, y):
    col = int(clamp(x, 0.0, 0.9999) * len(SCALE_NOTES))
    col = clamp(col, 0, len(SCALE_NOTES) - 1)

    octave_zone = int((1.0 - clamp(y, 0.0, 0.9999)) * NUM_OCTAVES)
    octave_zone = clamp(octave_zone, 0, NUM_OCTAVES - 1)

    midi_note = ROOT + 12 * octave_zone + SCALE_NOTES[col]
    return int(midi_note), col, octave_zone

MODEL_URL = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
MODEL_PATH = "hand_landmarker.task"

def ensure_model():
    if os.path.exists(MODEL_PATH):
        return
    print("Downloading MediaPipe hand model...")
    r = requests.get(MODEL_URL, timeout=60)
    r.raise_for_status()
    with open(MODEL_PATH, "wb") as f:
        f.write(r.content)
    print("Downloaded:", MODEL_PATH)

ensure_model()

# Hand Landamrk part
base_options = mp_python.BaseOptions(model_asset_path=MODEL_PATH)
options = mp_vision.HandLandmarkerOptions(
    base_options=base_options,
    running_mode=mp_vision.RunningMode.VIDEO,
    num_hands=2,
    min_hand_detection_confidence=0.6,
    min_hand_presence_confidence=0.6,
    min_tracking_confidence=0.6,
)
landmarker = mp_vision.HandLandmarker.create_from_options(options)

# Helper functions
def dist(a, b):
    return math.hypot(a.x - b.x, a.y - b.y)

def openness_to_cc(hand):
    wrist = hand[0]
    tips = [hand[4], hand[8], hand[12], hand[16], hand[20]]
    avg = sum(dist(wrist, tip) for tip in tips) / len(tips)
    t = (avg - 0.15) / (0.35 - 0.15)
    t = clamp(t, 0.0, 1.0)
    return int(t * 127)

def y_to_volume(y):
    # top = louder
    t = 1.0 - clamp(y, 0.0, 1.0)
    return int(t * 127)

def x_to_brightness(x):
    # left = darker, right = brighter
    t = clamp(x, 0.0, 1.0)
    return int(t * 127)

def chord_from_mode(root_note, mode):
    if mode == "single":
        return [root_note]
    elif mode == "major":
        return [root_note, root_note + 4, root_note + 7]
    elif mode == "spread":
        return [root_note - 12, root_note, root_note + 7, root_note + 12]
    return [root_note]

def stop_all_notes():
    global active_notes
    for n in active_notes:
        out.send(mido.Message("note_off", note=n, velocity=0))
    active_notes = []

def play_notes(notes, velocity=100):
    global active_notes
    stop_all_notes()
    for n in notes:
        out.send(mido.Message("note_on", note=int(n), velocity=velocity))
    active_notes = list(notes)

# state
PINCH_ON = 0.045
PINCH_OFF = 0.065

left_index_pinching = False
left_middle_pinching = False
right_index_pinching = False

active_notes = []
last_trigger_time = 0.0
last_mod_value = -1
last_volume_value = -1
last_brightness_value = -1
sustain_on = False

left_smoothed_x = None
left_smoothed_y = None
right_smoothed_x = None
right_smoothed_y = None
ALPHA = 0.2

# camera part
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    raise RuntimeError("Could not open camera. Enable Camera permission for VS Code/Terminal.")

print("Two-hand vision instrument running.")
print("LEFT HAND:")
print("- X = note")
print("- Y = octave")
print("- Thumb+index pinch = single note")
print("- Thumb+middle pinch = major chord")
print("- Both pinches = spread chord")
print("RIGHT HAND:")
print("- Y = volume")
print("- X = brightness / filter")
print("- Hand openness = modulation")
print("- Thumb+index pinch = sustain toggle")
print("Press q or ESC to quit.")

while True:
    ok, frame = cap.read()
    if not ok:
        break

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
    ts_ms = int(time.time() * 1000)

    result = landmarker.detect_for_video(mp_image, ts_ms)

    h, w = frame.shape[:2]

    # draw note columns
    for i in range(1, len(SCALE_NOTES)):
        xline = int(i * w / len(SCALE_NOTES))
        cv2.line(frame, (xline, 0), (xline, h), (80, 80, 80), 1)

    # draw octave bands
    for i in range(1, NUM_OCTAVES):
        yline = int(i * h / NUM_OCTAVES)
        cv2.line(frame, (0, yline), (w, yline), (80, 80, 80), 1)

    hands = []
    if result.hand_landmarks:
        for hand in result.hand_landmarks:
            avg_x = sum(lm.x for lm in hand) / len(hand)
            hands.append((avg_x, hand))

    hands.sort(key=lambda x: x[0])

    left_hand = hands[0][1] if len(hands) >= 1 else None
    right_hand = hands[1][1] if len(hands) >= 2 else None

    # left hand usage (notes)
    if left_hand is not None:
        left_thumb = left_hand[4]
        left_index = left_hand[8]
        left_middle = left_hand[12]

        x = left_index.x
        y = left_index.y
        left_smoothed_x = x if left_smoothed_x is None else (ALPHA * x + (1 - ALPHA) * left_smoothed_x)
        left_smoothed_y = y if left_smoothed_y is None else (ALPHA * y + (1 - ALPHA) * left_smoothed_y)

        root_note, col, octave_zone = midi_note_from_position(left_smoothed_x, left_smoothed_y)

        d_index = dist(left_thumb, left_index)
        d_middle = dist(left_thumb, left_middle)

        if not left_index_pinching and d_index < PINCH_ON:
            left_index_pinching = True
        elif left_index_pinching and d_index > PINCH_OFF:
            left_index_pinching = False

        if not left_middle_pinching and d_middle < PINCH_ON:
            left_middle_pinching = True
        elif left_middle_pinching and d_middle > PINCH_OFF:
            left_middle_pinching = False

        if left_index_pinching and left_middle_pinching:
            left_mode = "spread"
        elif left_middle_pinching:
            left_mode = "major"
        elif left_index_pinching:
            left_mode = "single"
        else:
            left_mode = "none"

        notes_to_play = []
        if left_mode != "none":
            notes_to_play = chord_from_mode(root_note, left_mode)

        now = time.time()
        if left_mode != "none":
            if (active_notes != notes_to_play) and (now - last_trigger_time > 0.08):
                velocity_base = 100
                velocity = velocity_base if last_volume_value < 0 else int(clamp(last_volume_value, 30, 127))
                play_notes(notes_to_play, velocity=velocity)
                last_trigger_time = now
        else:
            if active_notes and not sustain_on:
                stop_all_notes()

        cv2.circle(frame, (int(left_index.x * w), int(left_index.y * h)), 8, (255, 255, 255), -1)
        cv2.circle(frame, (int(left_middle.x * w), int(left_middle.y * h)), 8, (180, 180, 255), -1)
        cv2.circle(frame, (int(left_thumb.x * w), int(left_thumb.y * h)), 8, (255, 180, 180), -1)

        mode_label = {
            "single": "Single",
            "major": "Major chord",
            "spread": "Spread chord",
            "none": "No trigger"
        }[left_mode]
        
    else:
        left_smoothed_x = None
        left_smoothed_y = None
        left_index_pinching = False
        left_middle_pinching = False
        if active_notes and not sustain_on:
            stop_all_notes()

    # right hand usage (effects)
    if right_hand is not None:
        right_thumb = right_hand[4]
        right_index = right_hand[8]

        rx = right_index.x
        ry = right_index.y
        right_smoothed_x = rx if right_smoothed_x is None else (ALPHA * rx + (1 - ALPHA) * right_smoothed_x)
        right_smoothed_y = ry if right_smoothed_y is None else (ALPHA * ry + (1 - ALPHA) * right_smoothed_y)

        # volume (CC7)
        volume_value = y_to_volume(right_smoothed_y)
        if abs(volume_value - last_volume_value) >= 2:
            out.send(mido.Message("control_change", control=7, value=volume_value))
            last_volume_value = volume_value

        # brightness/filter (CC74)
        brightness_value = x_to_brightness(right_smoothed_x)
        if abs(brightness_value - last_brightness_value) >= 2:
            out.send(mido.Message("control_change", control=74, value=brightness_value))
            last_brightness_value = brightness_value

        # modulation (CC1)
        mod_value = openness_to_cc(right_hand)
        if abs(mod_value - last_mod_value) >= 2:
            out.send(mido.Message("control_change", control=1, value=mod_value))
            last_mod_value = mod_value

        # sustain toggle via right thumb-index pinch
        d_right_index = dist(right_thumb, right_index)
        just_toggled = False
        if not right_index_pinching and d_right_index < PINCH_ON:
            right_index_pinching = True
            sustain_on = not sustain_on
            out.send(mido.Message("control_change", control=64, value=127 if sustain_on else 0))
            if not sustain_on and not left_index_pinching and not left_middle_pinching:
                stop_all_notes()
            just_toggled = True
        elif right_index_pinching and d_right_index > PINCH_OFF:
            right_index_pinching = False

        cv2.circle(frame, (int(right_index.x * w), int(right_index.y * h)), 8, (100, 255, 100), -1)
        cv2.circle(frame, (int(right_thumb.x * w), int(right_thumb.y * h)), 8, (100, 180, 255), -1)


    else:
        right_smoothed_x = None
        right_smoothed_y = None
        right_index_pinching = False

    cv2.imshow("Two-Hand Vision Instrument", frame)
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q") or key == 27:
        break

stop_all_notes()
out.send(mido.Message("control_change", control=64, value=0))
cap.release()
cv2.destroyAllWindows()
landmarker.close()