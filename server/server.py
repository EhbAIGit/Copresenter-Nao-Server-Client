import os
import sys
import json
import time
import random
import socket
import threading
import warnings
import tempfile
from datetime import datetime, timezone, timedelta

import yaml
import numpy as np
import pandas as pd
import nltk
from nltk.tokenize import sent_tokenize
import sounddevice as sd
from scipy.io.wavfile import write
import usb.core
import usb.util
import re

from openai import OpenAI

warnings.filterwarnings("ignore")

# Constants
VENDOR_ID = 0x046d
PRODUCT_ID = 0xc52d
HOST = socket.gethostname()
PORT = 5000
OPENAI_KEY = open("openaikey.txt", 'r').read()

speech_controls = True
default_contextual = True

# Events for threading
start_listening_event = threading.Event()
stop_listening_event = threading.Event()
start_speaking_event = threading.Event()

# Load gestures from CSV
def load_gestures(file_path='./server/gestures_dataset/gestures.csv'):
    df = pd.read_csv(file_path, usecols=['Category', 'Gesture', 'Weight'])
    mappings = {}

    for category, group in df.groupby('Category'):
        gestures = group['Gesture'].tolist()
        weights = group['Weight'].tolist()
        mappings[category] = (gestures, weights)
    return mappings

mappings = load_gestures()

# Function to add entries to conversation log
def add_to_conversation_log(user_input, machine_response, parsed_response, file_name="conversation_log.json"):
    entry = {"user_input": user_input, "machine_response": machine_response, "parsed_response": parsed_response}
    with open(file_name, 'a') as file:
        file.write(json.dumps(entry) + '\n')

# Function to handle pointer events
def pointer_listener(device):
    global reset_conversation
    reset_conversation = False
    black_screen_pressed_time = 0
    pressed = False

    while True:
        data = device.read(endpoint.bEndpointAddress, endpoint.wMaxPacketSize, timeout=50000000)
        if data:
            if data[3] == 75:  # Previous Slide button code
                start_listening_event.set()
            elif data[3] == 0 and start_listening_event.is_set():  # Button released
                stop_listening_event.set()
            elif data[3] == 78:  # Next Slide button code
                start_speaking_event.set()
            elif data[3] == 55:  # Black screen button
                send_response(conn, "Internal Mandate: Sit")
                black_screen_pressed_time = time.time()
                pressed = True
            elif data[3] == 0 and pressed:
                press_duration = time.time() - black_screen_pressed_time             
                if press_duration >= 2:
                    print("Black Screen button released after 2 seconds: Context reset")
                    reset_conversation = True
                    pressed = False
            elif data[3] in (41, 62):  # Silent or other command
                send_response(conn, "Internal Mandate: Silent")

# Function to record audio
def record_audio(fs=44100, chunk_size=1024, min_duration=0.5):
    start_listening_event.wait()
    print("Listening started...")
    recorded_frames = []

    def callback(indata, frames, time, status):
        recorded_frames.append(indata.copy())

    with sd.InputStream(callback=callback, device=1, dtype='float32', channels=1, samplerate=fs, blocksize=chunk_size):
        while not stop_listening_event.is_set():
            time.sleep(0.1)
    stop_listening_event.clear()
    start_listening_event.clear()

    print("Listening stopped.")

    if recorded_frames:
        recording = np.concatenate(recorded_frames, axis=0)
        duration = len(recording) / fs

        if duration < min_duration:
            print("Recording dumped due to being too short.")
            return 0
        else:
            temp_file = tempfile.mktemp(prefix='recorded_audio_', suffix='.wav')
            write(temp_file, fs, recording)
            return temp_file
    return 0

# Function to create server socket
def create_server_socket(host, port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    return server_socket

# Function to accept client connection
def accept_connection(server_socket):
    conn, address = server_socket.accept()
    return conn, address

# Function to receive message from client
def receive_message(conn):
    return conn.recv(1024).decode()

# Function to send response to client
def send_response(conn, message):
    conn.send(message.encode())

# Function to close server connection
def close_server_connection(conn):
    conn.close()

# Function to tokenize sentences
def tokenize_sentences(text):
    sentences = sent_tokenize(text)
    return sentences

# Function to get random gesture choice
def get_random_choice(gesture):
    global speech_controls, default_contextual
    pause = 1000
    speed = 80
    volume = 100

    pause_marker = f"\\pau={pause}\\"
    speech_controls_markers = f"\\rspd={speed}\\ \\vol={volume}\\" if speech_controls else ""
    mode_marker = "" if default_contextual else "^mode(disabled)"

    if gesture in mappings:
        choices, weights = mappings[gesture]
        selected_choice = random.choices(choices, weights)[0]
        return f"{speech_controls_markers} ^start(animations/Stand/Gestures/{selected_choice}) {pause_marker} {mode_marker}"

# Function to replace brace and bracket contents with gestures and sentiments
def replace_bracket_contents(text):
    sentiments_dic = {
        '[happy]': '\\mrk=4001\\',
        '[sad]': '\\mrk=4002\\',
        '[humor]': '\\mrk=4003\\',
        '[info]': '\\mrk=4004\\',
        '[ponder]': '\\mrk=4005\\',
        '[privacy]': '\\mrk=4006\\',
        '[learning]': '\\mrk=4007\\'
    }

    def replace_sentiments(match):
        normalized_sentiment = match.group(0).lower()
        return sentiments_dic.get(normalized_sentiment, '')

    text = re.sub(r'\[.*?\]', replace_sentiments, text)

    def replace_braces(match):
        gesture = match.group(1)
        return get_random_choice(gesture)

    text = re.sub(r'\{([^}]+)\}', replace_braces, text)

    return text


# Set up the Logitech R400 device
device = usb.core.find(idVendor=VENDOR_ID, idProduct=PRODUCT_ID)
if device is None:
    sys.exit("Logitech Pointer not found")
else:
    print("Logitech Pointer found!")

device.set_configuration()
cfg = device.get_active_configuration()
interface_number = cfg[(0, 0)].bInterfaceNumber
alternate_setting = usb.control.get_interface(device, interface_number)
intf = usb.util.find_descriptor(cfg, bInterfaceNumber=interface_number, bAlternateSetting=alternate_setting)

endpoint = usb.util.find_descriptor(intf, custom_match=lambda e: usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_IN)
assert endpoint is not None

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_KEY)

# Load initial context from file
with open('server/context.txt', 'r', encoding='utf-8') as file:
    inhoud = file.read()

initial_messages = [{"role": "system", "content": inhoud}]
messages = initial_messages.copy()

pointer_thread = threading.Thread(target=pointer_listener, args=(device,))
pointer_thread.start()

server_socket = create_server_socket(HOST, PORT)
print("Server started. Waiting for the client...")
conn, address = accept_connection(server_socket)
print(f"Client connected from: {address}")

while True:
    if reset_conversation:
        messages = []
        messages = initial_messages.copy()
        print ("Conversation is reset")
        reset_conversation = False
    
    if start_listening_event.is_set() and not stop_listening_event.is_set():
        audio_file_path = record_audio()
        if audio_file_path:
            start_time_transcription = time.perf_counter()
            with open(audio_file_path, "rb") as audio_file:
                user_input = client.audio.transcriptions.create(
                    model="whisper-1", 
                    file=audio_file
                ).text
            end_time_transcription = time.perf_counter()
            total_time_transcription = end_time_transcription - start_time_transcription
            
            print(f"Total transcription time: {total_time_transcription:.2f} seconds, transcription: {user_input}")

            print("Prompting ChatGPT...")
            messages.append({"role": "user", "content": user_input})
            
            start_time_llm = time.perf_counter()
            # Generate a response from the model
            completion = client.chat.completions.create(
                model="gpt-4o",  # "gpt-3.5-turbo",
                messages=messages
                # max_tokens=70,
                # temperature=0.7
            )
            end_time_llm = time.perf_counter()
            total_time_llm = end_time_llm - start_time_llm
            
            print(f"Total LLM time: {total_time_llm:.2f} seconds.")
        
    if start_speaking_event.is_set() and audio_file_path:
        print("Speaking triggered")
        assistant_response = completion.choices[0].message.content
        print(assistant_response)
        
        sentences = tokenize_sentences(assistant_response)
        parsed_text = ""
        for sentence in sentences:
            parsed_sentence = replace_bracket_contents(sentence)
            # Safe mode; fall prevention
            if "BowShort_1" in parsed_sentence.strip():
                parsed_sentence += " ^wait(animations/Stand/Gestures/BowShort_1) ^pCall(ALMotion.rest())"
            parsed_text += parsed_sentence + "\n"
        print(parsed_text)
        
        ascii_text = parsed_text.encode('ascii', 'ignore').decode()
        send_response(conn, ascii_text)
        
        add_to_conversation_log(user_input, assistant_response, ascii_text)
        messages.append({"role": "assistant", "content": assistant_response})
        
        audio_thread_running = True
        start_speaking_event.clear()

