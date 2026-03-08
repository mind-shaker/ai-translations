import whisperx
import gc
import os
import sys

def format_timestamp(seconds: float) -> str:
    """Convert float seconds to SRT timestamp format (HH:MM:SS,mmm)."""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int(round((seconds - int(seconds)) * 1000))
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

def write_srt(segments: list, output_path: str):
    """Write whisperx segments to an SRT file."""
    with open(output_path, "w", encoding="utf-8") as f:
        for idx, segment in enumerate(segments, start=1):
            start_str = format_timestamp(segment["start"])
            end_str = format_timestamp(segment["end"])
            text = segment["text"].strip()
            
            f.write(f"{idx}\n")
            f.write(f"{start_str} --> {end_str}\n")
            f.write(f"{text}\n\n")

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 transcribe_video.py <video_path>")
        sys.exit(1)

    video_path = sys.argv[1]
    base_name = os.path.splitext(os.path.basename(video_path))[0]
    output_path = f"{base_name}.srt"

    if not os.path.exists(video_path):
        print(f"Error: Video file '{video_path}' not found.")
        sys.exit(1)

    device = "cpu"
    compute_type = "float32"
    batch_size = 16 # Reduce if OOM

    print(f"Loading WhisperX 'medium' model on {device}...")
    model = whisperx.load_model("medium", device, compute_type=compute_type, language="uk")

    print(f"Loading audio from '{video_path}'...")
    audio = whisperx.load_audio(video_path)

    print("Transcribing...")
    result = model.transcribe(audio, batch_size=batch_size)
    print("Base transcription complete.")

    print("Aligning timestamps...")
    model_a, metadata = whisperx.load_align_model(language_code=result["language"], device=device)
    result = whisperx.align(result["segments"], model_a, metadata, audio, device, return_char_alignments=False)
    
    # Save as SRT
    print(f"Saving format as SRT to '{output_path}'...")
    write_srt(result["segments"], output_path)

    # Print sentences
    for idx, s in enumerate(result["segments"], start=1):
        print(f"[{idx:3d}] [{s['start']:7.2f} - {s['end']:7.2f}] {s['text'].strip()}")

    print(f"\nSaved natively to '{output_path}'")
    
    # Clean up memory
    gc.collect()

if __name__ == "__main__":
    main()

