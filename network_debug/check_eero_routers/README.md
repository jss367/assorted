# Check Eero Routers

Checks the status of all eero nodes on your network via the eero cloud API.
Reports which eeros are online, their model, role (gateway vs leaf), connected
clients, and flags any that are down.

## Setup

```bash
pip install eero-api
```

## Usage

```bash
python check_eero.py
```

On the first run you'll be asked for the email or phone number on your eero
account, then a verification code sent via SMS/email. Credentials are cached
in `~/.eero_session` so subsequent runs are automatic.

**Note:** Amazon-linked eero accounts are not supported by the API. If your
account uses Amazon login, have someone in your household create a standard
eero account and invite them as an admin to your network.

## Example output

```
Network: Home  (status: green)
============================================================
  [  OK]  Living Room
         model: eero Pro 6E  |  role: gateway  |  clients: 12  |  ip: 192.168.4.1
  [  OK]  Upstairs
         model: eero Pro 6E  |  role: leaf  |  clients: 8  |  ip: 192.168.4.2
  [DOWN]  Basement
         model: eero Pro 6E  |  role: leaf  |  clients: 0  |  ip: n/a

WARNING: 1 eero(s) appear to be offline or degraded: Basement
```
