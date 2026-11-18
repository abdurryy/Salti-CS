#!/usr/bin/env python3
"""Interactive AT prompt against the modem.

Fastest way to tell a wiring or SIM problem from a software one. Useful first
commands: AT (modem alive), AT+CSQ (signal quality), AT+CREG? (registration).

Usage: python tools/at-console.py
"""

import time

import serial

PORT = "/dev/ttyUSB2"
BAUD = 115200


def main():
    ser = serial.Serial(PORT, BAUD)
    ser.flushInput()
    print(f"Connected to {PORT} at {BAUD} baud. Ctrl-C to quit.")

    while True:
        try:
            cmd = input("Enter AT command: ")
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not cmd.strip():
            continue

        ser.write(f"{cmd}\r\n".encode())
        time.sleep(3)
        print(ser.read(ser.inWaiting()).decode("utf-8", errors="replace"))

    ser.close()


if __name__ == "__main__":
    main()
