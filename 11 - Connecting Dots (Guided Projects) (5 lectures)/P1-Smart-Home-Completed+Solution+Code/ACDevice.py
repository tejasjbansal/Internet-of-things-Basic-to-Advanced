import time
import json
import paho.mqtt.client as mqtt

REGISTER_DEVICE = "device/register"  # Register device  : Device publishes. EdgeServer subscribes.
REGISTER_DEVICE_RESPONSE = "device/register/response"  # Register device  : EdgeServer publishes. Device subscribes.
DEVICE_STATUS = "device/status"  # Request to get device status : EdgeServer publishes. Device subscribes.
DEVICE_STATUS_RESPONSE = "device/status/response"  # Provides device status :  Device publishes. EdgeServer subscribes.
DEVICE_SET_STATUS = "device/status/set"  # Set device status :  EdgeServer publishes. Device subscribes.

HOST = "localhost"
PORT = 1883
WAIT_TIME = 0.20


class ACDevice:
    
    _MIN_TEMP = 18  
    _MAX_TEMP = 32  

    def __init__(self, device_id, room):
        
        self._device_id = device_id
        self._room_type = room
        self._temperature = 22
        self._device_type = "AC"
        self._device_registration_flag = False
        self.client = mqtt.Client(self._device_id)  
        self.client.on_connect = self._on_connect  
        self.client.on_message = self._on_message  
        self.client.on_disconnect = self._on_disconnect
        self.client.connect(HOST, PORT, keepalive=60)  
        self.client.loop_start()  
        self._register_device(self._device_id, self._room_type)
        self._switch_status = "OFF"

    def _on_disconnect(self, device_id, room_type, device_type):
        self.client.disconnect()

    # Connect method to subscribe to various topics. 
    def _on_connect(self, client, userdata, flags, result_code):
        self.client.subscribe(DEVICE_STATUS)
        self.client.subscribe(DEVICE_SET_STATUS)
        self.client.subscribe(REGISTER_DEVICE_RESPONSE)
        time.sleep(WAIT_TIME)
        if result_code != 0:
            print(f'bad connection for {self._device_type} instance {self._device_id} with result code {result_code}')
            if result_code == 4:
                print('MQTT Server not available')

    # method to process the received messages and publish them on relevant topics
    # this method can also be used to take the action based on received commands
    def _on_message(self, client, userdata, msg):
        received_message = json.loads((msg.payload.decode("utf-8", "ignore")))
        device_id = received_message['device_id']
        device_type = received_message['device_type']
        if msg.topic == REGISTER_DEVICE_RESPONSE and device_id == self._device_id:
            room = received_message['room']
            self._device_registration_flag = True
            print(f'AC-DEVICE Registered! - Registration status for device id ({device_id})'
                  f' device type ({device_type}) for ({room}) : {self._device_registration_flag}')
        elif msg.topic == DEVICE_STATUS:
            if (device_id == self._device_id and device_type == 'device_id') or \
                device_type == self._device_type or device_type == self._room_type or \
                    device_type == 'all':
                self._get_status()
        elif msg.topic == DEVICE_SET_STATUS:
            switch_state = received_message['switch_state']
            temperature = received_message.get('intensity')
            if temperature is None:  # if temperature is boe set default temperature
                temperature = 22
            room_type = received_message.get('room_type')

            # room_type value is not none only when AC temperature of particular room is to be set
            if room_type is not None:
                if device_type == self._device_type and room_type == self._room_type:
                    self._set_temperature(temperature)
                    self._get_status()
                return
            if (device_id == self._device_id and device_type == 'device_id') or \
                device_type == self._device_type or (device_type == self._room_type) or \
                    (device_type == 'all'):
                if self._set_status(switch_state) and self._set_temperature(temperature):
                    self._get_status()
        return

    # calling registration method to register the device on Edge Server
    def _register_device(self, device_id, room):
        print(f'\nRegistration request is acknowledged for device {self._device_type}  '
              f'with id \'{device_id}\' in {room}')
        ac_device = dict()
        ac_device['device_id'] = device_id
        ac_device['room'] = room
        ac_device['device_type'] = self._device_type
        self.client.publish(REGISTER_DEVICE, json.dumps(ac_device))
        time.sleep(WAIT_TIME)
        return

    # Getting the current switch status of devices
    def _get_status(self):
        device_status = dict()
        device_status['device_id'] = self._device_id
        device_status['device_type'] = self._device_type
        device_status['room'] = self._room_type
        device_status['switch_state'] = self._switch_status
        device_status['temperature'] = self._temperature
        self.client.publish(DEVICE_STATUS_RESPONSE, json.dumps(device_status))
        time.sleep(WAIT_TIME)
        return

    def get_device_type(self):
        return self._device_type

    # Setting the switch of devices
    def _set_status(self, switch_state):
        if switch_state in ('ON', 'OFF'):
            self._switch_status = switch_state
            return True
        else:
            print('AC DEVICE ERROR : INVALID VALUE OF SWITCH. Value should be ON or OFF')
            return False

    # Getting the temperature for the devices
    def _get_temperature(self):
        return self._temperature

    # Setting up the temperature of the devices
    def _set_temperature(self, temperature):
        if int(temperature) in range(self._MIN_TEMP,  self._MAX_TEMP):
            self._temperature = temperature
            return True
        else:
            print('AC DEVICE ERROR : INVALID VALUE OF TEMPERATURE. Value should be in '
                  'between ' + str(self._MIN_TEMP) + ' and ' + str(self._MAX_TEMP))
            return False
