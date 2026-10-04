#!/usr/bin/env python3
"""Dump full eero node details — serial, MACs, connection mode, uptime."""
import asyncio
import json
import sys


async def main() -> None:
    from eero import EeroClient

    async with EeroClient() as client:
        if not client.is_authenticated:
            login_id = input("Email or phone: ").strip()
            await client.login(login_id)
            code = input("Verification code: ").strip()
            await client.verify(code)

        eeros = await client.get_eeros()
        for e in eeros.get("data", []):
            print("=" * 60)
            print(f"Location:        {e.get('location')}")
            print(f"Serial:          {e.get('serial_number')}")
            print(f"Model:           {e.get('model')}  ({e.get('model_number')})")
            print(f"Status:          {e.get('status')}")
            print(f"IP (mgmt):       {e.get('ip_address')}")
            print(f"WAN IP:          {e.get('wan_ip')}")
            print(f"LAN IP:          {e.get('lan_ip')}")
            print(f"MAC (wired):     {e.get('mac_address')}")
            print(f"Ethernet status: {e.get('ethernet_status')}")
            print(f"Connection:      {e.get('connection_type')} wired={e.get('using_wan')}")
            print(f"Gateway flag:    {e.get('is_gateway')}")
            print(f"Clients:         {e.get('connected_clients_count')}")
            print(f"Last reboot:     {e.get('last_reboot')}")
            # Radios (BSSIDs per band)
            for key in ("wireless_mac_2", "wireless_mac_5", "wireless_mac_5_high",
                        "wireless_mac", "radios"):
                if key in e:
                    print(f"{key}: {e[key]}")
            # Fall back — dump anything else that contains 'mac' or 'bssid'
            for k, v in e.items():
                if ("mac" in k.lower() or "bssid" in k.lower()) and k not in (
                    "mac_address", "wireless_mac_2", "wireless_mac_5",
                    "wireless_mac_5_high", "wireless_mac"
                ):
                    print(f"  {k}: {v}")


if __name__ == "__main__":
    asyncio.run(main())
