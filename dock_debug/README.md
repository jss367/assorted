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

A second failure looked different. On 2026-10-15 the monitors were lit but the cursor couldn't reach them:

- macOS had both LGs online, unmirrored, and laid out edge to edge with the laptop. It placed the cursor on the external main display, so the monitors were most likely showing a frozen frame.
- The agent had been running since morning with no crash. Its log showed ScreenCaptureKit `stopCapture` errors (`SCStreamErrorDomain` code `-3808`) at 15:22 and 15:34.
- Running `./snapshot.sh bad` fixed it without restarting the agent or replugging. The agent started new capture streams at 15:37:33.28, the same second the snapshot began.

The snapshot's first slow step is `system_profiler SPDisplaysDataType`, which probes the displays. That probe probably made the agent rebuild its capture streams. The timing suggests this but doesn't prove it, and it has only happened once.

## When the monitors don't come up

1. Record the broken state before changing anything:

   ```bash
   ./snapshot.sh bad
   ```

   The snapshot probes the displays, which fixed a frozen picture once (see above). If the monitors come back, take a `good` snapshot right away and note that the probe fixed it.

2. If they're still broken, probe the displays once more to see whether the fix repeats:

   ```bash
   system_profiler SPDisplaysDataType > /dev/null
   ```

3. If that doesn't help, restart the DisplayLink agent instead of replugging:

   ```bash
   killall DisplayLinkUserAgent; open -a "DisplayLink Manager"
   ```

4. If that fixes it, the agent was the problem. Take a `good` snapshot and compare the two.

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

The script doesn't change any settings, but its display probe can make the DisplayLink agent restart its capture streams. `log show` may take a minute.
