import minimalmodbus
import paho.mqtt.client as mqtt
import json
import time

# Credentials of the MQTT Broker
broker_mqtt = '127.0.0.1'
port_mqtt = 1883
client_id = "weidmueller"
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

# Callback function of the mqtt connection state

def on_connect(client_mqtt, userdata, flags, rc):
    if rc == 0:
        print("Successfully connected with the local MQTT broker")
    else:
        print("Bad connection, Returned code=", rc)

# Load the mqtt configuration and connect with the local mqtt broker
client_mqtt = mqtt.Client(client_id)
client_mqtt.on_connect = on_connect
client_mqtt.loop_start()
client_mqtt.connect(broker_mqtt, port_mqtt, keepalive=60)
addresses = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]

# Define the Modbus RTU device
instrument = minimalmodbus.Instrument('/dev/ttyAMA2', 1)  # '/dev/ttyUSB0' is the port, and 1 is the slave address

# Set the communication parameters (baudrate, byte size, parity, stop bits)
instrument.serial.baudrate = 115200
instrument.serial.bytesize = 8
instrument.serial.parity = minimalmodbus.serial.PARITY_NONE
instrument.serial.stopbits = 1
instrument.serial.timeout = 1

# FAKTOREN

while (1):
    time.sleep(1)
    try:
        data = json.loads(_em_data)
        # Storing the values in the json structure
        data['sys']['Hz'] = round((instrument.read_register(0x33, 2) * 10), 2)
        data['sys']['kWh+'] = round((instrument.read_register(0x34, 2) * 10), 2)
        data['sys']['kWh-'] = round((instrument.read_register(0x4E, 2) * 10), 2)
        data['sys']['kvarh+'] = round((instrument.read_register(0x36, 2) * 10), 2)
        data['sys']['kvarh-'] = round((instrument.read_register(0x50, 2) * 10), 2)
        data['sys']['kW'] = round((instrument.read_register(0x28, 2) * 10 / 1000), 2)
        data['sys']['kVA'] = round((instrument.read_register(0x2A, 2) * 10 / 1000), 2)
        data['sys']['kvar'] = round((instrument.read_register(0x2C, 2) * 10 / 1000), 2)
        data['l1']['V'] = round((instrument.read_register(0x00, 2) * 10), 2)
        data['l1']['A'] = round((instrument.read_register(0x0C, 2) / 10), 2)
        data['l1']['kWh+'] = round((instrument.read_register(0x40, 2) * 10), 2)
        data['l1']['kWh-'] = round((instrument.read_register(0x60, 2) * 10), 2)
        data['l1']['kW'] = round((instrument.read_register(0x12, 2) * 10 / 1000), 2)
        data['l1']['kVA'] = round((instrument.read_register(0x18, 2) * 10 / 1000), 2)
        data['l1']['kvar'] = round((instrument.read_register(0x1E, 2) * 10 / 1000), 2)

        # Publish the data on the local mqtt broker
        client_mqtt.publish("s2/appmodule/em/1", payload=json.dumps(data))

    except Exception as error:
        pass

    
if __name__ == '__main__':
    main()
