import usb.core
import usb.util
import sys

# Constants for the Logitech R400
VENDOR_ID = 0x046d
PRODUCT_ID = 0xc52d

# Find the R400 device
device = usb.core.find(idVendor=VENDOR_ID, idProduct=PRODUCT_ID)

if device is None:
    sys.exit("Device not found")
else:
    print("Device found!")

# Set the active configuration. With no arguments, the first configuration will be the active one
device.set_configuration()

# Get the endpoint instance
cfg = device.get_active_configuration()
interface_number = cfg[(0,0)].bInterfaceNumber
alternate_setting = usb.control.get_interface(device, interface_number)
intf = usb.util.find_descriptor(
    cfg, bInterfaceNumber = interface_number,
    bAlternateSetting = alternate_setting
)

endpoint = usb.util.find_descriptor(
    intf,
    # match the first OUT endpoint
    custom_match = \
    lambda e: \
        usb.util.endpoint_direction(e.bEndpointAddress) == \
        usb.util.ENDPOINT_IN
)

assert endpoint is not None

# Read data
try:
    while True:
        data = device.read(endpoint.bEndpointAddress, endpoint.wMaxPacketSize, timeout=5000)
        if data:
            if data[3] == 78:
                print("Next Slide button pressed")
            elif data[3] == 75:
                print("Previous Slide button pressed")
            elif data[3] == 55:
                print("Black Screen button pressed")
            elif data[3] == 41:
                print("Start/Stop Presentation button pressed: Paused")
            elif data[3] == 62:
                print("Start/Stop Presentation button pressed: Started")
            elif data[3] == 0:
                print("Released")
                # print(type(data))
            else:
                print(f"Unknown data: {data}")
                print(data[3])
except KeyboardInterrupt:
    print("Stopped by user")
except usb.core.USBError as e:
    print(f"USB error: {e}")
