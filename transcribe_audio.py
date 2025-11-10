import os
import whisper
import torchaudio

project_root = os.path.dirname(os.path.abspath(__file__))

class SpeechTranscriber:
    def __init__(self, model_name="small"):
        print(f"Загрузка модели Whisper ({model_name})...")
        model_dir = os.path.join(project_root, "whisper_models")
        os.makedirs(model_dir, exist_ok=True)
        self.model = whisper.load_model(model_name, download_root=model_dir)
        print("Модель Whisper успешно загружена.")

    def transcribe_wav(self, file_path):
        print(f"\nОбработка: {file_path}")
        audio = whisper.load_audio(file_path)
        audio = whisper.pad_or_trim(audio)
        mel = whisper.log_mel_spectrogram(audio).to(self.model.device)

        _, probs = self.model.detect_language(mel)
        lang = max(probs, key=probs.get)

        result = whisper.decode(self.model, mel, whisper.DecodingOptions(fp16=False))
        text = result.text.strip()
        return lang, text

    def process_segments(self, segments_dir="segments"):
        wav_files = [f for f in os.listdir(segments_dir) if f.lower().endswith(".wav")]
        if not wav_files:
            print(f"Нет WAV-файлов в {segments_dir}")
            return

        for f in wav_files:
            wav_path = os.path.join(segments_dir, f)
            lang, text = self.transcribe_wav(wav_path)

            txt_path = os.path.splitext(wav_path)[0] + ".txt"
            with open(txt_path, "w", encoding="utf-8") as out:
                out.write(text)

            print(f"✅ Распознан ({lang}): {txt_path}")
            print(f"Текст (первые 100 символов): {text[:100]}...")


if __name__ == "__main__":
    print("=== Распознавание речи в сегментах ===")
    segments_dir = os.path.join(project_root, "segments")

    if not os.path.exists(segments_dir):
        print(f"Ошибка: каталог {segments_dir} не найден.")
        exit(1)

    transcriber = SpeechTranscriber()
    transcriber.process_segments(segments_dir)
