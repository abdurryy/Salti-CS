from salti import Salti
from fastapi import FastAPI
import os
import uvicorn
import socket

app = FastAPI()
salti_manager = Salti()
salti_manager.on()

@app.get("/")
def root():
    return {"Hello": "World"}

@app.get("/call/{number}")
def call(number: str):
    if salti_manager.inCall:
        return {"error": "already in call"}
    r = salti_manager.call(number)
    if r == 1:
        return {"status": "success"}
    else:
        return {"status": "failure"}

@app.get("/hangup")
def hangup():
    if not salti_manager.inCall:
        return {"error": "not in call"}
    salti_manager.hangup()
    return {"status": "success"}

@app.get("/status")
def status():
    return {
        "in_call": salti_manager.inCall,
        "call_server_dict": salti_manager.call_dict
    }

# run server and print server host
if __name__ == "__main__":
    print(f"Server running on {socket.gethostbyname(socket.gethostname())}")
    uvicorn.run(app, host="0.0.0.0", port=3001)   

