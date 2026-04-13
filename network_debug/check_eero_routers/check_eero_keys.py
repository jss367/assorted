#!/usr/bin/env python3
"""Dump every key/value for each eero so we can find the serial field."""
import asyncio
import json

async def main():
    from eero import EeroClient
    async with EeroClient() as client:
        if not client.is_authenticated:
            login_id = input("Email or phone: ").strip()
            await client.login(login_id)
            await client.verify(input("Code: ").strip())
        eeros = await client.get_eeros()
        for e in eeros.get("data", []):
            print("=" * 60)
            print(f"Location: {e.get('location')}")
            for k, v in sorted(e.items()):
                # Skip giant nested blobs we already saw
                if k in ("ethernet_status", "bssids_with_bands", "wifi_bssids"):
                    continue
                if isinstance(v, (dict, list)):
                    v = json.dumps(v)[:120]
                print(f"  {k}: {v}")

asyncio.run(main())
