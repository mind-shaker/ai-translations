import re
import sys
import json
import time
import requests

# --- Налаштування ---
API_KEY = "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"
MODEL = "arcee-ai/trinity-large-preview:free"
INPUT_FILE = "how.srt"
OUTPUT_FILE = "how_grouped.srt"
MAX_SEGMENTS_PER_BATCH = 20  # максимум сегментів в одній вибірці


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
    """Перевіряє чи завершується текст реченням."""
    text = text.strip()
    return text.endswith((".", "!", "?", "…"))


def make_batch(segments, start_idx):
    """
    Формує вибірку починаючи з start_idx.
    Остання сегмент вибірки обов'язково завершений крапкою.
    """
    batch = []
    i = start_idx

    while i < len(segments):
        batch.append(segments[i])
        i += 1

        # Якщо досягли ліміту — шукаємо найближчий завершений сегмент
        if len(batch) >= MAX_SEGMENTS_PER_BATCH:
            # Якщо поточний не завершений — додаємо ще поки не знайдемо крапку
            while i < len(segments) and not ends_sentence(batch[-1]["text"]):
                batch.append(segments[i])
                i += 1
            break

        # Якщо поточний завершений і набрали хоч щось — можна зупинитись
        # але продовжуємо до MAX щоб не робити забагато запитів
        if ends_sentence(batch[-1]["text"]) and len(batch) >= MAX_SEGMENTS_PER_BATCH // 2:
            break

    # Якщо останній сегмент не завершений — додаємо поки не знайдемо крапку
    while batch and not ends_sentence(batch[-1]["text"]) and i < len(segments):
        batch.append(segments[i])
        i += 1

    return batch, i


def call_api(batch_segments):
    """Відправляє вибірку в API і отримує згруповані сегменти."""

    # Формуємо текст для API
    srt_text = ""
    for seg in batch_segments:
        srt_text += f"{seg['index']}\n{seg['start']} --> {seg['end']}\n{seg['text']}\n\n"

    prompt = f"""Тобі надано фрагмент SRT субтитрів. Твоє завдання:
1. Об'єднай сегменти які не є завершеними реченнями з наступними сегментами
2. Кожен результуючий сегмент повинен бути завершеним реченням (закінчуватись крапкою, знаком питання або знаком оклику)
3. Для об'єднаних сегментів: start береться від першого сегменту, end береться від останнього
4. Перенумеруй сегменти починаючи з {batch_segments[0]['index']}
5. НЕ змінюй текст — лише об'єднуй сегменти
6. Поверни ТІЛЬКИ готовий SRT без пояснень і без markdown блоків

Ось SRT для обробки:

{srt_text}"""

    for attempt in range(3):
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
                }),
                timeout=60
            )

            data = response.json()

            if "error" in data:
                print(f"  API помилка: {data['error']['message']}")
                if response.status_code == 429:
                    print(f"  Rate limit — чекаю 30 секунд...")
                    time.sleep(30)
                    continue
                return None

            result = data["choices"][0]["message"]["content"].strip()

            # Прибираємо markdown якщо модель додала
            if result.startswith("```"):
                lines = result.split("\n")
                result = "\n".join(lines[1:-1])

            return result

        except Exception as e:
            print(f"  Помилка запиту: {e}")
            time.sleep(10)

    return None


def main():
    print(f"Читаю {INPUT_FILE}...")
    segments = parse_srt(INPUT_FILE)
    print(f"Всього сегментів: {len(segments)}")

    output_lines = []
    current_idx = 0
    batch_num = 0
    new_segment_index = 1

    while current_idx < len(segments):
        batch, next_idx = make_batch(segments, current_idx)
        batch_num += 1

        print(f"\nВибірка {batch_num}: сегменти {batch[0]['index']}–{batch[-1]['index']} ({len(batch)} шт.)")

        result = call_api(batch)

        if result is None:
            print(f"  Пропускаю вибірку — записую як є")
            for seg in batch:
                output_lines.append(f"{new_segment_index}")
                output_lines.append(f"{seg['start']} --> {seg['end']}")
                output_lines.append(seg['text'])
                output_lines.append("")
                new_segment_index += 1
        else:
            # Перенумеровуємо отримані сегменти
            blocks = result.strip().split("\n\n")
            for block in blocks:
                lines = [l.strip() for l in block.strip().split("\n") if l.strip()]
                if len(lines) < 3:
                    continue
                output_lines.append(f"{new_segment_index}")
                output_lines.append(lines[1])  # таймінг
                output_lines.append(" ".join(lines[2:]))  # текст
                output_lines.append("")
                new_segment_index += 1

            print(f"  Отримано сегментів після групування: {len(blocks)}")

        current_idx = next_idx
        time.sleep(2)  # пауза між запитами

    # Записуємо результат
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(output_lines))

    print(f"\nГотово! Збережено в {OUTPUT_FILE}")
    print(f"Сегментів на виході: {new_segment_index - 1}")


if __name__ == "__main__":
    main()