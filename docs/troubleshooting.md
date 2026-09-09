# Troubleshooting

## Check the HTTP service

```bash
systemctl status desk-lamp-bridge.service
journalctl -u desk-lamp-bridge.service -n 100 --no-pager
```

## Query the lamp through the bridge

```bash
curl -sS http://127.0.0.1:8765/status
```

If this request hangs or takes several seconds, communication with the lamp is usually the slow part.

## Check Wi-Fi

```bash
ping -c 10 <LAMP-IP>
```

High jitter, latency of several hundred milliseconds, or packet loss are suspicious. With multiple access points, also verify that the lamp is associated with the physically appropriate AP.

## `BrokenPipeError`

This can occur when the HTTP client has already timed out while the miIO request is still waiting for the lamp. It is often a secondary symptom of slow device communication.

## HTTP 403 on `/set`

The client is not configured as an allowed write source. This is intentional. `/status` may still remain readable.

## After changes

```bash
python3 -m py_compile bridge.py
sudo systemctl restart desk-lamp-bridge.service
curl -sS http://127.0.0.1:8765/status
```
