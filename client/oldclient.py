import sys
import time
import socket
import threading
import os
import yaml
import re

# Modify PYTHONPATH to access Nao's Python SDK library
sys.path.append('D:\\\Github\\Nao\\Copresenter-Nao-Server-Client\\client\\pythonsdk_old')

from naoqi import ALProxy  # Use ALProxy for NAOqi 2.1.4 compatibility

# Nao robot connection details
NAO_IP =  "10.2.172.127" # "192.168.129.8" #"192.168.30.101" #
NAO_PORT = 9559


# Load YAML utterances
def load_yaml(file_path):
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)

# Load utterances from YAML file
utterance = load_yaml('utterances.yaml')

def create_client_connection(host, port):
    client_socket = socket.socket()
    client_socket.connect((host, port))
    return client_socket

def listen_for_messages(client_socket, message_callback):
    while True:
        try:
            message = client_socket.recv(1024).decode()
            if message:
                # print("Received from server:", message)
                message_callback(message)
                send_message(client_socket, "success")  # Send success response
            else:
                break  # If an empty string is received, close the connection
        except (socket.error, Exception) as e:
            print("Socket error:", e)
            break  # The socket was closed or reset, so break out of the loop

def send_message(client_socket, message):
    client_socket.send(message.encode())

def close_connection(client_socket):
    client_socket.close()

def start_listening(client_socket, message_callback):
    thread = threading.Thread(target=listen_for_messages, args=(client_socket, message_callback))
    thread.daemon = True  # Daemon threads will shut down when the main program exits
    thread.start()


class SpeechEventListener:
    """ A class to react to the ALTextToSpeech/CurrentBookMark event """

    def __init__(self, memory, leds, motion):
        self.memory = memory
        self.leds = leds
        self.motion = motion
        # self.subscriber = self.memory.subscriber("ALTextToSpeech/CurrentBookMark")
        # self.subscriber.signal.connect(self.onBookmarkDetected)
        self.last_time = None  # Track the last time a bookmark was detected
        self.durations = []  # List to store durations between bookmarks 1 and 2

        # Subscribe to the "ALTextToSpeech/CurrentBookMark" event with a callback function
        self.memory.subscribeToEvent("ALTextToSpeech/CurrentBookMark", "SpeechEventListener", "onBookmarkDetected")

            
    def onBookmarkDetected(self, eventName, value, subscriberIdentifier):
        """ Callback for event ALTextToSpeech/CurrentBookMark """
        current_time = time.time()
        print("Bookmark detected:", eventName, "Value:", value)

        current_time = time.time()
        print("Bookmark detected:", value)
        # if value == 1001:
        #     self.leds.fadeRGB("FaceLeds", 0x00FF0000, 0.2)
        #     self.last_time = current_time
        # elif value == 1002 and self.last_time is not None:
        #     duration = current_time - self.last_time
        #     print("Duration between Bookmark 1 and 2:", duration, "seconds")
        #     self.durations.append(duration)
        #     self.last_time = None
        # elif value == 1003:
        #     self.leds.fadeRGB("FaceLeds", 0x000F00FF, 0.2)
        # elif value == 2001:
        #     self.motion.setAngles("HeadYaw", 0, 0.3)
        # elif value == 2002:
        #     self.motion.setAngles("HeadYaw", 1.0, 0.3)
        # elif value == 2003:
        #     self.motion.moveTo(0.5, 0.2, 0, 1, _async=True)
        # elif value == 64000:
        #     self.motion.rest()
        # elif value == 4001:
        #     self.leds.fadeRGB("FaceLeds", 0x00FFFF00, 0.2)  # Yellow
        # elif value == 4002:
        #     self.leds.fadeRGB("FaceLeds", 0x000000FF, 0.2)  # Blue
        # elif value == 4003:
        #     self.leds.fadeRGB("FaceLeds", 0x00FF6700, 0.2)  # Orange
        # elif value == 4004:
        #     self.leds.fadeRGB("FaceLeds", 0x004CAF50, 0.2)  # Green
        # elif value == 4005:
        #     self.leds.fadeRGB("FaceLeds", 0x00800080, 0.2)  # Purple
        # elif value == 4006:
        #     self.leds.fadeRGB("FaceLeds", 0x00FF0000, 0.2)  # Red
        # elif value == 4007:
        #     self.leds.fadeRGB("FaceLeds", 0x0000FFFF, 0.2)  # Cyan

def lock_eyeleds():
    """Continuously refresh EyeLEDs to maintain the current color."""
    global leds, current_color
    while True:
        try:
            leds.fadeRGB("FaceLeds", current_color, 0.1)  # Refresh LEDs with the current color
        except Exception as e:
            print("Error updating LEDs:", e)
        time.sleep(1)  # Refresh every 1 seconds

def listening_ears():
    global listening_active
    try:
        while listening_active:
            # Move the ear LEDs in a circular pattern, simulating a "listening" effect
            for angle in range(0, 360, 45):  # Change the step size to control animation smoothness
                if not listening_active:
                    break
                leds.earLedsSetAngle(angle, 0.1, True)
                time.sleep(0.1)
    except KeyboardInterrupt:
        # Turn off all ear LEDs when interrupted
        leds.off("EarLeds")
        print("Listening effect stopped.")

        
def handle_message(message):
    """Handle messages received from the server by initiating speech."""
    print("Received:", message)
    global listening_active
    global current_color
    
    def say_in_thread(content):
        try:
            tts.setLanguage("English")
            animatedSpeech.say(content)
            # animatedtts.say(content)
        except Exception as e:
            print("Error in speaking:", e)

    def say_in_thread_dutch(content):
        try:
            tts.setLanguage("Dutch")
            animatedSpeech.say(content)
        except Exception as e:
            print("Error in speaking Dutch:", e)

    def say_in_thread_french(content):  
        try:
            tts.setLanguage("French")
            animatedSpeech.say(content)
        except Exception as e:
            print("Error in speaking French:", e)

    message = message.encode("utf-8")

    try:

        # Replace newlines with spaces
        message = message.replace('\n', ' ')
        
        # Find any mrk values in the message
        match = re.search(r"\\mrk=(\d+)\\", message)


        if match:
            mrk_value = int(match.group(1))
            print("Parsed mrk value:", mrk_value)
            
            # Set LED color based on mrk value
            if mrk_value == 4001:
                leds.fadeRGB("FaceLeds", 0x00FF7700, 0.2)  # Yellow
                current_color = 0x00FF7700
            elif mrk_value == 4002:
                leds.fadeRGB("FaceLeds", 0x000000FF, 0.2)  # Blue
                current_color = 0x000000FF
            elif mrk_value == 4003:
                leds.fadeRGB("FaceLeds", 0x00FF3300, 0.2)  # Orange
                current_color = 0x00FF3300
            elif mrk_value == 4004:
                leds.fadeRGB("FaceLeds", 0x004CAF50, 0.2)  # Green
                current_color = 0x004CAF50
            elif mrk_value == 4005:
                leds.fadeRGB("FaceLeds", 0x00800080, 0.2)  # Purple
                current_color = 0x00800080
            elif mrk_value == 4006:
                leds.fadeRGB("FaceLeds", 0x00FF0000, 0.2)  # Red
                current_color = 0x00FF0000
            elif mrk_value == 4007:
                leds.fadeRGB("FaceLeds", 0x0000FFFF, 0.2)  # Cyan
                current_color = 0x0000FFFF
            else:
                print("Unrecognized mrk value:", mrk_value)

        if not message.startswith("Internal Mandate"):
            posture.goToPosture("Stand", 1)
            listening_active = False

            if "|EN|" in message:
                message = message.replace("|EN|", "")
                print("``EN``", message)
                # play_audio(message)
                try:
                    speech_thread = threading.Thread(target=say_in_thread, args=(message,))
                    speech_thread.start()
                except Exception as e:
                    print("Error in speech thread:", e)
            elif "|NL|" in message:
                message = message.replace("|NL|", "")
                print("``NL``", message)
                # play_audio(message)
                speech_thread = threading.Thread(target=say_in_thread_dutch, args=(message,))
                speech_thread.start()
            elif "|FR|" in message:
                message = message.replace("|FR|", "")
                print("``FR``", message)
                # play_audio(message)
                speech_thread = threading.Thread(target=say_in_thread_french, args=(message,))
                speech_thread.start()
            # If no language tag is found, assume English by **default**
            else:
                print("``DEFAULT NL``", message)
                # play_audio(message)
                try:
                    speech_thread = threading.Thread(target=say_in_thread_dutch, args=(message,))
                    speech_thread.start()
                except Exception as e:
                    print("Error in speech thread:", e)                
        else: 
            if message == "Internal Mandate: Silent":
                try:
                    listening_active = False
                    animatedSpeech._stopAll(1)
                    # animatedtts.stop()
                except Exception as e:
                    print("Error stopping speech:", e)
            elif message == "Internal Mandate: Sit": 
                try:
                    motion.rest()
                    listening_active = False
                except Exception as e:
                    print("Error going to rest mode:", e) 
            elif message == "Internal Mandate: Listen":
                try:
                    listening_active = True
                    thread = threading.Thread(target=listening_ears)
                    thread.daemon = True  # Set daemon to True to allow the thread to exit when the main program exits
                    thread.start()
                except Exception as e:
                    print("Error lighting up the earLeds:", e)
            elif message == "Internal Mandate: Deaf":
                try:
                    listening_active = False
                    leds.off("EarLeds")
                except Exception as e:
                    print("Error turning off earLeds:", e)

    except RuntimeError as e:
        print("Runtime error:", e)


        
def main():
    global listener, posture, motion, animatedSpeech, tts, leds
    global listening_active, current_color


    listening_active = False
    current_color = 0xFFFFFF   # White by default


    host = socket.gethostname()
    port = 5000
    client_socket = create_client_connection(host, port)

    # Establish ALProxy connections
    memory = ALProxy("ALMemory", NAO_IP, NAO_PORT)
    leds = ALProxy("ALLeds", NAO_IP, NAO_PORT)
    posture = ALProxy("ALRobotPosture", NAO_IP, NAO_PORT)
    animatedSpeech = ALProxy("ALAnimatedSpeech", NAO_IP, NAO_PORT)
    motion = ALProxy("ALMotion", NAO_IP, NAO_PORT)
    tts = ALProxy("ALTextToSpeech", NAO_IP, NAO_PORT)
    audio_device = ALProxy("ALAudioDevice",  NAO_IP, NAO_PORT)
    
    # Setting the master volume to (max = 100)
    audio_device.setOutputVolume(80)

    # Turning off autonomous life
    ALProxy("ALAutonomousLife", NAO_IP, NAO_PORT).setState("disabled")

    # Reseting the face LEDs 
    leds.reset("FaceLeds")

    # Set Dutch language
    tts.setLanguage("Dutch")

    # Initialize event listener for bookmarks
    listener = SpeechEventListener(memory, leds, motion)

    # Start listening for incoming messages from the server
    start_listening(client_socket, handle_message)

    # Start the LED-locking thread
    led_thread = threading.Thread(target=lock_eyeleds)
    led_thread.daemon = True  # Daemon thread will stop when the main program exits
    led_thread.start()

    try:
        while True:
            input("Press Ctrl+C to quit.")  # Simple prompt to keep the loop running
    except KeyboardInterrupt:
        print("Exiting program.")
        motion.rest()
    finally:
        motion.rest()
        close_connection(client_socket)
        os._exit(0)

if __name__ == '__main__':
    main()
