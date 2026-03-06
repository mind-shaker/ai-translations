import sys
import re

def parse_srt(path):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    blocks = content.strip().split("\n\n")
    parsed = []

    for block in blocks:
        lines = block.split("\n")
        if len(lines) >= 3:
            idx = lines[0]
            time = lines[1]
            text = " ".join(lines[2:])
            parsed.append({"idx": idx, "time": time, "text": text})

    return parsed

def merge_sentences(subs):
    merged = []
    buffer_text = ""
    start_time = None
    end_time = None

    for sub in subs:
        text = sub["text"].strip()
        if not text:
            continue

        if start_time is None:
            start_time = sub["time"].split(" --> ")[0]

        buffer_text += (" " if buffer_text else "") + text
        end_time = sub["time"].split(" --> ")[1]

        # якщо текст закінчується на крапку, знак оклику чи питання
        if re.search(r"[.!?]$", text):
            merged.append({
                "start": start_time,
                "end": end_time,
                "text": buffer_text.strip()
            })
            buffer_text = ""
            start_time = None
            end_time = None

    # залишок тексту без кінцевого знаку
    if buffer_text:
        merged.append({
            "start": start_time,
            "end": end_time,
            "text": buffer_text.strip()
        })

    return merged

def write_srt(subs, output_path):
    with open(output_path, "w", encoding="utf-8") as f:
        for i, sub in enumerate(subs, 1):
            f.write(f"{i}\n")
            f.write(f"{sub['start']} --> {sub['end']}\n")
            f.write(f"{sub['text']}\n\n")

def main():
    if len(sys.argv) < 2:
        print("Usage: python combine_sentences.py <input.srt>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = input_file.replace(".srt", "_fixed.srt")

    subs = parse_srt(input_file)
    merged = merge_sentences(subs)
    write_srt(merged, output_file)
    print(f"Saved merged SRT to '{output_file}'")

if __name__ == "__main__":
    main()