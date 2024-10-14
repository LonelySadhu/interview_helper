import wave
import json
from vosk import Model, KaldiRecognizer

class Transcriber:
    def __init__(self, model_path):
        self.model = Model(model_path)
    
    def transcribe_audio(self, audio_file_path):
        wf = wave.open(audio_file_path, "rb")

        # Убедитесь, что частота аудио совпадает с ожидаемой моделью (например, 16000 Hz)
        if wf.getnchannels() != 1:
            raise ValueError("Аудиофайл должен быть моно!")
        rec = KaldiRecognizer(self.model, wf.getframerate())
        rec.SetWords(True)

        result = []
        while True:
            data = wf.readframes(8000)  # Увеличение буфера для улучшения производительности
            if len(data) == 0:
                break
            if rec.AcceptWaveform(data):
                result.append(json.loads(rec.Result()))
            else:
                # Добавляем промежуточные результаты для повышения точности
                result.append(json.loads(rec.PartialResult()))
                
        # Обработка финальных результатов
        result.append(json.loads(rec.FinalResult()))
        wf.close()
        return result

    def write_transcription_to_file(self, audio_file_path, output_file_path):
        # Транскрибируем аудиофайл
        transcription_result = self.transcribe_audio(audio_file_path)

        # Фильтруем результаты, которые содержат текст
        text_results = [res['text'] for res in transcription_result if 'text' in res and res['text'].strip()]

        # Если нет текста, файл не создается
        if text_results:
            with open(output_file_path, "w") as f:
                for text in text_results:
                    f.write(text + "\n")
        else:
            print("Транскрипция не содержит текста. Файл не будет создан.")
