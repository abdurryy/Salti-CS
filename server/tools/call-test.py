#!/usr/bin/env python3
"""Dial a number, detect whether it was answered, then hang up.

Bypasses the API and the Salti class, so a failure here points at the modem,
the serial port or the SIM rather than at the gateway code.

Usage: python tools/call-test.py +46701234567
"""

import sys
import time

import serial

PORT = "/dev/ttyUSB2"
BAUD = 115200
RING_TIMEOUT = 15  # seconds to wait for the callee to answer


def main():
    if len(sys.argv) != 2:
        print(f"usage: {sys.argv[0]} <number>")
        return 1

    number = sys.argv[1]
    ser = serial.Serial(PORT, BAUD)
    ser.flushInput()

    print(f"Dialling {number}")
    ser.write(f"ATD{number};\r\n".encode())
    time.sleep(RING_TIMEOUT)
    print(ser.read(ser.inWaiting()).decode("utf-8", errors="replace"))

    ser.write(b"AT+CLCC\r\n")
    time.sleep(2)
    response = ser.read(ser.inWaiting()).decode("utf-8", errors="replace")
    print(response)

    if "+CLCC:" in response:
        print("Call accepted, hanging up in 5 seconds")
        time.sleep(5)
        ser.write(b"AT+CHUP\r\n")
    else:
        print("Call not accepted")

    ser.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
