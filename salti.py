# This project is fully coded and created by Abdurrahman Giumale.
# Read more on github: https://github.com/abdurryy/Salti-CS
# This is only for educational purposes.
from datetime import datetime
import RPi.GPIO as GPIO
import colorama
import time
import serial
import threading

class Salti:
    def __init__(self):
        colorama.init()
        self.serial = serial.Serial('/dev/ttyS0',115200)
        self.serial.flushInput()
        self.name = "[Salti CS]"
        self.inCall = False
    
    def time(self):
        return colorama.Fore.WHITE +"["+ datetime.now().strftime("%H:%M:%S")+"] "
    
    def log(self, msg:str, type:str="default"):
        color = colorama.Fore.BLUE
        if type == "error":
            color = colorama.Fore.RED
        elif type == "success":
            color = colorama.Fore.GREEN
        elif type == "failure":
            color = colorama.Fore.LIGHTRED_EX
        print(f"{self.time()}{colorama.Fore.LIGHTMAGENTA_EX} {self.name} {color}{msg}{colorama.Fore.BLUE}")

    
    
    def call(self, target:str):
        try:
            self.log(f"Calling {target}...")
            response = ''
            self.serial.write((f"ATD{target};"+'\r\n').encode())
            while True:
                time.sleep(1)
                if self.serial.inWaiting():
                    time.sleep(5)
                    response = self.serial.read(self.serial.inWaiting()).decode()
                    if not "VOICE" in response:
                        continue
                    print(response)
                    if "END" in response:
                        self.log(f"Call to {target} failed", "failure")
                        return 0
                    else:
                        self.inCall = True
                        self.log(f"Call to {target} successful", "success")
                        return 1
        except Exception as e:
            self.log(f"err: {str(e)}", "error")
            return 0
    
    def background(self):
        while True:
            try:
                time.sleep(1)
                response = self.serial.read(self.serial.inWaiting()).decode()
                if "END" in response:
                    self.log("Reciever ended call", "failure")  
                    self.hangup()  
            except Exception as e:
                self.log(f"err: {str(e)}", "error")

    def hangup(self):
        self.serial.write('AT+CHUP\r\n'.encode())
        self.log('Call disconnected')
        self.inCall = False
    
    def off(self):
        self.log('Shutting down')
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(6,GPIO.OUT)
        GPIO.output(6,GPIO.HIGH)
        GPIO.output(6,GPIO.LOW)
        self.serial.flushInput()
        self.log('Finished shutting down')

    def on(self):
        self.log('Booting up')
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(6,GPIO.OUT)
        GPIO.output(6,GPIO.HIGH)
        GPIO.output(6,GPIO.LOW)
        self.serial.flushInput()
        self.log('Finished booting up')

s = Salti()
s.on()
threading.Thread(target=s.background).start()
while True:
    if s.inCall:
        continue
    target = input("Enter number: ")
    if target == "exit":
        s.off()
        break
    s.call(target)