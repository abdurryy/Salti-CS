#!/usr/bin/python

import RPi.GPIO as GPIO
import serial
import time

ser = serial.Serial('/dev/ttyUSB2',115200)
ser.flushInput()

phone_number = '0724438573'
power_key = 6
rec_buff = ''

response = str(ser.read(ser.inWaiting()).decode("utf-8"))
print(response)