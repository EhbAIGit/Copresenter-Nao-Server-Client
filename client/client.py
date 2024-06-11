import sys
# Modify PYTHONPATH to access Nao's Python SDK library
sys.path.append('C:\\Users\\padin\\OneDrive\\Documents\\Github\\Nao-Client\\pythonsdk\\lib')

import qi   # qi framework is more enhanced than NAOqi for subscribing to memory events
from naoqi import ALProxy   # for Animated Speech, because it supports "stop"
import time
import socket
import threading
import os


# Nao robot connection details
NAO_IP = "10.2.172.130"
#NAO_IP = "10.4.44.131"
NAO_PORT = 9559

# class FallDetectionModule(object):
#     """ A module to detect when the robot has fallen. """
#     def __init__(self, session):
#         self.memory = session.service("ALMemory")
#         self.motion = session.service("ALMotion")
        
#         # Enable fall manager
#         self.motion.setFallManagerEnabled(True)
        
#         # Subscribe to the robotHasFallen event
#         self.subscriber = self.memory.subscriber("robotHasFallen")
#         self.subscriber.signal.connect(self.onRobotHasFallen)

#     def onRobotHasFallen(self, value):
#         """ This will be called when the robot has fallen. """
#         print("The robot has fallen!")
#         tts.say("Ik ben gevallen, maar met een beetje hulp kan ik opstaan!")

def create_client_connection(host, port):
    client_socket = socket.socket()
    client_socket.connect((host, port))
    return client_socket

def listen_for_messages(client_socket, message_callback):
    while True:
        try:
            message = client_socket.recv(1024).decode()
            ascii_message = message.encode('ascii', 'ignore')
            if message:
                print("Received from server", ascii_message)
                message_callback(ascii_message)
                send_message(client_socket, "success")  # Send success response
            else:
                break  # If an empty string is received, close the connection
        except socket.error as e:
            print ("Socket error: ", e)
            break  # The connection was reset by the server
        except Exception as e:
            print ("An error occurred: ", e)
            break  # The socket was closed, so break out of the loop

def send_message(client_socket, message):
    client_socket.send(message.encode())

def close_connection(client_socket):
    client_socket.close()

def start_listening(client_socket, message_callback):
    thread = threading.Thread(target=listen_for_messages, args=(client_socket, message_callback))
    thread.daemon = True  # Daemon threads will shut down when the main program exits
    thread.start()

class SpeechEventListener(object):
    """ A class to react to the ALTextToSpeech/CurrentBookMark event """

    def __init__(self, session):
        super(SpeechEventListener, self).__init__()
        self.memory = session.service("ALMemory")
        self.leds = session.service("ALLeds")
        self.subscriber = self.memory.subscriber("ALTextToSpeech/CurrentBookMark")
        self.subscriber.signal.connect(self.onBookmarkDetected)
        # This attribute keeps the subscriber reference alive
        self.last_time = None  # Track the last time a bookmark was detected
        self.durations = []  # List to store durations between bookmarks 1 and 2

    def onBookmarkDetected(self, value):
        """ Callback for event ALTextToSpeech/CurrentBookMark """
        current_time = time.time()  # Get the current time
        # print("Event detected! Value:", value)

        if value == 1001:
            self.leds.fadeRGB("FaceLeds", 0x00FF0000, 0.2)
            self.last_time = current_time  # Update the last time when bookmark 1 is hit
        elif value == 1002:
            self.leds.fadeRGB("FaceLeds", 0x000000FF, 0.2)
            if self.last_time is not None:
                duration = current_time - self.last_time
                print("Duration between Bookmark 1 and 2: ", duration, " seconds")
                self.durations.append(duration)  # Store the duration in the list
                self.last_time = None  # Reset the last time
        elif value == 1003:
            self.leds.fadeRGB("FaceLeds", 0x000F00FF, 0.2)       
        elif value ==2001:
            self.motion.setAngles("HeadYaw",0, 0.3)
        elif value ==2002:
            self.motion.setAngles("HeadYaw",1.0, 0.3)

        elif value ==2003:
            self.motion.moveTo(0.5, 0.2, 0, 1, _async=True)
        elif value ==64000:
            self.motion.rest()

        elif value == 4001:     # '[Happy]': '\\mrk=4001\\', Yellow
            self.leds.fadeRGB("FaceLeds", 0x00FFFF00, 0.2) #F8D664 former color
        elif value == 4002:     # '[Sad]': '\\mrk=4002\\', Blue
            self.leds.fadeRGB("FaceLeds", 0x000000FF, 0.2)           
        elif value == 4003:     # '[Humor]': '\\mrk=4003\\, Orange
            self.leds.fadeRGB("FaceLeds", 0x00FF6700, 0.2)        
        elif value == 4004:     # '[Info]': '\\mrk=4004\\', Green
            self.leds.fadeRGB("FaceLeds", 0x004CAF50, 0.2)        
        elif value == 4005:     # '[Ponder]': '\\mrk=4005\\', Purple
            self.leds.fadeRGB("FaceLeds", 0x00800080, 0.2)        
        elif value == 4006:     # '[Privacy]': '\\mrk=4006\\', Red
            self.leds.fadeRGB("FaceLeds", 0x00FF0000, 0.2)        
        elif value == 4007:     # '[Learning]': '\\mrk=4007\\', Cyan
            self.leds.fadeRGB("FaceLeds", 0x0000FFFF, 0.2)

def handle_message(message):
    """Handle messages received from the server by initiating speech."""
    print("Received: ", message)
    # Ensure the animatedSpeech service is properly initialized and connected
    def say_in_thread(content):
        try:
            animatedSpeech.say(content)
            # animatedtts.say(content)
        except Exception as e:
            print("Error in speaking:", e)
    try:

        posture.goToPosture("Stand",1)        
        
        if not message.startswith("Internal Mandate"):
            speech_thread = threading.Thread(target=say_in_thread, args=(message,))
            speech_thread.start()
        else: 
            if message == "Internal Mandate: Silent":
                try:
                    animatedSpeech._stopAll(1)
                    # animatedtts.stop()
                except Exception as e:
                    print("Error stopping speech:", e)
            elif message == "Internal Mandate: Sit": 
                try:
                    motion.rest()
                except Exception as e:
                    print("Error stopping speech:", e)                        

    except RuntimeError as e:
        print("Runtime error:", e)



def main():

    global listener, posture, motion, animatedSpeech, session, app, animatedtts, tts

    host = socket.gethostname()
    port = 5000
    client_socket = create_client_connection(host, port)



    app = qi.Application(["SpeechEventListener", "--qi-url=tcp://{}:{}".format(NAO_IP, NAO_PORT)])
    app.start()
    session = app.session

    start_listening(client_socket, lambda message: handle_message(message))

    listener = SpeechEventListener(session)
    # fall_detection = FallDetectionModule(session)

    posture = session.service("ALRobotPosture")
    animatedSpeech = session.service("ALAnimatedSpeech")
    motion = session.service("ALMotion")
    tts = session.service("ALTextToSpeech")
    tts.setLanguage("Dutch")
    animatedtts = ALProxy("ALAnimatedSpeech", NAO_IP, NAO_PORT)
    # tts.setVoice("naoenu")

    try:
        while True:
            input("Press Ctrl+C to quit.")  # Simple prompt to keep the loop running
    except KeyboardInterrupt:
        print("Exiting program.")
        motion.rest()
    finally:     
        motion.rest()
        os._exit(0)  # This ensures termination of program and availability of terminal
        close_connection(client_socket)
        listener.unsubscribe()
        app.stop()
if __name__ == '__main__':
    main()
