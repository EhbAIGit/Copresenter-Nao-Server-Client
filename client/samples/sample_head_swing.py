from naoqi import ALProxy

# Set up proxies for text-to-speech and motion
tts = ALProxy("ALTextToSpeech", "10.2.172.130", 9559)
motion = ALProxy("ALMotion", "10.2.172.130", 9559)

# Make sure the robot is in a standing posture and wake up motors
motion.wakeUp()

# Define the sentences to say
sentence1 = "I am turning my head to the left."
sentence2 = "Now, I am turning my head to the right."

# Define the joint names for head yaw (left and right movement)
headYaw = "HeadYaw"

# Define angles in radians (left and right) for head movement
# These are small angles to ensure the movement is gentle
leftAngle = 0.5  # 28.6 degrees to the left
rightAngle = -0.5  # 28.6 degrees to the right

# Define the time in seconds to perform the head movement
timeToMove = 2.0  # 2 seconds

# Execute head turning to the left and speaking in parallel
motion.post.angleInterpolation(headYaw, leftAngle, timeToMove, True)
tts.say(sentence1)

# Execute head turning to the right and speaking in parallel
motion.post.angleInterpolation(headYaw, rightAngle, timeToMove, True)
tts.say(sentence2)

# Bring the head back to the center position in a non-blocking manner
motion.post.angleInterpolation(headYaw, 0, timeToMove, True)

# Go to rest position after the action is done
# Since rest() is a blocking call, no need to use post here
motion.rest()
