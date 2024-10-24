import os
import wave
import json
import asyncio
from concurrent.futures import ThreadPoolExecutor
from vosk import Model, KaldiRecognizer

class Transcriber:
    def __init__(self, model_path):
        self.model = Model(model_path)
        self.executor = ThreadPoolExecutor()

    async def transcribe_audio(self, audio_file_path):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, self._transcribe_audio_sync, audio_file_path)

    def _transcribe_audio_sync(self, audio_file_path):
        wf = wave.open(audio_file_path, "rb")

        if wf.getnchannels() != 1:
            raise ValueError("The audio file must be mono!")
        rec = KaldiRecognizer(self.model, wf.getframerate())
        rec.SetWords(True)

        result = []
        while True:
            data = wf.readframes(8000)
            if len(data) == 0:
                break
            if rec.AcceptWaveform(data):
                result.append(json.loads(rec.Result()))
            else:
                result.append(json.loads(rec.PartialResult()))

        result.append(json.loads(rec.FinalResult()))
        wf.close()
        return result

    async def write_transcription_to_file(self, audio_file_path, output_file_path):
        transcription = await self.transcribe_audio(audio_file_path)
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(self.executor,
                                    self._write_transcription_to_file_sync,
                                    transcription,
                                    audio_file_path,
                                    output_file_path)

    def _write_transcription_to_file_sync(self,
                                         transcription,
                                         audio_file_path,
                                         output_file_path):
        base_name = os.path.splitext(os.path.basename(audio_file_path))[0]
        output_file_path = f'{output_file_path}\{base_name}.txt'
    
        # Filter the results that contain text
        text_results = [res['text'] for res in transcription if 'text' in res and res['text'].strip()]
        if text_results:
            with open(output_file_path, "w", encoding="utf-8") as f:
                for text in text_results:
                    f.write(text + "\n")