# ---- LIBRERIAS ----
import Adafruit_DHT
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import time
from gpiozero import LED
import serial
import RPi.GPIO as GPIO
import vlc
import os



# ---- VARIABLES ----
app = FastAPI()
SENSOR_DHT = Adafruit_DHT.DHT11  # SEÑALIZAMOS EL SENSOR
PIN_DHT = 4  # SEÑALIZAMOS EL PIN 4
led_regar = LED(17)
led_sembrar = LED(27)

#Motores -----ROVER-----
ena = 18			
in1 = 23
in2 = 24
enb = 19
in3 = 6
in4 = 5
velocidad=60
incremento=0
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


# SERVO
GPIO.setmode(GPIO.BCM)
servo_pin = 20
GPIO.setup(servo_pin, GPIO.OUT)
pwm = GPIO.PWM(servo_pin, 50)
pwm.start(7.5)
time.sleep(1)

# serial humedad_suelo
ser = serial.Serial('/dev/ttyACM0', 9600)




def leer_humedad_suelo():
    # SERIAL CALCULAR HUMEDAD
    read_serial = ser.readline().decode('utf-8').rstrip()
    dato = float(read_serial) * 100 / 1023
    humedad_suelo = 100 - dato
    humedad_suelo = round(humedad_suelo, 2)
    print('Humedad_suelo: ' + str(humedad_suelo) + '%')
    return humedad_suelo


def gira_servo_0():
    duty = 0 / 18 + 2.5
    pwm.ChangeDutyCycle(duty)
   


def gira_servo_180():
    duty = 180 / 18 + 2.5
    pwm.ChangeDutyCycle(duty)



# ---- PROCESO ----
def leer_sensores():
    humedad = None
    temperatura = None

    # Keep trying to read sensor data until both humidity and temperature are valid
    while humedad is None or temperatura is None:
        humedad, temperatura = Adafruit_DHT.read_retry(SENSOR_DHT, PIN_DHT)
       

    return humedad, temperatura


# funciones de sentido de giro de los motores
def  Giro_Favor_Reloj_MotorA():
	GPIO.output(in1,False)
	GPIO.output(in2,True)

def Giro_Contra_Reloj_MotorA():
	GPIO.output(in1,True)
	GPIO.output(in2,False)

def  Giro_Favor_Reloj_MotorB():
	GPIO.output(in3,True)
	GPIO.output(in4,False)

def Giro_Contra_Reloj_MotorB():
	GPIO.output(in3,False)
	GPIO.output(in4,True)
def terminar():
	GPIO.output(in3,False)
	GPIO.output(in4,False)
	GPIO.output(in1,False)
	GPIO.output(in2,False)
	
def avanzar_W():
	Giro_Favor_Reloj_MotorA()
	Giro_Favor_Reloj_MotorB()	
def retroceder_S():
	Giro_Contra_Reloj_MotorA()
	Giro_Contra_Reloj_MotorB()	

def giro_eje_a():
	Giro_Contra_Reloj_MotorA()
	Giro_Favor_Reloj_MotorB()

def giro_eje_d():
	Giro_Contra_Reloj_MotorB()
	Giro_Favor_Reloj_MotorA()
    
def velocity(velocidad, incremento):
    velocidad=velocidad+incremento
    pwm_a.ChangeDutyCycle(int(velocidad))
    pwm_b.ChangeDutyCycle(int(velocidad))
def velocitysetup(velocidad):
    pwm_a.ChangeDutyCycle(int(velocidad))
    pwm_b.ChangeDutyCycle(int(velocidad))


#####




@app.get("/", response_class=HTMLResponse)
def read_root():
    humedad, temperatura = leer_sensores()
    humedad_suelo = leer_humedad_suelo()
    print("Temperatura={0:0.1f}C  Humedad={1:0.1f}%".format(temperatura, humedad))

    return """
    <html>
      <head>
        <title>El Rasposo</title>
        <style>
          body {{
            font-family: Arial, sans-serif;
            background-color: #f1f1f1;
            margin: 0;
            padding: 0;
          }}

          .container {{
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
            background-color: #fff;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
          }}

          h1 {{
            text-align: center;
            color: #333;
          }}

          .data {{
            margin-top: 20px;
            display: flex;
            justify-content: space-between;
          }}

          .data-item {{
            text-align: center;
          }}

          .data-label {{
            font-weight: bold;
          }}

          .button-container {{
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            margin-top: 20px;
          }}

          .button-container button {{
            margin: 5px;
          }}

          .text-container {{
            text-align: center;
            margin-top: 10px;
          }}
        </style>
        <script>
          function updateSensorData() {{
            fetch("/sensor-data")
              .then(response => response.json())
              .then(data => {{
                const temperaturaElement = document.getElementById("temperatura");
                const humedadElement = document.getElementById("humedad");
                const humedadSueloElement = document.getElementById("humedad-suelo");

                temperaturaElement.innerText = data.temperatura.toFixed(1) + "C";
                humedadElement.innerText = data.humedad.toFixed(1) + "%";
                humedadSueloElement.innerText = data.humedadSuelo.toFixed(1) + "%";
              }});
          }}

          function sendCommand(command) {{
            fetch("/command/" + command)
              .then(response => response.json())
              .then(data => console.log(data));
          }}

          setInterval(updateSensorData, 5000);
        </script>
      </head>
      <body>
        <div class="container">
          <h1>El Rasposo</h1>
          <div class="data">
            <div class="data-item">
              <span class="data-label">Temperatura del ambiente:</span>
              <span id="temperatura">{0:0.1f}C</span>
            </div>
            <div class="data-item">
              <span class="data-label">Humedad del ambiente:</span>
              <span id="humedad">{1:0.1f}%</span>
            </div>
            <div class="data-item">
              <span class="data-label">Humedad del suelo:</span>
              <span id="humedad-suelo">{2:0.1f}%</span>
            </div>
          </div>
          <div class="button-container">
            <button onclick="sendCommand('up')">↑</button>
            <button onclick="sendCommand('down')">↓</button>
            <button onclick="sendCommand('detente')">||</button>
            <button onclick="sendCommand('left')">←</button>
            <button onclick="sendCommand('right')">→</button>
            <button onclick="sendCommand('activate_sample')">Activa_muestra</button>
            <button onclick="sendCommand('deactivate_sample')">Desactiva_muestra</button>
            <button onclick="sendCommand('increment')">Incrementar</button>
            <button onclick="sendCommand('decrement')">Decrementar</button>
          </div>
          <div class="button-container">
            <button onclick="sendCommand('regar')">Regar</button>
            <button onclick="sendCommand('sembrar')">Sembrar</button>
          </div>
          <div class="text-container">
            <span>Velocidad</span>
          </div>
        </div>
      </body>
    </html>
    """.format(temperatura, humedad, humedad_suelo)


@app.get("/sensor-data")
async def get_sensor_data():
    humedad, temperatura = leer_sensores()
    humedad_suelo = leer_humedad_suelo()
    return {"temperatura": temperatura, "humedad": humedad, "humedadSuelo": humedad_suelo}


@app.get("/command/{command}")
async def execute_command(command: str):

    if command == "down":
        velocitysetup(velocidad)
        retroceder_S()

    elif command == "up":
        velocitysetup(velocidad)
        avanzar_W()

    elif command == "detente":
        terminar()

    elif command == "left":
        velocitysetup(velocidad)
        giro_eje_a()

    elif command == "right":
        velocitysetup(velocidad)
        giro_eje_d()

    elif command == "regar":
        led_regar.on()
        time.sleep(4)
        led_regar.off()
    elif command == "sembrar":
        led_sembrar.on()
        time.sleep(4)
        led_sembrar.off()
    elif command == "activate_sample":
        gira_servo_0()
    elif command == "deactivate_sample":
        gira_servo_180()

    

    return {"message": f"Executing command: {command}"}
