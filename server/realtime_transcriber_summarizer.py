import os
import numpy as np
import speech_recognition as sr
import tempfile
import openai
from scipy.io.wavfile import write
import keyboard 
from datetime import datetime, timedelta, timezone
from queue import Queue
from time import sleep

keyfile = open("openaikey.txt",'r')
OPENAI_KEY = keyfile.read()
client = openai.Client(api_key=OPENAI_KEY)

def send_to_chatbot(text):
    message = [{'role': 'user', 'content': text}]
    response = client.chat.completions.create(
        model="gpt-4o",  # Or any other suitable model
        messages=message,
        max_tokens=150
    )
    return response.choices[0].message.content


def main():
    data_queue = Queue()
    recording = False  # Flag to control recording state

    recorder = sr.Recognizer()
    recorder.energy_threshold = 1000
    recorder.dynamic_energy_threshold = False

    record_timeout = 15
    phrase_timeout = 3

    transcription = ['']
    source = sr.Microphone(sample_rate=44100)
    with source:
        recorder.adjust_for_ambient_noise(source)

    def record_callback(_, audio: sr.AudioData) -> None:
        if recording:
            data = audio.get_raw_data()
            data_queue.put(data)

    recorder.listen_in_background(source, record_callback, phrase_time_limit=record_timeout)
    print("Model loaded.\n")

    phrase_time = None

    try:
        while True:
            if keyboard.is_pressed('Ctrl+$') and not recording:
                recording = True
                print("Recording started.")
            elif keyboard.is_pressed('Ctrl+$') and recording:
                recording = False
                print("Recording stopped.")

            if not data_queue.empty() and recording:
                phrase_complete = False
                now = datetime.now(timezone.utc)
                if phrase_time and now - phrase_time > timedelta(seconds=phrase_timeout):
                    phrase_complete = True
                phrase_time = now
                
                audio_data = b''.join(data_queue.queue)
                data_queue.queue.clear()
                
                audio_np = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0
                temp_file = tempfile.mktemp(prefix='recorded_audio_', suffix='.wav')
                write(temp_file, 44100, (audio_np * 32768).astype(np.int16))

                with open(temp_file, 'rb') as audio_file:
                    transcription_response = client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file
                    )
                text = transcription_response.text

                if phrase_complete:
                    transcription.append(text)
                    os.system('cls' if os.name == 'nt' else 'clear')
                    with open('transcription.txt', 'a', encoding='utf-8') as f:
                        # for line in transcription:
                        print(text)
                        f.write(text + '\n')
                    text = ""
                else:
                    transcription[-1] = text


                # for line in transcription:
                #     print(line)


            if keyboard.is_pressed('Ctrl+Shift+é') and transcription:
                print (transcription)
                command_prompt = """This is the transcirption of a live speech given by our keynote speaker Annelies Raes.
                                    Summarize the transcription into a plain text (maximum 1000 words) without any headings in Dutch."""
                                                            

                p_u = command_prompt + " ".join(transcription)
                chatbot_response = send_to_chatbot(p_u)
                print("\nChatbot says: ", chatbot_response)
                transcription = []  # Clear transcription after sending
                with open('context.txt', 'a', encoding='utf-8') as f:
                    f.write(chatbot_response + '\n')
                while keyboard.is_pressed('c'):
                    sleep(0.1)
            else:
                sleep(0.25)
    except KeyboardInterrupt:
        print("\n\nTranscription:")
        for line in transcription:
            print(line)

if __name__ == "__main__":
    main()
