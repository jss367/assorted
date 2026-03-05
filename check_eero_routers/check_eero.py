#!/usr/bin/env python3
"""
Check the status of all eero routers on your network.

Uses the eero cloud API to query each eero node's status, model,
and connected client count. Requires an eero account (email/phone —
Amazon login is not supported by the API).

First run will prompt for your phone number or email and a verification
code sent via SMS/email. Credentials are cached locally via the OS
keyring for subsequent runs.

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
            login_id = input("Enter the email or phone number on your eero account: ").strip()
            await client.login(login_id)
            verification_code = input("Enter the verification code sent to you: ").strip()
            await client.verify(verification_code)
            print("Login successful.\n")

        # Get network details (auto-discovers network ID)
        network = await client.get_network()
        net_data = network.get("data", {})
        net_name = net_data.get("name", "unknown")
        net_status = net_data.get("status", "unknown")
        print(f"Network: {net_name}  (status: {net_status})")
        print("=" * 60)

        # Get all eero nodes
        eeros = await client.get_eeros()
        eero_list = eeros.get("data", [])

        if not eero_list:
            print("  No eero devices found.\n")
            sys.exit(1)

        all_online = True
        for i, eero_node in enumerate(eero_list, 1):
            name = eero_node.get("location", eero_node.get("serial", f"eero-{i}"))
            status = eero_node.get("status", "unknown")
            model = eero_node.get("model", "unknown")
            clients = eero_node.get("connected_clients_count", "?")
            is_gateway = eero_node.get("is_gateway", False)
            role = "gateway" if is_gateway else "leaf"
            ip = eero_node.get("ip_address", "n/a")

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
