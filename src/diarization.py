#!/usr/bin/env python3
"""
diarization.py
Labels transcript segments with speaker information using pyannote.audio for speaker diarization.
"""

import os
import sys
import json
import logging
import argparse

try:
    from pyannote.audio import Pipeline
except ImportError:
    print("Error: The 'pyannote.audio' library is not installed. Install it with `pip install pyannote.audio`")
    sys.exit(1)

# --- Logging Setup ---
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

def load_diarization_pipeline(hf_token):
    """
    Loads the pyannote speaker diarization pipeline.
    
    Args:
        hf_token (str): HuggingFace token for accessing pre-trained models.
        
    Returns:
        Pipeline object or None if loading fails.
    """
    try:
        logger.info("Loading pyannote diarization pipeline...")
        pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization", use_auth_token=hf_token)
        logger.info("Diarization pipeline loaded successfully.")
        return pipeline
    except Exception as e:
        logger.exception("Failed to load diarization pipeline.")
        return None

def run_diarization(pipeline, audio_path):
    """
    Runs the diarization pipeline on the provided audio file.
    
    Args:
        pipeline: Loaded pyannote Pipeline.
        audio_path (str): Path to the audio file.
        
    Returns:
        Diarization result or None on error.
    """
    try:
        logger.info(f"Running diarization on {audio_path}...")
        diarization = pipeline(audio_path)
        logger.info("Diarization completed successfully.")
        return diarization
    except Exception as e:
        logger.exception("Error during diarization process.")
        return None

def convert_diarization_to_segments(diarization):
    """
    Converts pyannote diarization output to a list of dictionaries.
    
    Returns:
        List of dicts with keys: "start", "end", "speaker".
    """
    segments = []
    try:
        for segment, _, speaker in diarization.itertracks(yield_label=True):
            segments.append({
                "start": segment.start,
                "end": segment.end,
                "speaker": speaker
            })
        logger.debug(f"Converted diarization to segments: {segments}")
    except Exception as e:
        logger.exception("Error converting diarization output to segments.")
    return segments

def merge_transcripts_with_diarization(transcript_segments, diarization_segments):
    """
    Merges transcript segments with diarization segments by assigning the speaker 
    with the maximum overlap to each transcript segment.
    
    Args:
        transcript_segments (list): List of dicts with 'start', 'end', 'text'.
        diarization_segments (list): List of dicts with 'start', 'end', 'speaker'.
        
    Returns:
        List of transcript segments with an added 'speaker' key.
    """
    labeled_segments = []
    for t_seg in transcript_segments:
        t_start = t_seg.get("start", 0)
        t_end = t_seg.get("end", 0)
        overlap_durations = {}
        for d_seg in diarization_segments:
            d_start = d_seg["start"]
            d_end = d_seg["end"]
            # Calculate overlap duration
            overlap = max(0, min(t_end, d_end) - max(t_start, d_start))
            if overlap > 0:
                speaker = d_seg["speaker"]
                overlap_durations[speaker] = overlap_durations.get(speaker, 0) + overlap
        if overlap_durations:
            assigned_speaker = max(overlap_durations, key=overlap_durations.get)
        else:
            assigned_speaker = "Speaker Unknown"
        labeled_seg = t_seg.copy()
        labeled_seg["speaker"] = assigned_speaker
        labeled_segments.append(labeled_seg)
    logger.info("Merged transcript segments with speaker labels.")
    return labeled_segments

def label_speakers(audio_path, transcript_segments, hf_token):
    """
    Runs diarization on an audio file and merges the result with transcript segments.
    
    Args:
        audio_path (str): Path to the audio file.
        transcript_segments (list): Transcript segments with 'start', 'end', 'text'.
        hf_token (str): HuggingFace token for the diarization model.
        
    Returns:
        List of transcript segments with an added 'speaker' field, or None on error.
    """
    if not os.path.exists(audio_path):
        logger.error(f"Audio file not found: {audio_path}")
        return None

    pipeline = load_diarization_pipeline(hf_token)
    if pipeline is None:
        logger.error("Diarization pipeline could not be loaded.")
        return None

    diarization = run_diarization(pipeline, audio_path)
    if diarization is None:
        logger.error("Diarization process failed.")
        return None

    diarization_segments = convert_diarization_to_segments(diarization)
    if not diarization_segments:
        logger.error("No diarization segments were generated.")
        return None

    labeled_segments = merge_transcripts_with_diarization(transcript_segments, diarization_segments)
    return labeled_segments

# --- Command Line Interface ---
def main():
    parser = argparse.ArgumentParser(description="Label speakers in transcript segments using diarization.")
    parser.add_argument("audio", help="Path to the audio file.")
    parser.add_argument("transcript", help="Path to the transcript JSON file (should contain segments with 'start', 'end', 'text').")
    parser.add_argument("output", help="Path for the output JSON file with speaker labels.")
    parser.add_argument("--hf_token", required=True, help="HuggingFace token for accessing the diarization model.")
    args = parser.parse_args()

    if not os.path.exists(args.transcript):
        logger.error(f"Transcript file not found: {args.transcript}")
        sys.exit(1)

    try:
        with open(args.transcript, "r") as f:
            transcript_data = json.load(f)
        transcript_segments = transcript_data.get("segments", [])
        if not transcript_segments:
            logger.error("No transcript segments found in the transcript file.")
            sys.exit(1)
    except Exception as e:
        logger.exception("Failed to load transcript file.")
        sys.exit(1)

    labeled_segments = label_speakers(args.audio, transcript_segments, args.hf_token)
    if labeled_segments is None:
        logger.error("Labeling speakers failed.")
        sys.exit(1)

    output_data = {"segments": labeled_segments}
    try:
        with open(args.output, "w") as f:
            json.dump(output_data, f, indent=4)
        logger.info(f"Labeled transcript saved to {args.output}")
    except Exception as e:
        logger.exception("Failed to save output JSON file.")
        sys.exit(1)

if __name__ == "__main__":
    main()

