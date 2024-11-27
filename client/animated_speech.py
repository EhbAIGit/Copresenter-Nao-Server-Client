import sys
# Add the path to Python SDK libraries for Nao
# sys.path.append('C:\\Data\\Desktop\\Repos\\EhB\\Nao_Copresenter\\client\\pythonsdk\\lib')
sys.path.append('C:\\Data\\Desktop\\Repos\\EhB\\Nao_Copresenter\\client\\pythonsdk_old')
from naoqi import ALProxy
import yaml
import threading
import time

# Custom loader for YAML that fixes double backslashes
class CustomLoader(yaml.SafeLoader):
    def construct_scalar(self, node):
        value = super(CustomLoader, self).construct_scalar(node)
        return value.replace('\\\\', '\\')

def load_yaml(file_path):
    with open(file_path, 'r') as file:
        return yaml.load(file, Loader=CustomLoader)

# Load utterances from YAML file
utterance = load_yaml('utterances.yaml')

# Connect to Nao
nao_ip = "192.168.129.8" 
nao_port = 9559   

posture = ALProxy("ALRobotPosture", nao_ip, nao_port)
animatedSpeech = ALProxy("ALAnimatedSpeech", nao_ip, nao_port)
tts = ALProxy("ALTextToSpeech", nao_ip, nao_port)
motion = ALProxy("ALMotion", nao_ip, nao_port)
leds = ALProxy("ALLeds", nao_ip, nao_port)

# Print available voices, languages, posture families, and postures
print( "voices available: "+str(tts.getAvailableVoices()) )
print( "languages available: "+ str(tts.getAvailableLanguages()))
print(tts.getParameter('pitchShift'))
print(tts.getParameter('speed'))
print ("postures family available: " + str(posture.getPostureList()))
print ("postures available: " + posture.getPostureFamily())

# Make Nao rest
motion.rest()

# Stand posture
posture.goToPosture("Stand", 1)

# Set Dutch language and voice
def Set_Dutch():
    tts.setLanguage("Dutch")
    tts.setVoice("Jasmijn22Enhanced")

# Set English language and voice
def Set_English():
    tts.setLanguage("English")
    tts.setVoice("naoenu")

# Set nuanced English voice
def Nuanced_English():
    tts.setVoice("naoenu")
    tts.setParameter("speed", 100) #Acceptable range is [50 - 400]. 100 default.
    tts.setParameter("pitchShift", 1) #Acceptable range is [0.5 - 4]. 0 disables the effect. 1 default.
    tts.setParameter("volume", 100)#[0 - 100] 70 is ok if robot volume is 60


# Recalling bookmarks from memory
class SpeechEventListener(object):
    """ A class to react to the ALTextToSpeech/CurrentBookMark event """

    def __init__(self, session):
        super(SpeechEventListener, self).__init__()
        self.memory = session.service("ALMemory")
        self.leds = session.service("ALLeds")
        self.subscriber = self.memory.subscriber("ALTextToSpeech/CurrentBookMark")
        self.subscriber.signal.connect(self.onBookmarkDetected)
        # This attribute keeps the subscriber reference alive

    def onBookmarkDetected(self, value):
        """ Callback for event ALTextToSpeech/CurrentBookMark """
        print("Event detected!")
        print("Value:", value)

        if value == 1:
            self.leds.fadeRGB("FaceLeds", 0x00FF0000, 0.2) 
        if value == 2:
            self.leds.fadeRGB("FaceLeds", 0x000000FF, 0.2)
        if value == 3:
            self.leds.fadeRGB("FaceLeds", 0x000F00FF, 0.2)            
        if value == 4:
            self.leds.fadeRGB("FaceLeds", 0x00FFFF00, 0.2)

# Set nuanced English voice settings
Nuanced_English()

autonomousLife = ALProxy("ALAutonomousLife", nao_ip, nao_port)
autonomousLife.stopAll()

print("Autonomous Life state:", autonomousLife.getState())

# Function to enforce LEDs to remain white continuously
def lock_leds_to_white():
    while True:
        leds.fadeRGB("FaceLeds", 0xFFFFFF, 0.1)  # Keep LEDs white
        time.sleep(0.1)  # Repeat every 100 ms

# Start the LED-locking thread
led_thread = threading.Thread(target=lock_leds_to_white)
led_thread.daemon = True  # Daemon thread will stop when the main program exits
led_thread.start()

# posture = ALProxy("ALRobotPosture",  nao_ip, nao_port)
# posture.setExpressiveMode(False)

leds.fadeRGB("FaceLeds", 0xFFFFFF, 0.1) 

print("Message: ", utterance['sample4'])
# Make Nao say a sample utterance
animatedSpeech.say(utterance['sample4'])

# Make Nao rest again
motion.rest()