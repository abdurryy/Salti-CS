#!/usr/bin/python

import RPi.GPIO as GPIO
import serial
import time

ser = serial.Serial('/dev/ttyS0',115200)
ser.flushInput()

phone_number = '0724438573'
power_key = 6
rec_buff = ''

bytes_recieved = ser.inWaiting()
response = str(ser.read(ser.inWaiting()).decode("utf-8"))
print(bytes_recieved)