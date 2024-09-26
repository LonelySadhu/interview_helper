import pyaudio
import wave
import whisper
import openai

# 1. Запись аудио
def record_audio(filename, duration=5):
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000
    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
    print("Recording...")

    frames = []

    for _ in range(0, int(RATE / CHUNK * duration)):
        data = stream.read(CHUNK)
        frames.append(data)

    print("Recording finished.")

    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(filename, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

# 2. Преобразование аудио в текст с Whisper
def transcribe_audio(filename):
    model = whisper.load_model("base")  # Можно выбрать "small", "medium", "large"
    result = model.transcribe(filename)
    return result["text"]

# 3. Генерация ответа с помощью GPT
openai.api_key = "your-api-key"

def generate_response(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # или "gpt-4"
        messages=[{"role": "system", "content": "Ты ассистент на собеседовании."},
                  {"role": "user", "content": prompt}]
    )
    return response['choices'][0]['message']['content']

# Запуск пайплайна
filename = "output.wav"
record_audio(filename, duration=5)  # Записываем аудио
text_from_audio = transcribe_audio(filename)  # Преобразуем аудио в текст
print("Распознанный текст:", text_from_audio)

response = generate_response(text_from_audio)  # Генерируем ответ с помощью GPT
print("Ответ от GPT:", response)
