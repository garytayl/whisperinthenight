#!/usr/bin/env python3
"""
subtitle_export.py
Generates subtitle files (SRT and ASS) from transcript segments.
"""

import os
import sys
import json
import logging
import argparse
from datetime import timedelta

# --- Logging Setup ---
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

# --- Helper Functions for Time Formatting ---
def format_time_srt(seconds):
    """Format seconds into SRT time format: HH:MM:SS,mmm"""
    try:
        td = timedelta(seconds=seconds)
        total_seconds = int(td.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        secs = total_seconds % 60
        milliseconds = int((td.total_seconds() - total_seconds) * 1000)
        return f"{hours:02}:{minutes:02}:{secs:02},{milliseconds:03}"
    except Exception as e:
        logger.exception("Error formatting time for SRT.")
        return "00:00:00,000"

def format_time_ass(seconds):
    """Format seconds into ASS time format: H:MM:SS.cs"""
    try:
        td = timedelta(seconds=seconds)
        total_seconds = int(td.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        secs = total_seconds % 60
        centiseconds = int((td.total_seconds() - total_seconds) * 100)
        return f"{hours}:{minutes:02}:{secs:02}.{centiseconds:02}"
    except Exception as e:
        logger.exception("Error formatting time for ASS.")
        return "0:00:00.00"

# --- Subtitle Generation Functions ---
def generate_srt(segments, output_file):
    """
    Generate an SRT subtitle file from transcript segments.
    
    Args:
        segments (list): List of dicts with 'start', 'end', 'text' (and optionally 'speaker').
        output_file (str): Output file path for the SRT file.
    """
    try:
        logger.info(f"Generating SRT subtitles: {output_file}")
        with open(output_file, 'w', encoding='utf-8') as f:
            for idx, seg in enumerate(segments, start=1):
                start_time = format_time_srt(seg.get("start", 0))
                end_time = format_time_srt(seg.get("end", 0))
                text = seg.get("text", "").strip()
                # Prepend speaker label if available
                if "speaker" in seg:
                    text = f"{seg['speaker']}: {text}"
                f.write(f"{idx}\n")
                f.write(f"{start_time} --> {end_time}\n")
                f.write(f"{text}\n\n")
        logger.info("SRT subtitle generation completed successfully.")
    except Exception as e:
        logger.exception("Error generating SRT file.")
        raise

def assign_colors_to_speakers(segments):
    """
    Assign a color code to each unique speaker.
    
    Returns:
        dict: Mapping of speaker to ASS color code.
    """
    default_colors = [
        "&H00FF00",  # Green
        "&H0000FF",  # Blue
        "&HFF0000",  # Red
        "&H00FFFF",  # Cyan
        "&HFF00FF",  # Magenta
        "&HFFFF00",  # Yellow
    ]
    speakers = {}
    for seg in segments:
        speaker = seg.get("speaker", "Speaker Unknown")
        if speaker not in speakers:
            speakers[speaker] = True
    color_mapping = {speaker: default_colors[i % len(default_colors)] for i, speaker in enumerate(speakers.keys())}
    logger.debug(f"Assigned colors to speakers: {color_mapping}")
    return color_mapping

def generate_ass(segments, output_file):
    """
    Generate an ASS subtitle file from transcript segments.
    
    Args:
        segments (list): List of dicts with 'start', 'end', 'text', and optionally 'speaker'.
        output_file (str): Output file path for the ASS file.
    """
    try:
        logger.info(f"Generating ASS subtitles: {output_file}")
        # ASS file header
        ass_header = (
            "[Script Info]\n"
            "ScriptType: v4.00+\n"
            "Collisions: Normal\n"
            "PlayResX: 1920\n"
            "PlayResY: 1080\n"
            "Timer: 100.0000\n\n"
            "[V4+ Styles]\n"
            "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, "
            "Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, "
            "Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n"
            "Style: Default,Arial,36,&H00FFFFFF,&H000000FF,&H00000000,&H64000000,0,0,0,0,100,100,0,0,1,2,2,2,10,10,10,1\n\n"
            "[Events]\n"
            "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
        )
        color_mapping = assign_colors_to_speakers(segments)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(ass_header)
            for seg in segments:
                start_time = format_time_ass(seg.get("start", 0))
                end_time = format_time_ass(seg.get("end", 0))
                text = seg.get("text", "").strip()
                speaker = seg.get("speaker", "Speaker Unknown")
                # Add color override tag if available
                color_tag = f"{{\\c{color_mapping.get(speaker, '&H00FFFFFF')}}}"
                dialogue_line = (
                    f"Dialogue: 0,{start_time},{end_time},Default,{speaker},0000,0000,0000,,{color_tag}{text}\n"
                )
                f.write(dialogue_line)
        logger.info("ASS subtitle generation completed successfully.")
    except Exception as e:
        logger.exception("Error generating ASS file.")
        raise

# --- Command Line Interface ---
def main():
    parser = argparse.ArgumentParser(
        description="Generate subtitle files (SRT or ASS) from transcript segments."
    )
    parser.add_argument(
        "transcript",
        help="Path to the transcript JSON file (should contain segments with 'start', 'end', 'text', and optionally 'speaker')."
    )
    parser.add_argument("output", help="Path for the output subtitle file.")
    parser.add_argument(
        "--format",
        choices=["srt", "ass"],
        default="srt",
        help="Subtitle format to generate (default: srt)."
    )
    args = parser.parse_args()

    if not os.path.exists(args.transcript):
        logger.error(f"Transcript file not found: {args.transcript}")
        sys.exit(1)

    try:
        with open(args.transcript, "r", encoding="utf-8") as f:
            transcript_data = json.load(f)
        segments = transcript_data.get("segments", [])
        if not segments:
            logger.error("No transcript segments found in the transcript file.")
            sys.exit(1)
    except Exception as e:
        logger.exception("Failed to load transcript file.")
        sys.exit(1)

    if args.format == "srt":
        generate_srt(segments, args.output)
    elif args.format == "ass":
        generate_ass(segments, args.output)
    else:
        logger.error(f"Unsupported format: {args.format}")
        sys.exit(1)

if __name__ == "__main__":
    main()

