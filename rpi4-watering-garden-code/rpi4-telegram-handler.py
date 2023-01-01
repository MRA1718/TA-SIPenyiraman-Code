import telebot
import time
import threading
import RPi.GPIO as GPIO
import json
import serial
import schedule
import mysql.connector
import warnings
from datetime import datetime
from telebot import custom_filters
from telebot import TeleBot

#Ignore warning when opening rules file
warnings.filterwarnings("ignore", category=DeprecationWarning) 

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
soilFuzzySet = ['Kering', 'Lembab', 'basah'] #For soil moisture
tempFuzzySet = ['Dingin', 'Hangat', 'Panas'] #For Temperature
humidFuzzySet = ['Kering', 'Lembab', 'basah'] #For air humidity
#lightFuzzySet = ['Gelap', 'Redup', 'Terang'] #For light intensity

relayDurFuzzySet = ['Pendek', 'Sedang', 'Lama'] #For relay "on" duration

#Fuzzy Function
#Fuzzyfication
def soilFuzzy(soil):
    lngSoil = []
    if soil >= 0 and soil <= 40:
        lngSoil.append(soilFuzzySet[0]) #Kering
    if soil >= 20 and soil <= 80:
        lngSoil.append(soilFuzzySet[1]) #Lembab
    if soil >= 60 and soil <= 100:
        lngSoil.append(soilFuzzySet[2]) #Basah

    valSoil = []
    if len(lngSoil) > 1:
        if lngSoil[0] == soilFuzzySet[0] and lngSoil[1] == soilFuzzySet[1]:
            #Kering
            dry = -(soil - 40) / (40 - 20)
            valSoil.append([lngSoil[0], dry])
            #Lembab
            moist = (soil - 20) / (40 - 20)
            valSoil.append([lngSoil[1], moist])
        if lngSoil[0] == soilFuzzySet[1] and lngSoil[1] == soilFuzzySet[2]:
            #Lembab
            moist = -(soil - 80) / (80 - 60)
            valSoil.append([lngSoil[0], moist])
            #Basah
            wet = (soil - 60) / (80 - 60)
            valSoil.append([lngSoil[1], wet])
    else:
        valSoil.append([lngSoil[0], 1])

    return valSoil

def tempFuzzy(temp):
    lngTemp = []

    if temp >= 20 and temp <= 29:
        lngTemp.append(tempFuzzySet[0]) #Dingin
    if temp >= 26 and temp <= 36:
        lngTemp.append(tempFuzzySet[1]) #Hangat
    if temp >= 30 and temp <= 45:
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
        valTemp.append([lngTemp[0], 1])

    return valTemp

def humidFuzzy(humid):
    lngHumid = []
    if humid >= 0 and humid <= 40:
        lngHumid.append(humidFuzzySet[0]) #Kering
    if humid >= 20 and humid <= 80:
        lngHumid.append(humidFuzzySet[1]) #Lembab
    if humid >= 60 and humid <= 100:
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
            moist = -(humid - 80) / (80 - 60)
            valHumid.append([lngHumid[0], moist])
            #Basah
            wet = (humid - 60) / (80 - 60)
            valHumid.append([lngHumid[1], wet])
    else:
        valHumid.append([lngHumid[0], 1])

    return valHumid

# def lightFuzzy(light):
#     lngLight = []
#     if light >= 0 and light <= 400:
#         lngLight.append(lightFuzzySet[0]) #Gelap
#     if light >= 250 and light <=750:
#         lngLight.append(lightFuzzySet[1]) #Redup
#     if light >= 600 and light <= 1000:
#         lngLight.append(lightFuzzySet[2]) #Terang

#     valLight = []
#     if len(lngLight) > 1:
#         if lngLight[0] == lightFuzzySet[0] and lngLight[1] == lightFuzzySet[1]:
#             #Gelap
#             dark = -(light - 400) / (400 - 250)
#             valLight.append([lngLight[0], dark])
#             #Redup
#             dim = (light - 250) / (400 - 250)
#             valLight.append([lngLight[1], dim])
#         if lngLight[0] == lightFuzzySet[1] and lngLight[1] == lightFuzzySet[2]:
#             #Redup
#             dim = -(light - 750) / (750 - 600)
#             valLight.append([lngLight[0], dim])
#             #Terang
#             bright = (light - 600) / (750 - 600)
#             valLight.append([lngLight[1], bright])
#     else:
#         valLight.append([lngLight[0], 1])

#     return valLight

def inference(s1, s2, tmp, hmd, fuzzyRules):
    agenda = []
    possibility = []

    for data in s1:
        agenda.append(data)
    for data in s2:
        agenda.append(data)
    for data in tmp:
        agenda.append(data)
    for data in hmd:
        agenda.append(data)

    while agenda:
        item = agenda.pop(0)
        for rule in fuzzyRules:
            for j, premise in enumerate(rule[0]):
                if premise == item[0]:
                    rule[0][j] = [True, rule[0][j], item[1]]
            if check_hypothesis(rule[0]):
                conclusion = rule[1]
                possibility.append(rule)
                agenda.append(conclusion)
                rule[0] = [rule[0],'processed']

    return possibility

def defuzzyfication(input):
    
    result = float(0)

    #Pendek
    x1_short = 0
    x2_short = 100
    coefisien_short = float(0)

    #Sedang
    x1_medium = 80
    x2_medium = 150
    coefisien_medium = float(0)

    #Lama
    x1_long = 130
    x2_long = 180
    coefisien_long = float(0)

    shortNumerator = float(0)
    mediumNumerator = float(0)
    longNumerator = float(0)

    shortDenominator = float(0)
    mediumDenominator = float(0)
    longDenominator = float(0)

    for data in input:
        if data[0] == relayDurFuzzySet[0]:
            coefisien_short = data[1]
        if data[0] == relayDurFuzzySet[1]:
            coefisien_medium = data[1]
        if data[0] == relayDurFuzzySet[2]:
            coefisien_long = data[1]

    #Short and medium
    if coefisien_short != float(0) and coefisien_medium != float(0) and coefisien_long == float(0):
        x_startShort = x1_short
        x_endShort = x1_medium + 1 # should be plus 1

        x_startMedium = x2_short
        x_endMedium = x1_long + 1 # should be plus 1

        for i in range(x_startShort, x_endShort):
            shortNumerator += i * coefisien_short
            shortDenominator += coefisien_short

        for i in range(x_startMedium, x_endMedium):
            mediumNumerator += i * coefisien_medium
            mediumDenominator += coefisien_medium

        result = (mediumNumerator + shortNumerator) / (mediumDenominator + shortDenominator)
    
    #medium and long
    if coefisien_short == float(0) and coefisien_medium != float(0) and coefisien_long != float(0):

        x_startMedium = x2_short
        x_endMedium = x1_long + 1  # should be plus 1

        x_startLong = x2_medium
        x_endLong = x2_long + 1  # should be plus 1

        for i in range(x_startMedium, x_endMedium):
            mediumNumerator += i * coefisien_medium
            mediumDenominator += coefisien_medium

        for i in range(x_startLong, x_endLong):
            longNumerator += i * coefisien_long
            longDenominator += coefisien_long

        result = (mediumNumerator + longNumerator) / (mediumDenominator + longDenominator)

    #short, medium and long
    if coefisien_short != float(0) and coefisien_medium != float(0) and coefisien_long != float(0):

        x_startShort = x1_short
        x_endShort = x1_medium + 1  # should be plus 1

        x_startMedium = x2_short
        x_endMedium = x1_long + 1  # should be plus 1

        x_startLong = x2_medium
        x_endLong = x2_long + 1  # should be plus 1

        for i in range(x_startShort, x_endShort):
            shortNumerator += i * coefisien_short
            shortDenominator += coefisien_short

        for i in range(x_startMedium, x_endMedium):
            mediumNumerator += i * coefisien_medium
            mediumDenominator += coefisien_medium

        for i in range(x_startLong, x_endLong):
            longNumerator += i * coefisien_long
            longDenominator += coefisien_long

        result = (shortNumerator + mediumNumerator + longNumerator) / (shortNumerator + mediumDenominator + longDenominator)

    #Only short
    if coefisien_short != float(0) and coefisien_medium == float(0) and coefisien_long == float(0):
        x_startShort = x1_short
        x_endShort = x1_medium + 1  # should be plus 1

        for i in range(x_startShort, x_endShort):
            shortNumerator += i * coefisien_short
            shortDenominator += coefisien_short

        result = (shortNumerator) / (shortDenominator)
    
    #Only medium
    if coefisien_short == float(0) and coefisien_medium != float(0) and coefisien_long == float(0):
        x_startMedium = x2_short
        x_endMedium = x1_long + 1  # should be plus 1

        for i in range(x_startMedium, x_endMedium):
            mediumNumerator += i * coefisien_medium
            mediumDenominator += coefisien_medium

        result = (mediumNumerator) / (mediumDenominator)

    #Only long
    if coefisien_short == float(0) and coefisien_medium == float(0) and coefisien_long != float(0):
        x_startLong = x2_medium
        x_endLong = x2_long + 1  # should be plus 1

        for i in range(x_startLong, x_endLong):
            longNumerator += i * coefisien_long
            longDenominator += coefisien_long

        result = (longNumerator)/(longDenominator)

    return result

def check_hypothesis(hypothesis):
    for entry in hypothesis:
        if entry[0] != True:
            return False
    return True

def parse_kb_file(filename):
    kb_file = open(filename, 'rU')        # 'rU' is smart about line-endings
    kb_rules = []                         # variable to store rules

    for line in kb_file:                  # read the non-commented lines
        if not line.startswith('#') and line != '\n':
            kb_rules.append(split_and_build_literals(line.strip()))

    kb_file.close()
    return kb_rules

def split_and_build_literals(line):
    rules = []
    #Split the line of literals
    literals = line.split(' ')
    hypothesis = []
    
    while len(literals) > 1:
        hypothesis.append(literals.pop(0))
    rules.append(hypothesis)
    rules.append(literals.pop(0))
    
    return rules

#Function for automatic watering using fuzzy logic
def autoWatering():
    bot.send_message(GROUP_ID, 'Sistem penyiraman otomatis aktif.')
    time.sleep(0.5) #Short delay after message
    
    sTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    bot.send_message(GROUP_ID, 'Mengambil data sensor (' + str(sTime) + ')')
    
    snData = dataFetch() #Fetch data from sensor
    fTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    s1 = snData.get("soilc1")
    sn1 = snData.get("soil1")
    s2 = snData.get("soilc2")
    sn2 = snData.get("soil2")
    tmp = snData.get("temp")
    hmd = snData.get("humidity")
    lght = snData.get("light")
    
    sMsg = "Kelembaban Tanah (Pot 1): " + str(s1) + ("% (") + \
            str(sn1) + (")") + \
            "\nKelembaban Tanah (Pot 2): " + str(s2) + ("% (") + \
            str(sn2) + (")") + \
            "\nSuhu: " + str(tmp) + \
            "C\nKelembaban: " + str(hmd) + \
            "RH\nIntensitas Cahaya: " + str(lght)
    print(sMsg)
    bot.send_message(GROUP_ID, sMsg + "\n(" + str(fTime) + ")")
    time.sleep(0.5) #Short Delay after message
    bot.send_message(GROUP_ID, 'Menghitung durasi penyiraman... (' + str(fTime) + ')')
    
        soil1 = soilFuzzy(s1)
    soil2 = soilFuzzy(s2)
    temp = tempFuzzy(tmp)
    humid = humidFuzzy(hmd)
    #light = lightFuzzy(lght)
    rules = parse_kb_file('/home/pi4/Github_Repo/TA-SIPenyiraman-Code/rpi4-watering-garden-code/rules.kb')

    print("Output of Fuzzyfication:")
    print(soil1)
    print(soil2)
    print(temp)
    print(humid)
    #print(light)
    print("\n")

    inf = inference(soil1, soil2, temp, humid, rules)

    print(inf)
    print("\n")

    resRuleMin = []

    for data in inf:
        print(data[0][0][0][1], data[0][0][0][2], data[0][0][1][1], data[0][0][1][2], data[1])
        minimum = min(data[0][0][0][2], data[0][0][1][2])
        resRuleMin.append([data[1],minimum])
    print("\n")

    print(resRuleMin)

    resRuleMax = {}
    for data in resRuleMin:
        if data[0] in resRuleMax:
            resRuleMax[data[0]].add(data[1])
        else:
            resRuleMax[data[0]] = set([data[1]])
    
    outputInference = []
    for key, value in resRuleMax.items():
        outputInference.append([key,max(value)])

    print("\n")
    print("Output Inference: ", outputInference)
    print("\n")

    duration = int(defuzzyfication(outputInference))

    eTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print("Watering duration: ", duration)

    if duration > 0:    
        bot.send_message(GROUP_ID, 'Menyalakan pompa selama ' + str(duration) + ' detik. (' + str(eTime) + ')'  )
    
        relayOn()
        relayTimer = threading.Timer(duration, relayOff, args=[GROUP_ID])
        relayTimer.start()

    #Insert log data to database
    mycursor = mydb.cursor()

    sql = "INSERT INTO log_penyiraman_otomatis(ot_soil1, ot_soil2, ot_temp, ot_humid, ot_light, ot_time_start_op, ot_time_fi_fetch, ot_time_start_rly, ot_relay_duration)\
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
    val = (s1, s2, tmp, hmd, lght, sTime, fTime, eTime, duration)
    mycursor.execute(sql, val)
    mydb.commit()

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

@bot.message_handler(commands=['test'])
def testHandle(message):
    autoWatering()

def main():
    print('I am listening ...')
    bot.add_custom_filter(custom_filters.ChatFilter())
    threading.Thread(bot.infinity_polling(timeout=20)).start()

if __name__ == '__main__':
    main()