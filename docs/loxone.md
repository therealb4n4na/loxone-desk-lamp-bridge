# Loxone integration

## Set value

Point a virtual HTTP output at the bridge:

```text
http://<DIETPI-IP>:8765/set?v=<v>
```

`<v>` is the Lumitech numeric value.

## Feedback

For diagnostics and optional status visualization:

```text
http://<DIETPI-IP>:8765/status
```

The response contains power, brightness, and Kelvin values read directly from the lamp.

## Recommendation

Do not send the same value on every small internal Loxone cycle. Write only when the desired light state actually changes. This reduces unnecessary miIO traffic and makes wireless problems easier to diagnose.
