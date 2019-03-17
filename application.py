from flask import *

import Adafruit_DHT
import Adafruit_BBIO.GPIO as GPIO

app = Flask(__name__)

set_temp = 0  # temperatura ustawiona w aplikacji
actual_temp = 0  # temperatura odczytana z urzadzenia
avg_temp = 0  # temperatura po usunięciu wartości odstających i uśredniona
thermostat_state = False  # stan termostatu
fan_output = 0  # zasilanie wiatraczka
sensor = Adafruit_DHT.DHT11
sensor_pin = 'P8_11'  # DHT-11 data
fan_pin = 'P8_10'  # zasilanie diody


@app.route('/')  # strona główna w aplikacji webowej
def index():
    return render_template('index.html')


def getActualTemperature():  # odczyt temperatury z DHT-11
    temp = 25
    hum, temp = Adafruit_DHT.read_retry(sensor, sensor_pin)
    return temp


@app.route('/actualTemp')  # udostępnienie aktualnej temperatury do aplikacji webowej
def thermostatProcess():
    global actual_temp, fan_output
    if thermostat_state == True:
        actual_temp = getActualTemperature()
    # przekazanie do aplikacji odczytanej temperatury (temp) oraz stanu zasilania wiatraczka (fan_output)
    return render_template('actualTemp.html', temp=actual_temp, diode=str(fan_output))


@app.route('/setTemp', methods=['POST'])  # pobranie ustawionej temperatury z aplikacji
def setTemp():
    global set_temp
    content = request.get_json()
    set_temp = float(content['desiredTemp'])
    return 'Temp posted'


@app.route('/toggleState', methods=['POST'])  # przełączanie stanu termostatu
def toggleState():
    global thermostat_state, fan_output, actual_temp
    content = request.get_json()
    thermostat_state = content['state']
    actual_temp = getActualTemperature()
    if thermostat_state:  # wstępne nastawienie termostatu, jeśli jest uruchomiony
        if set_temp <= actual_temp:
            fan_output = 1
            GPIO.output(fan_pin, GPIO.HIGH)
        if set_temp > actual_temp:
            fan_output = 0
            GPIO.output(fan_pin, GPIO.LOW)
    else:
        GPIO.output(fan_pin, GPIO.LOW)
        fan_output = 0
    return 'State posted'

@app.route('/thermostatCorrections', methods=['POST'])
def thermostatCorrections():
    global set_temp, avg_temp, fan_output
    content = request.get_json()
    avg_temp = float(content['avgTemp'])
    # regulacja stanu wiatraczka w zaleznosci od temperatury
    if set_temp <= avg_temp:
        fan_output = 1
        GPIO.output(fan_pin, GPIO.HIGH)
    if set_temp > avg_temp:
        fan_output = 0
        GPIO.output(fan_pin, GPIO.LOW)
    return 'Thermostat corrections made'


if __name__ == '__main__':
    GPIO.setup(fan_pin, GPIO.OUT)
    app.run(host='192.168.0.114', port=8080, debug=True)
