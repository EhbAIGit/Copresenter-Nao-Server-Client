import sys
# Add the path to Python SDK libraries for Nao
sys.path.append('C:\\Users\\padin\\OneDrive\\Documents\\Github\\Nao-Client\\pythonsdk\\lib')
from naoqi import ALProxy
import yaml

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
nao_ip = "10.2.172.130" 
nao_port = 9559   

posture = ALProxy("ALRobotPosture", nao_ip, nao_port)
animatedSpeech = ALProxy("ALAnimatedSpeech", nao_ip, nao_port)
tts = ALProxy("ALTextToSpeech", nao_ip, nao_port)
motion = ALProxy("ALMotion", nao_ip, nao_port)

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
    tts.setParameter("volume", 70)#[0 - 100] 70 is ok if robot volume is 60


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


# Set nuanced English voice settings
Nuanced_English()

# Make Nao say a sample utterance
animatedSpeech.say(utterance['sample_falling'])

# Make Nao rest again
motion.rest()