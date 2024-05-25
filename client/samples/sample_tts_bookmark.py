import qi

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

if __name__ == "__main__":
    # Nao connection details
    nao_ip = "10.2.172.130"
    nao_port = 9559

    # Initialize qi framework
    connection_url = "tcp://" + nao_ip + ":" + str(nao_port)
    app = qi.Application(["SpeechEventListener", "--qi-url=" + connection_url])
    app.start()
    session = app.session
    speech_event_listener = SpeechEventListener(session)

    tts = session.service("ALTextToSpeech")
    while True:
        tts.say("Put that \\mrk=3\\ there.")
