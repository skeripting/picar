# *****************************************************************************
# ***************************  Python Source Code  ****************************
# *****************************************************************************
#
#   DESIGNER NAME:  Kushal Timsina
#
#       FILE NAME:  music.py
#
# DESCRIPTION
#    This code contains an extension for the CPT 210 final project to enable
#    the car to play musical notes, as well as complete songs. This module
#    can be adapted to play any song.
#
# *****************************************************************************

import RPi.GPIO as GPIO
import time

TEMPO_ADJUSTMENT = 0.5
BUZZER_NOTES = {  # Credit to ChatGPT for these notes
    "B0": 31,
    "C1": 33,
    "CS1": 35,
    "D1": 37,
    "DS1": 39,
    "E1": 41,
    "F1": 44,
    "FS1": 46,
    "G1": 49,
    "GS1": 52,
    "A1": 55,
    "AS1": 58,
    "B1": 62,
    "C2": 65,
    "CS2": 69,
    "D2": 73,
    "DS2": 78,
    "E2": 82,
    "F2": 87,
    "FS2": 93,
    "G2": 98,
    "GS2": 104,
    "A2": 110,
    "AS2": 117,
    "B2": 123,
    "C3": 131,
    "CS3": 139,
    "D3": 147,
    "DS3": 156,
    "E3": 165,
    "F3": 175,
    "FS3": 185,
    "G3": 196,
    "GS3": 208,
    "A3": 220,
    "AS3": 233,
    "B3": 247,
    "C4": 262,
    "CS4": 277,
    "D4": 294,
    "DS4": 311,
    "E4": 330,
    "F4": 349,
    "FS4": 370,
    "G4": 392,
    "GS4": 415,
    "A4": 440,
    "AS4": 466,
    "B4": 494,
    "C5": 523,
    "CS5": 554,
    "D5": 587,
    "DS5": 622,
    "E5": 659,
    "F5": 698,
    "FS5": 740,
    "G5": 784,
    "GS5": 831,
    "A5": 880,
    "AS5": 932,
    "B5": 988,
    "C6": 1047,
    "CS6": 1109,
    "D6": 1175,
    "DS6": 1245,
    "E6": 1319,
    "F6": 1397,
    "FS6": 1480,
    "G6": 1568,
    "GS6": 1661,
    "A6": 1760,
    "AS6": 1865,
    "B6": 1976,
    "C7": 2093,
    "CS7": 2217,
    "D7": 2349,
    "DS7": 2489,
    "E7": 2637,
    "F7": 2794,
    "FS7": 2960,
    "G7": 3136,
    "GS7": 3322,
    "A7": 3520,
    "AS7": 3729,
    "B7": 3951,
    "C8": 4186,
    "CS8": 4435,
    "D8": 4699,
    "DS8": 4978
}

# Define the notes' frequencies (in Hz)
BUZZER_NOTES_ALTERNATIVE = {
    'B4': 494,
    'E5': 659,
    'F#5': 740,
    'G5': 784,
    'A5': 880,
    'B5': 988,
    "D5": 587,
    'C#5': 554,
    'E4': 330,
    'A4': 440
}

JINGLE_BELLS = [
    ('E5', 1), ('E5', 1), ('E5', 2),
    ('E5', 1), ('E5', 1), ('E5', 2),
    ('E5', 1), ('G5', 1), ('C#5', 1), ('D5', 1), ('E4', 4),
    ('F#5', 1), ('F#5', 1), ('F#5', 1), ('F#5', 1), ('F#5',
                                                     1), ('E5', 1), ('E5', 1), ('E5', 1), ('E5', 1),
    ('E5', 1), ('D5', 1), ('D5', 1), ('E5', 1), ('D5', 2), ('G5', 2)
]


def play_tone(pwm, frequency, duration):
    pwm.ChangeFrequency(frequency)
    pwm.start(50)
    time.sleep(duration)
    pwm.stop()


def play_jingle_bells():
    BUZZER_PIN = 27
    GPIO.setup(BUZZER_PIN, GPIO.OUT)
    buzzer_pwm = GPIO.PWM(BUZZER_PIN, 100)
    buzzer_pwm.start(0)

    for note, length in JINGLE_BELLS:
        freq = BUZZER_NOTES_ALTERNATIVE[note]
        play_tone(buzzer_pwm, freq, length * TEMPO_ADJUSTMENT)
        time.sleep(0.05)
