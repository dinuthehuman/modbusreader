import minimalmodbus
import paho.mqtt.client as mqtt
import json
import time
import threading
import uuid


class ModbusReader:

    BROKER_MQTT = '127.0.0.1'
    PORT_MQTT = 1883
    CLIENT_ID = "powermodbus" + str(uuid.uuid4())
    ADRESSES = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]

    _em_data = '''
    {
        "sys": {
            "Hz": 0,
            "kWh+": 0,
            "kWh-": 0,
            "kvarh+": 0,
            "kvarh-": 0,
            "kW": 0,
            "kVA": 0,
            "kvar": 0
            },
        "l1": {
            "phase": "R",
            "V": 0,
            "A": 0,
            "kWh+": 0,
            "kWh-": 0,
            "kW": 0,
            "kVA": 0,
            "kvar": 0
            },
        "l2": {
            "phase": "S",
            "V": 0,
            "A": 0,
            "kWh+": 0,
            "kWh-": 0,
            "kW": 0,
            "kVA": 0,
            "kvar": 0
            },

        "l3": {
            "phase": "T",
            "V": 0,
            "A": 0,
            "kWh+": 0,
            "kWh-": 0,
            "kW": 0,
            "kVA": 0,
            "kvar": 0
            }
    }
    '''

    def __init__(self):
        self.client_mqtt = mqtt.Client(ModbusReader.CLIENT_ID)
        self.client_mqtt.on_connect = ModbusReader._on_connect
        self.client_mqtt.username_pw_set("dinu", "&94:would:malta:50&")
        self.client_mqtt.loop_start()
        self.client_mqtt.connect(ModbusReader.BROKER_MQTT, ModbusReader.PORT_MQTT, keepalive=60)
        # Define the Modbus RTU device
        self.instrument = minimalmodbus.Instrument('/dev/ttyAMA2', 1)  # '/dev/ttyUSB0' is the port, and 1 is the slave address

        # Set the communication parameters (baudrate, byte size, parity, stop bits)
        self.instrument.serial.baudrate = 115200
        self.instrument.serial.bytesize = 8
        self.instrument.serial.parity = minimalmodbus.serial.PARITY_NONE
        self.instrument.serial.stopbits = 1
        self.instrument.serial.timeout = 1

    @staticmethod
    def _on_connect(client_mqtt, userdata, flags, rc):
        if rc == 0:
            print("Successfully connected with the local MQTT broker")
        else:
            print("Bad connection, Returned code=", rc)

    def read_publish(self):
        try:
            data = json.loads(ModbusReader._em_data)
            # Storing the values in the json structure
            data['sys']['Hz'] = round((self.instrument.read_register(0x33, 2) * 10), 2)
            data['sys']['kWh+'] = round((self.instrument.read_register(0x34, 2) * 10), 2)
            data['sys']['kWh-'] = round((self.instrument.read_register(0x4E, 2) * 10), 2)
            data['sys']['kvarh+'] = round((self.instrument.read_register(0x36, 2) * 10), 2)
            data['sys']['kvarh-'] = round((self.instrument.read_register(0x50, 2) * 10), 2)
            data['sys']['kW'] = round((self.instrument.read_register(0x28, 2) * 10 / 1000), 2)
            data['sys']['kVA'] = round((self.instrument.read_register(0x2A, 2) * 10 / 1000), 2)
            data['sys']['kvar'] = round((self.instrument.read_register(0x2C, 2) * 10 / 1000), 2)
            data['l1']['V'] = round((self.instrument.read_register(0x00, 2) * 10), 2)
            data['l1']['A'] = round((self.instrument.read_register(0x0C, 2) / 10), 2)
            data['l1']['kWh+'] = round((self.instrument.read_register(0x40, 2) * 10), 2)
            data['l1']['kWh-'] = round((self.instrument.read_register(0x60, 2) * 10), 2)
            data['l1']['kW'] = round((self.instrument.read_register(0x12, 2) * 10 / 1000), 2)
            data['l1']['kVA'] = round((self.instrument.read_register(0x18, 2) * 10 / 1000), 2)
            data['l1']['kvar'] = round((self.instrument.read_register(0x1E, 2) * 10 / 1000), 2)

            # Publish the data on the local mqtt broker
            self.client_mqtt.publish("s2/appmodule/em/1", payload=json.dumps(data))
        except Exception as e:
            pass

    def run(self):
        while 1:
            time.sleep(1)
            self.read_publish()