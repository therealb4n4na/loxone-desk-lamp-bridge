#!/usr/bin/env python3
"""
Xiaomi Desk Lamp Pro -> Loxone Bridge
=====================================

Zweck
-----
Dauerhaft laufende HTTP-Bridge auf TCP 8765. Loxone uebergibt einen Lumitech-
Zahlenwert; die Bridge zerlegt ihn in Helligkeit + Farbtemperatur und sendet die
entsprechenden Xiaomi/miIO-Kommandos direkt an die Lampe.

Datenfluss
----------
Loxone -> GET /set?v=<Lumitech-Wert> -> decode_lumitech() -> set_lamp() ->
miIO an LAMP_IP (über die lokale Environment-Datei konfigurierbar)

Wichtige Endpunkte
------------------
/set?v=...  -> Lampe schalten / Helligkeit / Kelvin setzen
/status     -> power, bright und ct DIREKT von der Lampe lesen

Lumitech-Codierung
------------------
0                 -> AUS
200000000 +
(Helligkeit*10000) + Kelvin -> EIN mit 0..100 % und 2500..4800 K
Kelvin ausserhalb des Bereichs wird bewusst auf MIN_CT/MAX_CT begrenzt.

Code-Leseplan / Fehlersuche
---------------------------
decode_lumitech() -> Loxone-Zahl pruefen und in brightness/kelvin zerlegen
set_lamp()        -> miIO-Befehle seriell unter lock an die Lampe schicken
Handler.do_GET()  -> /set und /status behandeln
send_json()       -> einheitliche JSON-HTTP-Antwort erzeugen

Wichtig bei Fehlern
-------------------
- systemd "active" bedeutet nur: der HTTP-Server auf 8765 laeuft. Es beweist
  NICHT, dass die Lampe per miIO erreichbar ist.
- /status fuehrt einen echten get_prop-Aufruf zur Lampe aus. Wenn WLAN/miIO
  langsam oder gestoert ist, kann dieser HTTP-Aufruf mehrere Sekunden blockieren.
- Auch /set wartet synchron auf die Lampe. Ein Netzwerkproblem kann daher fuer
  Loxone wie ein Bridge-Timeout aussehen, obwohl der Python-Prozess weiterlaeuft.
- Alle Lampenzugriffe liegen unter einem gemeinsamen lock. Dadurch werden
  gleichzeitige Loxone-Befehle bewusst serialisiert und koennen sich nicht
  gegenseitig ueberschreiben.
- /set ist schreibend und akzeptiert nur die konfigurierte Steuer-IP (typisch
  Loxone) sowie localhost. /status bleibt für Diagnosezwecke aus dem erlaubten
  LAN lesbar.
- LAMP_IP, LAMP_TOKEN und optional PORT kommen aus lamp.env/systemd-Environment;
  das Token steht absichtlich nicht im Script.
- BrokenPipeError im Journal kann entstehen, wenn der HTTP-Client vorher in ein
  Timeout laeuft und die Verbindung schliesst, waehrend die Lampe spaeter antwortet.
"""

import os
import json
import threading
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from miio import Device

IP = os.environ.get("LAMP_IP", "192.168.1.60")
TOKEN = os.environ["LAMP_TOKEN"]
PORT = int(os.environ.get("PORT", "8765"))

# Nur die konfigurierte Steuer-IP (typisch Loxone) und localhost dürfen
# Schaltbefehle senden. Die lokale Installation setzt WRITE_CLIENT_IP in lamp.env.
WRITE_CLIENT_IP = os.environ.get("WRITE_CLIENT_IP", "192.168.1.50")

MIN_CT = 2500
MAX_CT = 4800

lamp = Device(IP, token=TOKEN)
lock = threading.Lock()


def decode_lumitech(value):
    value = int(round(float(value)))

    # Loxone AUS
    if value <= 0:
        return 0, None

    if value < 200000000:
        raise ValueError(f"Ungültiger Lumitech-Wert: {value}")

    raw = value - 200000000

    brightness = raw // 10000
    kelvin = raw % 10000

    if not 0 <= brightness <= 100:
        raise ValueError(f"Ungültige Helligkeit: {brightness}")

    kelvin = max(MIN_CT, min(MAX_CT, kelvin))

    return int(brightness), int(kelvin)


def set_lamp(brightness, kelvin):
    with lock:
        if brightness <= 0:
            return {
                "power": lamp.send("set_power", ["off"])
            }

        result = {}

        result["power"] = lamp.send("set_power", ["on"])
        result["brightness"] = lamp.send("set_bright", [brightness])
        result["kelvin"] = lamp.send("set_ct_abx", [kelvin])

        return result


class Handler(BaseHTTPRequestHandler):

    def send_json(self, status, data):
        body = json.dumps(data).encode("utf-8")

        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def write_allowed(self):
        return self.client_address[0] in {
            WRITE_CLIENT_IP,
            "127.0.0.1",
            "::1",
        }

    def do_GET(self):
        try:
            parsed = urlparse(self.path)
            query = parse_qs(parsed.query)

            if parsed.path == "/set":
                if not self.write_allowed():
                    self.send_json(403, {
                        "ok": False,
                        "error": "write_access_denied",
                        "client_ip": self.client_address[0]
                    })
                    return

                if "v" not in query:
                    raise ValueError("Parameter 'v' fehlt")

                value = query["v"][0]
                brightness, kelvin = decode_lumitech(value)
                result = set_lamp(brightness, kelvin)

                self.send_json(200, {
                    "ok": True,
                    "lumitech": value,
                    "brightness": brightness,
                    "kelvin": kelvin,
                    "result": result
                })
                return

            if parsed.path == "/status":
                with lock:
                    status = lamp.send(
                        "get_prop",
                        ["power", "bright", "ct"]
                    )

                self.send_json(200, {
                    "ok": True,
                    "power": status[0],
                    "brightness": status[1],
                    "kelvin": status[2]
                })
                return

            self.send_json(404, {"ok": False, "error": "Not found"})

        except Exception as e:
            self.send_json(500, {
                "ok": False,
                "error": str(e)
            })

    def log_message(self, format, *args):
        print(
            f"{self.client_address[0]} - "
            f"{format % args}"
        )


print(f"Desk Lamp Bridge")
print(f"Lamp: {IP}")
print(f"HTTP Port: {PORT}")
print(f"Color temperature: {MIN_CT}-{MAX_CT} K")

server = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
server.serve_forever()
