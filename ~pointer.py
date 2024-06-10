import threading
import usb.core
import usb.util
import sys
import time

# Constants
VENDOR_ID = 0x046d
PRODUCT_ID = 0xc52d


# Set up the Logitech R400 device
device = usb.core.find(idVendor=VENDOR_ID, idProduct=PRODUCT_ID)
if device is None:
    sys.exit("Logitech Pointer not found")
else:
    print("Logitech Pointer found!")

device.set_configuration()
cfg = device.get_active_configuration()
interface_number = cfg[(0, 0)].bInterfaceNumber
alternate_setting = usb.control.get_interface(device, interface_number)
intf = usb.util.find_descriptor(cfg, bInterfaceNumber=interface_number, bAlternateSetting=alternate_setting)

endpoint = usb.util.find_descriptor(intf, custom_match=lambda e: usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_IN)
assert endpoint is not None


# Function to handle pointer events
def pointer_listener(device):
    global temp, black_screen_pressed_time 
    black_screen_pressed_time = 0
    pressed = False
    temp = 0
    while True:
        data = device.read(endpoint.bEndpointAddress, endpoint.wMaxPacketSize, timeout=50000000)
        if data:
            if data[3] == 75:  # Previous Slide button code
                print("Previous Slide button pressed")
                temp = 1
            elif data[3] == 0 and temp == 1:  # Button released
                temp = 0
                print("Previous Slide button released")
            elif data[3] == 78:  # Next Slide button code
                print("Next Slide button pressed")
            elif data[3] == 55:  # Black screen button
                # if not pressed:
                black_screen_pressed_time = time.time()
                pressed = True

                print("Black Screen button pressed")
                # if pressed:
                #     if black_screen_pressed_time is not None:
                #         press_duration = time.time() - black_screen_pressed_time
                #         print (press_duration)
                #         if press_duration >= 2:
                #             print("Black Screen button released after 2 seconds")
                #             pressed = False
            elif data[3] == 0 and pressed:
                press_duration = time.time() - black_screen_pressed_time
                print (press_duration)                
                if press_duration >= 2:
                    print("Black Screen button released after 2 seconds")
                    pressed = False
            elif data[3] in (41, 62):  # Silent or other command
                print("Pause button pressed")


pointer_thread = threading.Thread(target=pointer_listener, args=(device,))
pointer_thread.start()