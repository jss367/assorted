# Network & Certificate Diagnostic Script

Diagnoses certificate errors, router issues, proxy interception, and clock drift.

## Usage

```bash
chmod +x ~/network-cert-debug.sh
~/network-cert-debug.sh
```

Results are printed to the terminal and saved to `~/cert-debug-results.txt`.

## Safety

This script is completely safe on a public network:
  - All read-only — it only looks at things, never changes anything
  - Ping/port checks — sends a tiny handful of packets to the router. Less traffic
  than loading a single webpage
  - No network scanning — it only talks to the router IP, never probes other people's
  devices
  - No auth attempts — it doesn't try to log into anything
  - Certificate checks — just normal HTTPS connections to public websites (github.com,
   google.com, apple.com), same as opening them in a browser
  - Traceroute — sends a few packets, totally standard

The only thing that touches the router at all is 3 pings and 5 port checks (which just see if a port is open, nothing more). A single Google search generates more network traffic.
