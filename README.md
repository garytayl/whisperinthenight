# whisperinthenight

## audio_extraction.py Summary

**Purpose:**  
Extracts audio from video files using FFmpeg.

**Key Function:**  
`extract_audio(video_path, output_audio_path)`  
- Verifies that the video file exists.  
- Executes FFmpeg to extract the audio while handling potential errors.  
- Logs detailed debug and error messages to assist in troubleshooting.

**CLI Usage:**  
Run the script with:
```bash
python audio_extraction.py <path_to_video> <output_audio_path>
```
**Logging:**

- Extensive INFO and DEBUG level logging to trace process flow and errors.
- Error messages help identify and fix issues during extraction.

## transcription.py Summary

**Purpose:**  
Transcribes an audio file using OpenAI's Whisper model.

**Key Function:**  
`transcribe_audio(audio_path, model_name="base", language="en")`  
- Checks that the audio file exists.  
- Loads the specified Whisper model.  
- Transcribes the audio and returns a dictionary containing segments (with start, end, and text) plus the full transcription text.  
- Logs detailed debug and error messages to assist in troubleshooting.

**CLI Usage:**  
Run the script with:
```bash
python transcription.py <path_to_audio> [--model base] [--language en]
```

**Logging:**

- Extensive INFO and DEBUG level logging to trace process flow and errors.
- Error messages help diagnose issues during model loading and transcription.
vbnet


## diarization.py Summary

**Purpose:**  
Labels transcript segments with speaker information using pyannote.audio for speaker diarization.

**Key Functions:**
- `label_speakers(audio_path, transcript_segments, hf_token)`  
  - Verifies that the audio file exists.
  - Loads the pyannote diarization pipeline using a HuggingFace token.
  - Runs diarization on the audio file.
  - Converts the diarization output to segments.
  - Merges transcript segments with diarization data by calculating overlap durations to assign speaker labels.
  - Returns transcript segments with an added `speaker` field.

**CLI Usage:**  
Run the script with:
```bash
python diarization.py <path_to_audio> <path_to_transcript_json> <output_json> --hf_token <your_huggingface_token>
```
**Logging:**

- Detailed INFO and DEBUG logging to trace pipeline loading, processing, and merging steps.
- Comprehensive error logging to diagnose issues with file I/O, model loading, or processing.

## subtitle_export.py Summary

**Purpose:**  
Generates subtitle files (SRT and ASS) from transcript segments.

**Key Functions:**
- `generate_srt(segments, output_file)`  
  - Converts transcript segments into an SRT file with formatted time codes.
- `generate_ass(segments, output_file)`  
  - Converts transcript segments into an ASS file with formatted time codes.
  - Dynamically assigns color codes to speakers for visual differentiation.

**CLI Usage:**  
Run the script with:
```bash
python subtitle_export.py <transcript_json> <output_subtitle_file> [--format srt|ass]
```
**Logging:**

- Detailed INFO and DEBUG logs track the generation process.
- Error logging captures issues during file I/O and formatting.

**Example Output**
Assuming a transcript JSON with the following content:
```bash
{
  "segments": [
    { "start": 0.0, "end": 3.2, "text": "Hello, world!", "speaker": "Speaker 1" },
    { "start": 3.3, "end": 5.0, "text": "This is a test.", "speaker": "Speaker 2" }
  ]
}
```
**Example SRT Output**
```bash
1
00:00:00,000 --> 00:00:03,200
Speaker 1: Hello, world!

2
00:00:03,300 --> 00:00:05,000
Speaker 2: This is a test.
```
**Example ASS Output**
```bash
[Script Info]
ScriptType: v4.00+
Collisions: Normal
PlayResX: 1920
PlayResY: 1080
Timer: 100.0000

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,36,&H00FFFFFF,&H000000FF,&H00000000,&H64000000,0,0,0,0,100,100,0,0,1,2,2,2,10,10,10,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,0:00:00.00,0:00:03.20,Default,Speaker 1,0000,0000,0000,,{\c&H00FF00}Hello, world!
Dialogue: 0,0:00:03.30,0:00:05.00,Default,Speaker 2,0000,0000,0000,,{\c&H0000FF}This is a test.
```

## main.py Summary

**Purpose:**  
Orchestrates the entire workflow—audio extraction, transcription, optional diarization, and subtitle generation.

**Workflow:**
1. **Audio Extraction:**  
   - Uses `audio_extraction.extract_audio()` to extract audio from the provided video file.
2. **Transcription:**  
   - Transcribes the extracted audio using `transcription.transcribe_audio()`.
3. **Diarization (Optional):**  
   - If `--use-diarization` is enabled, applies `diarization.label_speakers()` to assign speaker labels.
4. **Subtitle Generation:**  
   - Generates subtitles in SRT or ASS format using `subtitle_export.generate_srt()` or `generate_ass()`.

**CLI Usage:**  
Run the script with:
```bash
python main.py <video_file> <output_subtitle_file> [--format srt|ass] [--model base] [--language en] [--use-diarization] [--hf_token <token>]
```
**Logging:**
- Detailed INFO, DEBUG, and ERROR logs trace each step.
- Robust error handling ensures smooth troubleshooting.
**Temporary Files:**
- Generates temporary audio and transcript files which are cleaned up after processing.

