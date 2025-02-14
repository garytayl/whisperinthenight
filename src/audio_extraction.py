#!/usr/bin/env python3
"""
audio_extraction.py
Extracts audio from a video file using FFmpeg.
"""

import os
import subprocess
import logging
import sys
import argparse

# --- Logging Setup ---
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

# --- Core Function ---
def extract_audio(video_path, output_audio_path):
    """
    Extract audio from a video file using FFmpeg.
    
    Args:
        video_path (str): Path to the input video file.
        output_audio_path (str): Path where the audio will be saved.
    
    Returns:
        bool: True if extraction is successful, else False.
    """
    if not os.path.exists(video_path):
        logger.error(f"Video file not found: {video_path}")
        return False

    # Build the FFmpeg command
    command = [
        "ffmpeg",
        "-hide_banner",
        "-loglevel", "info",
        "-y",              # Overwrite without prompting
        "-i", video_path,
        "-vn",             # No video in output
        output_audio_path
    ]
    
    logger.info(f"Executing command: {' '.join(command)}")
    try:
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        logger.debug("FFmpeg STDOUT:\n" + result.stdout)
        logger.debug("FFmpeg STDERR:\n" + result.stderr)
        logger.info(f"Audio extraction succeeded. Output saved to: {output_audio_path}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error("FFmpeg encountered an error.")
        logger.error(f"Return code: {e.returncode}")
        logger.error("FFmpeg output:\n" + e.stderr)
        return False
    except Exception as ex:
        logger.exception("Unexpected error during audio extraction.")
        return False

# --- Command Line Interface ---
def main():
    parser = argparse.ArgumentParser(description="Extract audio from a video using FFmpeg.")
    parser.add_argument("video", help="Path to the input video file.")
    parser.add_argument("output", help="Path for the output audio file.")
    args = parser.parse_args()

    if not extract_audio(args.video, args.output):
        logger.error("Audio extraction failed.")
        sys.exit(1)
    else:
        logger.info("Audio extraction process completed successfully.")

if __name__ == "__main__":
    main()

