# This project is fully coded and created by Abdurrahman Giumale.
# Read more on github: https://github.com/abdurryy/Salti-CS
# This is only for educational purposes.
from datetime import datetime
import RPi.GPIO as GPIO
import colorama
import time
import serial

class Salti:
    def __init__(self):
        colorama.init()
        self.serial = serial.Serial('/dev/ttyS0',115200)
        self.serial.flushInput()
        self.name = "[Salti CS]"
    
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
            rec_buff = ''
            self.serial.write((f"ATD{target};"+'\r\n').encode())
            time.sleep(20)
            if self.serial.inWaiting():
                time.sleep(0.01 )
                rec_buff = self.serial.read(self.serial.inWaiting())
            response = rec_buff.decode()
            print("Call response: " + response)
            
            if "NO CARRIER" in response:
                self.log(f"Call to {target} was not picked up.", "failure")
                return 0
            elif "OK" not in response:
                self.log(f"Failure: {response}", "failure")
                return 0
            else:
                self.log(f"Successfully called {target}!", "success")
                return 1
        except Exception as e:
            self.log(f"err: {str(e)}", "error")
            return 0

    def hangup(self):
        self.serial.write('AT+CHUP\r\n'.encode())
        self.log('Call disconnected')
    
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
while True:
    target = input("Enter number: ")
    if target == "exit":
        s.off()
        break
    s.call(target)
    s.hangup()