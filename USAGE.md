# Sample Pad - Usage Guide

## Overview

Sample Pad is a keyboard-driven audio sample player. Load audio files onto 12 pads arranged in a 3x4 grid, trigger them with your keyboard, view their waveforms, and chop samples down to the exact region you want.

## Pad Layout

The pads map to your keyboard in three rows, matching the physical key positions:

```
┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐
│  E  │ │  R  │ │  T  │ │  Y  │
└─────┘ └─────┘ └─────┘ └─────┘
┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐
│  D  │ │  F  │ │  G  │ │  H  │
└─────┘ └─────┘ └─────┘ └─────┘
┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐
│  C  │ │  V  │ │  B  │ │  N  │
└─────┘ └─────┘ └─────┘ └─────┘
```

## Controls

| Action              | How                                              |
|---------------------|--------------------------------------------------|
| Select a pad        | Click it or press its key                        |
| Play a sample       | Press the pad's key or click it                  |
| Load a sample       | Select a pad, then press **Enter**               |
| Chop a sample       | Drag the **START** and **END** sliders           |

## Loading Samples

1. Select the pad you want to load a sample onto (click it or press its key).
2. Press **Enter** to open the file browser.
3. Navigate to an audio file and select it.
4. The pad turns green to show it has a sample loaded, and the filename appears on the pad.

### Supported Formats

- WAV
- MP3
- OGG
- FLAC
- AIFF

## Playing Samples

Press a pad's key or click it to trigger playback. Multiple pads can play at the same time — each pad has its own audio channel so sounds layer on top of each other.

If you press the **same pad** again while it's still playing, the previous playback stops and the sample restarts from the beginning. This gives you clean retriggering without overlapping copies of the same sound.

## Pad Colors

| Color         | Meaning                              |
|---------------|--------------------------------------|
| Dark gray     | Empty pad (no sample loaded)         |
| Dark green    | Sample loaded                        |
| Light green   | Currently selected pad with a sample |
| Orange flash  | Pad is being triggered               |
| Blue border   | Currently selected pad               |

## Waveform Display

Below the pad grid is a waveform viewer that shows the audio for the currently selected pad.

- The **full waveform** is drawn in a dim color.
- The **active region** (between the start and end chop points) is highlighted in bright blue.
- A **green dashed line** marks the start point.
- A **red dashed line** marks the end point.
- The X axis shows time in seconds, the Y axis shows amplitude.

## Chopping Samples

Use the **START** and **END** sliders below the waveform to trim a sample:

- **START slider** — sets where playback begins (0% = beginning of file).
- **END slider** — sets where playback ends (100% = end of file).

When you press the pad, only the region between START and END plays. This lets you isolate specific hits, notes, or sections from longer audio files.

The info bar at the bottom shows the chop duration and position as a percentage of the full sample.

## Tips

- You can load different samples onto every pad and trigger them in any combination.
- Chopping is per-pad — each pad remembers its own start and end points.
- Loading a new sample onto a pad resets its chop points to the full length.
- The waveform updates in real time as you adjust the sliders, so you can see exactly what region you're selecting.
- Works with both lowercase and uppercase key presses (Caps Lock won't break anything).
