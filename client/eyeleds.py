import sys
import time
import socket
import threading
import os
import yaml
import re

# Modify PYTHONPATH to access Nao's Python SDK library
sys.path.append('C:\\Data\\Desktop\\Repos\\EhB\\Nao_Copresenter\\client\\pythonsdk_old')

from naoqi import ALProxy  # Use ALProxy for NAOqi 2.1.4 compatibility

# Nao robot connection details
robot_ip =  "192.168.129.8" #"192.168.30.101" #
robot_port = 9559


behavior_proxy = ALProxy("ALBehaviorManager", robot_ip, robot_port)
memory_proxy = ALProxy("ALMemory", robot_ip, robot_port)

# Get and print all keys in ALMemory
keys = memory_proxy.getDataList("")
with open('memory_keys.txt', 'w') as f:
    for key in keys:
        f.write(key + '\n')


# Check if behavior is running
if behavior_proxy.isBehaviorRunning("leds"):
    # behavior_manager.stopBehavior("leds")
    print("Behavior is running")
else:
    print("Behavior is not running")


# List running behaviors
running_behaviors = behavior_proxy.getRunningBehaviors()
print("Running Behaviors:", running_behaviors)

if running_behaviors:
    print("Running behaviors:")
    for behavior in running_behaviors:
        print(behavior)

# # Stop behaviors potentially affecting LEDs
# for behavior in running_behaviors:
#     if "diagnostic" in behavior or "CircleEyes" in behavior:
#         behavior_proxy.stopBehavior(behavior)

# log_proxy = ALProxy("ALMemory", robot_ip, 9559)
# logs = log_proxy.getData("Log")
# print(logs)

behavior_manager = ALProxy("ALBehaviorManager", robot_ip, robot_port)
behavior_manager.stopBehavior("vub50/behavior_1")

leds = ALProxy("ALLeds", robot_ip, robot_port)
leds.reset("FaceLeds")

leds.fadeRGB("FaceLeds", 0x000000, 1.0)  # Turn off LEDs
print("LEDs turned off.")

alife = ALProxy("ALAutonomousLife", robot_ip, robot_port)
print(alife.getState())

# start_time = time.time()
# while time.time() - start_time < 3:
#     leds.fadeRGB("FaceLeds",  0x00FF7F00, 0.2)  # Yellow

# start_time = time.time()
# while time.time() - start_time < 3:
#     leds.fadeRGB("FaceLeds", 0x000000FF, 0.2)  # Blue

# start_time = time.time()
# while time.time() - start_time < 3:
#     leds.fadeRGB("FaceLeds", 0x00FF5500  , 0.2)  # Orange

# start_time = time.time()
# while time.time() - start_time < 3:
#     leds.fadeRGB("FaceLeds", 0x004CAF50, 0.2)  # Green

# start_time = time.time()
# while time.time() - start_time < 3:
#     leds.fadeRGB("FaceLeds", 0x00800080, 0.2)  # Purple

# start_time = time.time()
# while time.time() - start_time < 3:
#     leds.fadeRGB("FaceLeds", 0x00FF0000, 0.2)  # Red

# start_time = time.time()
# while time.time() - start_time < 3:
#     leds.fadeRGB("FaceLeds", 0x0000FFFF, 0.2)  # Cyan
            # elif mrk_value == 4002:
            #     leds.fadeRGB("FaceLeds", 0x000000FF, 0.2)  # Blue
            #     current_color = 0x000000FF
            # elif mrk_value == 4003:
            #     leds.fadeRGB("FaceLeds", 0x00FF3300, 0.2)  # Orange
            #     current_color = 0x00FF6700
            # elif mrk_value == 4004:
            #     leds.fadeRGB("FaceLeds", 0x004CAF50, 0.2)  # Green
            #     current_color = 0x004CAF50
            # elif mrk_value == 4005:
            #     leds.fadeRGB("FaceLeds", 0x00800080, 0.2)  # Purple
            #     current_color = 0x00800080
            # elif mrk_value == 4006:
            #     leds.fadeRGB("FaceLeds", 0x00FF0000, 0.2)  # Red
            #     current_color = 0x00FF0000
            # elif mrk_value == 4007:
            #     leds.fadeRGB("FaceLeds", 0x0000FFFF, 0.2)  # Cyan

            # Search for keys related to LEDs

keys = memory_proxy.getDataList("")
led_keys = [key for key in keys if "LED" in key or "led" in key]
print("LED-related keys:", led_keys)

memory = ALProxy("ALMemory", robot_ip, robot_port)

# List of keys to remove
keys_to_remove = [
    "_Behavior__animationsLEDCircleEyes901323760__root_3",
    "_Behavior__animationsSitWaitingZenCircles_1933589072__root_1__LED__blink__CircleEyes_3",
    "_Behavior__animationsSitReactionsTouchHead_4919780400__root_6__LED__touch__FaceLeds_1"
]

keys_to_remove = ['_Behavior__animationsLEDCircleEyes901323760__root_3__onStopped', '_Behavior__animationsLEDCircleEyes901323760__root_3/Speed', '_Behavior__animationsLEDCircleEyes901323760__root_3', '_Behavior__animationsSitWaitingZenCircles_1933589072__root_1__LED__blink__CircleEyes_3/Speed', '_Behavior__animationsSitWaitingMysticalPower_1912260320__root_10__LED__LED__CircleEyes_4/Speed', '_Behavior__animationsSitWaitingMysticalPower_1912260320__root_10__LED__LED__CircleEyes_4', '_Behavior__animationsSitReactionsTouchHead_4919780400__root_6__LED__touch__FaceLeds_1', '_Behavior__animationsSitReactionsTouchHead_11338228800__root_5__LED__touch__FaceLeds_1', '_Behavior__animationsSitReactionsTouchHead_31363107440__root_3__LED__touch__FaceLeds_1', 
'_Behavior__animationsStandWaitingVacuum_1152605720__root_8__LED__keyframe175__CircleEyes_3/Speed', '_Behavior__animationsStandEmotionsNeutralPuzzled_1148937360__root_1__onStopped', '_Behavior__animationsStandReactionsTouchHead_11009342592__root_4__LED__touch__FaceLeds_1', '_Behavior__animationsStandWaitingVacuum_1152605720__root_8__LED__keyframe175__CircleEyes_3', '_Behavior__animationsStandReactionsSeeSomething_11338726856__root_14__LED__keyframe1__blinkRandom_5', 'ALMotion/Protection/DisabledDevicesChanged', 'ALMotion/Hatch/MoveFailed', 'ALMotion/Safety/MoveFailed', '_Behavior__animationsStandReactionsTouchHead_31009957352__root_5__LED__touch__FaceLeds_1', '_Behavior__animationsSitWaitingZenCircles_1933589072__root_1__LED__blink__CircleEyes_3', '_Behavior__animationsStandReactionsTouchHead_21008089456__root_3__LED__touch__FaceLeds_1', 'ALLocalization/GoToFailed', 'packageInstalled', '_Behavior__animationsStandWaitingHelicopter_1151941584__root_1__LED__keyframe1__BlinkRandom_4', '_Behavior__animationsStandEmotionsNeutralPuzzled_1148937360__root_1', 'ALBehaviorManager/BehaviorFailed', '_Behavior__animationsStandWaitingMysticalPower_1150903912__root_10__LED__LED__CircleEyes_4', '_Behavior__animationsSitReactionsTouchHead_2157019696__root_4__LED__touch__FaceLeds_1', '_Behavior__animationsStandWaitingMysticalPower_1150903912__root_10__LED__LED__CircleEyes_4/Speed', '_Behavior__animationsStandReactionsTouchHead_41005789368__root_6__LED__touch__FaceLeds_1']

# # Remove each key
# for key in keys_to_remove:
#     try:
#         memory.removeData(key)
#         print("Removed", key)
#     except Exception as e:
#         print("Could not remove", key, "error", e)

service_manager = ALProxy("ALServiceManager", robot_ip, robot_port)

# List available methods for ALServiceManager
services = service_manager.services()
print("Registered services:", services)

while True:
    # leds.fadeRGB("FaceLeds", 0x00800080, 0.2)  # Purple    
    leds.fadeRGB("FaceLeds", 0x00FF7700      , 0.2)  # Cyan



# 0x00FF3300 Orange
# 0x00FF7700 Yellow