#!/usr/bin/env python3
"""
Check the status of all eero routers on your network.

Uses the eero cloud API to query each eero node's status, model,
and connected client count. Requires an eero account (email/phone —
Amazon login is not supported by the API).

First run will prompt for your email and a verification code.
Credentials are cached in your system keyring for subsequent runs.

Install:
    pip install eero-api

Usage:
    python check_eero.py
"""

import asyncio
import sys


async def main() -> None:
    try:
        from eero import EeroClient
    except ImportError:
        print("eero-api is not installed. Install it with:\n")
        print("    pip install eero-api\n")
        sys.exit(1)

    async with EeroClient() as client:
        # Authenticate
        if not client.is_authenticated:
            login_id = input("Enter the email or phone on your eero account: ").strip()
            await client.login(login_id)
            code = input("Enter the verification code sent to you: ").strip()
            await client.verify(code)
            print("Login successful.\n")

        # Get networks
        response = await client.get_networks()
        networks = response.get("data", {}).get("networks", [])
        if not networks:
            print("No eero networks found on this account.")
            sys.exit(1)

        for network_info in networks:
            network_url = network_info.get("url", "")
            network_id = network_url.rstrip("/").split("/")[-1]
            network_name = network_info.get("name", network_id)

            # Get network details
            network = await client.get_network(network_id)
            net_data = network.get("data", {})
            net_status = net_data.get("status", "unknown")
            print(f"Network: {network_name}  (status: {net_status})")
            print("=" * 60)

            # Get all eero nodes
            eeros_response = await client.get_eeros(network_id)
            eero_list = eeros_response.get("data", [])

            if not eero_list:
                print("  No eero devices found.\n")
                continue

            all_online = True
            for i, eero in enumerate(eero_list, 1):
                name = eero.get("location", eero.get("serial", f"eero-{i}"))
                status = eero.get("status", "unknown")
                model = eero.get("model", "unknown")
                clients = eero.get("connected_clients_count", "?")
                is_gateway = eero.get("is_gateway", False)
                role = "gateway" if is_gateway else "leaf"
                ip = eero.get("ip_address", "n/a")

                indicator = "OK" if status == "green" else "DOWN" if status == "red" else status.upper()
                if status != "green":
                    all_online = False

                print(f"  [{indicator:>4}]  {name}")
                print(f"         model: {model}  |  role: {role}  |  clients: {clients}  |  ip: {ip}")

            print()
            if all_online:
                print(f"All {len(eero_list)} eero(s) are online.")
            else:
                offline = [e.get("location", "?") for e in eero_list if e.get("status") != "green"]
                print(f"WARNING: {len(offline)} eero(s) appear to be offline or degraded: {', '.join(offline)}")
            print()


if __name__ == "__main__":
    asyncio.run(main())
