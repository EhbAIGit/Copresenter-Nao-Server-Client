import usb.core
import usb.util
import sys

# Constants for button codes
button_code_previous = 8
button_code_release = 0
button_code_next = 16
button_code_black_screen = 2
button_code_slideshow_start = 4
button_code_slideshow_stop = 1

# Constants for Logitech R400 device
vendor_id = 0x046d
product_id = 0xc538

# Function to initialize pointer device and endpoint
def initialize_pointer_device():
    device = usb.core.find(idVendor=vendor_id, idProduct=product_id)
    if device is None:
        sys.exit("Logitech Pointer not found")
    else:
        print("Logitech Pointer found!")
    
    # Set the active configuration. With no arguments, the first configuration will be the active one
    device.set_configuration()
    
    # Get the endpoint instance
    cfg = device.get_active_configuration()
    interface_number = cfg[(0, 0)].bInterfaceNumber
    alternate_setting = usb.control.get_interface(device, interface_number)
    intf = usb.util.find_descriptor(
        cfg, bInterfaceNumber=interface_number,
        bAlternateSetting=alternate_setting
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
    return device, endpoint