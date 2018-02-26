import serial
from serial import SerialException
import time
import datetime
import io
import psycopg2
import threading
import os
import aiocoap.resource as resource
import aiocoap
import asyncio
import logging
import rest

conn = psycopg2.connect(dbname="postgres", user="postgres", password=os.environ["POSTGRES_PASS"], host="postgres")
cur = conn.cursor()

alertTemperature = False
alertHumidity = False
alertCarbonous = False
alertSmoke = False

class read_serial_thread(threading.Thread):
    def __init__(self, delay):
        threading.Thread.__init__(self)
        self.delay = delay
    def run(self):
        global alertTemperature
        global alertHumidity
        global alertCarbonous
        global alertSmoke

        try:
            port = serial.Serial("/dev/ttyACM1", 9600, timeout = 5.1)
        except:
            port = serial.Serial("/dev/ttyACM0", 9600, timeout = 5.1)

        print(port.readline().decode())

        while True:
            time.sleep(self.delay)
            print(rest.limits)
            port.write('h'.encode())
            humidity = abs(float(port.readline().decode()))

            if humidity > rest.limits['humidity'] and alertHumidity == False:
                port.write('r'.encode())
                alertHumidity = True
            elif humidity < rest.limits['humidity'] and alertHumidity == True:
                port.write('r'.encode())
                alertHumidity = False

            port.write('t'.encode())
            temperature = abs(float(port.readline().decode()))

            if temperature > rest.limits['temperature'] and alertTemperature == False:
                port.write('g'.encode())
                alertTemperature = True
            elif temperature < rest.limits['temperature'] and alertTemperature == True:
                port.write('g'.encode())
                alertTemperature = False

            port.write('s'.encode())
            smoke = abs(float(port.readline().decode()))

            if smoke > rest.limits['smoke'] and alertSmoke == False:
                port.write('p'.encode())
                alertSmoke = True
            elif smoke < rest.limits['smoke'] and alertSmoke == True:
                port.write('p'.encode())
                alertSmoke = False

            port.write('c'.encode())
            carbonous = abs(float(port.readline().decode()))

            if carbonous > rest.limits['carbonous'] and alertCarbonous == False:
                port.write('l'.encode())
                alertCarbonous = True
            elif carbonous < rest.limits['carbonous'] and alertCarbonous == True:
                port.write('l'.encode())
                alertCarbonous = False

            cur.execute("INSERT INTO roody (temperature, humidity, smoke, carbonous, time_stamp) VALUES (%s, %s, %s, %s, %s);", (temperature, humidity, smoke, carbonous, datetime.datetime.utcnow().isoformat()))
            conn.commit()


class TimeResource(resource.ObservableResource):
    def __init__(self):
        super().__init__()
        self.handle = None
    async def render_get(self, request):
        await asyncio.sleep(2)

        payload = b"Hello"
        return aiocoap.Message(payload=payload)

#logging.basicConfig(level=logging.DEBUG)
#logging.getLogger("coap-server").setLevel(logging.DEBUG)

def run():
        print("starting coap")
        root = resource.Site()
        root.add_resource(('.well-known', 'core',), resource.WKCResource(root.get_resources_as_linkheader))
        root.add_resource(('time',), TimeResource())
        
        asyncio.Task(aiocoap.Context.create_server_context(site=root))
        asyncio.get_event_loop().run_forever()

thread1 = read_serial_thread(2)
thread2 = rest.rest_thread()
thread1.start()
thread2.start()
#run()
