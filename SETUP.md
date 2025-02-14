# Setup Instructions for whisperinthenight

Follow these steps to set up and run the project on your system.

---

## Prerequisites

- **Python 3.x** installed on your system.
- **FFmpeg** installed and available in your system's PATH.
- **Git** (optional) for cloning the repository.
- **Tkinter** (usually bundled with Python) for the GUI.

---

## Installation Steps

### 1. Clone the Repository

Open a terminal and run:
```bash
git clone https://github.com/garytayl/whisperinthenight.git
```

Navigate to the project directory:
```bash
cd whisperinthenight
```

### 2. (Optional) Create and Activate a Virtual Environment


#### On Windows:
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies

Install the required Python packages:
```bash
pip install -r requirements.txt
```

**Note:** FFmpeg is a system dependency. Ensure it is installed and in your PATH.

---

## Running the Project

### Command-Line Interface (CLI)
Run the main script with the required arguments:
```bash
python main.py <video_file> <output_subtitle_file> [--format srt|ass] [--model base] [--language en] [--use-diarization] [--hf_token <token>]
```

#### Example:
```bash
python main.py my_video.mp4 subtitles.srt --format srt --model base --language en --use-diarization --hf_token YOUR_HuggingFace_TOKEN
```

### Graphical User Interface (GUI)
For a more interactive experience, run:
```bash
python gui.py
```
The GUI allows you to select files via dialogs, set options, and view process logs in real time.

---

## Troubleshooting

### FFmpeg Issues:
Ensure FFmpeg is installed and correctly added to your system's PATH.

### Dependency Problems:
If you encounter issues with `openai-whisper` or `pyannote.audio`, verify that they are installed by checking your virtual environment (if using one) or your system’s Python installation.

### Model Loading or Transcription Errors:
Check the logs output by the scripts for detailed error messages. Adjust the model parameters if necessary.

### Temporary Files:
Temporary files (like audio extracts and transcript JSON files) are generated during processing and cleaned up automatically after each run.

---

## Additional Notes

### Version Pinning:
While version numbers are not strictly required in `requirements.txt`, pinning them is recommended for production to ensure consistency.

### Contributions:
Contributions, suggestions, or bug reports are welcome. Please refer to the `CONTRIBUTING.md` file if available.

---

Enjoy creating professional subtitles with **whisperinthenight**!
