import RPi.GPIO as GPIO
import time

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

pinRelay = 17
GPIO.setup(pinRelay, GPIO.OUT)
#GPIO.output(pinRelay, GPIO.HIGH)
#time.sleep(180)
GPIO.output(pinRelay, GPIO.LOW)
