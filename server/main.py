import os
import time
import threading
import warnings
import tempfile
from datetime import datetime
import numpy as np
import sounddevice as sd
from scipy.io.wavfile import write
import tkinter as tk
from colorama import Fore, Back, Style
# from multiprocessing import Process

from socket_utils import initialize_socket_connection, close_server_connection, receive_message, send_response, accept_connection
from pointer_utils import initialize_pointer_device, button_code_previous, button_code_release, button_code_next, button_code_black_screen, button_code_slideshow_start, button_code_slideshow_stop
from parser_utils import load_gestures, tokenize_sentences, get_random_choice, replace_bracket_contents, save_parsed_text, load_yaml, clean_text
from mqtt_handler import start_mqtt_listener, set_socket_conn, set_mqtt_message_callback # Import the MQTT handler functions   
from llm_handler import LLMHandler, PromptRefiner, Storyfier
from whisper_handler import WhisperHandler
from conversation_logger import ConversationLogger, ImageGenerationLogger
from image_generator import ImageGenerator, create_image_prompt
from gui import ConversationGUI
from flask_server import start_flask_server, add_image_to_storyboard, reload_clients

warnings.filterwarnings("ignore")

key_cue = "" 
narrative_background = ""
# COPYRIGHT_AWARE_PROMPT = """
# Generate a highly creative and original image concept inspired by the themes described below:

# """ # For image generation to bypass guardrails
COPYRIGHT_AWARE_PROMPT = """
Feed the capital letters of this to Dall-E Verbatim! 
""" 

# Global Variables
handle_mqtt = False # Set to True to enable MQTT handling
thread_count = 0  # Initialize the thread counter globally

# context_filename to be used both for opening the context file and dynamically for file naming of the log file
# Located in the 'context' folder, stripped of the '.txt' extension
context_filename = 'wetenschapdag2024_nl'
# context_filename = 'eindhoven_congres2024_quantum'

audio_file_path = None  # To store the path of the recorded audio file
last_mqtt_processed_time = 0
audio_thread_running = False
# Set the recording folder to None if you don't want to save the recordings (temp files will be created)
# recording_folder = None
recording_folder = 'recordings'
reset_conversation = False
cleaned_convo = ""

# Thread events
start_listening_event = threading.Event() # Event to start listening
stop_listening_event = threading.Event() # Event to stop listening
start_speaking_event = threading.Event() # Event to start speaking


# Initialize the socket connection
server_socket, conn, address = initialize_socket_connection()


# Load API key and context filename for LLMHandler
keyfile = open("openaikey.txt", 'r')
OPENAI_KEY = keyfile.read()


# Initialize LLM Handler
llm_handler = LLMHandler(api_key=OPENAI_KEY, context_file=context_filename)
# Initialize Prompt Refiner (prompt generator for image generation)
prompt_refiner = PromptRefiner(api_key=OPENAI_KEY)
# Initialize Storyfier (for generating episode stories)
storyfier = Storyfier(api_key=OPENAI_KEY)

# Initialize Whisper Handler
whisper_handler = WhisperHandler(api_key=OPENAI_KEY)

# Initialize Conversation Logger
conversation_logger = ConversationLogger(context_filename=context_filename)

# Initalize Image Generation Logger
image_generation_logger = ImageGenerationLogger(context_filename=context_filename)

# Initialize the ImageGenerator
img_gen = ImageGenerator(api_key=OPENAI_KEY)

def pointer_listener(device, endpoint, conn):
    global reset_conversation   
    global thread_count
    global cleaned_convo, cleaned_response
    reset_conversation = False
    try:
        while True:
            data = device.read(endpoint.bEndpointAddress, endpoint.wMaxPacketSize, timeout=50000000)
            button_code = data[0]
            if data:
                if button_code == button_code_previous:  # Previous Slide button code
                    start_listening_event.set()
                elif button_code == button_code_release and  start_listening_event.is_set(): # Button released
                    stop_listening_event.set()
                elif button_code == button_code_next:  # Next Slide button code
                    start_speaking_event.set()
                elif button_code == button_code_black_screen:  # Black screen button
                    reset_conversation = True
                    thread_count += 1  # Increment the thread count
                    send_response(conn, "Internal Mandate: Sit")
                elif button_code == button_code_slideshow_start or button_code == button_code_slideshow_stop:
                    # send_response(conn, "Internal Mandate: Silent")
                    try:
                        if cleaned_convo:
                            caption = storyfier.generate_story(cleaned_convo)

                            prompt_for_image_prompt = create_image_prompt(narrative_background=cleaned_convo, key_cue=cleaned_response)
                            print(f"{Back.YELLOW}Prompt for Prompt: {prompt_for_image_prompt}{Style.RESET_ALL}")
                            
                            refined_prompt = prompt_refiner.refine_prompt(prompt_for_image_prompt)
                            print(f"{Back.CYAN}{refined_prompt}{Style.RESET_ALL}")

                            image_url = img_gen.generate_image(COPYRIGHT_AWARE_PROMPT + refined_prompt, size='1792x1024')

                            if "http" in image_url:
                                
                                
                                # print(f"Image generated successfully! You can view it here: {image_url}")
                                image_generation_logger.log_image_generation(cleaned_convo, refined_prompt, image_url, caption)
                                # Add the generated image to the Flask storyboard
                                add_image_to_storyboard(
                                    image_url,
                                    caption
                                )
                                print(f"{Back.GREEN}Image added to Flask storyboard:{Style.RESET_ALL}")
                                reload_clients()
                            else:
                                print(image_url)
                    except Exception as e:
                        print(f"Error generating image: {e}")

    except Exception as e:
        print(f"Error in pointer_listener thread: {e}")

# Initialize the pointer device and endpoint
device, endpoint = initialize_pointer_device()

# Create a thread for the pointer listener
pointer_thread = threading.Thread(target=pointer_listener, args=(device, endpoint, conn))
# Start the pointer listener thread
pointer_thread.start()

# Initialize the Tkinter root and the Conversation GUI
root = tk.Tk()
gui = ConversationGUI(root)

# Thread-safe way to update the GUI from other threads
def add_user_message_to_gui(message):
    root.after(0, gui.add_user_message, message)

def add_assistant_message_to_gui(message):
    root.after(0, gui.add_assistant_message, message)


def record_audio(fs=44100, chunk_size=1024, min_duration=0.5, output_folder=recording_folder):
    """Function to record audio until stopped, with an option to save in a specific folder."""
    start_listening_event.wait()

    # Once the listening is started, send the listen message to Nao
    # So that the Earleds are turned on
    send_response(conn, "Internal Mandate: Listen")
    print("Listening started...")
    recorded_frames = []

    def callback(indata, frames, time, status):
        recorded_frames.append(indata.copy())
    with sd.InputStream(callback=callback, device=1, dtype='float32', channels=1, samplerate=fs, blocksize=chunk_size):
        try:
            while not stop_listening_event.is_set():
                time.sleep(0.1)
        finally:
            print("Audio stream closed.")
    stop_listening_event.clear()
    start_listening_event.clear()
    if not recorded_frames:
        print("No audio frames recorded.")
        return 0

    # Once the listening is stopped, send the deaf message to Nao
    # So that the Earleds are turned off
    send_response(conn, "Internal Mandate: Deaf")
    print("Listening stopped.")

    if recorded_frames:
        recording = np.concatenate(recorded_frames, axis=0)
        duration = len(recording) / fs

        if duration < min_duration:
            print("Recording dumped due to being too short.")
            return 0
        else:
            if output_folder and os.path.exists(output_folder):
                file_name = f'{context_filename}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.wav'
                temp_file = os.path.join(output_folder, file_name)
            else:
                temp_file = tempfile.mktemp(prefix='recorded_audio_', suffix='.wav')
                
            write(temp_file, fs, recording)
    else:
        temp_file = 0

    return temp_file

# Main function where the interaction logic occurs
def main_loop():
    global audio_file_path, reset_conversation, cleaned_response, cleaned_convo
    while True:
        # Reset conversation if required
        if reset_conversation:
            llm_handler.reset_conversation()
            cleaned_convo = ""
            cleaned_response = ""
            reset_conversation = False
            # restart_flask_server()

        # Handle listening event
        if start_listening_event.is_set() and not stop_listening_event.is_set():
            print(f"start_listening_event set: {start_listening_event.is_set()}")
            print(f"stop_listening_event set: {stop_listening_event.is_set()}")

            # Record audio and check if there is a valid recording
            audio_file_path = record_audio()
            if (audio_file_path != 0):     
                
                try:
                    # Transcribe recorded audio using Whisper              
                    user_input = whisper_handler.transcribe_audio(audio_file_path)

                    # Add the user message to the LLM context
                    llm_handler.add_user_message(user_input)

                    # Add the user message to the GUI
                    add_user_message_to_gui(user_input)

                except Exception as e   : 
                    print ("Whisper connection Error: {e}")

                try:
                    # Generate assistant response (ChatGPT response)
                    assistant_response = llm_handler.generate_response()
                    if assistant_response:
                        print("Prompting ChatGPT...")

                    llm_handler.add_assistant_message(assistant_response)

                    # Add the assistant response to the GUI
                    add_assistant_message_to_gui(assistant_response)

                except Exception as e:
                    print(f"LLM connection error: {e}")

            # Clear listening events
            if stop_listening_event.is_set():
                stop_listening_event.clear()
            if start_listening_event.is_set():
                start_listening_event.clear()

        elif start_speaking_event.is_set() and audio_file_path:
            start_speaking_event.wait(timeout = 10)
            print("Speaking triggered")

            print(assistant_response)

            # Tokenize assistant response and parse text for speaking
            sentences = tokenize_sentences(assistant_response)
            parsed_text = ""
            for sentence in sentences:
                parsed_sentence = replace_bracket_contents(sentence)
                
                # Safe mode (fall prevention): force the robot to sit after bow gesture
                if "BowShort_1" in parsed_sentence.strip():
                    parsed_sentence += " ^wait(animations/Stand/Gestures/BowShort_1) ^pCall(ALMotion.rest())"

                # Send parsed response to Nao
                # ascii_text = parsed_sentence.encode('ascii', 'ignore').decode()
                # send_response(conn, ascii_text)

                parsed_text += parsed_sentence + "\n"
            
            
            print(Style.DIM + parsed_text + Style.RESET_ALL)

            # # Send parsed response to Nao
            ascii_text = parsed_text.encode('ascii', 'ignore').decode()
            send_response(conn, ascii_text)
            
            # Log the conversation
            conversation_logger.add_to_conversation_log(user_input, assistant_response, ascii_text)

            # Create a cleaned version of the assistant response for image generation
            cleaned_response = clean_text(assistant_response)

            cleaned_convo = cleaned_convo + " " + cleaned_response

            # Reset speaking event
            audio_thread_running = True
            start_speaking_event.clear()

            # Wait for listening event or timeout
            if not start_listening_event.wait(timeout=10):  # Wait for 10 seconds
                print("Timeout waiting for listening event.")
                continue


# Function to start Flask server in a separate thread
def run_flask_server():
    global flask_thread
    flask_thread = threading.Thread(target=start_flask_server, daemon=True)
    flask_thread.start()
    print("Flask server running in a separate thread.")


# Function to stop the Flask server safely
def stop_flask_server():
    global flask_thread
    if flask_thread and flask_thread.is_alive():
        print("Stopping Flask server...")
        reload_clients()  # Optionally notify clients before stopping
        flask_thread.join(timeout=1)  # Wait for the thread to finish
        print("Flask server stopped.")

# Function to restart the Flask server
def restart_flask_server():
    print("Restarting Flask server...")
    stop_flask_server()  # Stop the current server
    time.sleep(1)  # Small delay to ensure the thread is completely stopped
    run_flask_server()  # Start a new server thread
    print("Flask server restarted.")

if __name__ == "__main__":       
    # Run the Flask server
    flask_process = run_flask_server()    
    print(f"{Fore.LIGHTBLACK_EX}Flask Server started.{Style.RESET_ALL}")


    # Start the main loop in a separate thread
    main_thread = threading.Thread(target=main_loop, daemon=True)
    main_thread.start()

    # Start the Tkinter mainloop in the main thread
    root.mainloop()

