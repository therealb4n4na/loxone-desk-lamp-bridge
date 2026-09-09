# Fehlersuche

## HTTP-Dienst prüfen

```bash
systemctl status desk-lamp-bridge.service
journalctl -u desk-lamp-bridge.service -n 100 --no-pager
```

## Lampe direkt über die Bridge testen

```bash
curl -sS http://127.0.0.1:8765/status
```

Wenn dieser Aufruf hängt oder mehrere Sekunden benötigt, ist meist die Kommunikation zur Lampe langsam.

## WLAN prüfen

```bash
ping -c 10 <LAMP-IP>
```

Auffällig sind hoher Jitter, mehrere hundert Millisekunden Latenz oder Paketverlust. Bei mehreren Access Points außerdem prüfen, ob die Lampe wirklich am räumlich passenden AP hängt.

## BrokenPipeError

Kann entstehen, wenn der HTTP-Client bereits in einen Timeout gelaufen ist, während die miIO-Abfrage noch auf eine Antwort wartet. Das ist häufig ein Folgefehler einer langsamen Gerätekommunikation.

## HTTP 403 bei `/set`

Der Client ist nicht als Schreibquelle freigegeben. Das ist beabsichtigt. `/status` kann trotzdem lesbar sein.

## Nach Änderungen

```bash
python3 -m py_compile bridge.py
sudo systemctl restart desk-lamp-bridge.service
curl -sS http://127.0.0.1:8765/status
```
