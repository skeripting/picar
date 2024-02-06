# *****************************************************************************
# ***************************  Python Source Code  ****************************
# *****************************************************************************
#
#   DESIGNER NAME:  Kushal Timsina & Soban Mahmud
#
#       FILE NAME:  project.py
#
# DESCRIPTION
#    This code interfaces with the Raspberry Pi 4 and controls a
#    Remote Controlled Car for the CPT 210 class as taught by
#    Professor Bruce Link at MCC. Starting up the program creates a
#    web server for the PiCar, where you can control it.
#
#    The mode is changed through the buttons under the "Car Mode" header.
#    The webserver also features a slider for the car speed, which controls
#    the speed, as well as the direction. A Jingle Bells button is also
#    added at the bottom, where the car plays jingle bells.
#
# NOTES
#    The jingle bells is a part of music.py, which is our own module that
#    we extended to this file. It can be used to play any song, as long
#    as you have the piano notes.
#
#    In the future, we would've added a complete CSS theme and a music
#    control system, capable of cycling through multiple tracks using
#    the speaker, but we ran short of time.
#
# *****************************************************************************

import RPi.GPIO as GPIO
import time
import threading
from music import play_jingle_bells
from bottle import route, run, template, request
from datetime import datetime

# ---------------------------------------------------
# Constants to be used in program
# ---------------------------------------------------

TEN_MICROSECONDS = 0.00001
TRIGGER_FACTOR_CONVERSION = 0.000001
TRIGGER_UNIT_CONVERSION = 1000000
SPEED_OF_SOUND = 340
TWO_TIME_TRAVEL = 2
UNIT_CONVERSION_MICROSECONDS = 10000
MAX_DISTANCE = 220  # Max measured distance in cm
TIME_OUT_PERIOD = MAX_DISTANCE * 60

# Define the GPIO pins for the L293D
MOTOR_1A_OUT_PIN = 23  # IN1
MOTOR_1B_OUT_PIN = 24  # IN2
ENABLE_1_PIN = 18

# Define GPIO pins for Motor 2
MOTOR_2A_OUT_PIN = 25  # IN3
MOTOR_2B_OUT_PIN = 17   # IN4
ENABLE_2_PIN = 12

# Define GPIO pins for ultrasonic sensor
TRIG_PIN = 13
ECHO_PIN = 14

# Define pin for IR sensor
IR_SENSOR_1_PIN = 4
IR_SENSOR_2_PIN = 5

SENSED_BLACK = 1
SENSED_WHITE = 0

UV_MINIMUM_DISTANCE = 0
UV_MAXIMUM_DISTANCE = 7

PWM_FREQUENCY = 100

# Globals
global_speed = 100
global_mode = "manual"
global_motor_pwm1 = None
global_motor_pwm2 = None
global_automatic_thread = None
global_avoiding_object = False

# -----------------------------------------------------------------------------
# DESCRIPTION
#   This function sets up the GPIO in the Raspberry Pi 4.
#
# INPUT PARAMETERS:
#   none
#
# OUTPUT PARAMETERS:
#   none
#
# RETURN:
#   none
# -----------------------------------------------------------------------------


def setup_gpio():
    global global_motor_pwm1
    global global_motor_pwm2
    # Use Broadcom SOC Pin numbers
    GPIO.setmode(GPIO.BCM)
    # Set up the GPIO Pins
    GPIO.setup(MOTOR_1A_OUT_PIN, GPIO.OUT)
    GPIO.setup(MOTOR_1B_OUT_PIN, GPIO.OUT)
    GPIO.setup(ENABLE_1_PIN, GPIO.OUT)

    GPIO.setup(MOTOR_2A_OUT_PIN, GPIO.OUT)
    GPIO.setup(MOTOR_2B_OUT_PIN, GPIO.OUT)
    GPIO.setup(ENABLE_2_PIN, GPIO.OUT)

    # Set up the IR sensor
    GPIO.setup(IR_SENSOR_1_PIN, GPIO.IN)
    GPIO.setup(IR_SENSOR_2_PIN, GPIO.IN)

    # Trig/Echo
    GPIO.setup(TRIG_PIN, GPIO.OUT)
    GPIO.setup(ECHO_PIN, GPIO.IN)

    global_motor_pwm1 = GPIO.PWM(ENABLE_1_PIN, PWM_FREQUENCY)
    global_motor_pwm2 = GPIO.PWM(ENABLE_2_PIN, PWM_FREQUENCY)

    global_motor_pwm1.start(0)
    global_motor_pwm2.start(0)

# -----------------------------------------------------------------------------
# DESCRIPTION
#   This function is the pre-emptive setup for the move_forward
#   function. It sets up the motor pins to rotate forward.
#
# INPUT PARAMETERS:
#   none
#
# OUTPUT PARAMETERS:
#   none
#
# RETURN:
#   none
# -----------------------------------------------------------------------------


def setup_move_forward():
    GPIO.output(MOTOR_1A_OUT_PIN, GPIO.HIGH)
    GPIO.output(MOTOR_1B_OUT_PIN, GPIO.LOW)
    GPIO.output(MOTOR_2A_OUT_PIN, GPIO.HIGH)
    GPIO.output(MOTOR_2B_OUT_PIN, GPIO.LOW)

# -----------------------------------------------------------------------------
# DESCRIPTION
#   This function is the pre-emptive setup for the move_backward
#   function. It sets up the motor pins to rotate backward.
#
# INPUT PARAMETERS:
#   none
#
# OUTPUT PARAMETERS:
#   none
#
# RETURN:
#   none
# -----------------------------------------------------------------------------


def setup_move_backward():
    GPIO.output(MOTOR_1A_OUT_PIN, GPIO.LOW)
    GPIO.output(MOTOR_1B_OUT_PIN, GPIO.HIGH)
    GPIO.output(MOTOR_2A_OUT_PIN, GPIO.LOW)
    GPIO.output(MOTOR_2B_OUT_PIN, GPIO.HIGH)

# -----------------------------------------------------------------------------
# DESCRIPTION
#   This function sets the motor speed
#
# INPUT PARAMETERS:
#   pwm - the PWM handle object for the motor
#   speed - the speed of the motor
#
# OUTPUT PARAMETERS:
#   none
#
# RETURN:
#   none
# -----------------------------------------------------------------------------


def set_motor_speed(pwm, speed):
    pwm.ChangeDutyCycle(speed)

# -----------------------------------------------------------------------------
# DESCRIPTION
#   This function makes both motors move forward
#
# INPUT PARAMETERS:
#   pwm - the PWM handle object for the motor
#   speed - the speed of the motor
#
# OUTPUT PARAMETERS:
#   none
#
# RETURN:
#   none
# -----------------------------------------------------------------------------


def move_forward(speed):
    global global_motor_pwm1
    global global_motor_pwm2
    setup_move_forward()
    set_motor_speed(global_motor_pwm1, speed)
    set_motor_speed(global_motor_pwm2, speed)

# -----------------------------------------------------------------------------
# DESCRIPTION
#   This function makes both motors move backward
#
# INPUT PARAMETERS:
#   speed - the speed of the motor
#
# OUTPUT PARAMETERS:
#   none
#
# RETURN:
#   none
# -----------------------------------------------------------------------------


def move_backward(speed):
    global global_motor_pwm1
    global global_motor_pwm2
    setup_move_backward()
    set_motor_speed(global_motor_pwm1, speed)
    set_motor_speed(global_motor_pwm2, speed)

# -----------------------------------------------------------------------------
# DESCRIPTION
#   This function makes the car move left.
#
# INPUT PARAMETERS:
#   speed - the speed of the motor
#
# OUTPUT PARAMETERS:
#   none
#
# RETURN:
#   none
# -----------------------------------------------------------------------------


def move_left(speed):
    global global_motor_pwm1
    global global_motor_pwm2
    setup_move_forward()
    set_motor_speed(global_motor_pwm1, 0)
    set_motor_speed(global_motor_pwm2, speed)

# -----------------------------------------------------------------------------
# DESCRIPTION
#   This function makes the car move right.
#
# INPUT PARAMETERS:
#   none
#
# OUTPUT PARAMETERS:
#   none
#
# RETURN:
#   none
# -----------------------------------------------------------------------------


def move_right(speed):
    global global_motor_pwm1
    global global_motor_pwm2
    setup_move_forward()
    set_motor_speed(global_motor_pwm1, speed)
    set_motor_speed(global_motor_pwm2, 0)

# -----------------------------------------------------------------------------
# DESCRIPTION
#   This function checks if the left infrared sensor is detecting black
#
# INPUT PARAMETERS:
#   none
#
# OUTPUT PARAMETERS:
#   none
#
# RETURN:
#   none
# -----------------------------------------------------------------------------


def ir_1_senses():
    return GPIO.input(IR_SENSOR_1_PIN)

# -----------------------------------------------------------------------------
# DESCRIPTION
#   This function checks if the right infrared sensor is detecting black
#
# INPUT PARAMETERS:
#   none
#
# OUTPUT PARAMETERS:
#   none
#
# RETURN:
#   none
# -----------------------------------------------------------------------------


def ir_2_senses():
    return GPIO.input(IR_SENSOR_2_PIN)

# -----------------------------------------------------------------------------
# DESCRIPTION
#   This function measures the pulse time from the echo pin.
#
# INPUT PARAMETERS:
#   none
#
# OUTPUT PARAMETERS:
#   none
#
# RETURN:
#   none
# -----------------------------------------------------------------------------


def measure_return_echo(pin, level, timeout_period):
    GPIO.output(TRIG_PIN, GPIO.HIGH)
    time.sleep(TEN_MICROSECONDS)
    GPIO.output(TRIG_PIN, GPIO.LOW)
    pingTime = send_trigger_pulse(pin, level, timeout_period)
    return pingTime

# -----------------------------------------------------------------------------
# DESCRIPTION
#   This function sends a trigger pulse.
#
# INPUT PARAMETERS:
#   pin - The trigger pin
#
# OUTPUT PARAMETERS:
#   none
#
# RETURN:
#   none
# -----------------------------------------------------------------------------


def send_trigger_pulse(pin, level, timeout_period):
    t0 = time.time()
    while (GPIO.input(pin) != level):
        if ((time.time() - t0) > timeout_period * TRIGGER_FACTOR_CONVERSION):
            return 0
    t0 = time.time()
    while (GPIO.input(pin) == level):
        if ((time.time() - t0) > timeout_period * TRIGGER_FACTOR_CONVERSION):
            return 0
    pulseTime = (time.time() - t0) * TRIGGER_UNIT_CONVERSION
    return pulseTime

# -----------------------------------------------------------------------------
# DESCRIPTION
#   This function detects the distance using the ultrasonic sensor.
#
# INPUT PARAMETERS:
#   none
#
# OUTPUT PARAMETERS:
#   none
#
# RETURN:
#   none
# -----------------------------------------------------------------------------


def detect_distance():
    ping_time = measure_return_echo(ECHO_PIN,
                                    GPIO.HIGH, TIME_OUT_PERIOD)
    distance = ping_time * SPEED_OF_SOUND / \
        TWO_TIME_TRAVEL / UNIT_CONVERSION_MICROSECONDS
    return distance

# -----------------------------------------------------------------------------
# DESCRIPTION
#   This function is the thread for the detect_distance function.
#
# INPUT PARAMETERS:
#   none
#
# OUTPUT PARAMETERS:
#   none
#
# RETURN:
#   none
# -----------------------------------------------------------------------------


def detect_distance_thread():
    global global_avoiding_object
    global global_speed
    while True:
        dist = detect_distance()
        if (dist > UV_MINIMUM_DISTANCE and dist < UV_MAXIMUM_DISTANCE):
            global_avoiding_object = True
            for i in range(10):
                move_backward(global_speed)
        global_avoiding_object = False
        time.sleep(0.5)

# -----------------------------------------------------------------------------
# DESCRIPTION
#   This function renders the main homepage containing the modes, music, and
#   stop features using bottle.
#
# INPUT PARAMETERS:
#   none
#
# OUTPUT PARAMETERS:
#   none
#
# RETURN:
#   none
# -----------------------------------------------------------------------------


@route('/')
def home():
    return template('''
        <style>
            * {
                font-family: Verdana;
            }
        </style>
        <h1>PiCar Version 1.0</h1>
        <p>Welcome to the new PiCar!</p>
        <p>Below, you can find the controls for the PiCar.</p>
        <h2>Car Mode</h2>
        <button id="manual">Manual</button>
        <button id="automatic">Automatic</button>
        <h2>Car Speed</h2>
        <input id="speedSlider" type="range" min="-100" max="100" value="0" orient="vertical">
        <div>
            <span id="speedValue">Speed: 0</span>
        </div>
        <h2>Music Controls</h2>
        <p>You can control the music with the following buttons</p>
        <button id="jingle-bells">Jingle Bells</button>
        <h2>Stop</h2>
        <p>You can stop the car completely with this button.</p>
        <button id="immediate-stop">Stop</button>
        <script>
            var slider = document.getElementById("speedSlider");
            var output = document.getElementById("speedValue");
            var jingleBellsButton = document.getElementById("jingle-bells")
            var automaticButton = document.getElementById("automatic")
            var manualButton = document.getElementById("manual")
            var stopButton = document.getElementById("immediate-stop")
            output.innerHTML = "Speed: " + slider.value;
            
            jingleBellsButton.onclick = function() {
                var xhr = new XMLHttpRequest();
                xhr.open('POST', '/play_jingle_bells', true);
                xhr.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
                xhr.send()
            }
            
            automaticButton.onclick = function() {
                var xhr = new XMLHttpRequest();
                xhr.open('POST', '/switch_automatic_thread', true);
                xhr.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
                xhr.send()
                output.innerHTML = "Speed: Automatic"
            }
            
            manualButton.onclick = function() {
                var xhr = new XMLHttpRequest();
                xhr.open('POST', '/switch_manual', true);
                xhr.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
                xhr.send()
            }
                    
            stopButton.onclick = function() {
                var xhr = new XMLHttpRequest();
                xhr.open('POST', '/cleanup', true);
                xhr.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
                xhr.send()
            }
            
            slider.oninput = function() {
                output.innerHTML = "Speed: " + this.value;
                var xhr = new XMLHttpRequest();
                xhr.open('POST', '/set_speed', true);
                xhr.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
                xhr.send('speed=' + this.value);
            }
        </script>
    ''')

# -----------------------------------------------------------------------------
# DESCRIPTION
#   This function switches the mode to manual.
#
# INPUT PARAMETERS:
#   none
#
# OUTPUT PARAMETERS:
#   none
#
# RETURN:
#   none
# -----------------------------------------------------------------------------


@route("/switch_manual", method="POST")
def switch_manual():
    global global_automatic_thread
    global global_mode
    global_automatic_thread.stop()
    global_mode = "manual"

# -----------------------------------------------------------------------------
# DESCRIPTION
#   This function switches the mode to automatic, enabling the UV sensors
#   to detect the direction the car should spin
#
# INPUT PARAMETERS:
#   none
#
# OUTPUT PARAMETERS:
#   none
#
# RETURN:
#   none
# -----------------------------------------------------------------------------


def switch_automatic():
    global global_avoiding_object
    global global_speed
    global global_mode

    global_mode = "automatic"

    while (global_mode == "automatic"):
        if (not global_avoiding_object):
            if (ir_2_senses() == SENSED_BLACK and ir_1_senses() == SENSED_WHITE):
                move_right(global_speed)
            elif (ir_1_senses() == SENSED_BLACK and ir_2_senses() == SENSED_WHITE):
                move_left(global_speed)
            else:
                # The code below was part of the ultrasonic sensor, and is
                # commented to disable it.
                """dist = detect_distance()
                if (dist > 0 and dist < 7):
                    global_avoiding_object = True
                    for i in range(10):
                        move_backward(100)
                        time.sleep(0.1)
                global_avoiding_object = False"""
                move_forward(abs(global_speed))

# -----------------------------------------------------------------------------
# DESCRIPTION
#   This function creates the thread for the switch_automatic function.
#
# INPUT PARAMETERS:
#   none
#
# OUTPUT PARAMETERS:
#   none
#
# RETURN:
#   none
# -----------------------------------------------------------------------------


@route("/switch_automatic_thread", method="POST")
def switch_automatic_thread():
    global global_automatic_thread
    global_automatic_thread = threading.Thread(target=switch_automatic)
    global_automatic_thread.start()

# -----------------------------------------------------------------------------
# DESCRIPTION
#   This function is the handler to set the speed of the motors using
#   the slider.
#
# INPUT PARAMETERS:
#   none
#
# OUTPUT PARAMETERS:
#   none
#
# RETURN:
#   none
# -----------------------------------------------------------------------------


@route('/set_speed', method='POST')
def set_speed():
    global global_speed
    try:
        global_speed = int(request.forms.get('speed'))
        if (global_speed < 0):
            move_backward(abs(global_speed))
        else:
            move_forward(global_speed)
    except Exception as e:
        return e
    return ''

# -----------------------------------------------------------------------------
# DESCRIPTION
#   This function creates the handler to set the speed of the motors using
#   the slider.
#
# INPUT PARAMETERS:
#   none
#
# OUTPUT PARAMETERS:
#   none
#
# RETURN:
#   none
# -----------------------------------------------------------------------------


@route('/play_jingle_bells', method='POST')
def do_buzz():
    play_jingle_bells()

# -----------------------------------------------------------------------------
# DESCRIPTION
#   This function routes the webserver to do the cleanup.
#
# INPUT PARAMETERS:
#   none
#
# OUTPUT PARAMETERS:
#   none
#
# RETURN:
#   none
# -----------------------------------------------------------------------------


@route("/cleanup", method='POST')
def do_cleanup():
    cleanup()

# -----------------------------------------------------------------------------
# DESCRIPTION
#   This function cleans up the GPIO.
#
# INPUT PARAMETERS:
#   none
#
# OUTPUT PARAMETERS:
#   none
#
# RETURN:
#   none
# -----------------------------------------------------------------------------


def cleanup():
    global global_motor_pwm1
    global global_motor_pwm2
    global_motor_pwm1.stop()
    global_motor_pwm2.stop()
    GPIO.cleanup()

# -----------------------------------------------------------------------------
# DESCRIPTION
#   This is the main function that sets the GPIO up and runs the server.
#
# INPUT PARAMETERS:
#   none
#
# OUTPUT PARAMETERS:
#   none
#
# RETURN:
#   none
# -----------------------------------------------------------------------------


def main():
    try:
        setup_gpio()
        run(host="0.0.0.0", port=80)

    except KeyboardInterrupt:
        cleanup()


# if file execute standalone then call the main function.
if __name__ == '__main__':
    main()
