import json
import os

REPLACEMENTS = {
    "вчачі піти": "ChatGPT",
    "вчачі піті": "ChatGPT",
    "чаджі піті": "ChatGPT",
    "чаджі піти": "ChatGPT",
    "Чаджі Піті": "ChatGPT",
    "адліцької": "англійської",
    "синьлітою": "цим відео",
    "на лінії А1": "на рівні А1",
    "на рівня А1": "на рівні А1",
    "тусвічений": "досвідчений",
    "десі": "десять",
    "нацелати": "надсилати",
    "нацелає": "надсилає",
    "корально": "кардинально", # "вчити не окремими словами, а готовими мовними шматочками" -> maybe "ментально" or "правильно"? Actually "корально" might be "правильно".
    "детсь": "десь",
    "гіолога": "діалогу",
    "гіолог": "діалог",
    "лізькою": "англійською",
    "степільного": "стабільного",
    "промд": "промпт",
    "промді": "промпті",
    "промдів": "промптів",
    "грамитиці": "граматики",
    "граматичних": "граматичних",
    "впізнавати": "впізнавати",
    "життємові": "життєвій",
    "набільше": "найбільше",
    "радомне": "рандомне",
    "відшліфовувати": "відшліфовувати",
    "спити": "складатись", # "Спити шести речень" -> "Складатись з шести речень"
    "через эту": "через цю",
    "вівень": "рівень",
    "видавати їх": "видавати їх",
    "кліво": "кльово",
    "промки": "промпти",
    "Папа": "Па-па",
}

def correct_text(text):
    corrected = text
    for old, new in REPLACEMENTS.items():
        corrected = corrected.replace(old, new)
    return corrected

def main():
    input_path = "how.json"
    output_path = "how_fixed.json"

    if not os.path.exists(input_path):
        print(f"Error: {input_path} not found.")
        return

    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Correct top-level text
    if 'text' in data:
        data['text'] = correct_text(data['text'])

    # Correct segments while keeping timestamps
    if 'segments' in data:
        for segment in data['segments']:
            if 'text' in segment:
                segment['text'] = correct_text(segment['text'])

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Successfully saved corrected transcription to {output_path}")

if __name__ == "__main__":
    main()
