import paho.mqtt.client as mqttclient
import time
import naoqi
from naoqi import ALProxy
broker = "broker.emqx.io"
nao_host = "localhost"
nao_port = 9559
import math
import threading

tts = ALProxy("ALTextToSpeech", nao_host, nao_port)
animatedTts = ALProxy("ALAnimatedSpeech", nao_host, nao_port)
motion = ALProxy("ALMotion", nao_host, nao_port)
posture = ALProxy("ALRobotPosture", nao_host, nao_port)
asr = ALProxy("ALSpeechRecognition", nao_host, nao_port)
behavior = ALProxy("ALBehaviorManager", nao_host, nao_port)
leds = ALProxy("ALLeds",nao_host,nao_port)
AutonomousAbility = ALProxy("ALAutonomousLife",nao_host,nao_port)
AutonomousAbility.setAutonomousAbilityEnabled("BasicAwareness", False)
volume = ALProxy("ALAudioDevice",nao_host,nao_port)

#TODO 
def say_in_thread(content):
    try:
        animatedTts.say(content)
    except Exception as e:
        print("Error in speaking:", e)

def extract_ip():
    st = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        st.connect(('10.255.255.255', 1))
        IP = st.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        st.close()
    return IP


def setLanguage(setLanguage):
    global tts,language
    tts.setLanguage(setLanguage)
    language=setLanguage

def launchAndStopBehavior(behavior_mng_service, behavior_name):
    """
    Launch and stop a behavior, if possible.
    """
    # Check that the behavior exists.
    if (behavior_mng_service.isBehaviorInstalled(behavior_name)):
        # Check that it is not already running.
        if (not behavior_mng_service.isBehaviorRunning(behavior_name)):
            # Launch behavior. This is a blocking call, use _async=True if you do not
            # want to wait for the behavior to finish.
            behavior_mng_service.runBehavior(behavior_name, _async=True)
            time.sleep(0.5)
        else:
            print "Behavior is already running."

    else:
        print "Behavior not found."
    return


topics = ['NAO/POSTURE','NAO/SAY','NAO/MOTION','NAO/BATTERY','NAO/LANGUAGE','NAO/VOCABULARY','NAO/VOLUME','NAO/LISTEN','NAO/EARLEDS','NAO/POSEBALL','NAO/POSEBALLINTRO','NAO/WALK', 'NAO/STOP_SPEAKING']
language="Dutch"


def on_publish(client,userdata,mid):
    print("Message Published")



def on_message(client, userdata, message):
    #TODO
    global tts,animatedTts
    
    content = str(message.payload.decode("utf-8"))
    topic =  str(message.topic.decode("utf-8"))
    print("message topic=",topic)
    print("message received ", content)

    #REVISE
    if (topic == "NAO/SAY") :
        #REVISE
        # Start the speech in a new thread
        speech_thread = threading.Thread(target=say_in_thread, args=(content,))
        speech_thread.start()

    elif topic == "NAO/STOP_SPEAKING":
        try:
            # This will stop any ongoing speech. However, note that
            # you may need additional logic to cleanly interrupt and join the thread.
            animatedTts.stop()
        except Exception as e:
            print("Error stopping speech:", e)


    if (topic == "NAO/LANGUAGE") :
        global tts
        if (content == "NL") :
            tts.setLanguage("Dutch")
        if (content == "FR") :
            tts.setLanguage("French")
        if (content == "EN") :
            tts.setLanguage("English")


    if (topic == "VOCABULARY") :
        global vocabulary,asr,language
        asr.setLanguage(language)
        asr.pause(True)
        vocabulary = content.split("|")
        asr.setVocabulary(vocabulary, False)

    if (topic == "NAO/POSTURE") :
        global posture
        posture.goToPosture(content,1)
	

    if (topic == "NAO/WALK") :
        global motion

        if (content != "") : 

            x_str, y_str, z_str = content.split(",")
            x = float(x_str)
            y = float(y_str)
            z = float(z_str)
    
            # Perform the motion with the specified speed
            motion.moveTo(x, y, z, 1, _async=True)

            # Wait for a moment to complete the motion
            time.sleep(2.0)  # Adjust the time as needed


    if (topic == "NAO/MOTION") :
        global motion
        if (content == "REST") :
            motion.rest()
        if (content == "HEADLEFT") :
            motion.setAngles("HeadYaw",1.0, 0.3)
        if (content == "HEADRIGHT") :
            motion.setAngles("HeadYaw",-1.0, 0.3)
        if (content == "HEADFRONT") :
            motion.setAngles("HeadYaw",0, 0.3)
        if (content == "DANCE"):
            behavior.startBehavior("animations/Stand/Waiting/FunnyDancer_1")
        if (content == "TURNLEFT"):
           angle_to_turn = math.radians(-30)
           max_speed_fraction = 0.2  # Adjust the speed as needed (0.0 to 1.0)
           # Set the target angles for the motion
           left_leg = [0.0, 0.0, -angle_to_turn]
           right_leg = [0.0, 0.0, angle_to_turn]

           # Perform the motion with the specified speed
           #motion.angleInterpolationWithSpeed("LHipYawPitch", left_leg,max_speed_fraction)
           #motion.angleInterpolationWithSpeed("RHipYawPitch", right_leg, max_speed_fraction)
           motion.moveTo(0.5,0.0,1, _async=True)

           # Wait for a moment to complete the motion
           time.sleep(2.0)  # Adjust the time as needed

    if (topic == "EARLEDS") :
        global leds
        if (content == "ON") :
            leds.fade('EarLeds', 1, 0.1)
            leds.fade('FaceLeds', 1, 0.1)
        if (content == "OFF") :
            leds.fade('EarLeds', 0, 0.1)
            leds.fade('FaceLeds', 0, 0.1)

    if (topic == "NAO/BATTERY") :
        global nao_host, nao_port,tts
        if (content == "BATTERY") :
            battery = ALProxy("ALBattery", nao_host, nao_port)
            batteryLevel = battery.getBatteryCharge()
            tts.say("Mijn batterijniveau is")
            tts.say(str(batteryLevel))
            tts.say("percent")

      # Choregraphe simplified export in Python.

    if (topic == "NAO/POSEBALL") :
        launchAndStopBehavior(behavior, "poseballdemonstration-10f799/behavior_1")
    if (topic == "NAO/POSEBALLINTRO") :
        launchAndStopBehavior(behavior, "saxintro-6660d6/behavior_1")

    if (topic == "NAO/VOLUME") :
      newVolume = int(content)
      volume.setOutputVolume(newVolume)
      tts.say("Volume" + content)
    
    client.publish("NAO/DONE","FINISHED")
     

tts.say("Ik ben opgestart.")



client=mqttclient.Client("Client1")
client.connect(broker)
client.loop_start() #start the loop

for topic in topics :
    client.subscribe(topic)

client.on_message=on_message #attach function to callback
client.on_publish=on_publish
time.sleep(3600)
client.loop_stop() #stop the loop

