# Loxone Xiaomi Desk Lamp Bridge

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
![Python 3](https://img.shields.io/badge/Python-3.x-blue.svg)
![Platform](https://img.shields.io/badge/Linux-DietPi%20%2F%20Debian-informational.svg)
![Protocol](https://img.shields.io/badge/Protocol-local%20miIO-success.svg)

<!-- project-meta -->
> **Status:** Stable · **Current release:** `v1.0.0` · **License:** MIT · **Documentation:** English · **Issues/PRs:** English preferred

[Changelog](CHANGELOG.md) · [Contributing](CONTRIBUTING.md) · [Security](SECURITY.md) · [Loxone integration](docs/loxone.md) · [Troubleshooting](docs/troubleshooting.md) · [Project collection](https://github.com/therealb4n4na/loxone-smart-home-projects)
<!-- /project-meta -->

A small local HTTP bridge for controlling a Xiaomi/Yeelight-compatible desk lamp from Loxone. The bridge decodes a Loxone Lumitech numeric value into brightness and color temperature and sends the corresponding commands directly to the lamp through miIO.

## What this project gives you

- power on/off
- brightness 0–100 %
- color temperature 2500–4800 K
- direct device status feedback
- non-blocking cached `/health` endpoint with transient miIO failure tolerance
- serialized miIO access so parallel commands do not overlap
- write access restricted to the configured Loxone/controller IP

## Architecture

```text
Loxone
  │ HTTP GET /set?v=...
  ▼
bridge.py :8765
  │ miIO
  ▼
Desk lamp on the local Wi-Fi network
```

## Lumitech encoding

The bridge expects:

```text
0 -> OFF
200000000 + (brightness * 10000) + Kelvin -> ON
```

Example for 50 % brightness at 3000 K:

```text
200503000
```

Color temperature is clamped to the supported range of 2500–4800 K.

## Tested hardware

This bridge is developed and operated with a **Xiaomi Desk Lamp Pro** using local miIO control.

The tested lamp supports power control, brightness and a color-temperature range of 2500–4800 K. Other Xiaomi/Yeelight-compatible lamps may use different commands or ranges and should not be assumed compatible without verification.

## Requirements

- Linux / DietPi / Debian
- Python 3
- `python-miio`
- local IP address of the lamp
- miIO token for your own lamp

Example virtual environment:

```bash
python3 -m venv venv
./venv/bin/pip install python-miio
```

## Configuration

Production values are loaded through environment variables. Template:

[`lamp.env.example`](lamp.env.example)

Create a local file such as `lamp.env`; it is excluded by `.gitignore`.

Relevant values:

```text
LAMP_IP                  local IP address of the lamp
LAMP_TOKEN               local miIO token
PORT                     HTTP port of the bridge (default 8765)
WRITE_CLIENT_IP          only remote IP allowed to write, typically Loxone
HEALTH_INTERVAL          cached reachability probe interval (default 60 s)
HEALTH_PROBE_TIMEOUT     probe timeout (default 1.5 s)
HEALTH_FAILURE_THRESHOLD consecutive failed probes before health degrades (default 3)
```

A miIO token is a secret and must never be committed to GitHub.

## HTTP endpoints

### Set lamp state

```text
GET http://<HOST>:8765/set?v=<LUMITECH_VALUE>
```

This is a write endpoint and accepts requests only from the configured controller IP and localhost.

### Read status

```text
GET http://<HOST>:8765/status
```

The status is read directly from the lamp. A running HTTP process therefore does not automatically mean that the lamp itself is reachable over Wi-Fi.

### Health

```text
GET http://<HOST>:8765/health
```

`/health` returns a cached miIO reachability result and never waits on a live lamp request. A background probe runs every 60 seconds by default; one or two consecutive failures are treated as transient, while the third consecutive failure degrades health. This keeps monitoring responsive without hiding sustained Wi-Fi/miIO outages.

## Wi-Fi note

miIO devices can react poorly to unstable Wi-Fi. If `/status` takes several seconds or times out intermittently, check AP association, signal quality, packet loss, and latency first. Reinstalling the bridge will not fix a weak wireless link.

## Loxone

The Loxone side only needs to generate the Lumitech value and send it to `/set?v=...`.

Details: [`docs/loxone.md`](docs/loxone.md).

## Troubleshooting

See [`docs/troubleshooting.md`](docs/troubleshooting.md).

## Security

- keep the token only in a local environment file
- restrict `/set` to the Loxone/controller IP
- keep `/status` readable for diagnostics if desired
- do not version token-extraction data or other local helper data

## License

MIT License – see [`LICENSE`](LICENSE).
