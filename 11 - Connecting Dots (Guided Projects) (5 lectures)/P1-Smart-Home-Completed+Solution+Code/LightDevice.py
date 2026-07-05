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


class LightDevice:
    # setting up the intensity choices for Smart Light Bulb
    _INTENSITY = ["LOW", "HIGH", "MEDIUM", "OFF"]

    def __init__(self, device_id, room):
        # Assigning device level information for each of the devices. 
        self._device_id = device_id
        self._room_type = room
        self._light_intensity = self._INTENSITY[0]
        self._device_type = "LIGHT"
        self._device_registration_flag = False
        self.client = mqtt.Client(self._device_id)  
        self.client.on_connect = self._on_connect  
        self.client.on_message = self._on_message  
        self.client.on_disconnect = self._on_disconnect
        self.client.connect(HOST, PORT, keepalive=60)  
        self.client.loop_start()
        self._register_device(self._device_id, self._room_type)
        self._switch_status = "OFF"

    def _register_device(self, device_id, room):
        while not self.client.is_connected():
            pass
        print(f'\nRegistration request is acknowledged for device {self._device_type}  '
              f'with id \'{device_id}\' in {room}')
        light_device = dict()
        light_device['device_id'] = device_id
        light_device['room'] = room
        light_device['device_type'] = self._device_type
        self.client.publish(REGISTER_DEVICE, json.dumps(light_device))
        time.sleep(WAIT_TIME)
        self._device_registration_flag = True
        return

    # Connect method to subscribe to various topics. 
    def _on_connect(self, client, userdata, flags, result_code):
        self.client.subscribe(DEVICE_STATUS)
        self.client.subscribe(DEVICE_SET_STATUS)
        self.client.subscribe(REGISTER_DEVICE_RESPONSE)
        if result_code != 0:
            print(f'bad connection for {self._device_type} instance {self._device_id} with '
                  f'result code {result_code}')
            if result_code == 4:
                print('MQTT Server not available')

    # Define Disconnect method
    def _on_disconnect(self, client, userdata, flags, result_code):
        self.client.disconnect()
        print(f'Client Disconnected with result code {result_code}')

    # method to process the received messages and publish them on relevant topics
    # this method can also be used to take the action based on received commands
    def _on_message(self, client, userdata, msg):
        received_message = json.loads((msg.payload.decode("utf-8", "ignore")))
        device_id = received_message['device_id']
        device_type = received_message['device_type']
        if msg.topic == REGISTER_DEVICE_RESPONSE and device_id == self._device_id:
            room = received_message['room']
            self._device_registration_flag = True
            print(f'Light-Device Registered! Registration status for device id ({device_id}) '
                  f'device type ({device_type}) room ({room}) : {self._device_registration_flag}')
        elif msg.topic == DEVICE_STATUS:
            # get status if value matches with device id OR device type OR room type OR all
            if (device_id == self._device_id and device_type == 'device_id') or \
                device_type == self._device_type or device_type == self._room_type or \
                    (device_type == 'all'):
                self._get_status()
        elif msg.topic == DEVICE_SET_STATUS:
            switch_state = received_message['switch_state']
            intensity = received_message.get('intensity')
            if intensity is None:  # if temperature is boe set default temperature
                intensity = 'MEDIUM'
            room_type = received_message.get('room_type')

            # room_type value is not none only when Light intensity of particular room is to be set
            if room_type is not None:
                if device_type == self._device_type and room_type == self._room_type:
                    self._set_light_intensity(intensity)
                    self._get_status()
                return
            if (device_id == self._device_id and device_type == 'device_id') or \
                device_type == self._device_type or device_type == self._room_type or \
                    (device_type == 'all'):
                if self._set_status(switch_state) and self._set_light_intensity(intensity):
                    self._get_status()
        return

    # Getting the current switch status of devices
    def _get_status(self):
        device_status = dict()
        device_status['device_id'] = self._device_id
        device_status['device_type'] = self._device_type
        device_status['room'] = self._room_type
        device_status['switch_state'] = self._switch_status
        device_status['intensity'] = self._light_intensity

        self.client.publish(DEVICE_STATUS_RESPONSE, json.dumps(device_status))
        time.sleep(WAIT_TIME)
        return

    # Getting the current switch status of devices
    def get_device_type(self):
        return self._device_type

    # Setting the switch of devices
    def _set_status(self, switch_state):
        if switch_state in ('ON', 'OFF'):
            self._switch_status = switch_state
            # If  switch is off setting intensity to off
            if self._switch_status == 'OFF':
                self._set_light_intensity('OFF')
            else:
                self._set_light_intensity('MEDIUM')
            return True
        else:
            print('LIGHT DEVICE ERROR : INVALID VALUE OF SWITCH. Value should be ON or OFF')
            return False

    # Getting the light intensity for the devices
    def _get_light_intensity(self):
        return self._light_intensity

    # Setting the light intensity for devices
    def _set_light_intensity(self, light_intensity):
        if light_intensity in self._INTENSITY:
            self._light_intensity = light_intensity
            return True
        else:
            print('LIGHT DEVICE ERROR : INVALID VALUE OF INTENSITY. Value should be in  ' + str(self._INTENSITY))
            return False
