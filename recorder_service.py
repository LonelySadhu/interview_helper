import pyaudio
import wave
from logger import logger

# Recording parameters
FORMAT = pyaudio.paInt16  # Audio format
CHANNELS = 1               # Number of channels (1 - mono, 2 - stereo)
RATE = 44100               # Sampling frequency
CHUNK = 1024               # Block size
RECORD_SECONDS = 30      # Recording time in seconds
WAVE_OUTPUT_FILENAME = "recorders/output.wav"  # Output file name

def record_audio():
    cycle = 1
    try:
        while True:
            logger.info(f"Recording {cycle}...")
     
            audio = pyaudio.PyAudio()

            stream = audio.open(format=FORMAT,
                                channels=CHANNELS,
                                rate=RATE,
                                input=True,
                                frames_per_buffer=CHUNK)
     
            frames = []

            for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
                data = stream.read(CHUNK)
                frames.append(data)

            logger.info(f"Recording {cycle} completed.")


            stream.stop_stream()
            stream.close()
            audio.terminate()
            
            filename = WAVE_OUTPUT_FILENAME.split('.')[0] + f"_{cycle}.wav"
            # Saving recorded audio to a WAV file
            with wave.open(filename, 'wb') as wf:
                wf.setnchannels(CHANNELS)
                wf.setsampwidth(audio.get_sample_size(FORMAT))
                wf.setframerate(RATE)
                wf.writeframes(b''.join(frames))

            logger.info(f"File save as {filename}")
            cycle += 1
    except KeyboardInterrupt:
        stream.stop_stream()
        stream.close()
        audio.terminate()
        filename = WAVE_OUTPUT_FILENAME.split('.')[0] + f"_{cycle}.wav"
       
        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(audio.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(frames))

        logger.info(f"File save as {filename}")
        logger.info("User interrupted recording!")

record_audio()