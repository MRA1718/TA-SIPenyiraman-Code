import json
import serial
import time
from datetime import datetime

def dataFetch():
    dict_json = ""
    ser = serial.Serial('/dev/ttyACM0', 115200, timeout=1)
    ser.reset_input_buffer()
    #i=1
    while dict_json == "":
    #while i <= 5:
        ser.write("collectData\n".encode('utf-8'))
        data = ser.readline().decode("utf-8")
        dtime = datetime.now()
        try:
            dict_json = json.loads(data)
            return(dict_json, dtime)
        except json.JSONDecodeError as e:
            return("JSON:", e, dtime)
        #i += 1
        #time.sleep(1)
"""
print(dict_json.get("soil1"))
print(dict_json.get("soil2"))
print(round(dict_json.get("temp"), 2))
print(round(dict_json.get("humidity"), 2))
print(dict_json.get("light"))
"""