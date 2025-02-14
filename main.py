#!/usr/bin/env python3
"""
main.py
Orchestrates audio extraction, transcription, optional diarization, and subtitle generation.
"""

import os
import sys
import json
import argparse
import logging

# --- Logging Setup ---
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

# Import our modules
import audio_extraction
import transcription
import diarization
import subtitle_export

def main():
    parser = argparse.ArgumentParser(
        description="Orchestrate audio extraction, transcription, diarization, and subtitle generation."
    )
    parser.add_argument("video", help="Path to the input video file.")
    parser.add_argument("subtitle", help="Path for the output subtitle file.")
    parser.add_argument("--format", choices=["srt", "ass"], default="srt", help="Subtitle format to generate (default: srt).")
    parser.add_argument("--model", default="base", help="Whisper model to use (default: base).")
    parser.add_argument("--language", default="en", help="Language code for transcription (default: en).")
    parser.add_argument("--use-diarization", action="store_true", help="Enable speaker diarization.")
    parser.add_argument("--hf_token", help="HuggingFace token for diarization (required if --use-diarization is set).")
    args = parser.parse_args()

    if args.use_diarization and not args.hf_token:
        logger.error("HuggingFace token required for diarization. Use --hf_token <token>.")
        sys.exit(1)

    video_path = args.video
    audio_output_path = "temp_audio.wav"
    transcript_json = "temp_transcript.json"

    # Step 1: Extract audio from video
    logger.info("Starting audio extraction...")
    if not audio_extraction.extract_audio(video_path, audio_output_path):
        logger.error("Audio extraction failed. Exiting.")
        sys.exit(1)

    # Step 2: Transcribe the extracted audio
    logger.info("Starting transcription...")
    transcript_result = transcription.transcribe_audio(audio_output_path, model_name=args.model, language=args.language)
    if transcript_result is None:
        logger.error("Transcription failed. Exiting.")
        sys.exit(1)
    segments = transcript_result.get("segments", [])
    if not segments:
        logger.error("No transcription segments found. Exiting.")
        sys.exit(1)

    # Step 3: Optional speaker diarization
    if args.use_diarization:
        logger.info("Starting diarization...")
        labeled_segments = diarization.label_speakers(audio_output_path, segments, args.hf_token)
        if labeled_segments is None:
            logger.error("Diarization failed. Exiting.")
            sys.exit(1)
        segments = labeled_segments

    # Save transcript to a temporary JSON (for record/debug purposes)
    try:
        with open(transcript_json, "w", encoding="utf-8") as f:
            json.dump({"segments": segments}, f, indent=4)
        logger.info(f"Temporary transcript JSON saved to {transcript_json}")
    except Exception as e:
        logger.exception("Failed to save temporary transcript JSON.")

    # Step 4: Generate subtitle file
    logger.info("Generating subtitles...")
    try:
        if args.format == "srt":
            subtitle_export.generate_srt(segments, args.subtitle)
        elif args.format == "ass":
            subtitle_export.generate_ass(segments, args.subtitle)
        else:
            logger.error(f"Unsupported subtitle format: {args.format}")
            sys.exit(1)
    except Exception as e:
        logger.exception("Subtitle generation failed. Exiting.")
        sys.exit(1)

    logger.info("Subtitle generation completed successfully!")

    # Cleanup temporary files
    try:
        if os.path.exists(audio_output_path):
            os.remove(audio_output_path)
            logger.debug(f"Removed temporary audio file: {audio_output_path}")
        if os.path.exists(transcript_json):
            os.remove(transcript_json)
            logger.debug(f"Removed temporary transcript file: {transcript_json}")
    except Exception as e:
        logger.warning("Error cleaning up temporary files.")

if __name__ == "__main__":
    main()

