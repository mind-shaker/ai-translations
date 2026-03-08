import sys
import os
import requests

# --- Налаштування ---
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "YOUR_KEY_HERE")
MODEL = "google/gemini-flash-1.5:free"  # безкоштовна модель, можна змінити

PROMPT_SYSTEM = """Ти — редактор транскрибованих субтитрів. 
Тобі дають SRT файл який був автоматично транскрибований через Whisper і містить помилки.

Твоє завдання:
- Виправити невірно розпізнані слова спираючись на контекст
- Виправити граматичні помилки які виникли через неточну транскрибацію
- НЕ змінювати таймінги (рядки з -->)
- НЕ змінювати номери сегментів
- НЕ додавати і НЕ видаляти сегменти
- НЕ змінювати стиль або зміст речень — лише виправляти помилки транскрибації
- Повернути ТІЛЬКИ виправлений SRT файл без жодних коментарів, пояснень чи markdown блоків"""


def correct_srt(input_path: str, output_path: str):
    if not os.path.exists(input_path):
        print(f"Error: файл {input_path} не знайдено")
        sys.exit(1)

    with open(input_path, "r", encoding="utf-8") as f:
        srt_content = f.read()

    print(f"Завантажено: {input_path} ({len(srt_content)} символів)")
    print(f"Відправляю до OpenRouter ({MODEL})...")

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/mind-shaker/ai-translations",
    }

    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "system",
                "content": PROMPT_SYSTEM
            },
            {
                "role": "user",
                "content": f"Ось SRT файл для корекції:\n\n{srt_content}"
            }
        ],
        "temperature": 0.1,  # низька температура = більш передбачувані виправлення
    }

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=120
        )
        response.raise_for_status()
    except requests.exceptions.Timeout:
        print("Error: запит перевищив час очікування (120с)")
        sys.exit(1)
    except requests.exceptions.HTTPError as e:
        print(f"Error: HTTP {response.status_code} — {response.text}")
        sys.exit(1)

    data = response.json()

    # Перевірка на помилку від API
    if "error" in data:
        print(f"Error від OpenRouter: {data['error']}")
        sys.exit(1)

    corrected_text = data["choices"][0]["message"]["content"].strip()

    # Прибрати можливі markdown блоки якщо модель їх додала
    if corrected_text.startswith("```"):
        lines = corrected_text.split("\n")
        corrected_text = "\n".join(lines[1:-1])

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(corrected_text)

    # Статистика токенів
    usage = data.get("usage", {})
    print(f"\nГотово! Збережено: {output_path}")
    print(f"Токени: вхід={usage.get('prompt_tokens','?')}, вихід={usage.get('completion_tokens','?')}, всього={usage.get('total_tokens','?')}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 correct_srt_ai.py <input.srt> [output.srt]")
        print("       OPENROUTER_API_KEY=your_key python3 correct_srt_ai.py input.srt")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else input_path.replace(".srt", "_corrected.srt")

    if OPENROUTER_API_KEY == "YOUR_KEY_HERE":
        print("Error: встанови OPENROUTER_API_KEY")
        print("  export OPENROUTER_API_KEY=your_key")
        sys.exit(1)

    correct_srt(input_path, output_path)


if __name__ == "__main__":
    main()