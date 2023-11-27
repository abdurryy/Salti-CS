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
        self.serial = serial.Serial('/dev/ttyUSB2',115200)
        self.serial.flushInput()
        self.name = "[Salti CS]"
        self.inCall = False
        self.call_dict = {
            "status": -1, # 0 = not called, 1 = called, 2 = call accepted, 3 = call ended
            "number": ""
        }
    
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

    def init_call(self, target):
        try:
            while True:
                time.sleep(1)
                bytes_recieved = self.serial.inWaiting()
                if str(bytes_recieved) == "0":
                    continue
                response = self.serial.read(self.serial.inWaiting()).decode("utf-8")
                print(response)
                open("debug.txt", "w").write(response)
                if "ERROR" in response:
                    self.call_dict["status"] = 3
                    self.inCall = False
                    self.log(f"Call to {target} failed due to error.", "failure")
                    break
                elif "OK" in response:
                    self.call_dict["status"] = 1
                    self.log(f"Calling {target}, waiting for response...", "success")
                    return 1
                else:
                    self.call_dict["status"] = 3
                    self.inCall = False
                    self.log(f"Call to {target} failed due to no OK.", "failure")
            return 0
        except Exception as e:
            self.log(f"err: {str(e)}", "error")
            return 0
    
    def response_call(self, target):
        try:
            while True:
                time.sleep(1)
                bytes_recieved = self.serial.inWaiting()
                

                time.sleep(2)
                response = str(self.serial.read(self.serial.inWaiting()).decode("utf-8"))
                print(response)
                open("debug.txt", "w").write(response)

                if "BEGIN" in response:
                    for i in range(16):
                        time.sleep(1)
                        bytes_recieved = self.serial.inWaiting()
                        if str(bytes_recieved) == "0":
                            continue
                        time.sleep(2)
                        response = str(self.serial.read(self.serial.inWaiting().decode("utf-8")))
                        if "NO CARRIER" in response:
                            self.call_dict["status"] = 3
                            self.inCall = False
                            self.log(f"Call to {target} failed due to no carrier.", "failure")
                            return 0
                        elif "END" in response:
                            self.call_dict["status"] = 3
                            self.inCall = False
                            self.log(f"Call to {target} failed due to end.", "failure")
                            return 0
                    self.call_dict["status"] = 2
                    self.log(f"Call to {target} accepted.", "success")
                    return 1
                else:
                    if "" in response: # THERE IS NOTHING IN THE RESPONSE
                        continue
                    self.call_dict["status"] = 3
                    self.inCall = False
                    self.log(f"Call to {target} failed due to no begin.", "failure")
                    return 0
        except Exception as e:
            if "int" in str(e):
                return 0
            self.log(f"err: {str(e)}", "error")
            return 0
    
    
    def call(self, target:str):
        if self.inCall:
            self.log("Already in call", "error")
            return 0
        self.serial.flushInput()
        
        self.inCall = True
        self.log(f"Calling {target}...")
        self.serial.write((f'ATD{target};\r\n').encode())
                    
        t = time.time()
        self.call_dict = {
            "status": 0, # 0 = not called, 1 = called, 2 = call accepted, 3 = call ended
            "number": target
        }

        if self.init_call(target) == 1:
            if self.response_call(target) == 1:
                return 1
        return 0

    
    def background(self):
        while True:
            time.sleep(1)
            if self.call_dict["status"] == 2:
                self.serial.write((f'AT+CLCC\r\n').encode())
                time.sleep(2)
                response = str(self.serial.read(self.serial.inWaiting()).decode("utf-8"))
                if not "+CLCC:" in response:
                    self.log("Call not accepted")
                    self.inCall = False
                    self.call_dict["status"] = 3
                    self.call_dict["number"] = ""
                

    def hangup(self):
        self.serial.write((f'AT+CLCC\r\n').encode())
        time.sleep(2)
        response = str(self.serial.read(self.serial.inWaiting()).decode("utf-8"))
        if "+CLCC:" in response:
            self.serial.write((f'AT+CHUP\r\n').encode())
            self.log('Call disconnected')
            self.inCall = False
            return 1
        else:
            self.log('Tried to hangup non-existing call!', "error")
            self.inCall = False
            self.call_dict["status"] = -1
            self.call_dict["number"] = ""
            return 0
    
    def off(self):
        self.log('Shutting down')
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(6, GPIO.OUT)
        GPIO.output(6, GPIO.HIGH)
        time.sleep(2)
        GPIO.output(6, GPIO.LOW)
        self.serial.flushInput()
        time.sleep(5)
        self.log('Finished shutting down')

    def on(self):
        self.log('Booting up')
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(6,GPIO.OUT)
        GPIO.output(6,GPIO.HIGH)
        GPIO.output(6,GPIO.LOW)
        self.serial.flushInput()
        time.sleep(5)
        self.log('Finished booting up')

