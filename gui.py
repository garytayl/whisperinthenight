#!/usr/bin/env python3
"""
gui.py
A simple Tkinter GUI for the Whisper Subtitle Generator.
"""

import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import logging
import os
import json

import audio_extraction
import transcription
import diarization
import subtitle_export

# Configure a basic logger (optional, as our modules already log)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class WhisperGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Whisper Subtitle Generator")
        self.create_widgets()

    def create_widgets(self):
        # Video file selection
        frame_video = tk.Frame(self.root)
        frame_video.pack(padx=10, pady=5, fill='x')
        tk.Label(frame_video, text="Video File:").pack(side='left')
        self.video_entry = tk.Entry(frame_video, width=50)
        self.video_entry.pack(side='left', padx=5)
        tk.Button(frame_video, text="Browse", command=self.browse_video).pack(side='left')

        # Output subtitle file selection
        frame_output = tk.Frame(self.root)
        frame_output.pack(padx=10, pady=5, fill='x')
        tk.Label(frame_output, text="Output Subtitle File:").pack(side='left')
        self.output_entry = tk.Entry(frame_output, width=50)
        self.output_entry.pack(side='left', padx=5)
        tk.Button(frame_output, text="Browse", command=self.browse_output).pack(side='left')

        # Subtitle format options
        frame_format = tk.Frame(self.root)
        frame_format.pack(padx=10, pady=5, fill='x')
        tk.Label(frame_format, text="Subtitle Format:").pack(side='left')
        self.format_var = tk.StringVar(value="srt")
        tk.Radiobutton(frame_format, text="SRT", variable=self.format_var, value="srt").pack(side='left')
        tk.Radiobutton(frame_format, text="ASS", variable=self.format_var, value="ass").pack(side='left')

        # Whisper model input
        frame_model = tk.Frame(self.root)
        frame_model.pack(padx=10, pady=5, fill='x')
        tk.Label(frame_model, text="Whisper Model:").pack(side='left')
        self.model_entry = tk.Entry(frame_model, width=20)
        self.model_entry.insert(0, "base")
        self.model_entry.pack(side='left', padx=5)

        # Language input
        frame_lang = tk.Frame(self.root)
        frame_lang.pack(padx=10, pady=5, fill='x')
        tk.Label(frame_lang, text="Language:").pack(side='left')
        self.lang_entry = tk.Entry(frame_lang, width=10)
        self.lang_entry.insert(0, "en")
        self.lang_entry.pack(side='left', padx=5)

        # Diarization option
        frame_dia = tk.Frame(self.root)
        frame_dia.pack(padx=10, pady=5, fill='x')
        self.dia_var = tk.IntVar(value=0)
        tk.Checkbutton(frame_dia, text="Use Diarization", variable=self.dia_var, command=self.toggle_hf_entry).pack(side='left')
        tk.Label(frame_dia, text="HF Token:").pack(side='left', padx=(10, 0))
        self.hf_entry = tk.Entry(frame_dia, width=30)
        self.hf_entry.pack(side='left', padx=5)
        self.hf_entry.configure(state='disabled')

        # Run button
        self.run_button = tk.Button(self.root, text="Run", command=self.run_process)
        self.run_button.pack(pady=10)

        # Log display area
        self.log_text = tk.Text(self.root, height=10, state='disabled')
        self.log_text.pack(padx=10, pady=5, fill='both', expand=True)

    def toggle_hf_entry(self):
        if self.dia_var.get():
            self.hf_entry.configure(state='normal')
        else:
            self.hf_entry.configure(state='disabled')

    def browse_video(self):
        file_path = filedialog.askopenfilename(title="Select Video File")
        if file_path:
            self.video_entry.delete(0, tk.END)
            self.video_entry.insert(0, file_path)

    def browse_output(self):
        file_path = filedialog.asksaveasfilename(title="Save Subtitle File As", defaultextension=".srt")
        if file_path:
            self.output_entry.delete(0, tk.END)
            self.output_entry.insert(0, file_path)

    def log(self, message):
        self.log_text.configure(state='normal')
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.configure(state='disabled')
        self.log_text.see(tk.END)

    def run_process(self):
        # Run the process in a separate thread to keep the GUI responsive
        thread = threading.Thread(target=self.process_thread)
        thread.start()

    def process_thread(self):
        video_file = self.video_entry.get()
        output_file = self.output_entry.get()
        subtitle_format = self.format_var.get()
        model = self.model_entry.get()
        language = self.lang_entry.get()
        use_dia = self.dia_var.get() == 1
        hf_token = self.hf_entry.get() if use_dia else None

        if not video_file or not output_file:
            messagebox.showerror("Error", "Please specify both video and output subtitle file.")
            return

        # Disable run button during processing
        self.run_button.config(state='disabled')
        self.log("Starting process...")

        audio_output = "temp_audio.wav"
        transcript_json = "temp_transcript.json"

        try:
            # Audio extraction
            self.log("Extracting audio...")
            if not audio_extraction.extract_audio(video_file, audio_output):
                self.log("Audio extraction failed.")
                messagebox.showerror("Error", "Audio extraction failed.")
                return

            # Transcription
            self.log("Transcribing audio...")
            transcript_result = transcription.transcribe_audio(audio_output, model_name=model, language=language)
            if transcript_result is None:
                self.log("Transcription failed.")
                messagebox.showerror("Error", "Transcription failed.")
                return

            segments = transcript_result.get("segments", [])
            if not segments:
                self.log("No transcription segments found.")
                messagebox.showerror("Error", "No transcription segments found.")
                return

            # Optional Diarization
            if use_dia:
                self.log("Running diarization...")
                labeled_segments = diarization.label_speakers(audio_output, segments, hf_token)
                if labeled_segments is None:
                    self.log("Diarization failed.")
                    messagebox.showerror("Error", "Diarization failed.")
                    return
                segments = labeled_segments

            # Save temporary transcript JSON (optional)
            try:
                with open(transcript_json, "w", encoding="utf-8") as f:
                    json.dump({"segments": segments}, f, indent=4)
                self.log("Saved temporary transcript JSON.")
            except Exception as e:
                self.log("Failed to save temporary transcript JSON.")

            # Subtitle Generation
            self.log("Generating subtitles...")
            if subtitle_format == "srt":
                subtitle_export.generate_srt(segments, output_file)
            elif subtitle_format == "ass":
                subtitle_export.generate_ass(segments, output_file)
            else:
                self.log("Unsupported subtitle format.")
                messagebox.showerror("Error", "Unsupported subtitle format.")
                return

            self.log("Subtitle generation completed successfully!")
            messagebox.showinfo("Success", "Process completed successfully!")
        except Exception as e:
            self.log(f"Error: {e}")
            messagebox.showerror("Error", f"An error occurred: {e}")
        finally:
            # Cleanup temporary files
            if os.path.exists(audio_output):
                os.remove(audio_output)
            if os.path.exists(transcript_json):
                os.remove(transcript_json)
            self.run_button.config(state='normal')

if __name__ == "__main__":
    root = tk.Tk()
    app = WhisperGUI(root)
    root.mainloop()
