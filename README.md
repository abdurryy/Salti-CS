# Salti-CS

*A bridge between you and the unreachable.*

Salti-CS is a WebRTC to GSM voice gateway. It takes an inbound call over the internet and bridges it onto a circuit-switched GSM call, so callers can reach people in regions where voice coverage exists but mobile data is unusable. The control plane is implemented: AT command transport over serial, a call state machine and a REST API driving a SIM7600 modem on a Raspberry Pi. Closing the media path is the subject of a bachelor thesis in spring 2027.

## Status

This is a working prototype of the signalling half of the gateway, not a finished product.

Implemented:

- Serial transport to a SIM7600 modem over USB (`/dev/ttyUSB2`, 115200 baud)
- Modem power sequencing through the Raspberry Pi GPIO power key (BCM pin 6)
- Call setup with `ATD`, answer detection by polling `AT+CLCC`, teardown with `AT+CHUP`
- A call state machine with four states, polled by a background thread so remote hangups are detected
- A REST API over FastAPI exposing call, hangup and status
- A browser client that places and ends calls and shows live call state

Not implemented:

- Audio. No media is carried in either direction. The modem's PCM audio interface is not wired to the gateway, and there is no WebRTC peer connection in the client, so the browser side is signalling only.
- Inbound calls from the GSM side (`RING` / `ATA` handling)
- Authentication on the API, which currently accepts any caller on the local network
- Concurrent calls. The gateway handles one call at a time by design of the current state machine.

The parts left open are the parts the thesis work will deal with: the PCM audio path off the modem, an RTP bridge against the browser's WebRTC stream, echo and clock drift between the two clock domains, and call quality measurement. The signalling layer here is meant to be the starting point for that, not the end of it.

## Architecture

```
Browser (HTML + JS)
      |  HTTP/REST, polled once per second
      v
FastAPI server  (server/server.py)   <- control plane
      |
      v
Salti class      (server/salti.py)   <- AT command transport + call state machine
      |  pyserial over /dev/ttyUSB2
      v
SIM7600 4G HAT   (Raspberry Pi)      <- circuit-switched GSM call
      |
      v
GSM network -> callee's phone
```

The planned media path, which does not exist yet, runs from the browser over WebRTC to a bridge process on the Pi, and from there over the modem's PCM lines into the same GSM call.

### Call states

`salti.py` tracks the call in `call_dict["status"]`:

| Status | Meaning |
| ------ | ------- |
| `-1`   | No call has been attempted since boot |
| `0`    | Dial requested, not yet acknowledged by the modem |
| `1`    | Modem accepted the dial, ringing at the far end |
| `2`    | Callee answered, call is up |
| `3`    | Call ended, declined or failed |

A background thread polls `AT+CLCC` while in state `2`. When the call disappears from the modem's call list, the far end hung up and the state moves to `3`.

## Hardware

- Raspberry Pi (tested on a Pi 4)
- Waveshare SIM7600-series 4G HAT, developed against the SIM7600E-H
- A SIM card with a voice plan

The HAT presents several USB serial devices. `/dev/ttyUSB2` is the AT command port on this board; the number can differ on other firmware revisions. Check with `ls /dev/ttyUSB*` and verify with the AT console described below.

## Requirements

- Python 3.7 or later
- Node.js 16 or later
- Raspberry Pi OS, since the server imports `RPi.GPIO` and will not run on a desktop machine

## Installation

```bash
git clone https://github.com/abdurryy/Salti-CS.git
cd Salti-CS
```

Server, on the Raspberry Pi:

```bash
cd server
python -m pip install -r requirements.txt
python server.py
```

The server listens on `0.0.0.0:3001` and prints the host address it resolved. It powers the modem on at startup, which takes a few seconds.

Client, on the Pi or any machine on the same network:

```bash
cd client
npm install
node client.js
```

The client serves the page on port 3000 and talks to the API on port 3001 of whatever host served the page, which is correct when both run on the same Pi. To run them apart, set `server_api_url` at the top of `client/public/js/call.js` to the Pi's address, and add the client's origin to `origins` in `server/server.py`, since the CORS policy allows `http://localhost:3000` only.

## API

| Method | Path             | Response |
| ------ | ---------------- | -------- |
| GET    | `/`              | `{"Hello": "World"}`, a liveness check |
| GET    | `/call/{number}` | `{"status": "success"}` when the callee answered, `{"status": "failure"}` otherwise, `{"error": "already in call"}` if a call is up |
| GET    | `/hangup`        | `{"status": "success"}`, or `{"error": "not in call"}` |
| GET    | `/status`        | `{"in_call": bool, "call_server_dict": {"status": int, "number": str}}` |

`/call/{number}` is synchronous and blocks until the call is answered or fails, which can take up to half a minute. The client works around this by polling `/status` once per second rather than waiting on the response.

Numbers are passed to the modem as written, so give them in a format the network accepts, either national (`07XXXXXXXX`) or international (`+46XXXXXXXXX`).

## Repository layout

```
server/
  salti.py          Salti class: serial transport, call state machine, GPIO power control
  server.py         FastAPI app and background status thread
  requirements.txt
  tools/
    at-console.py   Interactive AT prompt against the modem, for bring-up and debugging
    call-test.py    Minimal dial, detect answer and hang up script, without the API
client/
  client.js         Express static file server
  public/
    index.html      Dialer UI
    js/call.js      Calls the REST API and renders call state
    styles/main.css
```

## Debugging

`tools/at-console.py` opens a prompt and sends whatever you type to the modem, which is the fastest way to tell a wiring problem from a software one:

```
$ python tools/at-console.py
Enter AT command: AT
OK
Enter AT command: AT+CSQ
+CSQ: 21,99
Enter AT command: AT+CREG?
+CREG: 0,1
```

`AT` with no answer at all means the wrong serial device or an unpowered modem. `AT+CSQ` reports signal quality and `AT+CREG?` network registration, both of which need to look sane before a call will go through.

`salti.py` writes the last raw modem response to `server/debug.txt` on every read, which is untracked and safe to delete.

## Known issues

Documented rather than hidden, and first on the list for the rewrite:

- Answer detection in `response_call()` is unreliable. It is the `AT+CLCC` poll in `background()` that keeps the state correct in practice, not the detection path itself.
- `init_call()` treats any response without `OK` or `ERROR` as a failure, so unsolicited modem output during dialling can abort a call that would otherwise have connected.
- The AT parser matches on substrings of whatever happens to be in the serial buffer instead of reading complete response lines, which is the root cause of both points above.
- The API has no authentication, and the GPIO power sequence runs at import time, so starting the server toggles the modem whether or not a call is ever placed.

## Background

Built in 2023 as a personal project, before the courses that cover any of it. It is picked up again as a bachelor thesis in spring 2027, where the goal is the media path and a proper evaluation: audio over the PCM interface, an RTP bridge to the browser, and measurements of latency and call quality against a plain GSM call as the baseline. The code in this repository will be rewritten rather than extended where it needs to be, and the known issues above are part of the reason.

## Credits

Written by Abdurrahman Giumale.

## License

MIT, see [LICENSE](LICENSE).
