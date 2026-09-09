# Loxone Xiaomi Desk Lamp Bridge

<!-- project-meta -->
> **Status:** Stable · **Current release:** `v1.0.0` · **License:** MIT · **Documentation:** Deutsch · **Issues/PRs:** Deutsch or English

[Changelog](CHANGELOG.md) · [Contributing](CONTRIBUTING.md) · [Security](SECURITY.md) · [Loxone-Doku](docs/loxone.md) · [Troubleshooting](docs/troubleshooting.md) · [Project collection](https://github.com/therealb4n4na/loxone-smart-home-projects)
<!-- /project-meta -->

Kleine lokale HTTP-Bridge, mit der eine Xiaomi/Yeelight-kompatible Schreibtischlampe über Loxone angesteuert werden kann. Die Bridge übersetzt einen Loxone-Lumitech-Zahlenwert in Helligkeit und Farbtemperatur und sendet die entsprechenden miIO-Befehle direkt an die Lampe.

## Funktionen

- Ein/Aus
- Helligkeit 0–100 %
- Farbtemperatur 2500–4800 K
- direkter Geräte-Status
- serialisierte miIO-Zugriffe, damit parallele Befehle sich nicht überschreiben
- Schreibzugriff nur von der freigegebenen Loxone-IP

## Architektur

```text
Loxone
  │ HTTP GET /set?v=...
  ▼
bridge.py :8765
  │ miIO
  ▼
Desk Lamp im lokalen WLAN
```

## Lumitech-Codierung

Die Bridge erwartet:

```text
0 -> AUS
200000000 + (Helligkeit * 10000) + Kelvin -> EIN
```

Beispiel für 50 % bei 3000 K:

```text
200503000
```

Die Farbtemperatur wird auf den unterstützten Bereich 2500–4800 K begrenzt.

## Voraussetzungen

- Linux / DietPi / Debian
- Python 3
- `python-miio`
- lokale IP-Adresse der Lampe
- miIO-Token der eigenen Lampe

Installation des Python-Pakets beispielsweise in einer virtuellen Umgebung:

```bash
python3 -m venv venv
./venv/bin/pip install python-miio
```

## Konfiguration

Die produktiven Werte werden über Umgebungsvariablen geladen. Vorlage:

[`lamp.env.example`](lamp.env.example)

Die echte Datei heißt lokal beispielsweise `lamp.env` und wird durch `.gitignore` ausgeschlossen.

Relevante Werte:

```text
LAMP_IP           IP-Adresse der Lampe
LAMP_TOKEN        lokaler miIO-Token
PORT              HTTP-Port der Bridge (Standard 8765)
WRITE_CLIENT_IP   einzige entfernte IP mit Schreibrecht, typischerweise Loxone
```

Wichtig: Ein miIO-Token ist ein Geheimnis und darf nicht in GitHub landen.

## HTTP-Endpunkte

### Lampe setzen

```text
GET http://<HOST>:8765/set?v=<LUMITECH_VALUE>
```

Dieser Endpunkt ist schreibend und akzeptiert nur die freigegebene Loxone-IP sowie localhost.

### Status lesen

```text
GET http://<HOST>:8765/status
```

Der Status wird direkt von der Lampe abgefragt. Ein laufender HTTP-Prozess bedeutet deshalb noch nicht automatisch, dass die Lampe im WLAN erreichbar ist.

## WLAN-Hinweis

miIO-Geräte reagieren empfindlich auf schlechte WLAN-Verbindungen. Wenn `/status` mehrere Sekunden benötigt oder sporadisch timeouts erzeugt, zuerst AP-Zuordnung, RSSI, Paketverlust und Latenz prüfen. Eine Bridge-Neuinstallation behebt kein schlechtes Funknetz.

## Loxone

Die eigentliche Loxone-Logik muss nur den Lumitech-Wert erzeugen und an `/set?v=...` senden.

Details: [`docs/loxone.md`](docs/loxone.md).

## Fehlersuche

Siehe [`docs/troubleshooting.md`](docs/troubleshooting.md).

## Sicherheit

- Token nur in lokaler Environment-Datei
- `/set` auf die Loxone-IP begrenzt
- `/status` bleibt für Diagnose lesbar
- Token-Extractor und andere lokale Hilfsdaten werden nicht versioniert

## Lizenz

MIT License – siehe [`LICENSE`](LICENSE).
