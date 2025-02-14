#!/usr/bin/env python3
"""
transcription.py
Transcribes an audio file using OpenAI's Whisper model.
"""

import os
import sys
import logging
import argparse

try:
    import whisper
except ImportError:
    print("Error: The 'whisper' library is not installed. Install it with `pip install openai-whisper`")
    sys.exit(1)

# --- Logging Setup ---
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

# --- Core Function ---
def transcribe_audio(audio_path, model_name="base", language="en"):
    """
    Transcribe an audio file using OpenAI's Whisper.

    Args:
        audio_path (str): Path to the audio file.
        model_name (str): Whisper model variant (e.g., "base", "small", "medium", "large").
        language (str): Language code (default "en").

    Returns:
        dict: Transcription result containing 'segments' and full 'text', or None on error.
              Each segment is a dict: {"start": float, "end": float, "text": str}.
    """
    if not os.path.exists(audio_path):
        logger.error(f"Audio file not found: {audio_path}")
        return None

    try:
        logger.info(f"Loading Whisper model '{model_name}'...")
        model = whisper.load_model(model_name)
    except Exception as e:
        logger.exception("Failed to load the Whisper model.")
        return None

    try:
        logger.info(f"Transcribing audio: {audio_path}")
        result = model.transcribe(audio_path, language=language)
        logger.debug("Transcription result:\n%s", result)
        logger.info("Transcription completed successfully.")
        return result
    except Exception as e:
        logger.exception("Error during transcription process.")
        return None

# --- Command Line Interface ---
def main():
    parser = argparse.ArgumentParser(description="Transcribe audio using OpenAI's Whisper model.")
    parser.add_argument("audio", help="Path to the input audio file.")
    parser.add_argument("--model", default="base", help="Whisper model to use (default: base)")
    parser.add_argument("--language", default="en", help="Language code (default: en)")
    args = parser.parse_args()

    transcription = transcribe_audio(args.audio, model_name=args.model, language=args.language)
    if transcription is None:
        logger.error("Transcription failed.")
        sys.exit(1)
    else:
        # Output the full transcription text and segments
        print("\nFull Transcription:\n", transcription.get("text", ""))
        print("\nSegments:")
        for seg in transcription.get("segments", []):
            print(f"[{seg['start']:.2f} - {seg['end']:.2f}]: {seg['text']}")
        logger.info("Transcription process completed successfully.")

if __name__ == "__main__":
    main()
