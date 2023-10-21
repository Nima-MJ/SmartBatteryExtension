import asyncio
import time
import json
import RPi.GPIO as GPIO
from azure.iot.device import Message, MethodResponse, IoTHubModuleClient
from azure.iot.device.aio import IoTHubDeviceClient
from gps import *
import Adafruit_ADS1x15
adc = Adafruit_ADS1x15.ADS1115(address=0x48, busnum=1)
import Adafruit_DHT as dht

CONNECTION_STRING = "HostName=CapstoneEE.azure-devices.net;DeviceId=azCapstone;SharedAccessKey=WghL1z4VO484wsZmvzvTmzZucbKyRob2KWRWTiixy5o="  

PAYLOAD = '{{"temperature": {temperature}, "humidity": {humidity}, "voltage": {voltage}}}'
#Set DATA pin
DHT = 4

# send payload data to the IoT Hub
async def send_data_to_hub(data):
    msg = Message(data)
    await device_client.send_message(msg)
    print("Data sent to IoT Hub: {}".format(data))

device_client = IoTHubDeviceClient.create_from_connection_string(CONNECTION_STRING, connection_retry=False)
print("connection created")

async def main():
    
    try:
        # Initialize GPIO
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.cleanup()
        await device_client.connect()
        
        print("Sending serivce started. Press Ctrl-C to exit")
        while True:
            
            try:
                value = adc.read_adc(1)
                voltage = value * 0.0006225099602
                
                #Read TEmp and Hum from DHT22
                humidity,temperature = dht.read_retry(dht.DHT22, DHT)
                
                data = PAYLOAD.format(temperature=temperature, humidity=humidity, voltage=voltage)
                await send_data_to_hub(data)
                print("Message successfully sent")
                await asyncio.sleep(5)
                
            except KeyboardInterrupt:
                print("Service stopped")
                GPIO.cleanup()
                break
    except Exception as error:
        print(error.args[0])
 

if __name__ == '__main__':
    asyncio.run(main())
