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

    def init_call(self):
        try:
            while True:
                time.sleep(1)
                bytes_recieved = self.serial.inWaiting()
                if str(bytes_recieved) == "0":
                    continue
                print(str(self.serial.inWaiting())+" bytes recieved")
                response = self.serial.read(self.serial.inWaiting()).decode("utf-8")
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
    
    def response_call(self):
        try:
            while True:
                time.sleep(1)
                bytes_recieved = self.serial.inWaiting()
                if str(bytes_recieved) == "0":
                    continue

                time.sleep(2)
                response = str(self.serial.read(self.serial.inWaiting()).decode("utf-8"))
                

                if "BEGIN" in response:
                    self.call_dict["status"] = 2
                    self.log(f"Call to {target} successful", "success")
                    for i in range(15):
                        time.sleep(1)
                        bytes_recieved = self.serial.inWaiting()
                        if str(bytes_recieved) == "0":
                            self.log("[RESP 22] no extra...")
                            continue
                        time.sleep(2)
                        print(f"{bytes_recieved} bytes recieved")
                        response = self.serial.read(self.serial.inWaiting())
                        print(f"b: {response}")
                        response = str(response.decode("utf-8"))

                        print(f"extra: {response}")
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
                    return 1
                else:
                    self.call_dict["status"] = 3
                    self.inCall = False
                    self.log(f"Call to {target} failed due to no begin.", "failure")
                    return 0
        except Exception as e:
            self.log(f"err: {str(e)}", "error")
            return 0
    
    
    def call(self, target:str, timeout:int=20):
        if self.inCall:
            self.log("Already in call", "error")
            return 0
        self.serial.flushInput()
        
        self.inCall = True
        self.log(f"Calling {target}...")
        response = ''
        self.serial.write((f'ATD{target};\r\n').encode())
                    
        t = time.time()
        self.call_dict = {
            "status": 0, # 0 = not called, 1 = called, 2 = call accepted, 3 = call ended
            "number": target
        }

        if self.init_call() == 1:
            if self.response_call() == 1:
                return 1
        return 0

            

        """rint(self.serial.inWaiting())
        print(response)
        break
        if self.serial.inWaiting():
            while True:
                time.sleep(2)
                if time.time() - t > timeout:
                    self.log(f"Call to {target} timed out", "failure")
                    self.inCall = False
                    return 0
                
                
                response = self.serial.read(self.serial.inWaiting()).decode()
                print(self.serial.inWaiting())
                print(response)
                if not "VOICE" in response:
                    continue
                if "END" in response:
                    self.inCall = False
                    self.log(f"Call to {target} failed", "failure")
                    return 0
                else:
                    self.inCall = True
                    self.log(f"Call to {target} successful", "success")
                    return 1"""

    
    def background(self):
        while True:
            try:
                time.sleep(1)
                response = self.serial.read(self.serial.inWaiting()).decode("utf-8")
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

s = Salti()
s.on()
#threading.Thread(target=s.background).start()
while True:
    time.sleep(1)
    if not s.inCall:
        target = input("Enter number: ")
        if target == "exit":
            s.off()
            break
        if s.call(target) == 1:
            s.log("Call successful", "success")
        else:
            s.log("Call failed", "failure")
        s.hangup()
        s.off()
        break
