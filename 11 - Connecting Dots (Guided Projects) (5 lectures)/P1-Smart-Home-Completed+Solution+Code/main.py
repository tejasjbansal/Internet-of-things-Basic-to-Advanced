import time
from EdgeServer import EdgeServer
from LightDevice import LightDevice
from ACDevice import ACDevice

WAIT_TIME = 0.20
ROOM_LIST = ["Kitchen", "Garage", "Living Room", "BR1", "BR2"]
DEVICE_TYPE = ["LIGHT", "AC"]

print("\nSmart Home Simulation started.")
# Creating the edge-server for the communication with the user

edge_server_1 = EdgeServer('edge_server_1')
time.sleep(WAIT_TIME)  

print('\n******************* REGISTRATION OF THE DEVICES THROUGH SERVER *******************')

# Creating the light_device
print('\n******************* REGISTRATION OF LIGHT DEVICES INITIATED *******************')

light_device_1 = LightDevice("light_1", "Kitchen")
time.sleep(WAIT_TIME)  
light_device_2 = LightDevice("light_2", "Garage")
time.sleep(WAIT_TIME)
light_device_3 = LightDevice("light_3", "Living Room")
time.sleep(WAIT_TIME)
light_device_4 = LightDevice("light_4", "BR1")
time.sleep(WAIT_TIME)
light_device_5 = LightDevice("light_5", "BR2")
time.sleep(WAIT_TIME)
light_device_6 = LightDevice("light_6", "Living Room")
time.sleep(WAIT_TIME)
light_device_7 = LightDevice("light_7", "Living Room")
time.sleep(WAIT_TIME)

# Creating the ac_device
print('\n******************* REGISTRATION OF AC DEVICES INITIATED *******************')

ac_device_1 = ACDevice("ac_1", "BR1")
time.sleep(WAIT_TIME)  
ac_device_2 = ACDevice("ac_2", "BR2")
time.sleep(WAIT_TIME)
ac_device_3 = ACDevice("ac_3", "Living Room")
time.sleep(WAIT_TIME*2)
ac_device_4 = ACDevice("ac_4", "Living Room")
time.sleep(WAIT_TIME*2)

print('\n******************* REGISTRATION DEVICES ON THE SERVER *******************')
print('\nFetching the list of registered devices from EdgeServer :')
print('Registered device on Edge Server :')

registered_device_list = edge_server_1.get_registered_device_list()
for registered_device in registered_device_list:
    print(registered_device)

print('\n******************* GETTING THE STATUS AND CONTROLLING THE DEVICES *******************')

print('\n******************* GETTING THE STATUS BY DEVICE_ID *******************')
cmd = 1
edge_server_1.get_status(cmd, 'device_id', 'light_1')
time.sleep(WAIT_TIME)

cmd += 1
edge_server_1.get_status(cmd, 'device_id', 'light_2')
time.sleep(WAIT_TIME)

cmd += 1
edge_server_1.get_status(cmd, 'device_id', 'light_3')
time.sleep(WAIT_TIME)

cmd += 1
edge_server_1.get_status(cmd, 'device_id', 'light_4')
time.sleep(WAIT_TIME)

cmd += 1
edge_server_1.get_status(cmd, 'device_id', 'light_5')
time.sleep(WAIT_TIME)

cmd += 1
edge_server_1.get_status(cmd, 'device_id', 'ac_1')
time.sleep(WAIT_TIME)

cmd += 1
edge_server_1.get_status(cmd, 'device_id', 'ac_2')
time.sleep(WAIT_TIME)

cmd += 1
edge_server_1.get_status(cmd, 'device_id', 'ac_3')
time.sleep(WAIT_TIME*2)

print('\n******************* GETTING THE STATUS BY DEVICE_TYPE *******************')
cmd += 1
edge_server_1.get_status(cmd, 'device_type', 'LIGHT')
time.sleep(WAIT_TIME)

cmd += 1
edge_server_1.get_status(cmd, 'device_type', 'AC')
time.sleep(WAIT_TIME)

print('\n******************* GETTING THE STATUS BY ROOM_TYPE *******************')

cmd += 1
edge_server_1.get_status(cmd, 'room', 'Kitchen')
time.sleep(WAIT_TIME)

cmd += 1
edge_server_1.get_status(cmd, 'room', 'BR1')
time.sleep(WAIT_TIME)

cmd += 1
edge_server_1.get_status(cmd, 'room', 'BR2')
time.sleep(WAIT_TIME)

cmd += 1
edge_server_1.get_status(cmd, 'room', 'Living Room')
time.sleep(WAIT_TIME)

cmd += 1
edge_server_1.get_status(cmd, 'room', 'Garage')
time.sleep(WAIT_TIME)

print('\n******************* GETTING THE STATUS FOR ENTIRE HOME *******************')

cmd += 1
edge_server_1.get_status(cmd, 'all', 'all')
time.sleep(WAIT_TIME)

print('\n******************* SETTING  THE STATUS AND CONTROLLING THE DEVICE  *******************')

print('\n******* SETTING DEVICE STATUS (ON or OFF BY DEVICE ID *********')
cmd += 1
edge_server_1.set_status(cmd, 'device_id', 'light_1', 'ON')
time.sleep(WAIT_TIME)

cmd += 1
edge_server_1.set_status(cmd, 'device_id', 'ac_1', 'ON')
time.sleep(WAIT_TIME)

cmd += 1
edge_server_1.set_status(cmd, 'device_id', 'light_2', 'OFF')
time.sleep(WAIT_TIME)

cmd += 1
edge_server_1.set_status(cmd, 'device_id', 'light_3', 'ON', )
time.sleep(WAIT_TIME)

cmd += 1
edge_server_1.set_status(cmd, 'device_id', 'ac_2', 'OFF')
time.sleep(WAIT_TIME)

print('\n******* SETTING DEVICE STATUS BY DEVICE TYPE *********')
cmd += 1
edge_server_1.set_status(cmd, 'device_type', 'LIGHT', 'ON')
time.sleep(WAIT_TIME)

cmd += 1
edge_server_1.set_status(cmd, 'device_type', 'AC', 'ON')
time.sleep(WAIT_TIME)

print('\n******* SETTING DEVICE STATUS BY ROOM *********')
# Set switch status ON or OFF of all device in a particular  room.
# Default intensity of light (MEDIUM) and temperature  of AC (27) will be set
cmd += 1
edge_server_1.set_status(cmd, 'room', 'BR1', 'ON')
time.sleep(WAIT_TIME)

cmd += 1
edge_server_1.set_status(cmd, 'room', 'Living Room', 'ON')
time.sleep(WAIT_TIME)

print('\n******* SETTING DEVICE STATUS FOR ENTIRE HOUSE  *********')
# Set status (ON or OFF) of all device in house.
# Default intensity of light (MEDIUM) and temperature  of AC (27) will be set

cmd += 1
edge_server_1.set_status(cmd, 'all', 'all', 'OFF')
time.sleep(WAIT_TIME)

print('\n******************* SETTING LIGHT INTENSITY / AC TEMPERATURE  *******************')

print('\n******* SETTING LIGHT INTENSITY / AC TEMPERATURE BY DEVICE ID *********')
# edge_server_1.set() function is used to set intensity / temperature of LIGHT/AC

edge_server_1.set(cmd, 'device_id', 'ac_1', 30)
time.sleep(WAIT_TIME)

edge_server_1.set(cmd, 'device_id', 'light_1', 'HIGH')
time.sleep(WAIT_TIME)

print('\n******* SETTING DEVICE VALUE BY ALL (TEMPERATURE FOR AC / INTENSITY FOR LIGHT) *********')
# All device in home will be set to this value
edge_server_1.set(cmd, 'all', 'LIGHT', 'LOW')
time.sleep(WAIT_TIME)

edge_server_1.set(cmd, 'all', 'AC', 29)
time.sleep(WAIT_TIME)

print('\n******* SETTING DEVICE VALUE BY ROOM (TEMPERATURE FOR AC / INTENSITY FOR LIGHT) *********')

edge_server_1.set(cmd, 'room', 'AC', 28, 'Living Room')
time.sleep(WAIT_TIME)

edge_server_1.set(cmd, 'room', 'LIGHT', 'LOW', 'Living Room')
time.sleep(WAIT_TIME)

print('\n******************* CURRENT  STATUS FOR ENTIRE HOME BEFORE CLOSING THE PROGRAM *******************')
cmd += 1
edge_server_1.get_status(cmd, 'all', 'all')
time.sleep(WAIT_TIME)

print("\nSmart Home Simulation stopped.")
edge_server_1.terminate()
