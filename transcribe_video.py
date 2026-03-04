import whisper
import json
import os
import sys

def group_by_sentence(result):
    """Groups word-level timestamps into sentences ending with . ! or ?"""
    segments = []
    current_sentence = []
    
    # We use all words from all segments to regroup them
    all_words = []
    for segment in result.get('segments', []):
        all_words.extend(segment.get('words', []))
    
    if not all_words:
        return result.get('segments', [])

    start_time = all_words[0]['start']
    
    for word_data in all_words:
        word = word_data['word']
        current_sentence.append(word.strip())
        
        # Check if the word ends with sentence-ending punctuation
        if any(word.strip().endswith(p) for p in ['.', '!', '?']):
            end_time = word_data['end']
            text = " ".join(current_sentence)
            segments.append({
                'start': start_time,
                'end': end_time,
                'text': text
            })
            # Prepare for next sentence
            current_sentence = []
            # Find index of next word if available
            idx = all_words.index(word_data)
            if idx + 1 < len(all_words):
                start_time = all_words[idx + 1]['start']
    
    # Add leftovers if any
    if current_sentence:
        segments.append({
            'start': start_time,
            'end': all_words[-1]['end'],
            'text': " ".join(current_sentence)
        })
        
    return segments

def main():
    video_path = "how.mp4"
    output_path = "how.json"

    if not os.path.exists(video_path):
        print(f"Error: Video file '{video_path}' not found.")
        sys.exit(1)

    print("Loading Whisper 'medium' model...")
    try:
        model = whisper.load_model("medium")
    except Exception as e:
        print(f"Error loading Whisper model: {e}")
        sys.exit(1)

    print(f"Starting transcription of '{video_path}' with word timestamps...")
    try:
        # We enable word_timestamps for precise sentence grouping
        result = model.transcribe(video_path, verbose=False, word_timestamps=True)
        
        # Regroup result to have sentences ending with punctuation
        print("Regrouping segments by sentences...")
        custom_segments = group_by_sentence(result)
        
        final_data = {
            'text': result['text'],
            'segments': custom_segments
        }
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(final_data, f, ensure_ascii=False, indent=2)
            
        print(f"Successfully saved transcription to '{output_path}'.")
        print(f"Total sentences found: {len(custom_segments)}")
        
    except Exception as e:
        print(f"Error during transcription: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
