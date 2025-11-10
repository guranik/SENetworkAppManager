import os
import torch
import torchaudio
import datetime

project_root = os.path.dirname(os.path.abspath(__file__))

class AudioSplitter:
    def __init__(self):
        print("Загрузка модели Silero VAD...")
        self.model, self.utils = torch.hub.load(
            repo_or_dir='snakers4/silero-vad',
            model='silero_vad',
            force_reload=False,
            onnx=False
        )
        self.model.eval()

    def read_wav(self, file_path):
        waveform, sample_rate = torchaudio.load(file_path)
        return waveform, sample_rate

    def save_wav(self, file_path, data, sample_rate):
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        torchaudio.save(file_path, data, sample_rate)

    def detect_speech_segments(self, waveform, sample_rate):
        get_speech_timestamps = self.utils[0]
        speech_timestamps = get_speech_timestamps(
            waveform,
            self.model,
            sampling_rate=sample_rate,
            min_speech_duration_ms=500,
            min_silence_duration_ms=500,
            speech_pad_ms=200,
        )
        return speech_timestamps

    def split_and_save(self, input_path, output_dir="segments"):
        waveform, sample_rate = self.read_wav(input_path)
        print(f"Файл загружен: {input_path}")
        
        timestamps = self.detect_speech_segments(waveform, sample_rate)
        print(f"Найдено сегментов речи: {len(timestamps)}")

        os.makedirs(output_dir, exist_ok=True)

        for i, seg in enumerate(timestamps, 1):
            start_sample = seg['start']
            end_sample = seg['end']
            segment = waveform[:, start_sample:end_sample]

            start_time = start_sample / sample_rate
            duration = (end_sample - start_sample) / sample_rate
            start_str = str(datetime.timedelta(seconds=int(start_time))).replace(":", "-")

            out_name = f"segment_{i:03d}_start_{start_str}.wav"
            out_path = os.path.join(output_dir, out_name)
            self.save_wav(out_path, segment, sample_rate)

            print(f"Сохранён сегмент {i}: {out_path} ({duration:.2f} сек)")

        print("\n✅ Разделение завершено.")


if __name__ == "__main__":
    print("=== Разделение WAV-файла на речевые сегменты ===")

    input_dir = os.path.join(project_root, "input")
    output_dir = os.path.join(project_root, "segments")

    if not os.path.exists(input_dir):
        print(f"Ошибка: каталог {input_dir} не найден. Создайте папку и поместите туда WAV-файл.")
        exit(1)

    wav_files = [f for f in os.listdir(input_dir) if f.lower().endswith(".wav")]

    if not wav_files:
        print(f"Нет WAV-файлов в {input_dir}.")
        exit(1)

    splitter = AudioSplitter()

    for file in wav_files:
        input_path = os.path.join(input_dir, file)
        splitter.split_and_save(input_path, output_dir)
