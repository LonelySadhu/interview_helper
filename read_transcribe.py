import os
from time import sleep
from transcriber import Transcriber

# Укажите путь к папке
audio_files_path = 'recorders'
output_file_path = 'transcribers'


if __name__ == '__main__':
    
    audio_files = sorted([f for f in os.listdir(audio_files_path) if f.endswith('.wav')])
    transcriber = Transcriber('model')
    for file in audio_files:
        transcriber.write_transcription_to_file(os.path.join(audio_files_path, file), 
                                                os.path.join(output_file_path,
                                                               f'{file.split(".")[0]}.txt')) 
    while True:
        sleep(5)  
        new_audio_files = sorted([f for f in os.listdir(audio_files_path) if f.endswith('.wav')])
        if new_audio_files != audio_files:
            for file in new_audio_files:
                if file not in audio_files:
                    transcriber.write_transcription_to_file(os.path.join(audio_files_path, file),
                                                 os.path.join(output_file_path,
                                                               f'{file.split(".")[0]}.txt'))
                audio_files = new_audio_files
        else:
            print("Waiting new audio files...\n")
                    
