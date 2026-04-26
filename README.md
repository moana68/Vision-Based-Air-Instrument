# Vision-Based Instrument README

This guide explains how to set up, run, and use the vision-based instrument project on a Mac. It is written for someone starting from scratch.

---

## What this project is

This project uses:
- a webcam,
- Python,
- MediaPipe hand tracking,
- MIDI output,
- and GarageBand

to turn hand gestures into music.

The camera tracks your hands in real time. The program detects where your hands are and what gestures you are making, then sends MIDI notes and control messages into GarageBand.

---

## What the instrument does

### Left hand = notes and chords
The left hand is the musical hand.

It controls:
- **left/right position** -> which note you are selecting
- **up/down position** -> which octave you are selecting
- **thumb + index pinch** -> play a single note
- **thumb + middle pinch** -> play a chord
- **thumb + index pinch + thumb + middle pinch together** -> play a larger spread chord

### Right hand = expression and effects
The right hand shapes the sound.

It controls:
- **up/down position** -> volume
- **left/right position** -> brightness / filter-style control
- **open vs closed hand** -> modulation / expression
- **thumb + index pinch** -> sustain toggle

You can think of it like this:
- **Left hand = what notes you play**
- **Right hand = how those notes sound**

---

## What you need

### Hardware
- A Mac
- A webcam (built-in webcam is fine)
- Speakers or headphones

### Software
- Python 3
- Visual Studio Code or Terminal
- GarageBand
- The Python packages used by the project

---

## Project files

You should have a folder, for example:

```bash
vision_air_harp
```

Inside it, you should have your Python script, for example:

```bash
two_hand_instrument.py
```

The first time you run the code, it will also download a file called:

```bash
hand_landmarker.task
```

That is the MediaPipe hand tracking model.

---

## Step 1: Install GarageBand

If GarageBand is not already installed:
1. Open the **App Store**.
2. Search for **GarageBand**.
3. Install it.

GarageBand is used as the sound engine. Python sends MIDI into GarageBand, and GarageBand produces the actual sound.

---

## Step 2: Enable the IAC virtual MIDI driver on Mac

This is required so Python can send MIDI to GarageBand.

### How to enable it
1. Open **Audio MIDI Setup**.
   - Use Spotlight: `Cmd + Space`
   - Type: `Audio MIDI Setup`
   - Press Enter
2. In the top menu bar, click:
   - **Window -> Show MIDI Studio**
3. Double-click **IAC Driver**.
4. Check **Device is online**.
5. Make sure **Bus 1** exists.
6. Click **Apply**.

Now your Mac has a virtual MIDI bus that Python can use.

---

## Step 3: Make a project folder

Create a folder somewhere convenient, for example on your Desktop:

```bash
~/Desktop/vision_air_harp
```

Put your Python script there.

---

## Step 4: Open the project in VS Code

1. Open **VS Code**.
2. Click **File -> Open Folder...**
3. Select the project folder.
4. Open it.

If VS Code asks whether you trust the folder, click **Yes**.

---

## Step 5: Install the Python extension in VS Code

If the Python extension is not already installed:
1. Open the **Extensions** panel.
2. Search for **Python**.
3. Install **Python** by Microsoft.

This helps VS Code recognize Python files properly.

---

## Step 6: Open the terminal in VS Code

In VS Code:
- Click **Terminal -> New Terminal**

You should now see a terminal open at the bottom of the editor.

---

## Step 7: Install the required Python packages

Run this command in the terminal:

```bash
python3 -m pip install mido python-rtmidi opencv-python mediapipe requests
```

These packages do the following:
- `mido` -> MIDI messages
- `python-rtmidi` -> MIDI output support
- `opencv-python` -> webcam access and display window
- `mediapipe` -> hand tracking
- `requests` -> downloads the hand tracking model if needed

If it says `Requirement already satisfied`, that is fine.

---

## Step 8: Save the Python script

Create a Python file such as:

```bash
two_hand_instrument.py
```

Paste the instrument code into that file.

**Important:** save the file before running it.

In VS Code, press:

```bash
Cmd + S
```

If the file is not saved, Python may run an old version of the code or an empty file.

---

## Step 9: Open GarageBand correctly

1. Open **GarageBand**.
2. Create a **New Project**.
3. Choose **Software Instrument**.
4. Pick an instrument sound.
   - Piano works well for testing.
   - Synth patches are also good.
5. Make sure the instrument track is selected.

GarageBand must stay open while you run the script.

---

## Step 10: Run the script

In the terminal, make sure you are inside the project folder, for example:

```bash
cd ~/Desktop/vision_air_harp
```

Then run:

```bash
python3 two_hand_instrument.py
```

If everything is set up correctly, you should see:
- terminal messages saying the instrument is running,
- a webcam window,
- and GarageBand should respond when you make gestures.

---

## Step 11: Camera permissions on macOS

If the webcam does not open, macOS is probably blocking camera access.

To fix it:
1. Open **System Settings**.
2. Go to **Privacy & Security -> Camera**.
3. Enable camera access for:
   - **Visual Studio Code**, if running from VS Code
   - or **Terminal**, if running from Terminal
4. Fully quit and reopen the app.
5. Run the script again.

---

## How to use the instrument

## Left hand: notes and chords

### Note selection
The left hand chooses the note.

- Move **left/right** to choose the note lane.
- Move **up/down** to choose the octave.

The note lanes are based on a C major layout:
- C
- D
- E
- F
- G
- A
- B

### Left-hand gestures
- **Thumb + index pinch** -> play a single note
- **Thumb + middle pinch** -> play a major chord
- **Both pinches together** -> play a spread chord

### Simple way to think about it
The left hand acts like a keyboard in the air.

---

## Right hand: effects and expression

### Volume
- Move the right hand **up** to make it louder
- Move the right hand **down** to make it quieter

### Brightness / filter
- Move the right hand **left/right** to change brightness
- Depending on the GarageBand instrument, this may sound darker or brighter

### Modulation
- Open or close the right hand to change expression / modulation
- This depends on the GarageBand instrument patch

### Sustain toggle
- **Thumb + index pinch on the right hand** toggles sustain on or off
- Sustain means notes keep ringing even after the left hand stops triggering them

### Simple way to think about it
The right hand acts like the effects and expression controls.

---

## Best way to test it the first time

Do this in order:

1. Ignore the right hand at first.
2. Use only the left hand.
3. Move the left hand around.
4. Try **thumb + index pinch** to play a note.
5. Check whether pitch changes as you move around.
6. Then try **thumb + middle pinch** for chords.
7. After that, start using the right hand for volume and sustain.

This is much easier than trying to learn both hands at once.

---

## What you should expect on screen

The webcam window usually shows:
- your camera view,
- note lanes,
- octave zones,
- tracked fingertip markers,
- and text showing the current note / mode.

This helps you debug whether the mapping is actually changing.

If the on-screen note label changes but the sound feels the same, the issue may be the GarageBand patch, not the hand tracking.

---

## How to quit the program

### Normal exit
Click the webcam window and press:

```bash
q
```

or press:

```bash
Esc
```

### If that does not work
In the terminal, press:

```bash
Ctrl + C
```

That force-stops the script.

---

## Troubleshooting

## Problem: nothing happens when I run the script
Possible causes:
- the file was not saved,
- the wrong file was run,
- GarageBand is not open,
- the GarageBand track is not selected.

### Fix
- Save the file with `Cmd + S`
- Make sure you run the correct filename
- Keep GarageBand open
- Make sure the Software Instrument track is selected

---

## Problem: Python says a package is missing
Example:

```bash
ModuleNotFoundError
```

### Fix
Run:

```bash
python3 -m pip install mido python-rtmidi opencv-python mediapipe requests
```

---

## Problem: camera does not open
### Fix
Enable camera permissions in:

**System Settings -> Privacy & Security -> Camera**

Then reopen VS Code or Terminal.

---

## Problem: no sound in GarageBand
### Check these things
- GarageBand is open
- You created a **Software Instrument** track
- The track is selected
- The IAC Driver is enabled
- The script is using the IAC output port

---

## Problem: gestures feel too sensitive or unstable
The script has thresholds and smoothing values that can be tuned.

Examples:
- lower pinch threshold if pinches trigger too easily
- raise pinch threshold if it is hard to trigger
- reduce smoothing if movement feels too slow
- increase smoothing if note selection jitters

---

## Problem: the sound does not change much with the right hand
That depends on the GarageBand patch.

Some instrument sounds respond strongly to:
- modulation,
- brightness,
- sustain,
- volume

Others barely react.

If the controls seem weak, try a different instrument patch in GarageBand.
Synth patches often respond more obviously than piano patches.

---

## Suggested first test setup

A very good test setup is:
- left hand: single notes only at first
- right hand: ignore at first
- GarageBand patch: piano or synth lead

Then, once that works:
- try left-hand chords
- add right-hand volume
- add sustain
- add modulation

---

## Summary

This instrument works like this:

### Left hand
- chooses the note
- chooses the octave
- pinches to trigger notes or chords

### Right hand
- changes volume
- changes brightness / filter
- changes modulation
- toggles sustain

So the cleanest mental model is:

- **Left hand = what you play**
- **Right hand = how it sounds**

---

## Typical run commands

Install packages:

```bash
python3 -m pip install mido python-rtmidi opencv-python mediapipe requests
```

Go into project folder:

```bash
cd ~/Desktop/vision_air_harp
```

Run the instrument:

```bash
python3 two_hand_instrument.py
```

---

## Notes for collaborators

If you are sending this to someone else, make sure you also send:
- the Python script file,
- this README,
- and remind them that GarageBand + IAC Driver setup are required.

Without the IAC Driver enabled, Python will not be able to send MIDI to GarageBand.
