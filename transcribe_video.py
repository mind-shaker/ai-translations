import whisper
import json
import os
import sys
import subprocess


def extract_audio(video_path):
    """Extract audio to WAV for stable transcription."""
    audio_path = "temp_audio.wav"
    print(f"Extracting audio to {audio_path}...")
    try:
        command = [
            "ffmpeg", "-y", "-i", video_path,
            "-ar", "16000", "-ac", "1", "-c:a", "pcm_s16le",
            audio_path
        ]
        subprocess.run(command, check=True, capture_output=True)
        return audio_path
    except Exception as e:
        print(f"Error extracting audio: {e}")
        return None


def merge_segments_into_sentences(segments):
    """
    Merge Whisper's native segments into full sentences.
    
    Key: uses segment['text'] (always complete, never loses words)
    instead of reconstructing from words[].
    Sentence boundary = text ends with . ! or ?
    """
    sentences = []
    buffer_text = ""
    buffer_words = []
    start_time = None

    for seg in segments:
        text = seg.get("text", "").strip()
        if not text:
            continue

        if start_time is None:
            start_time = seg["start"]

        buffer_text += (" " if buffer_text else "") + text
        buffer_words.extend(seg.get("words", []))

        # Check if this segment ends a sentence
        if text[-1] in ".!?":
            sentences.append({
                "id": len(sentences),
                "start": start_time,
                "end": seg["end"],
                "text": buffer_text,
                "words": buffer_words,
            })
            buffer_text = ""
            buffer_words = []
            start_time = None

    # Leftover text (no final punctuation)
    if buffer_text:
        sentences.append({
            "id": len(sentences),
            "start": start_time,
            "end": segments[-1]["end"],
            "text": buffer_text,
            "words": buffer_words,
        })

    return sentences


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 transcribe_video.py <video_path>")
        sys.exit(1)

    video_path = sys.argv[1]
    base_name = os.path.splitext(os.path.basename(video_path))[0]
    output_path = f"{base_name}.json"

    if not os.path.exists(video_path):
        print(f"Error: Video file '{video_path}' not found.")
        sys.exit(1)

    # 1. Extract audio
    audio_path = extract_audio(video_path)
    if not audio_path:
        sys.exit(1)

    # 2. Load model
    print("Loading Whisper 'medium' model...")
    model = whisper.load_model("medium")

    # 3. Transcribe
    print(f"Transcribing '{audio_path}'...")
    result = model.transcribe(
        audio_path,
        verbose=False,
        word_timestamps=True,
        language="uk",
        beam_size=5,
        best_of=5,
    )

    raw_segments = result.get("segments", [])
    print(f"Whisper returned {len(raw_segments)} raw segments.")

    # 4. Merge into sentences (text from segment['text'], NOT from words[])
    sentences = merge_segments_into_sentences(raw_segments)
    print(f"Merged into {len(sentences)} sentences.")

    # 5. Save
    output = {
        "text": result.get("text", ""),
        "language": result.get("language", ""),
        "segments": sentences,
    }
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    # Print sentences
    for s in sentences:
        print(f"[{s['id']:3d}] [{s['start']:7.2f} - {s['end']:7.2f}] {s['text']}")

    print(f"\nSaved to '{output_path}'")

    # Cleanup
    if os.path.exists(audio_path):
        os.remove(audio_path)


if __name__ == "__main__":
    main()
