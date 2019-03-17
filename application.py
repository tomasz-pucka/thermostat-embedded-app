from flask import *

# import Adafruit_DHT
# import Adafruit_BBIO.PWM as PWM

app = Flask(__name__)

max_duty_cycle = 100
min_duty_cycle = 30
start = False
accuracy = 3
duty_cycle = min_duty_cycle
set_temp = 0
actual_temp = 0
thermostat_state = False


# pwm_pin = 'P9_14'

# sensor = Adafruit_DHT.DHT11
# sensor_pin = 'P8_11'

def getActualTemperature():
    temp = 25
    # hum, temp = Adafruit_DHT.read_retry(sensor, sensor_pin)
    return temp


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/actualTemp')
def thermostatProcess():
    global actual_temp, duty_cycle, start
    if (thermostat_state == True):
        actual_temp = getActualTemperature()
        if start and set_temp <= actual_temp:
            duty_cycle = (1 - (set_temp / actual_temp) ** 8) * 100
            start = False
        if start and set_temp > actual_temp:
            duty_cycle = min_duty_cycle
            start = False
        duty_cycle += (duty_cycle * (1 - (set_temp / actual_temp))) / accuracy  # round; /accuracy
        if (duty_cycle > max_duty_cycle):
            duty_cycle = max_duty_cycle
        if (duty_cycle < min_duty_cycle):
            duty_cycle = min_duty_cycle
        duty_cycle = round(duty_cycle, 1)
        # PWM.set_duty_cycle(pwm_pin, duty_cycle)
    return render_template('actualTemp.html', temp=actual_temp, duty_cycle=duty_cycle)


@app.route('/setTemp', methods=['POST'])
def setTemp():
    global set_temp
    content = request.get_json()
    set_temp = float(content['desiredTemp'])
    return 'Temp posted'


@app.route('/setAccuracy', methods=['POST'])
def setAccuracy():
    global accuracy
    content = request.get_json()
    accuracy = float(content['accuracy'])
    return 'Accuracy posted'


@app.route('/toggleState', methods=['POST'])
def toggleState():
    global thermostat_state, start
    content = request.get_json()
    thermostat_state = content['state']
    if (thermostat_state == True):
        start = True
    return 'State posted'


if __name__ == '__main__':
    # PWM.start(pwm_pin, 0, 25000)
    app.run(host='127.0.0.1', port=8080, debug=True)
