import pyaudio
import wave

# Параметры записи
FORMAT = pyaudio.paInt16  # Формат аудио
CHANNELS = 1               # Количество каналов (1 - моно, 2 - стерео)
RATE = 44100               # Частота дискретизации
CHUNK = 1024               # Размер блока
RECORD_SECONDS = 30      # Время записи в секундах
WAVE_OUTPUT_FILENAME = "recorders/output.wav"  # Имя выходного файла

if __name__ == "__main__":
    cycle = 1
    try:
        while True:
            print(f"Запись {cycle}...")
        # Инициализация PyAudio
            audio = pyaudio.PyAudio()

            # Открытие потока для записи
            stream = audio.open(format=FORMAT,
                                channels=CHANNELS,
                                rate=RATE,
                                input=True,
                                frames_per_buffer=CHUNK)

            

            frames = []

            # Запись аудио

            for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
                data = stream.read(CHUNK)
                frames.append(data)

            print(f"Запись {cycle} завершена.")

            # Остановка записи
            stream.stop_stream()
            stream.close()
            audio.terminate()
            
            filename = WAVE_OUTPUT_FILENAME.split('.')[0] + f"_{cycle}.wav"
            # Сохранение записанного аудио в WAV-файл
            with wave.open(filename, 'wb') as wf:
                wf.setnchannels(CHANNELS)
                wf.setsampwidth(audio.get_sample_size(FORMAT))
                wf.setframerate(RATE)
                wf.writeframes(b''.join(frames))

            print(f"Файл сохранен как {filename}")
            cycle += 1
    except KeyboardInterrupt:
        stream.stop_stream()
        stream.close()
        audio.terminate()
        filename = WAVE_OUTPUT_FILENAME.split('.')[0] + f"_{cycle}.wav"
        # Сохранение записанного аудио в WAV-файл
        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(audio.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(frames))

        print(f"Файл сохранен как {filename}")
        print("Цикл прерван пользователем.")