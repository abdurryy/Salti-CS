import RPi.GPIO as GPIO
import serial
import time

ser = serial.Serial('/dev/ttyUSB2',115200)
ser.flushInput()

ser.write((f'ATD0724438573;\r\n').encode())
time.sleep(15)
response = str(ser.read(ser.inWaiting()).decode("utf-8"))
print(response)
time.sleep(5)
ser.write((f'AT+CLCC\r\n').encode())
time.sleep(2)
response = str(ser.read(ser.inWaiting()).decode("utf-8"))
print(response)
if "+CLCC:" in response:
    print("Call accepted")
    time.sleep(5)
    ser.write((f'AT+CHUP\r\n').encode())
else:
    print("Call not accepted")