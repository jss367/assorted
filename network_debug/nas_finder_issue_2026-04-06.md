# Finder Can't Connect to Synology NAS (2026-04-06)

> **Correction added 2026-04-12:** This doc treats `192.168.1.x` and
> `192.168.4.x` as two eero-managed subnets. That's wrong —
> `192.168.1.0/24` is the **AT&T ONT's LAN**, and `192.168.4.0/22` is
> the eero LAN (the eero has a WAN IP on the ONT's network and NATs its
> own LAN). Struck-through items below reflect that. See
> `Wifi situation.md` for the corrected topology.

## Symptom

Finder couldn't connect to the Synology NAS despite the NAS being visible via Bonjour.

## Diagnosis

- Mac was on `192.168.1.84/24` (via Wi-Fi on eero)
- NAS resolved via mDNS to `192.168.4.75` (DHCP, connected directly to eero)
- Ping to `192.168.4.75` showed 100% packet loss
- Assumed `192.168.4.x` was wrong because all other devices were on `192.168.1.x`

## What we tried

1. Checked NAS network config — already DHCP, not a static IP misconfiguration
2. Rebooted NAS — still got `192.168.4.75`
3. Rebooted eero via the app — NAS kept `192.168.4.75` but became **reachable**

## What actually happened

The `192.168.4.x` address was likely intentional or at least valid on the eero network.
The real problem was a **routing/connectivity issue on the eero itself**, not the subnet
mismatch we assumed. Rebooting the eero fixed the routing, even though the IP didn't
change.

## Lessons

- ~~eero can apparently hand out addresses on multiple subnets — `192.168.4.x` alongside
  `192.168.1.x` doesn't necessarily indicate a problem.~~ (The two subnets are
  actually ONT and eero respectively; the Mac being on `.1.x` was always a problem.)
- We spent time trying to "fix" the NAS IP when the NAS config was fine all along.
- ~~The correct first step should have been rebooting the eero, since it was the DHCP
  server and router responsible for connectivity between subnets.~~ (Rebooting eero
  did help, but not for the reason given — the ONT handles `.1.x`, not the eero.)
- Bonjour/mDNS discovery working while SMB fails = likely a routing problem, not a
  discovery or NAS config problem.
