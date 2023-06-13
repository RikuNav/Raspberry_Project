import RPi.GPIO as GPIO
import time
GPIO.setmode(GPIO.BCM)

servo_pin=17
GPIO.setup(servo_pin, GPIO.OUT)

pwm= GPIO.PWM(servo_pin,50)

pwm.start(2.5)
time.sleep(1)

def gira_servo(grados):
    duty=grados/18+2.5
    pwm.ChangeDutyCycle(duty)
    time.sleep(1)
