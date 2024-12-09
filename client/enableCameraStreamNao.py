# To activate camera top on Nao, you have to ssh to nao and then run command :
# For top camera
#  gst-launch-0.10 -v v4l2src device=/dev/video-top ! video/x-raw-yuv,width=640,height=480,framerate=30/1 ! ffmpegcolorspace ! jpegenc ! multipartmux! tcpserversink port=3000

# Or following for bottom camera :

#  gst-launch-0.10 -v v4l2src device=/dev/video-bottom ! video/x-raw-yuv,width=640,height=480,framerate=30/1 ! ffmpegcolorspace ! jpegenc ! multipartmux! tcpserversink port=3001
# You can run both in another terminal of Nao

import sys
# Modify PYTHONPATH to access Nao's Python SDK library
#sys.path.append('C:\\Users\\Padin\\OneDrive\\Desktop\\Nao\\client\\pythonsdk\\lib')
sys.path.append('D:\\Development\\NAO\\client\\pythonsdk\\lib')
import qi   # qi framework is more enhanced than NAOqi for subscribing to memory events
from naoqi import ALProxy   # for Animated Speech, because it supports "stop"

NAO_IP = "192.168.0.65" 
NAO_PORT = 9559

video_device = ALProxy("ALVideoDevice", NAO_IP, NAO_PORT)
active_clients = video_device.getSubscribers()
for client in active_clients:
    video_device.unsubscribe(client)

print("Camera disabled by unsubscribing all clients.")
