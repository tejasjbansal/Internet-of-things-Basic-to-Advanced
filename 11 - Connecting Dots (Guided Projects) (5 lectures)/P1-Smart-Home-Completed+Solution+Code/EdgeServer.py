
import json
import time
import paho.mqtt.client as mqtt

HOST = "localhost"
PORT = 1883     
WAIT_TIME = 0.20

ROOM_LIST = ["Kitchen", "Garage", "Living Room", "BR1", "BR2"]
DEVICE_TYPE_LIST = ["LIGHT", "AC"]

# Topics
REGISTER_DEVICE = "device/register"  # Register device  : Device publishes. EdgeServer subscribes.
REGISTER_DEVICE_RESPONSE = "device/register/response"  # Register device  : EdgeServer publishes. Device subscribes.
DEVICE_STATUS = "device/status"  # Device status Request : EdgeServer publishes. Device subscribes.
DEVICE_STATUS_RESPONSE = "device/status/response"  # Device status response:  Device publishes. EdgeServer subscribes.
DEVICE_SET_STATUS = "device/status/set"  # Set device status :  EdgeServer publishes. Device subscribes.


class EdgeServer:
    
    def __init__(self, instance_name):

        self._instance_id = instance_name
        self.client = mqtt.Client(self._instance_id)
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.client.connect(HOST, PORT, keepalive=60)
        self.client.loop_start()

        self._registered_device_id = []
        self._registered_device_list = []

    # Terminating the MQTT broker and stopping the execution
    def terminate(self):
        self.client.disconnect()
        self.client.loop_stop()

    # Connect method to subscribe to various topics.     
    def _on_connect(self, client, userdata, flags, result_code):
        self.client.subscribe(REGISTER_DEVICE)
        self.client.subscribe(DEVICE_STATUS_RESPONSE)
        if result_code != 0:
            print(f'Edge server is not available. Result code : {result_code}')
            if result_code == 4:
                print(f'MQTT is not running')

    # method to process the received messages and publish them on relevant topics
    # this method can also be used to take the action based on received commands
    def _on_message(self, client, userdata, msg):
        received_message = json.loads((msg.payload.decode("utf-8", "ignore")))
        device_id = received_message['device_id']
        room = received_message['room']
        device_type = received_message['device_type']
        if msg.topic == REGISTER_DEVICE:
            self._register_device(device_id, room, device_type)
        elif msg.topic == DEVICE_STATUS_RESPONSE:
            print(f'Here is the current device status for {device_id} : {received_message}')
        return

    # Register a new device on Edge Server
    def _register_device(self, device_id, room, device_type):
        device = dict()
        device['device_id'] = device_id
        device['room'] = room
        device['device_type'] = device_type
        self._registered_device_id.append(device_id)
        self._registered_device_list.append(device)
        self.client.publish(REGISTER_DEVICE_RESPONSE, json.dumps(device))
        print(f'Request is processed for {device_id}')
        time.sleep(WAIT_TIME)
        return

    # Returning the current registered list
    def get_registered_device_list(self):
        return self._registered_device_list

    # Getting the status for the connected devices Command_type can be :-
    # device_id to get status of particular device
    # device_type to get status of all device type all AC or all LIGHT
    # room  to get status of all device in a particular room
    # all to get status of all devices in entire house
    def get_status(self, cmd, command_type, device_id):
        print(f'\nGet Status based on {command_type} : {device_id}')
        print(f'Command ID {cmd} request is initiated...')
        if command_type == 'device_id':
            if device_id not in self._registered_device_id:
                print(f'Incorrect device id : {device_id}')
                return False
            device = dict()
            device['device_id'] = device_id
            device['device_type'] = command_type
            self.client.publish(DEVICE_STATUS, json.dumps(device))
            time.sleep(WAIT_TIME)
        elif command_type in ('device_type', 'room', 'all'):
            if command_type == 'device_type' and device_id not in DEVICE_TYPE_LIST:
                print(f'Incorrect device type : {device_id}. Device Id can be {DEVICE_TYPE_LIST}')
                return False
            elif command_type == 'room' and device_id not in ROOM_LIST:
                print(f'Incorrect device type : {device_id}. Device Id can be {DEVICE_TYPE_LIST}')
                return False
            device = dict()
            device['device_id'] = ''
            device['device_type'] = device_id  # Set device type to it to LIGHT OR AC or room type or all
            self.client.publish(DEVICE_STATUS, json.dumps(device))
            time.sleep(WAIT_TIME*3)
        else:
            print(f'Incorrect device type provided : {command_type}.'
                  f' Device type can be : device_id, device_type, room, all')
            return False
        print(f'Command ID {cmd} request is executed...')

    # Set the status ON or OFF for the connected devices Command_type can be :-
    # device_id to get status of particular device
    # device_type to get status of all device type all AC or all LIGHT
    # room  to get status of all device in a particular room
    # all to get status of all devices in entire house
    def set_status(self, cmd, command_type, device_id, switch_state):
        print(f'\nSet Status based on {command_type} : {device_id}...')
        print(f'Setting status of {device_id} to {switch_state} ...')
        print(f'Command ID {cmd} request is initiated...')
        device = dict()
        device['device_type'] = command_type
        device['switch_state'] = switch_state
        if command_type == 'device_id':
            if device_id not in self._registered_device_id:
                print(f'Incorrect device id : {device_id}')
                return False
            device['device_id'] = device_id
        elif command_type in ('device_type', 'room', 'all'):
            if command_type == 'device_type' and device_id not in DEVICE_TYPE_LIST:
                print(f'Incorrect device type : {device_id}. Device Id can be {DEVICE_TYPE_LIST}')
                return False
            elif command_type == 'room' and device_id not in ROOM_LIST:
                print(f'Incorrect Room type : {device_id}. Device Id can be {ROOM_LIST}')
                return False
            device['device_id'] = ''
            device['device_type'] = device_id  # Set device type to LIGHT OR AC or room type or all
        else:
            print(f'Incorrect device type provided : {command_type}.'
                  f' Device type can be : device_id, device_type, room, all')
            return False
        self.client.publish(DEVICE_SET_STATUS, json.dumps(device))
        time.sleep(WAIT_TIME)
        print(f'Command ID {cmd} request is executed')

    # Set function sets the intensity for light or temperature in case of AC
    # command_type is 'device_id' or 'all' or 'room'
    # 1. If command_type is 'device_id' - 3rd param is device_id and 4th param is value (intensity or temperature)
    # 2. If command_type is 'all' or 'room
    #                 3rd param - device_id is device type i.e. LIGHT or AC
    #                 4th param  value -  will be applied to devices in entire home for all and  room for 'room'
    #                 5th param room_type - required only if command_type is 'room'

    def set(self, cmd, command_type, device_id, value, room_type=None):

        cmd_type_value = device_id
        if room_type is not None:
            cmd_type_value = device_id + ' in room ' + room_type
        print(f'\nSet Value based on {command_type} : {cmd_type_value}...')
        print(f'Setting value of {device_id} to  ({value})...')
        print(f'Command ID {cmd} request is initiated...')
        device = dict()
        device['switch_state'] = 'ON'  # Set the default switch_state to ON
        device['intensity'] = value
        if command_type == 'device_id':
            if device_id not in self._registered_device_id:
                print(f'Incorrect device id : {device_id}')
                return False
            device['device_id'] = device_id
            device['device_type'] = command_type
        elif command_type == 'all':
            if device_id not in DEVICE_TYPE_LIST:
                print(f'Incorrect device type : {device_id}. Device Id can be {DEVICE_TYPE_LIST}')
                return False
            device['device_id'] = ''
            device['device_type'] = device_id  # Set device type to LIGHT OR AC
        elif command_type == 'room':
            if room_type not in ROOM_LIST:
                print(f'Incorrect Room type : {device_id}. Device Id can be {ROOM_LIST}')
                return False
            device['device_id'] = ''
            device['device_type'] = device_id  # Set device type to LIGHT OR AC
            device['room_type'] = room_type
        else:
            print(f'Incorrect device type provided : {command_type}.'
                  f' Device type can be : device_id, device_type, room, all')
            return False
        self.client.publish(DEVICE_SET_STATUS, json.dumps(device))
        time.sleep(WAIT_TIME)
        print(f'Command ID {cmd} request is executed')
