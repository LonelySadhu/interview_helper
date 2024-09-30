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
        with open(output_file_path, "w") as f:
            for res in self.transcribe_audio(audio_file_path):
                if 'text' in res:  # Убедимся, что результат содержит текст
                    f.write(res['text'] + "\n")
