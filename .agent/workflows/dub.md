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
1. **Initialize Project**: Create a new DaVinci Resolve project named "translate".
   `python3 init_project.py`
2. **Import Video**: Import the target video and create the Main Timeline.
   `python3 import_video.py <video_path>`
3. **Transcribe**: Generate a JSON file with sentence-level timestamps.
   `python3 transcribe_video.py <video_path>`
4. **Agent Correction**: (PAUSE) Ask the AI agent (me) to fix transcription errors using contextual AI logic.
   `python3 correct_transcription.py <base>.json <base>_fixed.json`
5. **Agent Translation**: (PAUSE) Ask the AI agent (me) to translate the fixed transcription into English.
   `python3 translate_transcription.py <base>_fixed.json <base>_en.json`
6. **Synthesize**: Generate audio files for each translated segment using Kokoro TTS.
   `python3 synthesize_audio.py <base>_en.json`
7. **Assemble**: Place the generated audio segments onto Track 2 of the DaVinci Resolve timeline.
   `python3 assemble_timeline.py <video_name> <base>_en_audio.json`

### Крок 7: Збірка таймлінії
// turbo
8. Точний монтаж відео та аудіо на таймлінії (Track 2):
`python3 assemble_timeline.py`
