import usb.core
import usb.util
import array
import sys
import time
import binascii

controls_types = ['button', 'encoder', 'central_encoder', 'slider']
events_types = ['touch', 'value']
encoders_direction = ['down', 'up']
buttons_states = ['released', 'pressed']
touchs_states = ['touched', 'free']

def init():
    """Initialize Nocturn device
    Raises:
        ValueError: [description]

    Returns:
        USBInput: USB input object
        USBOutput: USB output object
    """
    dev = usb.core.find(idVendor=0x1235, idProduct=0x000a)
    if dev is None:
        raise ValueError('Novation Nocturn not found')

    if dev.is_kernel_driver_active(0):
        dev.detach_kernel_driver(0)

    cfg = dev[1]
    intf = cfg[(0,0)]

    device_input = intf[0]    
    device_output = intf[1]

    device_output.write(binascii.unhexlify("b00000"))
    device_output.write(binascii.unhexlify("28002b4a2c002e35"))
    device_output.write(binascii.unhexlify("2a022c722e30"))
    device_output.write(binascii.unhexlify("7f00"))

    for j in range(0,16):
        setButtonLED(j, 1, device_output)
        time.sleep(0.04)

    for j in range(0,16):
        setButtonLED(j, 0, device_output)
        time.sleep(0.04)

    for i in range(0,8):
        setRingLEDsMode(i,0, device_output)

    return (device_input, device_output)

def setRingLEDsMode (ring, mode, device_output):
    """Set ring LED mode

    Args:
        ring (int): ring index (0 - 7)
        mode (int): 0 starts from min, 1 from max, 2 from mid single direction, 3 MID both directions, 4 single Value and 5 single Value inverted 
        device (USB ouput): USB output object

    Raises:
        ValueError: [description]
        ValueError: [description]
    """
    if ((ring > 7) | (ring < 0)):
        raise ValueError("Invalid [ring] param (0 - 7)")
    
    if ((mode < 0) | (mode > 5)):
        raise ValueError("Invalid [mode] param (0 and 5)")

    device_output.write(chr(ring + 0x48) + chr(mode << 4))

def setRingLEDsValue (ring, value, device_output):
    """Sets the ring value

    Args:
        ring (int): [description]
        value (int): [description]
        device_output (USB ouput): USB output object

    Raises:
        ValueError: Invalid [ring] param (0 - 7)
        ValueError: Invalid [value] param (0 and 127)
    """
    if ((ring > 8) | (ring < 0)):
        raise ValueError("Invalid [ring] param (0 - 7)")
    
    if ((value < 0) | (value > 127)):
        raise ValueError("Invalid [value] param (0 and 127)")
    
    device_output.write(chr(0x40 + ring) + chr(value))
    
def setButtonLED (button, value, device_output):
    """Sets button LED state

    Args:
        button (int): button index (0 - 15)
        val (int): 0 to turn LED off and 1 to turn it on 
        device_output (USB ouput): USB output object

    Raises:
        ValueError: Invalid [button] param (0 - 15)
        ValueError: Invalid [value] param (0 - 1)
    """
    
    if ((button < 0) | (button > 15)):
        raise ValueError("Invalid [button] param (0 - 15)")
    
    if ((value == 0) | (value == 1)):
        device_output.write(chr(0x70 + button) + chr(value))
        return

    raise ValueError("Invalid [value] param (0 - 1)")

def readControlDataRaw (device_input):
    """Reads control event

    Args:
        device_input (USB input): USB input object

    Returns:
        Bytes array: Bytes array with the raw control event USB data
    """
    try:
        data = device_input.read(device_input.wMaxPacketSize,10)
        
        return data
    
    except usb.core.USBError:
        return

def parseControlEvent(event):
    
    control_id = -1
    control_type = controls_types[0]
    event_type = events_types[0]
    value = ''

    if event != None:
        event_descriptor = event[1]
        event_value = event[2]

        if event_descriptor == 82:
            control_id = 0
            control_type = controls_types[2]
            event_type = events_types[0]
            if event_value == 127:
                value = touchs_states[0]
            else:
                value = touchs_states[1]

        if event_descriptor == 74:
            control_id = 0
            control_type = controls_types[2]
            event_type = events_types[1]
            if event_value == 127:
                value = encoders_direction[0]
            else:
                value = encoders_direction[1]

        if event_descriptor == 83:
            control_id = 0
            control_type = controls_types[3]
            event_type = events_types[0]
            if event_value == 127:
                value = touchs_states[0]
            else:
                value = touchs_states[1]

        if event_descriptor == 72:
            control_id = 0
            control_type = controls_types[3]
            event_type = events_types[1]
            if event_value == 127:
                value = event_value
            else:
                value = event_value

        if event_descriptor > 63 and event_descriptor < 72:
            control_id = event_descriptor - 64
            control_type = controls_types[1]
            event_type = events_types[1]
            if event_value == 127:
                value = encoders_direction[0]
            else:
                value = encoders_direction[1]

        if event_descriptor > 111 and event_descriptor < 128:
            control_id = event_descriptor - 112
            control_type = controls_types[0]
            event_type = events_types[1]
            if event_value == 127:
                value = buttons_states[1]
            else:
                value = buttons_states[0]

    return (control_id, control_type, event_type, value)

def listen(device_input, callback):
    """Listen to control events

    Args:((
        device_input (USB input): USB input object
        callback (function): Callback function, requires data parameter
    """
    while True:
        time.sleep(0.01)
        event = readControlDataRaw(device_input)
        (control_id, control_type, event_type, value) = parseControlEvent(event)
        if control_id != -1:
            callback(control_id, control_type, event_type, value)
