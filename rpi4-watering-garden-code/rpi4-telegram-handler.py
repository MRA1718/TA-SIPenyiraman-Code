import time
import random
import datetime
import telepot
import RPi.GPIO as GPIO
from telepot.loop import MessageLoop

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
pinRelay = 17
GPIO.setup(pinRelay, GPIO.OUT)
pumpFlag = 0
"""
def relay():
    global pumpFlag
    
    GPIO.output(pinRelay, GPIO.HIGH)
    pumpFlag = 1
    time.sleep(180)
    GPIO.output(pinRelay, GPIO.LOW)
    pumpFlag = 0
"""
def handle(msg):
    chat_id = msg['chat']['id']
    command = msg['text']
    global pumpFlag

    print ('Got command: %s' % command)

    if command == '/pompa':
        if pumpFlag == 0:
            bot.sendMessage(chat_id, 'Menyalakan pompa selama 3 menit.')
            print('1st msg')
            GPIO.output(pinRelay, GPIO.HIGH)
            pumpFlag = 1
            time.sleep(180)
            GPIO.output(pinRelay, GPIO.LOW)
            pumpFlag = 0
            bot.sendMessage(chat_id, 'Mematikan pompa, penyiraman selesai')
        else:
            bot.sendMessage(chat_id, 'Pompa sedang menyala')
            print('2nd msg')

bot = telepot.Bot('5725314127:AAHxruba6S34B0He6rQ8vVRlJ6IZ_0ucgQ4')

MessageLoop(bot, handle).run_as_thread()
print ('I am listening ...')

while 1:
    time.sleep(10)