# Loxone-Einbindung

## Setzen

Virtuellen HTTP-Ausgang auf die Bridge richten:

```text
http://<DIETPI-IP>:8765/set?v=<v>
```

`<v>` ist der Lumitech-Zahlenwert.

## Rückmeldung

Für Diagnose und optional eine Statusvisualisierung:

```text
http://<DIETPI-IP>:8765/status
```

Der Status enthält den tatsächlich von der Lampe gelesenen Power-, Helligkeits- und Kelvin-Wert.

## Empfehlung

Nicht bei jedem kleinen internen Loxone-Zyklus denselben Wert erneut senden. Nur bei einer tatsächlichen Änderung des gewünschten Lichtzustands schreiben. Das reduziert unnötige miIO-Kommunikation und macht WLAN-Probleme leichter erkennbar.
