import time
import threading
import telepot 
import RPi.GPIO as GPIO
import json
import serial
from datetime import datetime
from telepot.loop import MessageLoop


GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
pinRelay = 17
GPIO.setup(pinRelay, GPIO.OUT)
pumpFlag = 0 #act as status of relay

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
            return(dict_json)
        except json.JSONDecodeError as e:
            ("JSON:", e)
        #i += 1
        #time.sleep(1)

#Function for turning on pump relay
def relayOn():
    global pumpFlag
    
    GPIO.output(pinRelay, GPIO.HIGH)
    pumpFlag = 1

#Function for turning off pump relay
def relayOff(chat_id):
    global pumpFlag

    GPIO.output(pinRelay, GPIO.LOW)
    pumpFlag = 0
    bot.sendMessage(chat_id, 'Mematikan pompa, penyiraman selesai')

#Function for telegram message handling
def handle(msg):
    chat_id = msg['chat']['id']
    command = msg['text']
    global pumpFlag

    print ('Got command: %s' % command)

    if command == '/pompa':
        if pumpFlag == 0:
            bot.sendMessage(chat_id, 'Menyalakan pompa selama 3 menit.')
            relayOn()
            timer= threading.Timer(180.0, relayOff, args=[chat_id])
            timer.start()
        elif pumpFlag == 1:
            bot.sendMessage(chat_id, 'Pompa sedang menyala')
    elif command == '/sensor':
        sData = dataFetch()
        sMsg = "Sensor Tanah 1: " + str(sData.get("soil1")) + \
            "\nSensor Tanah 2: " + str(sData.get("soil2")) + \
            "\nSuhu: " + (("%.2f") % sData.get("temp")) + \
            "C\nKelembaban: " + (("%.2f") % sData.get("humidity")) + \
            "RH\nSensor Cahaya: " + str(sData.get("light"))
        print(sMsg)
        bot.sendMessage(chat_id, sMsg)
    else:
        bot.sendMessage(chat_id, "List Command: /pompa")
            

bot = telepot.Bot('5725314127:AAHxruba6S34B0He6rQ8vVRlJ6IZ_0ucgQ4')

MessageLoop(bot, handle).run_as_thread()
print ('I am listening ...')

while 1:
    time.sleep(10)