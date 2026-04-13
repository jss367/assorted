Notes from 12 March 2026:

I have AT&T Fiber. The device connecting to the internet is an AT&T ONT (fiber terminal). It has a yellow fiber cable running to it. It's installed flush against the back of the network panel so I can't see the model number. I also don't see any other connections coming out of it. Based on traceroute, it appears to be at IP 192.168.1.254.

All three eeros I can see are Model B010001 and are connected wirelessly.

The bedroom eero has serial number GAC9-7662-64Y6-33XF. It has two ethernet connections — one to my NAS and one to a network switch. The network switch is connected to a bunch of home devices. The third cable to it is power. There is no ethernet cable between the ONT and the eero. The gateway IP is 192.168.4.1.

There are two additional eero units — one on the middle floor and one on the bottom floor. The one in the middle floor is labeled Family Room and has serial number GABY-4993-QHEH-T1ZT. The one on the bottom floor is labeled Office and has serial number GC3T-1476-6590-N92N.

There are also two devices listed as Gateway eero Pro. I don't know where these devices are. They could be inside the network panel. There shouldn't be two gateways, but it seems to work, so I'm not messing with them. They are labeled Unknown Gateway and Living Room, though I don't think it's in the living room. There is also a third eero device labeled Unknown. It's usually been off-line but as I'm typing might not be anymore. Though it was last active on 10/31/2025

When I plugged in the cables to the switch, I saw these new devices:

  - Resideo — thermostat (Honeywell Home)
  - AMPAK Technologies - a WiFi/Bluetooth module manufacturer. Their chips are embedded in tons of smart home devices
  (Roku, smart TVs, IoT hubs, etc.). So it's likely a smart TV or streaming device that was connected via ethernet through that
   switch.
  - iDevices — smart plug/switch
  - General Electric Consumer — likely a smart appliance (range, washer, etc.)


---

# Verified findings as of 2026-04-12

These update / correct some of the notes above. Facts here are from direct
tool output (wdutil, ifconfig, `check_eero.py`, eero app UI, ONT admin UI),
not inference.

## eero network

- Network SSID: **eeroJK42**
- DHCP & NAT mode (eero app): **Automatic**
- Guest network: **Off**
- eero LAN subnet: **192.168.4.0/22** (covers 192.168.4.x – 192.168.7.x)
- eero LAN gateway IP: **192.168.4.1**
- eero WAN IP (from eero app): **192.168.1.65** (assigned by the ONT)

## eeros on the network (from `check_eero_routers/check_eero.py`)

The old notes said 3 eeros of model B010001. The API reports **6 eeros, all
model "eero Pro"** (not B010001). Either the old notes were wrong or the
network was replaced since.

| Name             | Status | IP (mgmt) | Clients | Notes                                   |
|------------------|--------|-----------|---------|-----------------------------------------|
| Bedroom          | OK     | 192.168.4.1  | 3    | Actual gateway (its IP is the LAN GW)   |
| Office           | OK     | 192.168.4.22 | 6    |                                         |
| Family Room      | OK     | 192.168.4.25 | 10   |                                         |
| Living Room      | OK     | 192.168.4.20 | 0    |                                         |
| Unknown Gateway  | OK     | 192.168.4.24 | 6    | Just a name — a leaf, not a real gateway |
| Unknown          | DOWN   | n/a       | 0       | Offline; no IP, no clients              |

Note: the eero API returns `is_gateway: false` for *all* eeros in this
response. That field isn't populated reliably; the real gateway is the
eero whose mgmt IP equals the LAN gateway (192.168.4.1), i.e. Bedroom.

Resolves the old worry about "two Gateway eero Pro" — there is only one
real gateway (Bedroom). "Unknown Gateway" is just a misleading label on a
leaf node.

## AT&T ONT (upstream of eero)

- ONT / AT&T gateway IP: **192.168.1.254**
- ONT MAC: **d0:fc:d0:f7:c7:51**
- ONT subnet: **192.168.1.0/24**
- ONT Wi-Fi: **ENABLED** on both 2.4 GHz and 5 GHz
  - Home SSID: **ATTyj4pnxU** (WPA-2, enabled on both bands)
  - Guest SSID: **ATTyj4pnxU_Guest** (disabled)

## Mac

- Hardware Wi-Fi MAC: **60:3e:5f:48:47:57**
- macOS "Private Wi-Fi address" is active for eeroJK42 — the Mac presents
  a locally-administered MAC (e.g. `56:81:11:09:cc:e4`, `f2:18:f8:bc:e6:bc`)
  that changes when the network is forgotten+rejoined. Attempting to turn
  it off via System Settings didn't stick in our tests.
- Saved Wi-Fi networks include **eeroJK42** but **no AT&T variant**. The
  Mac is not silently auto-connecting to ATTyj4pnxU.

## Unresolved behaviour

When the Mac shows it is connected to SSID `eeroJK42`, it sometimes lands
on `192.168.1.x` (the ONT's subnet) instead of `192.168.4.x` (the eero
LAN). Confirmed via `ipconfig getsummary en0`:

```
server_identifier: 192.168.1.254   (the ONT)
router:            192.168.1.254
DHCP server MAC:   d0:fc:d0:f7:c7:51  (the ONT)
```

So the DHCP lease is coming from the ONT, not the eero. But per the eero
API, every online eero has an IP in `192.168.4.x` — no eero has a visible
presence on `192.168.1.x`. And the Mac isn't silently on the AT&T SSID
(not saved, and `wdutil` shows SSID redacted but Mac-OS-level saved-network
list doesn't contain it). We could not determine from the Mac alone which
physical AP the Mac is actually associated with (BSSID redacted even under
`sudo wdutil info`).

Not yet explained. Possibilities not yet ruled out:
- A non-eero AP is broadcasting the `eeroJK42` SSID (extender, old router,
  or an ONT feature)
- One of the eeros is selectively bridging some client traffic onto the
  ONT's LAN despite the eero running in router mode
- The `wdutil` IPv4 section reflects a prior association that hasn't fully
  cleared (stale DHCP lease on a Wi-Fi interface that re-associated)
