# NAS Connectivity Lost Again (2026-04-09)

## Symptom

Finder couldn't connect to Synology NAS. Same symptom as 2026-04-06 incident.

## Diagnosis

- NAS was discoverable via Bonjour/mDNS (`synology_nas._smb._tcp.local`)
- NAS was reachable via QuickConnect (internet relay), confirming it had working internet
- Mac was on `192.168.1.84/24`, NAS was on `192.168.4.75` — different subnets
- Ping to `192.168.4.75` and gateway `192.168.4.1` both showed 100% packet loss
- ARP table had no `192.168.4.x` entries before the fix

## What we tried

1. Rebooted eero via the app (worked last time) — didn't immediately fix it
2. Re-checked after reboot settled — Mac's IP changed from `192.168.1.84/24` to `192.168.4.35/22`
3. Once on the same subnet, NAS was reachable: ping succeeded, SMB port 445 open

## What happened

The eero reboot did fix it, but differently than last time:
- **April 6:** Reboot fixed routing between subnets; NAS stayed on `192.168.4.75`, Mac stayed on `192.168.1.84`
- **April 9:** Reboot moved the Mac onto `192.168.4.x/22`, putting both devices on the same subnet

## Root cause pattern

The eero network runs (at least) two subnets: `192.168.1.x` and `192.168.4.x`. It
inconsistently assigns devices to one or the other, and inter-subnet routing is unreliable.
When the Mac lands on `192.168.1.x/24` and the NAS is on `192.168.4.x`, they can't reach
each other even though Bonjour (multicast) still works across the boundary.

Key clue: Bonjour/mDNS discovery works but SMB connection fails = routing problem, not
discovery or NAS config problem.

## Possible preventive measures

- Reserve the NAS's IP via eero app (DHCP reservation) so it stays predictable
- Reserve the Mac's IP in the same subnet range
- Investigate whether eero has a setting to consolidate to a single subnet
- As a last resort, set a static IP on the NAS itself (less preferred — DHCP reservation
  is cleaner)
