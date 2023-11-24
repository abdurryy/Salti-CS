#!/usr/bin/python

import RPi.GPIO as GPIO
import serial
import time

ser = serial.Serial('/dev/ttyUSB2',115200)
ser.flushInput()

while True:
    cmd = input("Enter AT command: ")
    ser.write((f'ATD{cmd};\r\n').encode())
    response = str(ser.read(ser.inWaiting()).decode("utf-8"))
    print(response)