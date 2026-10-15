# Dock Debug

Captures the state of a DisplayLink dock so a working setup can be compared with a broken one.

This was written for a Wavlink WS-UTD41-B on an M4 Pro MacBook Pro. The external monitors sometimes stayed dark until the dock had been replugged many times.

## What the dock is doing

The WS-UTD41-B is a Thunderbolt 4 dock, but its monitor outputs run through a DisplayLink chip (USB `17e9:6000`). The Mac doesn't send video to those monitors directly. `DisplayLinkUserAgent` (part of DisplayLink Manager) creates virtual displays, captures them with ScreenCaptureKit, and streams the pixels to the dock over USB.

In the logs from one bad morning:

- macOS brought both virtual displays online after every plug-in, including the ones where the monitors stayed dark.
- `DisplayLinkUserAgent` crashed three times. Every crash was the same `EXC_BAD_ACCESS` at address `0x18` (DisplayLink Manager 16.0.16, macOS 27.0.1).
- The monitors started working on the first plug-in after a crash relaunched the agent.

So the likely culprit is the DisplayLink agent, not the cable or the dock. That's an inference: the logs don't show the moment the monitors had no picture.

## When the monitors don't come up

1. Record the broken state before changing anything:

   ```bash
   ./snapshot.sh bad
   ```

2. Restart the DisplayLink agent instead of replugging:

   ```bash
   killall DisplayLinkUserAgent; open -a "DisplayLink Manager"
   ```

3. If that fixes it, the agent was the problem. Take a `good` snapshot and compare the two.

## Usage

```bash
./snapshot.sh [label]
```

Each run writes `~/dock-debug/<timestamp>-<label>/`, which contains:

| File | Contents |
| --- | --- |
| `summary.txt` | macOS and DisplayLink versions, DisplayLink process start times, recent crash reports, the displays macOS sees, the DisplayLink USB device, the Thunderbolt tree |
| `timeline.log` | Last 20 minutes: dock plug-ins, virtual displays coming online, DisplayLink errors and crashes |
| `full.log` | Last 20 minutes of DisplayLink, Thunderbolt, and virtual display log lines, without the screen-capture spam |
| `*.ips` | The three newest `DisplayLinkUserAgent` crash reports |

Snapshots stay outside this repo because they contain device serial numbers, window titles, and crash reports. The script makes `~/dock-debug/` and everything in it readable only by you, and the label must be a plain name (no `/` or leading `.`).

If any part of the capture fails, the script names the failed parts and exits nonzero.

The script is read-only. `log show` may take a minute.
