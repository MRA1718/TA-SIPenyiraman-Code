import telebot
import time
import threading
import RPi.GPIO as GPIO
import json
import serial
import schedule
from datetime import datetime
from telebot import custom_filters
from telebot import TeleBot

TOKEN = '5725314127:AAHxruba6S34B0He6rQ8vVRlJ6IZ_0ucgQ4'
GROUP_ID = -675364128

#Initial setup for pin for relay control
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM) #Change to use GPIO number instead of pin number
pinRelay = 17
GPIO.setup(pinRelay, GPIO.OUT)

relayStatus = 0

#Function for turning on pump relay
def relayOn():
    global relayStatus
    
    GPIO.output(pinRelay, GPIO.HIGH)
    relayStatus = 1

#Function for turning off pump relay
def relayOff(chat_id):
    global relayStatus

    GPIO.output(pinRelay, GPIO.LOW)
    relayStatus = 0
    bot.send_message(chat_id, 'Mematikan pompa, penyiraman selesai')

#Function for sensor data fetch
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

#Initialize Telebot API
bot = telebot.TeleBot(TOKEN)

bot.send_message(GROUP_ID, "Bot aktif, silahkan masukkan command: \
    (/pompa, /sensor, /modeotomatis)")

@bot.message_handler(commands=['help', 'start', 'modeotomatis'])
def send_welcome(message):
    bot.send_message(message.chat.id, "Bot aktif, silahkan masukkan command (/pompa, /sensor)")
    #print(message)


@bot.message_handler(commands=['pompa'])
def pumpHandle(message):
    global relayStatus
    args = message.text.split()

    if len(args) > 1 and args[1].isdigit():
        minutes = (args[1])
        sec = int(minutes)*60
        if relayStatus == 0:
            bot.send_message(message.chat.id, 'Menyalakan pompa selama ' + minutes + ' menit.' )
            relayOn()
            relayTimer = threading.Timer(sec, relayOff, args=[message.chat.id])
            relayTimer.start()
        elif relayStatus == 1:
            bot.send_message(message.chat.id, 'Pompa sedang menyala')
    else:
        bot.send_message(message.chat.id, "Penggunaan: /pompa <menit>")

@bot.message_handler(commands=['sensor'])
def sensorHandle(message):
    sData = dataFetch()
    sMsg = "Sensor Tanah 1: " + str(sData.get("soil1")) + \
            "\nSensor Tanah 2: " + str(sData.get("soil2")) + \
            "\nSuhu: " + (("%.2f") % sData.get("temp")) + \
            "C\nKelembaban: " + (("%.2f") % sData.get("humidity")) + \
            "RH\nSensor Cahaya: " + str(sData.get("light"))
    print(sMsg)
    bot.send_message(message.chat.id, sMsg)

#@bot.message_handler(commands=['modeotomatis'])

print ('I am listening ...')
bot.add_custom_filter(custom_filters.ChatFilter())
threading.Thread(bot.infinity_polling(timeout=20)).start()