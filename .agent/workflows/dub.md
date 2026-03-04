---
description: Disciplined step-by-step DaVinci Resolve dubbing automation
---

### Крок 1: Відкрити DaVinci Resolve та ініціалізувати проект
// turbo
1. Відкрити програму DaVinci Resolve:
`open -a "DaVinci Resolve"`

// turbo
2. Створити порожній проект "translate" (видаливши старий):
`sleep 10 && python3 init_project.py`

### Крок 2: Імпорт відео та створення таймлінії
// turbo
3. Імпортувати how.mp4 та створити таймлінію:
`python3 import_video.py`

### Крок 3: Транскрибація відео
// turbo
4. Транскрибувати how.mp4 (Whisper medium, групування за реченнями):
`source /Users/olegdanilchenko1/venv_312/bin/activate && python3 transcribe_video.py`

### Крок 4: Корекція тексту
// turbo
5. Виправити помилки розпізнавання та контексту:
`python3 correct_transcription.py`

### Крок 5: Переклад англійською
// turbo
6. Перекласти транскрибацію на англійську мову:
`python3 translate_transcription.py`

### Крок 6: Озвучування (Kokoro TTS)
// turbo
7. Згенерувати аудіо для кожного сегмента:
`source /Users/olegdanilchenko1/venv_312/bin/activate && python3 synthesize_audio.py`

### Крок 7: Збірка таймлінії
// turbo
8. Точний монтаж відео та аудіо на таймлінії (Track 2):
`python3 assemble_timeline.py`
