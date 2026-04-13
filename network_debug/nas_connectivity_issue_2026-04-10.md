# NAS Connectivity Lost Again (2026-04-10)

Third occurrence in five days. Same symptom, same fix, but the pattern is
now clear enough to act on.

## Symptom

Finder couldn't connect to Synology NAS. Identical to 2026-04-06 and
2026-04-09 incidents.

## Diagnosis

- Mac on `192.168.1.84/24`, gateway `192.168.1.254` (reachable, ~10ms)
- NAS resolved via mDNS to `192.168.4.75` (Bonjour discovery working)
- Ping to `192.168.4.75`: 100% packet loss
- Ping to `192.168.4.1`: 100% packet loss — no route into the other subnet
- ARP table had only `192.168.1.x` entries; no `192.168.4.x`

Same cross-subnet routing failure as before.

## Fix

Rebooted eero via the app. After settle:

- Mac moved from `192.168.1.84/24` → `192.168.4.35/22` (gateway `192.168.4.1`)
- NAS still at `192.168.4.75`, now reachable (~7ms, 0% loss)

## Pattern across three incidents

| Date  | Mac before   | NAS       | Fix mechanism                          |
|-------|--------------|-----------|-----------------------------------------|
| 04-06 | 192.168.1.84 | 192.168.4.75 | Routing between subnets restored   |
| 04-09 | 192.168.1.84 | 192.168.4.75 | Mac relocated to 192.168.4.x/22    |
| 04-10 | 192.168.1.84 | 192.168.4.75 | Mac relocated to 192.168.4.x/22    |

Two of three fixes worked by moving the Mac onto the NAS's subnet rather
than repairing routing. This is mild evidence that inter-subnet routing
between `192.168.1.0/24` and `192.168.4.0/22` on the eero may be broken
*all the time*, and the reboot "fix" is really just DHCP re-assignment
luck. The NAS has consistently been on `192.168.4.75` across all three
incidents.

## New finding: Mac is using a randomized private Wi-Fi MAC

- Hardware MAC (Wi-Fi): `60:3e:5f:48:47:57`
- Current MAC on en0: `f2:18:f8:bc:e6:bc` (locally-administered bit set)

macOS's "Private Wi-Fi address" feature is active for this SSID. In the
default "Fixed" mode this address is stable per-SSID, but in "Rotating"
mode (macOS Sequoia+) it changes every ~2 weeks, and any reset/toggle of
the setting will also change it. This is relevant because:

1. A DHCP reservation tied to a private MAC will silently break the next
   time the MAC rotates or is reset.
2. When the eero sees a "new" MAC, it may assign the device into whichever
   subnet pool — possibly explaining why the Mac lands on `.1.x` some times
   and `.4.x` other times.

## Preventive measures taken

Goal: get both Mac and NAS onto the same subnet permanently, independent
of whichever pool eero feels like assigning to.

Plan:

1. On the Mac, turn off "Private Wi-Fi address" for this SSID so the Mac
   presents its hardware MAC `60:3e:5f:48:47:57` to the eero.
2. In the eero app, add DHCP reservations:
   - NAS (`90:09:d0:2b:58:b7`) → `192.168.4.75` (where it already is)
   - Mac (`60:3e:5f:48:47:57`) → an unused address in `192.168.4.0/22`
3. Reconnect the Mac to Wi-Fi so it picks up the new lease.
4. Verify both devices land on the same subnet and the NAS is reachable.

## Deeper question (not yet investigated)

Why does this eero network have two subnets (`192.168.1.0/24` and
`192.168.4.0/22`) in the first place? Possible causes:

- A guest network or IoT network bridged into the main
- Leftover config from a prior setup
- An eero secondary/bridged device handing out its own scope

Worth checking in the eero app → Settings → Network Settings. Fixing this
at the source (collapsing to a single subnet) would be more robust than
DHCP reservations papering over it.

---

# Follow-up 2026-04-12

Issue recurred again. Spent a long session trying to diagnose and apply
the preventive measures above. Hypotheses in the "Preventive measures"
section above were partially wrong — recording what we actually confirmed
below so we don't go down the same dead ends next time.

## The two subnets are not "the eero's two subnets"

The `192.168.1.0/24` network is the **AT&T ONT's LAN**, not part of the
eero at all. The eero runs one LAN on `192.168.4.0/22` and has a WAN IP
of `192.168.1.65` (assigned by the ONT). So it's a double-router topology:

```
Internet — [AT&T ONT @ 192.168.1.254, 192.168.1.0/24] — [eero gateway WAN=.1.65, LAN=192.168.4.1/22] — clients
```

The NAS (at `192.168.4.75`) is plugged into the eero's LAN. When a client
is on `192.168.1.x`, it's on the ONT's LAN and outside the eero's NAT, so
it can't reach the NAS. That matches every incident's symptom.

## What we ruled out

- **Rogue eero:** all 6 eeros in the mesh have mgmt IPs on `192.168.4.x`
  per `check_eero.py`. No eero is on `192.168.1.x`. See updated
  `Wifi situation.md` for the full table.
- **Mac silently on the AT&T SSID:** the Mac's saved-networks list does
  **not** contain `ATTyj4pnxU` or any AT&T variant. The Mac isn't roaming
  to AT&T's Wi-Fi.
- **Second ATT SSID spoofing eeroJK42:** ATT ONT UI shows only
  `ATTyj4pnxU` (home) on both bands; guest SSID `ATTyj4pnxU_Guest` is
  disabled.
- **"Two gateway eeros" from the old notes:** only the Bedroom eero is a
  real gateway (IP `192.168.4.1`). "Unknown Gateway" is a misnamed leaf.

## Preventive-measure attempts that didn't work

1. **Disabling "Private Wi-Fi address" on the Mac.** System Settings →
   Wi-Fi → Details → Off didn't take effect on the live connection.
   Forgetting + rejoining the SSID caused macOS to generate a *new*
   private MAC (`56:81:11:09:cc:e4`) but still not use the hardware MAC.
   Couldn't force the Mac onto its hardware MAC within a reasonable amount
   of fiddling. **Next time: probably skip this step** and reserve whatever
   private MAC the Mac is currently using.
2. DHCP reservations were not added because we never got the Mac onto a
   stable MAC we were confident would persist.

## The remaining mystery

With the Mac's menu-bar SSID showing `eeroJK42`, `ipconfig getsummary en0`
reports the DHCP lease came from `192.168.1.254` (the ONT), not from any
eero. Per `check_eero.py`, no eero is on `192.168.1.x`. And the Mac's
saved-networks list has no AT&T entries.

We could not get `wdutil` or `airport` to reveal the actual BSSID the Mac
is associated with — macOS redacts SSID/BSSID for privacy, even under
`sudo`. So we can't tell from the Mac's side whether it's associated with
an eero AP (that's somehow bridging to the ONT) or some other AP with the
same SSID name.

## Worth trying next time

- Log into the AT&T gateway admin (`http://192.168.1.254`) and check the
  **DHCP leases table** — if the current Mac IP `192.168.1.116` appears
  there with the Mac's private MAC, the ONT issued the lease directly.
  The ONT leases view may also reveal a second wireless client (an eero?)
  bridging traffic.
- In the AT&T gateway admin, try disabling the **5 GHz** and **2.4 GHz**
  home Wi-Fi entirely (not just restart). The eero mesh will still provide
  Wi-Fi. If the Mac's Wi-Fi stays up and lands on `192.168.4.x`, the ONT's
  Wi-Fi was part of the problem.
- Ask for sudo and inspect `/Library/Preferences/com.apple.wifi.known-networks.plist`
  to see the full per-SSID config the Mac has saved.
- Investigate the network panel physically: the old notes mentioned a
  switch and "two Gateway eero Pro" devices the user didn't know the
  location of. Old/forgotten hardware in the panel is still a plausible
  vector for the ghost AP.
