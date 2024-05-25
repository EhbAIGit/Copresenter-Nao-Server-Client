from naoqi import ALProxy
import time

# Replace these with your Nao's IP and port
NAO_IP = "10.2.172.130"
NAO_PORT = 9559

# Connect to the motion proxy
motion = ALProxy("ALMotion", NAO_IP, NAO_PORT)
posture = ALProxy("ALRobotPosture", NAO_IP, NAO_PORT)

# Wake up the robot
motion.wakeUp()

# Go to the Stand Init posture.
posture.goToPosture("StandInit", 0.5)

# Disable autonomous movements
motion.setBreathEnabled('Body', False)
motion.setIdlePostureEnabled('Body', False)

# Set stiffness to enable movement
motion.setStiffnesses("Body", 1.0)

# Define the target angles for the "heart" gesture (in radians)
# Shoulder pitch and roll for both arms
# Elbow yaw and roll for both arms
# Note: These angles are more of an approximation and may require adjustment
targetAngles = [0.7, 0.7,  # LShoulderPitch, RShoulderPitch
                1.5, -1.5,  # LShoulderRoll, RShoulderRoll
                -1.0, 1.0,  # LElbowYaw, RElbowYaw
                -1.2, 1.2]  # LElbowRoll, RElbowRoll

# The corresponding joints
jointNames = ["LShoulderPitch", "RShoulderPitch",
              "LShoulderRoll", "RShoulderRoll",
              "LElbowYaw", "RElbowYaw",
              "LElbowRoll", "RElbowRoll"]

# Movement speed as a fraction of maximum speed
speed = 0.2

# Execute the movement
motion.angleInterpolationWithSpeed(jointNames, targetAngles, speed)

# Keep the pose for a few seconds
time.sleep(3)

# Return to a resting position
posture.goToPosture("StandInit", 0.5)
