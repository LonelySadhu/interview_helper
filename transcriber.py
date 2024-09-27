import wave
import json
from vosk import Model, KaldiRecognizer

class Transcriber:
    def __init__(self, model_path):
        self.model = Model(model_path)
    
    def transcribe_audio(self, audio_file_path):
        wf = wave.open(audio_file_path, "rb")
        rec = KaldiRecognizer(self.model, wf.getframerate())
        rec.SetWords(True)
  
        result = []
        while True:
            data = wf.readframes(4000)
            if len(data) == 0:
                break
            if rec.AcceptWaveform(data):
                result.append(json.loads(rec.FinalResult()))
        wf.close()
        return result

    def write_transcription_to_file(self, audio_file_path, output_file_path):
        with open(output_file_path, "w") as f:
            for res in self.transcribe_audio(audio_file_path):
                f.write(res['text'] + "\n")

                