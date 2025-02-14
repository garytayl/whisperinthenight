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
