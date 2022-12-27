import telebot
import time
import threading
import RPi.GPIO as GPIO
import json
import serial
import schedule
import mysql.connector
from datetime import datetime
from telebot import custom_filters
from telebot import TeleBot


#Initialze database connection
mydb = mysql.connector.connect(
    host="localhost",
    user="rpi4db",
    password="sqlrpi4",
    database="rpi4watering"
)

#Fetch token telegram & group ID
mycursor = mydb.cursor()
telsql = "SELECT token_telegram FROM Telegram"
mycursor.execute(telsql)
restl = mycursor.fetchall()

TOKEN = restl[0][0]
GROUP_ID = restl[1][0]

#Initial setup for pin for relay control
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM) #Change to use GPIO number instead of pin number
pinRelay = 17
GPIO.setup(pinRelay, GPIO.OUT)

relayStatus = 0
wtrMode = 0 #Status for used mode, 0 as manual mode

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
        ser.write("collectdata\n".encode('utf-8'))
        data = ser.readline().decode("utf-8")
        try:
            dict_json = json.loads(data)
            return(dict_json)
        except json.JSONDecodeError as e:
            ("JSON:", e)
        #i += 1

def autoWatering():
    #bot.send_message(GROUP_ID, 'Scheduling berjalan ' + str(datetime.now()))
    sTime = datetime.now()
    snData = dataFetch()
    sh1 = snData.get("soilc1")
    sh2 = snData.get("soilc2")
    temp = snData.get("temp")
    humid = snData.get("humid")

    bot.send_message(GROUP_ID, (sh1, sh2, temp, humid, sTime, datetime.now()))


#Function for scheduling sensor data fetch
def autoSchedWatering():
    global wtrMode
    schedule.every().minute.at(":00").do(autoWatering).tag('otomatis')
    
    while wtrMode == 1:
        schedule.run_pending()
    

#Initialize Telebot API
bot = telebot.TeleBot(TOKEN)

bot.send_message(GROUP_ID, 'Bot aktif, silahkan masukkan command: (/pompa <menit>, /sensor)')

@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    bot.send_message(message.chat.id, 'List Command:\n- /pompa <menit>\n- /sensor')

#Bot command list
#Command /pompa for manually relay control
@bot.message_handler(commands=['pompa'])
def pumpHandle(message):
    global relayStatus
    global relayTimer
    global wtrMode
    args = message.text.split()

    if wtrMode == 0:
        if len(args) > 1 and args[1].isdigit():
            minutes = (args[1])
            sec = int(minutes)*60
            if relayStatus == 0:
                bot.send_message(message.chat.id, 'Menyalakan pompa selama ' + minutes + ' menit.' )
                relayOn()
                relayTimer = threading.Timer(sec, relayOff, args=[message.chat.id])
                relayTimer.start()
            elif relayStatus == 1:
                bot.send_message(message.chat.id, 'Pompa sedang menyala, gunakan /pompa STOP untuk mematikan')
        elif len(args) > 1 and args[1] == 'stop' and relayStatus == 1:
            relayTimer.cancel()
            GPIO.output(pinRelay, GPIO.LOW)
            relayStatus = 0
            bot.send_message(message.chat.id, 'Mematikan pompa, gunakan "/pompa <menit>" untuk menyalakan kembali')
        else:
            bot.send_message(message.chat.id, 'Penggunaan: /pompa <menit>')
    elif wtrMode == 1:
        bot.send_message(message.chat.id, 'Dalam mode otomatis, silahkan ganti /mode untuk menggunakan command pompa')


#Command /sensor for collecting data sensor
@bot.message_handler(commands=['sensor'])
def sensorHandle(message):
    sData = dataFetch()
    sMsg = "Kelembaban Tanah (Pot 1): " + (("%.2f") % sData.get("soilc1")) + ("% (") + \
            str(sData.get("soil1")) + (")") + \
            "\nKelembaban Tanah (Pot 2): " + (("%.2f") % sData.get("soilc2")) + ("% (") + \
            str(sData.get("soil2")) + (")") + \
            "\nSuhu: " + (("%.2f") % sData.get("temp")) + \
            "C\nKelembaban: " + (("%.2f") % sData.get("humidity")) + \
            "RH\nIntensitas Cahaya: " + str(sData.get("light"))
    print(sMsg)
    bot.send_message(message.chat.id, sMsg)

#Command /mode for manual or automatic operation
@bot.message_handler(commands=['mode'])
def modeHandle(message):
    global wtrMode
    mdargs = message.text.split()

    if len(mdargs) > 1 and mdargs[1] == 'manual':
        if wtrMode == 1:
            wtrMode = 0
            schedule.clear('otomatis')
            bot.send_message(message.chat.id, 'mengganti mode penyiraman ke manual')
        elif wtrMode == 0:
            bot.send_message(message.chat.id, 'Mode penyiraman: manual. gunakan "/mode otomatis" untuk mengganti mode penyiraman')
    elif len(mdargs) > 1 and mdargs[1] == 'otomatis':
        if wtrMode == 1:
            bot.send_message(message.chat.id, 'Mode penyiraman: otomatis. gunakan "/mode manual" untuk mengganti mode penyiraman')
        elif wtrMode == 0:
            wtrMode = 1
            bot.send_message(message.chat.id, 'mengganti mode penyiraman ke otomatis')
            autoSchedWatering()
    elif len(mdargs) > 1 and mdargs[1] == 'status':
        if wtrMode == 1:
            bot.send_message(message.chat.id, 'Mode penyiraman: otomatis')
        elif wtrMode == 0:
            bot.send_message(message.chat.id, 'Mode penyiraman: manual')
    else: bot.send_message(message.chat.id, 'Command "/mode (status/manual/otomatis)"')

print('I am listening ...')
bot.add_custom_filter(custom_filters.ChatFilter())
botTele = threading.Thread(bot.infinity_polling(timeout=20))
botTele.start()