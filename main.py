import sys
import nocturn_lib

def controls_handler(control_id, control_type, event_type, value):
    print(control_id, control_type, event_type, value)

(device_input, device_output) = nocturn_lib.init()

nocturn_lib.listen(device_input, controls_handler)



