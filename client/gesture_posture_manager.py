import qi
import yaml
import time
import sys

sys.path.append('C:\\Data\\Desktop\\GitHub\\EhBAI\\nao\\Nao-Client\\pythonsdk\\lib')

class SpeechEventListener(object):
    """ A class to react to the ALTextToSpeech/CurrentBookMark event """

    def __init__(self, session):
        super(SpeechEventListener, self).__init__()
        self.memory = session.service("ALMemory")
        self.leds = session.service("ALLeds")
        self.motion = session.service("ALMotion")
        self.subscriber = self.memory.subscriber("ALTextToSpeech/CurrentBookMark")
        self.subscriber.signal.connect(self.onBookmarkDetected)
        # This attribute keeps the subscriber reference alive
        self.last_time = None  # Track the last time a bookmark was detected
        self.durations = []  # List to store durations between bookmarks 1 and 2

    def onBookmarkDetected(self, value):
        """ Callback for event ALTextToSpeech/CurrentBookMark """
        current_time = time.time()  # Get the current time
        print("Event detected! Value:", value)

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
        elif value ==3000:
            # postureProxy.goToPosture("LyingBelly", 1.0)
            pass
        elif value ==64000:
            self.motion.rest()

def main():
    # Nao connection details
    nao_ip = "10.2.172.130"
    nao_port = 9559

    class CustomLoader(yaml.SafeLoader):
        def construct_scalar(self, node):
            value = super(CustomLoader, self).construct_scalar(node)
            return value.replace('\\\\', '\\')

    def load_yaml(file_path):
        with open(file_path, 'r') as file:
            return yaml.load(file, Loader=CustomLoader)

    utterance = load_yaml('utterances.yaml')

    # Initialize qi framework
    connection_url = "tcp://" + nao_ip + ":" + str(nao_port)
    app = qi.Application(["SpeechEventListener", "--qi-url=" + connection_url])
    app.start()
    session = app.session
    speech_event_listener = SpeechEventListener(session)

    # Initiaize proxies
    posture = session.service("ALRobotPosture")
    animatedSpeech = session.service("ALAnimatedSpeech")
    motion = session.service("ALMotion")
    tts = session.service("ALTextToSpeech")

    def Set_Language(language):
        # Dutch
        if language == 'Dutch':
            tts.setLanguage("Dutch")
            tts.setVoice("Jasmijn22Enhanced")

        # English
        if language == 'English':
            tts.setLanguage("English")
            tts.setVoice("naoenu")
            tts.setParameter("speed", 70) #Acceptable range is [50 - 400]. 100 default.
            tts.setParameter("pitchShift", 1) #Acceptable range is [0.5 - 4]. 0 disables the effect. 1 default.
            tts.setParameter("volume", 100)#[0 - 100] 70 is ok if robot volume is 60

        # More Nuanced English 
        if language == 'Nuanced_English':
            tts.setLanguage("English")
            tts.setVoice("naoenu")

    def print_available_modules ():
        ### available voices
        print( "voices available: "+str(tts.getAvailableVoices()) )
        print( "languages available: "+ str(tts.getAvailableLanguages()))
        print ("postures family available: " + posture.getPostureFamily())
        print ("postures available: " + str(posture.getPostureList()))  

    def save_current_posture ():
        # Put Nao in Animation Mode (via Choregraphe) and then save the current posture         
        file_name = "M_Sit1.pose"

        posture._saveCurrentPostureWithName(9946, "M_Sit1")
        custom_posture_id = 9946
        stand_posture_id = posture._getIdFromName("Stand")
        posture._addNeighbourToPosture(stand_posture_id, custom_posture_id, 1)
        posture._addNeighbourToPosture(custom_posture_id, stand_posture_id, 1)

        posture._savePostureLibrary(file_name)

        posture._loadPostureLibraryFromName(file_name)
        posture._generateCartesianMap()

    def record_durations():
        filename = 'durations/durations.txt'

        # rounding durations to two decimal points
        rounded_durations = [round(duration, 2) for duration in listener.durations]

        # Writing each duration to a file, each on a new line
        with open(filename, 'w') as file:
            for duration in rounded_durations:
                file.write("%s\n" % duration)  # Using string formatting compatible with Python 2.7

        print ("Durations saved to", filename)

        posture.goToPosture("Stand", 0.5)
        time.sleep(1)

    # # Call the saved posture here 
    # print_available_modules ()
    # save_current_posture()
    # posture.goToPosture("M_Sit1", 0.5)
    # time.sleep(2)

    # posture.goToPosture("Stand",0.2)

    # Set Nao's Language
    Set_Language('Nuanced_English')
    
    listener = SpeechEventListener(session)

    # Say an utterance from the YAML file
    animatedSpeech.say(utterance['new_maarten2'])

    # Record the durations if there is a bookmark, e.g, \mrk=1000\
    # Do not use values greater than 20. They are called erroneously in memory! 
    record_durations()
    print("Durations recorded:", listener.durations)

    # Put Nao in the rest mode after each test
    motion.rest()

    app.stop()

if __name__ == "__main__":
    try:
        main() 
    except KeyboardInterrupt:
        print("KeyboardInterrupt caught, shutting down...")
        sys.exit(0)