import re
import time
import json
import requests

INPUT_FILE = "how_grouped.srt"
OUTPUT_FILE = "how_corrected.srt"

API_KEY = "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"
MODEL = "arcee-ai/trinity-large-preview:free"



BATCH_SIZE = 200       # сегментів у вибірці
RETRY_COUNT = 3
RETRY_DELAY = 30
REQUEST_DELAY = 3


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
    return any(text.strip().endswith(e) for e in (".", "!", "?", "…", "..."))


def make_batch(segments, start_idx):
    batch = []
    i = start_idx
    while i < len(segments):
        batch.append(segments[i])
        i += 1
        if len(batch) >= BATCH_SIZE:
            while i < len(segments) and not ends_sentence(batch[-1]["text"]):
                batch.append(segments[i])
                i += 1
            break
    return batch, i


def segments_to_srt(segments):
    result = ""
    for seg in segments:
        result += f"{seg['index']}\n{seg['start']} --> {seg['end']}\n{seg['text']}\n\n"
    return result.strip()


def parse_response(text):
    # Відрізаємо преамбулу — шукаємо перший рядок з числом
    lines = text.split("\n")
    start_line = 0
    for i, line in enumerate(lines):
        if line.strip().isdigit():
            start_line = i
            break
    text = "\n".join(lines[start_line:])

    # Прибираємо markdown
    if "```" in text:
        text = re.sub(r"```[a-z]*\n?", "", text).strip()

    segments = []
    blocks = text.strip().split("\n\n")
    for block in blocks:
        lines = [l.strip() for l in block.strip().split("\n") if l.strip()]
        if len(lines) < 3:
            continue
        m = re.match(r"(\d{2}:\d{2}:\d{2},\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2},\d{3})", lines[1])
        if not m:
            continue
        segments.append({
            "index": lines[0],
            "start": m.group(1),
            "end": m.group(2),
            "text": " ".join(lines[2:])
        })
    return segments


def call_api(batch_segments):
    srt_text = segments_to_srt(batch_segments)

    prompt = (
        "можеш виправити недоліки транскрибації які є в наступному srt файлі "
        "і повернути відповідь зберігаючи даний формат srt\n\n"
        + srt_text
    )

    print(f"\n--- ПРОМПТ ---\n{prompt}\n--- КІНЕЦЬ ПРОМПТУ ---\n")

    for attempt in range(1, RETRY_COUNT + 1):
        try:
            response = requests.post(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {API_KEY}",
                    "Content-Type": "application/json",
                },
                data=json.dumps({
                    "model": MODEL,
                    "messages": [{"role": "user", "content": prompt}],
                    "reasoning": {"enabled": True},
                    "temperature": 0.1,
                }),
                timeout=120
            )

            data = response.json()

            if "error" in data:
                code = response.status_code
                msg = data["error"].get("message", "")
                print(f"    Спроба {attempt}/{RETRY_COUNT}: помилка {code} — {msg}")
                if code == 429:
                    print(f"    Rate limit — чекаю {RETRY_DELAY}с...")
                    time.sleep(RETRY_DELAY)
                else:
                    time.sleep(5)
                continue

            result = data["choices"][0]["message"]["content"].strip()
            print("\n--- ВІДПОВІДЬ ---\n" + result + "\n--- КІНЕЦЬ ВІДПОВІДІ ---\n")
            return result

        except requests.exceptions.Timeout:
            print(f"    Спроба {attempt}/{RETRY_COUNT}: timeout")
            time.sleep(10)
        except Exception as e:
            print(f"    Спроба {attempt}/{RETRY_COUNT}: {e}")
            time.sleep(5)

    return None


def main():
    print(f"Читаю {INPUT_FILE}...")
    segments = parse_srt(INPUT_FILE)
    total = len(segments)
    print(f"Всього сегментів: {total}")
    print(f"Модель: {MODEL}")
    print(f"Розмір вибірки: {BATCH_SIZE} сегментів\n")

    output_segments = []
    current_idx = 0
    batch_num = 0

    while current_idx < total:
        batch, next_idx = make_batch(segments, current_idx)
        batch_num += 1

        print(f"Вибірка {batch_num}: сегменти #{batch[0]['index']}–#{batch[-1]['index']} ({len(batch)} шт.)...")

        result = call_api(batch)

        if result is None:
            print(f"  Не вдалось — записую оригінал без змін")
            output_segments.extend(batch)
        else:
            corrected = parse_response(result)
            if len(corrected) != len(batch):
                print(f"  Увага: отримано {len(corrected)} сегментів замість {len(batch)} — записую оригінал")
                output_segments.extend(batch)
            else:
                for orig, corr in zip(batch, corrected):
                    output_segments.append({
                        "index": orig["index"],
                        "start": orig["start"],
                        "end": orig["end"],
                        "text": corr["text"]
                    })
                print(f"  Готово ✓")

        current_idx = next_idx
        if current_idx < total:
            time.sleep(REQUEST_DELAY)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for seg in output_segments:
            f.write(f"{seg['index']}\n")
            f.write(f"{seg['start']} --> {seg['end']}\n")
            f.write(f"{seg['text']}\n\n")

    print(f"\nГотово! Збережено в {OUTPUT_FILE}")
    print(f"Оброблено вибірок: {batch_num}")


if __name__ == "__main__":
    main()