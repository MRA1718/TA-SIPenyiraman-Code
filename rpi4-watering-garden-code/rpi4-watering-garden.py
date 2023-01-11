import telebot
import time
import threading
import RPi.GPIO as GPIO
import json
import serial
import schedule
import mysql.connector
import warnings
import atexit
import numpy as np
import skfuzzy as fuzz
import matplotlib.pyplot as plt
from skfuzzy import control as ctrl
from datetime import datetime
from telebot import custom_filters
from telebot import TeleBot

#Ignore warning when opening rules file
warnings.filterwarnings("ignore", category=DeprecationWarning) 

#Initialze database connection
config = {'host': 'localhost',
    'user': 'rpi4db',
    'password': 'sqlrpi4',
    'database': 'rpi4watering'}
mydb = mysql.connector.connect(**config)

#Fetch token telegram & group ID
mycursor = mydb.cursor()
telsql = "SELECT token_telegram FROM telegram"
mycursor.execute(telsql)
restl = mycursor.fetchall()
mycursor.close()
mydb.close()

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
#Fuzzy input
soil1 = ctrl.Antecedent(np.arange(0, 100, 1), 'soil1')
soil2 = ctrl.Antecedent(np.arange(0, 100, 1), 'soil2')
temperature = ctrl.Antecedent(np.arange(20, 45, 1), 'temperature')
humidity = ctrl.Antecedent(np.arange(0, 100, 1), 'humidity')
light = ctrl.Antecedent(np.arange(0, 1000, 1), 'light')
#Fuzzy output
duration = ctrl.Consequent(np.arange(0, 180, 1), 'duration')

#soil1
soil1['kering'] = fuzz.trapmf(soil1.universe, [0, 0, 30, 45])
soil1['lembab'] = fuzz.trapmf(soil1.universe, [30, 50, 70, 85])
soil1['basah'] = fuzz.trapmf(soil1.universe, [70, 80, 100, 100])

#soil2
soil2['kering'] = fuzz.trapmf(soil2.universe, [0, 0, 30, 45])
soil2['lembab'] = fuzz.trapmf(soil2.universe, [30, 50, 70, 85])
soil2['basah'] = fuzz.trapmf(soil2.universe, [70, 80, 100, 100])

#temperature
temperature['dingin'] = fuzz.trapmf(temperature.universe, [20, 20, 22, 25])
temperature['hangat'] = fuzz.trapmf(temperature.universe, [23, 25, 32, 36])
temperature['panas'] = fuzz.trapmf(temperature.universe, [30, 35, 45, 45]) 

#humidity
humidity['kering'] = fuzz.trapmf(humidity.universe, [0, 0, 30, 40])
humidity['lembab'] = fuzz.trapmf(humidity.universe, [30, 40, 60, 80])
humidity['basah'] = fuzz.trapmf(humidity.universe, [70, 80, 100, 100])

#light
light['gelap'] = fuzz.trapmf(light.universe, [0, 0, 200, 400])
light['redup'] = fuzz.trapmf(light.universe, [200, 400, 600, 800])
light['terang'] = fuzz.trapmf(light.universe, [600, 800, 1000, 1000])

#duration
duration['pendek'] = fuzz.trapmf(duration.universe, [0, 0, 45, 75])
duration['sedang'] = fuzz.trapmf(duration.universe, [40, 75, 105, 135])
duration['lama'] = fuzz.trapmf(duration.universe, [105, 135, 180, 180])

#Fuzzy rule
rule1 = ctrl.Rule(soil1['basah'] & soil2['basah'] & temperature['dingin'] & humidity['basah'], duration['pendek'])
rule2 = ctrl.Rule(soil1['basah'] & soil2['basah'] & temperature['dingin'] & humidity['lembab'], duration['pendek'])
rule3 = ctrl.Rule(soil1['basah'] & soil2['basah'] & temperature['dingin'] & humidity['kering'], duration['pendek'])
rule4 = ctrl.Rule(soil1['basah'] & soil2['basah'] & temperature['hangat'] & humidity['basah'], duration['pendek'])
rule5 = ctrl.Rule(soil1['basah'] & soil2['basah'] & temperature['hangat'] & humidity['lembab'], duration['pendek'])
rule6 = ctrl.Rule(soil1['basah'] & soil2['basah'] & temperature['hangat'] & humidity['kering'], duration['pendek'])
rule7 = ctrl.Rule(soil1['basah'] & soil2['basah'] & temperature['panas'] & humidity['basah'], duration['pendek'])
rule8 = ctrl.Rule(soil1['basah'] & soil2['basah'] & temperature['panas'] & humidity['lembab'], duration['sedang'])
rule9 = ctrl.Rule(soil1['basah'] & soil2['basah'] & temperature['panas'] & humidity['kering'], duration['sedang'])

rule10 = ctrl.Rule(soil1['basah'] & soil2['lembab'] & temperature['dingin'] & humidity['basah'], duration['pendek'])
rule11 = ctrl.Rule(soil1['basah'] & soil2['lembab'] & temperature['dingin'] & humidity['lembab'], duration['pendek'])
rule12 = ctrl.Rule(soil1['basah'] & soil2['lembab'] & temperature['dingin'] & humidity['kering'], duration['pendek'])
rule13 = ctrl.Rule(soil1['basah'] & soil2['lembab'] & temperature['hangat'] & humidity['basah'], duration['pendek'])
rule14 = ctrl.Rule(soil1['basah'] & soil2['lembab'] & temperature['hangat'] & humidity['lembab'], duration['sedang'])
rule15 = ctrl.Rule(soil1['basah'] & soil2['lembab'] & temperature['hangat'] & humidity['kering'], duration['sedang'])
rule16 = ctrl.Rule(soil1['basah'] & soil2['lembab'] & temperature['panas'] & humidity['basah'], duration['lama'])
rule17 = ctrl.Rule(soil1['basah'] & soil2['lembab'] & temperature['panas'] & humidity['lembab'], duration['lama'])
rule18 = ctrl.Rule(soil1['basah'] & soil2['lembab'] & temperature['panas'] & humidity['kering'], duration['lama'])

rule19 = ctrl.Rule(soil1['lembab'] & soil2['basah'] & temperature['dingin'] & humidity['basah'], duration['pendek'])
rule20 = ctrl.Rule(soil1['lembab'] & soil2['basah'] & temperature['dingin'] & humidity['lembab'], duration['pendek'])
rule21 = ctrl.Rule(soil1['lembab'] & soil2['basah'] & temperature['dingin'] & humidity['kering'], duration['pendek'])
rule22 = ctrl.Rule(soil1['lembab'] & soil2['basah'] & temperature['hangat'] & humidity['basah'], duration['pendek'])
rule23 = ctrl.Rule(soil1['lembab'] & soil2['basah'] & temperature['hangat'] & humidity['lembab'], duration['sedang'])
rule24 = ctrl.Rule(soil1['lembab'] & soil2['basah'] & temperature['hangat'] & humidity['kering'], duration['sedang'])
rule25 = ctrl.Rule(soil1['lembab'] & soil2['basah'] & temperature['panas'] & humidity['basah'], duration['lama'])
rule26 = ctrl.Rule(soil1['lembab'] & soil2['basah'] & temperature['panas'] & humidity['lembab'], duration['lama'])
rule27 = ctrl.Rule(soil1['lembab'] & soil2['basah'] & temperature['panas'] & humidity['kering'], duration['lama'])

rule28 = ctrl.Rule(soil1['lembab'] & soil2['lembab'] & temperature['dingin'] & humidity['basah'], duration['sedang'])
rule29 = ctrl.Rule(soil1['lembab'] & soil2['lembab'] & temperature['dingin'] & humidity['lembab'], duration['sedang'])
rule30 = ctrl.Rule(soil1['lembab'] & soil2['lembab'] & temperature['dingin'] & humidity['kering'], duration['sedang'])
rule31 = ctrl.Rule(soil1['lembab'] & soil2['lembab'] & temperature['hangat'] & humidity['basah'], duration['sedang'])
rule32 = ctrl.Rule(soil1['lembab'] & soil2['lembab'] & temperature['hangat'] & humidity['lembab'], duration['sedang'])
rule33 = ctrl.Rule(soil1['lembab'] & soil2['lembab'] & temperature['hangat'] & humidity['kering'], duration['lama'])
rule34 = ctrl.Rule(soil1['lembab'] & soil2['lembab'] & temperature['panas'] & humidity['basah'], duration['lama'])
rule35 = ctrl.Rule(soil1['lembab'] & soil2['lembab'] & temperature['panas'] & humidity['lembab'], duration['lama'])
rule36 = ctrl.Rule(soil1['lembab'] & soil2['lembab'] & temperature['panas'] & humidity['kering'], duration['lama'])

rule37 = ctrl.Rule(light['terang'], duration['lama'])
rule38 = ctrl.Rule(light['redup'], duration['sedang'])
rule39 = ctrl.Rule(light['gelap'], duration['pendek'])
rule40 = ctrl.Rule(light['terang'] | light['redup'], duration['sedang'])
rule41 = ctrl.Rule(light['redup'] | light['gelap'], duration['pendek'] )

#Function for automatic watering using fuzzy logic
def autoWatering():
    global mydb
    global config

    bot.send_message(GROUP_ID, 'Sistem penyiraman otomatis aktif')
   
    sTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    bot.send_message(GROUP_ID, 'Mengambil data sensor... (' + str(sTime) + ')')
    
    snData = dataFetch() #Fetch data from sensor
    fTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    s1 = snData.get("soilc1")
    sn1 = snData.get("soil1")
    s2 = snData.get("soilc2")
    sn2 = snData.get("soil2")
    tmp = snData.get("temp")
    hmd = snData.get("humidity")
    lght = snData.get("light")
    
    sMsg = "Kelembaban Tanah (Sensor 1): " + str(s1) + ("% (") + \
            str(sn1) + (")") + \
            "\nKelembaban Tanah (Sensor 2): " + str(s2) + ("% (") + \
            str(sn2) + (")") + \
            "\nSuhu: " + str(tmp) + \
            "C\nKelembaban: " + str(hmd) + \
            "RH\nIntensitas Cahaya: " + str(lght)
    print(sMsg)
    bot.send_message(GROUP_ID, sMsg + "\n(" + str(fTime) + ")")
    
    bot.send_message(GROUP_ID, 'Menghitung durasi penyiraman...')
    
    #Fuzzy process
    rules = [rule1, rule2, rule3, rule4, rule5, rule6, 
            rule7, rule8, rule9, rule10, rule11, rule12, 
            rule13, rule14, rule15, rule16, rule17, rule18,
            rule19, rule20, rule21, rule22, rule23, rule24,
            rule25, rule26, rule27, rule28, rule29, rule30,
            rule31, rule32, rule33, rule34, rule35, rule36,
            rule37, rule38, rule39, rule40, rule41]
    
    drtn_ctrl = ctrl.ControlSystem(rules)

    duratn = ctrl.ControlSystemSimulation(drtn_ctrl)

    duratn.input['soil1'] = s1
    duratn.input['soil2'] = s2
    duratn.input['temperature'] = tmp
    duratn.input['humidity'] = hmd
    duratn.input['light'] = lght

    duratn.compute()

    rDuration = round(duratn.output['duration'])

    eTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print("Watering duration: ", rDuration)
    
    if rDuration > 0:    
        bot.send_message(GROUP_ID, 'Menyalakan pompa selama ' + str(rDuration) + ' detik (' + str(eTime) + ')'  )

        relayOn()
        relayTimer = threading.Timer(rDuration, relayOff, args=[GROUP_ID])
        relayTimer.start()

    #Insert log data to database
    mydb = mysql.connector.connect(**config)
    mycursor = mydb.cursor()

    sql = "INSERT INTO log_penyiraman_otomatis(ot_soil1, ot_soil2, ot_temp, ot_humid, ot_light, ot_time_start_op, ot_time_fi_fetch, ot_time_start_rly, ot_relay_duration)\
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
    val = (s1, s2, tmp, hmd, lght, sTime, fTime, eTime, rDuration)
    mycursor.execute(sql, val)
    mydb.commit()
    mycursor.close()
    mydb.close()

def autoReminder():
    bot.send_message(GROUP_ID, 'Penyiraman otomatis akan dilakukan dalam 1 jam')

#Function for scheduling sensor data fetch
def autoSchedWatering():
    global wtrMode
    schedule.every().day.at("08:00").do(autoWatering).tag('otomatis')
    schedule.every().day.at("07:00").do(autoReminder).tag('otomatis')
    
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

def exit_handler():
    bot.send_message(GROUP_ID, 'Bot dinonaktifkan')

#Initialize Telebot API
bot = telebot.TeleBot(TOKEN)

bot.send_message(GROUP_ID, 'Bot aktif, silahkan masukkan command: (/pompa, /sensor, /mode)')

@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    bot.send_message(message.chat.id, 'List Command:\n- /pompa\n- /sensor\n- /mode')

#Bot command list
#Command /pompa for manually relay control
@bot.message_handler(commands=['pompa'])
def pumpHandle(message):
    global relayStatus
    global relayTimer
    global wtrMode
    args = message.text.split()
    fname = message.from_user.first_name
    lname = message.from_user.last_name
    name = str(fname) + ' ' + str(lname)

    if wtrMode == 0:
        if len(args) > 1 and args[1].isdigit():
            seconds = int(args[1])
            if relayStatus == 0:
                bot.send_message(message.chat.id, 'Menyalakan pompa selama ' + args[1] + ' detik' )
                sTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                relayOn()
                relayTimer = threading.Timer(seconds, relayOff, args=[message.chat.id])
                relayTimer.start()
                
                #Insert log to database
                mydb = mysql.connector.connect(**config)
                mycursor = mydb.cursor()

                sql = "INSERT INTO log_penyiraman_manual(m_name, m_time_start, m_relay_duration)\
                    VALUES (%s, %s, %s)"
                val = (name, sTime, seconds)
                mycursor.execute(sql, val)
                mydb.commit()
                mycursor.close()
                mydb.close()
            elif relayStatus == 1:
                bot.send_message(message.chat.id, 'Pompa sedang menyala, gunakan /pompa STOP untuk menghentikan')
        elif len(args) > 1 and args[1] == 'stop' and relayStatus == 1:
            relayTimer.cancel()
            GPIO.output(pinRelay, GPIO.LOW)
            relayStatus = 0
            bot.send_message(message.chat.id, 'Menghentikan pompa')
        else:
            bot.send_message(message.chat.id, 'Penggunaan:\n- /pompa <detik> (Menyalakan pompa selama durasi tertentu)\n- /pompa stop (Menghentikan pompa jika menyala)')
    elif wtrMode == 1:
        bot.send_message(message.chat.id, 'Dalam mode otomatis, silahkan ganti /mode untuk menggunakan command pompa')

#Command /sensor for collecting data sensor
@bot.message_handler(commands=['sensor'])
def sensorHandle(message):
    bot.send_message(message.chat.id, "Membaca nilai sensor (" + str(datetime.now().strftime("%H:%M:%S")) + ")")
    sData = dataFetch()
    sMsg = "Kelembaban Tanah (Sensor 1): " + str(sData.get("soilc1")) + ("% (") + \
            str(sData.get("soil1")) + (")") + \
            "\nKelembaban Tanah (Sensor 2): " + str(sData.get("soilc2")) + ("% (") + \
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
    else: bot.send_message(message.chat.id, 'Penggunaan:\n- /mode status (Menampilkan mode penyiraman)\n- /mode manual (Penyiraman manual)\n- /mode otomatis (Penyiraman otomatis setiap hari pada jam 08:00)')

def main():
    atexit.register(exit_handler)
    print('Bot listening ...')
    bot.add_custom_filter(custom_filters.ChatFilter())
    threading.Thread(bot.infinity_polling(timeout=20)).start()

if __name__ == '__main__':
    main()