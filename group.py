import re
import sys

INPUT_FILE = "how.srt"
OUTPUT_FILE = "how_grouped.srt"

SENTENCE_ENDINGS = (".", "!", "?", "…", "...", '."', '!"', '?"')


def parse_srt(path):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    segments = []
    blocks = content.strip().split("\n\n")
    for block in blocks:
        lines = [l.strip() for l in block.strip().split("\n") if l.strip()]
        if len(lines) < 3 or not lines[0].isdigit():
            continue
        m = re.match(r"(\d{2}:\d{2}:\d{2},\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2},\d{3})", lines[1])
        if not m:
            continue
        segments.append({
            "index": int(lines[0]),
            "start": m.group(1),
            "end": m.group(2),
            "text": " ".join(lines[2:])
        })
    return segments


def ends_sentence(text):
    text = text.strip()
    return any(text.endswith(e) for e in SENTENCE_ENDINGS)


def merge_segments(segments):
    merged = []
    buffer = None

    for seg in segments:
        if buffer is None:
            buffer = {
                "start": seg["start"],
                "end": seg["end"],
                "text": seg["text"]
            }
        else:
            buffer["end"] = seg["end"]
            buffer["text"] = buffer["text"] + " " + seg["text"]

        if ends_sentence(buffer["text"]):
            merged.append(buffer)
            buffer = None

    if buffer is not None:
        merged.append(buffer)

    return merged


def write_srt(segments, path):
    with open(path, "w", encoding="utf-8") as f:
        for i, seg in enumerate(segments, 1):
            f.write(f"{i}\n")
            f.write(f"{seg['start']} --> {seg['end']}\n")
            f.write(f"{seg['text']}\n\n")


def main():
    print(f"Читаю {INPUT_FILE}...")
    segments = parse_srt(INPUT_FILE)
    print(f"Сегментів до об'єднання: {len(segments)}")

    merged = merge_segments(segments)
    print(f"Сегментів після об'єднання: {len(merged)}")

    write_srt(merged, OUTPUT_FILE)
    print(f"Збережено в {OUTPUT_FILE}")

    incomplete = [s for s in merged if not ends_sentence(s["text"])]
    if incomplete:
        print(f"\nУвага: {len(incomplete)} сегментів без знаку кінця речення:")
        for s in incomplete:
            print(f"  \"{s['text'][:60]}\"")


if __name__ == "__main__":
    main()