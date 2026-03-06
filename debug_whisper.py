import whisper
import json
import os
import sys

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 debug_whisper.py <video_path>")
        sys.exit(1)
        
    video_path = sys.argv[1]
    
    print("Loading Whisper 'medium' model...")
    model = whisper.load_model("medium")
    
    print(f"Transcribing '{video_path}'...")
    result = model.transcribe(video_path, verbose=False, word_timestamps=True)
    
    # Save the RAW result to see what Whisper actually outputs
    with open("raw_whisper.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print("Raw output saved to raw_whisper.json")

if __name__ == "__main__":
    main()
