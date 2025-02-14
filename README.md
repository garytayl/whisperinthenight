# whisperinthenight

Welcome to **whisperinthenight**—an automated subtitle generation pipeline that extracts audio from videos, transcribes the audio using OpenAI's Whisper, optionally assigns speaker labels via diarization, and produces polished subtitle files (SRT/ASS) ready for use in your video editing software.

---

## Table of Contents
- [Overview](#overview)
- [Workflow](#workflow)
- [Modules](#modules)
  - [audio_extraction.py](#audio_extractionpy-summary)
  - [transcription.py](#transcriptionpy-summary)
  - [diarization.py](#diarizationpy-summary)
  - [subtitle_export.py](#subtitle_exportpy-summary)
  - [main.py](#mainpy-summary)
  - [utils.py](#utilspy-summary)
  - [gui.py](#guipy-summary)
- [Usage](#usage)
- [Requirements](#requirements)
- [License](#license)

---

## Overview
**whisperinthenight** is designed to transform your video files into professionally formatted subtitles by executing the following steps:
1. **Audio Extraction:** Extract audio from your video using FFmpeg.
2. **Transcription:** Transcribe the audio with OpenAI's Whisper.
3. **Diarization (Optional):** Label speakers using pyannote.audio.
4. **Subtitle Generation:** Format the transcript into SRT or ASS subtitle files.
5. **Orchestration:** Tie everything together via a CLI or GUI interface.

---

## Workflow
1. **Audio Extraction:**  
   - The process begins with `main.py`, which calls the `audio_extraction.py` module.
   - **How they talk:** `main.py` passes the input video file path to `audio_extraction.extract_audio()`, which extracts the audio and saves it as a temporary audio file.

2. **Transcription:**  
   - Next, `main.py` invokes `transcription.py` by calling `transcription.transcribe_audio()`, supplying the temporary audio file.
   - **How they talk:** The output is a transcript (a dictionary with timestamped segments) that `main.py` receives for further processing.

3. **Diarization (Optional):**  
   - If enabled, `main.py` then calls `diarization.label_speakers()`, passing in the temporary audio file and the transcript segments.
   - **How they talk:** `diarization.py` processes these segments, assigning speaker labels based on overlap analysis, and returns the enriched transcript to `main.py`.

4. **Subtitle Generation:**  
   - With the final transcript ready, `main.py` calls the appropriate function from `subtitle_export.py` (either `generate_srt()` or `generate_ass()`).
   - **How they talk:** The transcript (with or without speaker labels) is formatted into the desired subtitle file, which is then output for use in video editing software.

5. **Orchestration & Cleanup:**  
   - Throughout the process, `main.py` uses `utils.py` functions to manage logging, check file existence, and safely remove temporary files.
   - **How they talk:** `main.py` orchestrates the overall flow, ensuring that each module receives the correct input from the previous step and cleans up temporary artifacts after processing.

6. **Graphical Interface:**  
   - For users preferring a visual approach, `gui.py` provides a Tkinter-based interface that wraps the entire CLI process.
   - **How they talk:** The GUI collects user inputs and then internally calls the same functions from `main.py`, providing real-time log updates and file dialogs.

---
---

## Modules

### audio_extraction.py Summary
**Purpose:**  
Extracts audio from video files using FFmpeg.

**Key Function:**  
```python
extract_audio(video_path, output_audio_path)
```
- **Verification:** Checks that the video file exists.
- **Execution:** Runs FFmpeg to extract the audio.
- **Logging:** Provides detailed INFO and DEBUG logs for process tracing and error handling.

**CLI Usage:**  
```bash
python audio_extraction.py <path_to_video> <output_audio_path>
```

---

### transcription.py Summary
**Purpose:**  
Transcribes an audio file using OpenAI's Whisper model.

**Key Function:**  
```python
transcribe_audio(audio_path, model_name="base", language="en")
```
- **Verification:** Ensures the audio file exists.
- **Model Loading:** Loads the specified Whisper model.
- **Transcription:** Converts audio to text with timestamped segments.
- **Logging:** Offers comprehensive debug and error messages.

**CLI Usage:**  
```bash
python transcription.py <path_to_audio> [--model base] [--language en]
```

---

### diarization.py Summary
**Purpose:**  
Labels transcript segments with speaker information using pyannote.audio.

**Key Function:**  
```python
label_speakers(audio_path, transcript_segments, hf_token)
```
- **Verification:** Confirms that the audio file exists.
- **Pipeline Loading:** Loads the pyannote diarization pipeline using a HuggingFace token.
- **Processing:** Runs diarization on the audio file.
- **Merging:** Aligns transcript segments with speaker labels.

**CLI Usage:**  
```bash
python diarization.py <path_to_audio> <path_to_transcript_json> <output_json> --hf_token <your_huggingface_token>
```

---

### subtitle_export.py Summary
**Purpose:**  
Generates subtitle files (SRT and ASS) from transcript segments.

**Key Functions:**
```python
generate_srt(segments, output_file)  # Formats transcript segments into an SRT file
generate_ass(segments, output_file)  # Formats transcript segments into an ASS file with color coding
```

**CLI Usage:**  
```bash
python subtitle_export.py <transcript_json> <output_subtitle_file> [--format srt|ass]
```

---

### main.py Summary
**Purpose:**  
Orchestrates the entire workflow—audio extraction, transcription, optional diarization, and subtitle generation.

**Workflow:**
- **Audio Extraction:** Calls `extract_audio()` to obtain the audio track.
- **Transcription:** Uses `transcribe_audio()` to generate timestamped text.
- **Diarization (Optional):** Applies `label_speakers()` if enabled.
- **Subtitle Generation:** Outputs subtitles in SRT or ASS format.
- **Cleanup:** Removes temporary files after processing.

**CLI Usage:**  
```bash
python main.py <video_file> <output_subtitle_file> [--format srt|ass] [--model base] [--language en] [--use-diarization] [--hf_token <token>]
```

---

### gui.py Summary
**Purpose:**  
Provides a Tkinter-based GUI for ease of use.

**Features:**
- Drag-and-drop file selection
- Format, model, and language options
- Real-time log display
- Non-blocking execution via threading

**Usage:**  
```bash
python gui.py
```

---

## Usage
For command-line usage, run `main.py` with the appropriate parameters, or launch the GUI with `gui.py`.

**Example (CLI):**
```bash
python main.py my_video.mp4 subtitles.srt --format srt --model base --language en --use-diarization --hf_token YOUR_HF_TOKEN
```

**Example (GUI):**
```bash
python gui.py
```

---

## Requirements
- Python 3.x
- FFmpeg
- OpenAI Whisper (`pip install openai-whisper`)
- pyannote.audio (`pip install pyannote.audio`)
- Tkinter (included with Python)
- Other standard Python libraries (e.g., `argparse`, `logging`, `json`)

---

Enjoy creating professional subtitles with **whisperinthenight**!
