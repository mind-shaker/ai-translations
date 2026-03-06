import json
import os
import re
import sys
import soundfile as sf

try:
    from kokoro import KPipeline
except ImportError:
    print("Error: kokoro library not found. Please install it in your virtual environment.")
    sys.exit(1)


def parse_srt(path):
    """Parse SRT file into list of segments with index, start, end, text."""
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    segments = []
    blocks = content.strip().split("\n\n")

    for block in blocks:
        lines = [l.strip() for l in block.strip().split("\n") if l.strip()]
        if len(lines) < 3:
            continue
        if not lines[0].isdigit():
            continue

        index = int(lines[0])
        time_match = re.match(
            r"(\d{2}:\d{2}:\d{2},\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2},\d{3})",
            lines[1]
        )
        if not time_match:
            continue

        start = time_match.group(1)
        end = time_match.group(2)
        text = " ".join(lines[2:])

        segments.append({
            "index": index,
            "start": start,
            "end": end,
            "text": text
        })

    return segments


def srt_time_to_seconds(t):
    """Convert SRT timestamp to float seconds."""
    h, m, rest = t.split(":")
    s, ms = rest.split(",")
    return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 synthesize_audio.py <input.srt>")
        sys.exit(1)

    input_path = sys.argv[1]

    if not input_path.lower().endswith(".srt"):
        print("Error: input file must be an .srt file")
        sys.exit(1)

    if not os.path.exists(input_path):
        print(f"Error: {input_path} not found.")
        sys.exit(1)

    base_name = os.path.splitext(os.path.basename(input_path))[0]
    output_json_path = f"{base_name}_audio.json"
    audio_dir = "audio"

    if not os.path.exists(audio_dir):
        print(f"Creating directory: {audio_dir}")
        os.makedirs(audio_dir)

    segments = parse_srt(input_path)
    total = len(segments)
    print(f"Parsed {total} segments from {input_path}")

    print("Initializing Kokoro pipeline...")
    # 'a' for American English, 'b' for British English
    pipeline = KPipeline(lang_code='a')

    print(f"Starting synthesis of {total} segments...")

    result_segments = []

    for seg in segments:
        i = seg["index"]
        text = seg["text"].strip()

        filename = f"{base_name}_{i:03d}.wav"
        filepath = os.path.join(audio_dir, filename)

        entry = {
            "index": i,
            "start": seg["start"],
            "end": seg["end"],
            "start_seconds": srt_time_to_seconds(seg["start"]),
            "end_seconds": srt_time_to_seconds(seg["end"]),
            "text": text,
            "audio_path": None
        }

        if not text:
            print(f"[{i}/{total}] Skipping empty segment")
            result_segments.append(entry)
            continue

        if os.path.exists(filepath):
            print(f"[{i}/{total}] Skipping {filename} (already exists)")
            entry["audio_path"] = filepath
            result_segments.append(entry)
            continue

        print(f"[{i}/{total}] Synthesizing: {text[:60]}...")
        try:
            generator = pipeline(text, voice='af_heart', speed=1, split_pattern=None)

            all_audio = []
            for gs, ps, audio in generator:
                all_audio.append(audio)

            if all_audio:
                import numpy as np
                merged_audio = np.concatenate(all_audio)
                sf.write(filepath, merged_audio, 24000)
                entry["audio_path"] = filepath
                print(f"          Saved: {filepath}")
            else:
                print(f"Warning: No audio generated for segment {i}")

        except Exception as e:
            print(f"Error synthesizing segment {i}: {e}")

        result_segments.append(entry)

    # Save JSON
    output = {
        "source_srt": input_path,
        "total_segments": total,
        "segments": result_segments
    }

    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    synthesized = sum(1 for s in result_segments if s["audio_path"])
    print(f"\nSynthesis complete.")
    print(f"  Audio files saved in: {audio_dir}/")
    print(f"  Segments synthesized: {synthesized}/{total}")
    print(f"  Metadata saved to:    {output_json_path}")


if __name__ == "__main__":
    main()