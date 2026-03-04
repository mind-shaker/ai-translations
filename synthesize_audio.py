import json
import os
import sys
import soundfile as sf
try:
    from kokoro import KPipeline
except ImportError:
    print("Error: kokoro library not found. Please install it in your virtual environment.")
    sys.exit(1)

def main():
    input_path = "how_en.json"
    output_path = "how_en_audio.json"
    audio_dir = "audio"

    if not os.path.exists(input_path):
        print(f"Error: {input_path} not found. Run Step 5 first.")
        sys.exit(1)

    if not os.path.exists(audio_dir):
        print(f"Creating directory: {audio_dir}")
        os.makedirs(audio_dir)

    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    print("Initializing Kokoro pipeline...")
    # 'a' for American English, 'b' for British English
    pipeline = KPipeline(lang_code='a') 

    segments = data.get("segments", [])
    total = len(segments)
    print(f"Starting synthesis of {total} segments...")

    for i, segment in enumerate(segments):
        text = segment.get("text", "").strip()
        if not text:
            continue

        filename = f"en_{i+1:03d}.wav"
        filepath = os.path.join(audio_dir, filename)

        # Skip if already exists (optional, but good for resuming)
        if os.path.exists(filepath):
            print(f"[{i+1}/{total}] Skipping {filename} (already exists)")
            segment["audio_path"] = filepath
            continue

        print(f"[{i+1}/{total}] Synthesizing: {text[:50]}...")
        try:
            # generator yields (graphemes, phonemes, audio_tensor)
            generator = pipeline(text, voice='af_heart', speed=1, split_pattern=None)
            
            # Since we want one file per segment, we take the first result 
            # (or merge if split_pattern was complex, but we use None)
            all_audio = []
            for gs, ps, audio in generator:
                all_audio.append(audio)
            
            if all_audio:
                import numpy as np
                merged_audio = np.concatenate(all_audio)
                sf.write(filepath, merged_audio, 24000)
                segment["audio_path"] = filepath
            else:
                print(f"Warning: No audio generated for segment {i+1}")

        except Exception as e:
            print(f"Error synthesizing segment {i+1}: {e}")

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"\nSynthesis complete. Audio files saved in '{audio_dir}/'.")
    print(f"Updated metadata saved to '{output_path}'.")

if __name__ == "__main__":
    main()
