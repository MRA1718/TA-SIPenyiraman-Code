import json
import serial
import time
from datetime import datetime


dict_json = ""
ser = serial.Serial('/dev/ttyACM0', 115200, timeout=1)
ser.reset_input_buffer()
#i=1
while dict_json == "":
#while i <= 5:
    ser.write("collectdata\n".encode('utf-8'))
    data = ser.readline().decode("utf-8")
    dtime = datetime.now()
    try:
        dict_json = json.loads(data)
        print(dict_json, dtime)
    except json.JSONDecodeError as e:
        print("JSON:", e, dtime)
        #i += 1
        #time.sleep(1)


print(dict_json.get("soil1"))
print(dict_json.get("soil2"))
print(dict_json.get("temp"))
print(isinstance(dict_json.get("humidity"), int))
print(dict_json.get("light"))
