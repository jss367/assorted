#!/usr/bin/env python3
"""
Check the status of all eero routers on your network.

Uses the eero cloud API to query each eero node's status, model,
and connected client count. Requires an eero account (email/phone —
Amazon login is not supported by the API).

First run will prompt for your phone number or email and a verification
code sent via SMS/email. Credentials are cached locally in
~/.eero_session for subsequent runs.

Install:
    pip install eero-api

Usage:
    python check_eero.py
"""

import asyncio
import json
import sys
from pathlib import Path

SESSION_FILE = Path.home() / ".eero_session"


def save_session(token: str) -> None:
    SESSION_FILE.write_text(token)


def load_session() -> str | None:
    if SESSION_FILE.exists():
        return SESSION_FILE.read_text().strip()
    return None


async def login(api) -> str:
    login_id = input("Enter the email or phone number on your eero account: ").strip()
    user_token = await api.login(login_id)
    verification_code = input("Enter the verification code sent to you: ").strip()
    await api.login_verify(user_token, verification_code)
    print("Login successful.\n")
    return user_token


async def main() -> None:
    try:
        from eero_api import EeroClient
    except ImportError:
        print("eero-api is not installed. Install it with:\n")
        print("    pip install eero-api\n")
        sys.exit(1)

    client = EeroClient()

    # Authenticate
    token = load_session()
    if token is None:
        token = await login(client.api)
        save_session(token)
    client.api.cookie = token

    # Get networks
    networks = await client.get_networks()
    if not networks.get("data"):
        print("No eero networks found on this account.")
        sys.exit(1)

    for network_info in networks["data"]:
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
        eeros = await client.get_eeros(network_id)
        eero_list = eeros.get("data", [])

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

    # Clean up
    await client.close()


if __name__ == "__main__":
    asyncio.run(main())
