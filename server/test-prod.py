#!/usr/bin/python

import RPi.GPIO as GPIO
import serial
import time

ser = serial.Serial('/dev/ttyS0',115200)
ser.flushInput()

while True:
    cmd = input("Enter AT command: ")
    ser.write((f'{cmd}\r\n').encode())
    time.sleep(3)
    response = str(ser.read(ser.inWaiting()).decode("utf-8"))
    print(response)