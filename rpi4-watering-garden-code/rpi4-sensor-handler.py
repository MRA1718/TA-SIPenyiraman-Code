import json
import serial

dict_json = ""

ser = serial.Serial('/dev/ttyACM0', 115200, timeout=1)
ser.reset_input_buffer()
#i=1
while dict_json == "":
    ser.write("collectData\n".encode('utf-8'))
    data = ser.readline().decode("utf-8")
    try:
        dict_json = json.loads(data)
        print(dict_json)
    except json.JSONDecodeError as e:
        print("JSON:", e)
    #i += 1
print(dict_json.get("soil1"))    