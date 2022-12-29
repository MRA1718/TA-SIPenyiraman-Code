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

#Fuzzy set declaration
soilFuzzySet = ['Basah', 'Lembab', 'Kering'] #For soil moisture
tempFuzzySet = ['Dingin', 'Hangat', 'Panas'] #For Temperature
humidFuzzySet = ['Basah', 'Lembab', 'Keqing'] #For air humidity
lightFuzzySet = ['Gelap', 'Redup', 'Terang'] #For light intensity

relayFuzzySet = ['Pendek', 'Sedang', 'Lama'] #For relay "on" duration

#Fuzzy Function
#Fuzzyfication
def soilFuzzy(soil):
    lngSoil = []
    if soil >= 0 and soil <= 30:
        lngSoil.append(soilFuzzySet[0]) #Kering
    if soil >= 20 and soil <= 80:
        lngSoil.append(soilFuzzySet[1]) #Lembab
    if soil >= 70 and soil <= 100:
        lngSoil.append(soilFuzzySet[2]) #Basah

    valSoil = []
    if len(lngSoil) > 1:
        if lngSoil[0] == soilFuzzySet[0] and lngSoil[1] == soilFuzzySet[1]:
            #Kering
            dry = -(soil - 30) / (30 - 20)
            valSoil.append([lngSoil[0], dry])
            #Lembab
            moist = (soil - 20) / (30 - 20)
            valSoil.append([lngSoil[1], moist])
        if lngSoil[0] == soilFuzzySet[1] and lngSoil[1] == soilFuzzySet[2]:
            #Lembab
            moist = -(soil - 80) / (80 - 70)
            valSoil.append([lngSoil[0], moist])
            #Basah
            wet = (soil - 70) / (80 - 70)
            valSoil.append([lngSoil[1], wet])
    else:
        valSoil.append(lngSoil[0], 1)

    return valSoil

def tempFuzzy(temp):
    lngTemp = []

    if temp >= 20 and temp <= 28:
        lngTemp.append(tempFuzzySet[0]) #Dingin
    if temp >= 26 and temp <= 35:
        lngTemp.append(tempFuzzySet[1]) #Hangat
    if temp >= 32 and temp <= 45:
        lngTemp.append(tempFuzzySet[2]) #Panas

    valTemp = []

    if len(lngTemp) > 1:
        if lngTemp[0] == tempFuzzySet[0] and lngTemp[1] == tempFuzzySet[1]:
            #Dingin
            cold = -(temp - 28) / (28 - 26)
            valTemp.append([lngTemp[0], cold])
            #Hangat
            warm = (temp - 26) / (28 - 26)
            valTemp.append([lngTemp[1], warm])
        if lngTemp[0] == tempFuzzySet[1] and lngTemp[1] == tempFuzzySet[2]:
            #Hangat
            warm = -(temp - 35) / (35 - 32)
            valTemp.append([lngTemp[0], warm])
            #Panas
            hot = (temp - 32) / (35 - 32)
            valTemp.append([lngTemp[1], hot])
    else:
        valTemp.append(lngTemp[0], 1)

    return valTemp

def humidFuzzy(humid):
    lngHumid = []
    if humid >= 0 and humid <= 40:
        lngHumid.append(humidFuzzySet[0]) #Kering
    if humid >= 30 and humid <= 80:
        lngHumid.append(humidFuzzySet[1]) #Lembab
    if humid >= 70 and humid <= 100:
        lngHumid.append(humidFuzzySet[2]) #Basah

    valHumid = []
    if len(lngHumid) > 1:
        if lngHumid[0] == humidFuzzySet[0] and lngHumid[1] == humidFuzzySet[1]:
            #Kering
            dry = -(humid - 40) / (40 - 20)
            valHumid.append([lngHumid[0], dry])
            #Lembab
            moist = (humid - 20) / (40 - 20)
            valHumid.append([lngHumid[1], moist])
        if lngHumid[0] == humidFuzzySet[1] and lngHumid[1] == humidFuzzySet[2]:
            #Lembab
            moist = -(humid - 80) / (80 - 70)
            valHumid.append([lngHumid[0], moist])
            #Basah
            wet = (humid - 70) / (80 - 70)
            valHumid.append([lngHumid[1], wet])
    else:
        valHumid.append(lngHumid[0], 1)

    return valHumid

def lightFuzzy(light):
    lngLight = []
    if light >= 0 and light <= 400:
        lngLight.append(lightFuzzySet[0]) #Gelap
    if light >= 250 and light <=750:
        lngLight.append(lightFuzzySet[1]) #Redup
    if light >= 600 and light <= 1000:
        lngLight.append(lightFuzzySet[2]) #Terang

    valLight = []
    if len(lngLight) > 1:
        if lngLight[0] == lightFuzzySet[0] and lngLight[1] == lightFuzzySet[1]:
            #Gelap
            dark = -(light - 400) / (400 - 250)
            valLight.append([lngLight[0], dark])
            #Redup
            dim = (light - 250) / (400 - 250)
            valLight.append([lngLight[1], dim])
        if lngLight[0] == lightFuzzySet[1] and lngLight[1] == lightFuzzySet[2]:
            #Redup
            dim = -(light - 750) / (750 - 600)
            valLight.append([lngLight[0], dim])
            #Terang
            bright = (light - 600) / (750 - 600)
            valLight.append([lngLight[1], bright])
    else:
        valLight.append(lngLight[0], 1)

    return valLight

def interference(s1Val, s2Val, tVal, hVal, lVal):
    print(s1Val, s2Val, tVal, hVal, lVal)

def defuzzyfication():
    x = 0

#Function for automatic watering using fuzzy logic
def autoWatering():
    #bot.send_message(GROUP_ID, 'Scheduling berjalan ' + str(datetime.now()))
    # sTime = datetime.now()
    # snData = dataFetch()
    # soil1 = snData.get("soilc1")
    # soil2 = snData.get("soilc2")
    # temp = snData.get("temp")
    # humid = snData.get("humid")
    # light = snData.get("light")

    bot.send_message(GROUP_ID, 'Menyalakan pompa selama 2 menit 30 detik.' )
    relayOn()
    relayTimer = threading.Timer(150, relayOff, args=[GROUP_ID])
    relayTimer.start()

#Function for scheduling sensor data fetch
def autoSchedWatering():
    global wtrMode
    schedule.every().day.at("09:00").do(autoWatering).tag('otomatis')
    
    while wtrMode == 1:
        schedule.run_pending()
        time.sleep(1)

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
    bot.send_message(message.chat.id, "Membaca nilai sensor (" + str(datetime.now().strftime("%H:%M:%S")) + ")")
    sData = dataFetch()
    sMsg = "Kelembaban Tanah (Pot 1): " + str(sData.get("soilc1")) + ("% (") + \
            str(sData.get("soil1")) + (")") + \
            "\nKelembaban Tanah (Pot 2): " + str(sData.get("soilc2")) + ("% (") + \
            str(sData.get("soil2")) + (")") + \
            "\nSuhu: " + str(sData.get("temp")) + \
            "C\nKelembaban: " + str(sData.get("humidity")) + \
            "RH\nIntensitas Cahaya: " + str(sData.get("light"))
    print(sMsg)
    bot.send_message(message.chat.id, sMsg + "\n(" + str(datetime.now().strftime("%H:%M:%S")) + ")")

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

def main():
    print('I am listening ...')
    bot.add_custom_filter(custom_filters.ChatFilter())
    threading.Thread(bot.infinity_polling(timeout=20)).start()

if __name__ == '__main__':
    main()