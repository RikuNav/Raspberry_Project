#! /usr/bin/env python
import RPi.GPIO as GPIO
import os
import time
#Define nombre de las entradas del puente H
ena = 18			
in1 = 23
in2 = 24

enb = 19
in3 = 6
in4 = 5
#configura los pines segun el microprocesador Broadcom
GPIO.setmode(GPIO.BCM)
#configura los pines como salidas
GPIO.setup(ena,GPIO.OUT)
GPIO.setup(enb,GPIO.OUT)
GPIO.setup(in1, GPIO.OUT)
GPIO.setup(in2, GPIO.OUT)
GPIO.setup(in3, GPIO.OUT)
GPIO.setup(in4, GPIO.OUT)
#Define las salidas PWM q
pwm_a = GPIO.PWM(ena,500)
pwm_b = GPIO.PWM(enb,500)
#inicializan los PWM con un duty Cicly de cero
pwm_a.start(0)
pwm_b.start(0)
# funciones de sentido de giro de los motores
def  Giro_Favor_Reloj_MotorA():
	GPIO.output(in1,False)
	GPIO.output(in2,True)

def Giro_Contra_Reloj_MotorA():
	GPIO.output(in1,True)
	GPIO.output(in2,False)

def  Giro_Favor_Reloj_MotorB():
	GPIO.output(in3,False)
	GPIO.output(in4,True)

def Giro_Contra_Reloj_MotorB():
	GPIO.output(in3,True)
	GPIO.output(in4,False)
def terminar():
	GPIO.output(in3,False)
	GPIO.output(in4,True)
	GPIO.output(in1,False)
	GPIO.output(in2,True)
#limpia la pantalla
os.system('clear')
print("Elija motor[A-B], el sentido [F-R] y la velocidad [0-100]")
print("ejemplo 'AF50' MOTOR A Foward a 50%. de velocidad")
print("CTRL-C para salir")
print
try:
	while True:
		cmd = input("inserte el comando ")
		cmd = cmd.lower()
		motor = cmd[0]
		direccion =cmd[1]
		velocidad =cmd[2:5]

		if motor == "a":
			if direccion == "f":
				Giro_Favor_Reloj_MotorA()
				print("motor A, CW, vel="+velocidad)
			elif direccion== "r":
				Giro_Contra_Reloj_MotorA()
				print("motor A, CCW, vel="+velocidad)
			else:
				print("comando no reconocido")
			pwm_a.ChangeDutyCycle(int(velocidad))
			print
		
		elif motor=="x":
			break
		elif motor == "b":
			if direccion == "f":
				Giro_Favor_Reloj_MotorB()
				print("motor B, CW, vel="+velocidad)
			elif direccion == "r":
				Giro_Contra_Reloj_MotorB()
			else:
				print("comando no reconocido")
			pwm_b.ChangeDutyCycle(int(velocidad))
			print
		else:
			print
			print("comando no reconocido")
			print
except KeyboardInterrupt:
	pwm_a.stop()
	pwm_b.stop()
	GPIO.cleanup()
	os.system('clear')
	print
	print("Programa Terminado por el usuario")
	print
	exit()