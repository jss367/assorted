#!/bin/bash
# Network & Certificate Diagnostic Script
# Run this while connected to the problematic network.

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m' # No Color

ok()   { echo -e "  ${GREEN}[OK]${NC} $*"; }
warn() { echo -e "  ${YELLOW}[WARN]${NC} $*"; }
err()  { echo -e "  ${RED}[FAIL]${NC} $*"; }
info() { echo -e "  ${BLUE}[INFO]${NC} $*"; }
header() { echo -e "\n${BOLD}--- $* ---${NC}"; }

# Portable openssl s_client with timeout (macOS doesn't have `timeout`)
ssl_check() {
    local host="$1" port="$2"
    echo | openssl s_client -connect "$host:$port" -servername "$host" 2>&1 &
    local pid=$!
    ( sleep 5; kill "$pid" 2>/dev/null ) &
    local watchdog=$!
    wait "$pid" 2>/dev/null
    kill "$watchdog" 2>/dev/null
    wait "$watchdog" 2>/dev/null
}

TIMESTAMP=$(date '+%Y%m%d_%H%M%S')
OUTPUT_FILE="$HOME/cert-debug-results_${TIMESTAMP}.txt"
exec > >(tee "$OUTPUT_FILE") 2>&1

echo -e "${BOLD}========================================${NC}"
echo -e "${BOLD}  Network & Certificate Diagnostics${NC}"
echo -e "${BOLD}  $(date)${NC}"
echo -e "${BOLD}========================================${NC}"

# 1. Basic network info
header "1. Network Info"
ACTIVE_IF=$(route get default 2>/dev/null | awk '/interface:/{print $2}')
if [ -n "$ACTIVE_IF" ]; then
    ok "Active interface: $ACTIVE_IF"
    networksetup -listallhardwareports 2>/dev/null | grep -A1 "$ACTIVE_IF" | head -2
else
    err "Could not determine active network interface"
fi

echo
WIFI_NET=$(networksetup -getairportnetwork en0 2>/dev/null)
if [ $? -eq 0 ] && ! echo "$WIFI_NET" | grep -q "not associated"; then
    ok "Wi-Fi: $WIFI_NET"
else
    info "Not on Wi-Fi (or Wi-Fi not associated)"
fi

GATEWAY_IP=$(route get default 2>/dev/null | awk '/gateway:/{print $2}')
if [ -n "$GATEWAY_IP" ]; then
    ok "Router/gateway IP: $GATEWAY_IP"
else
    err "Could not determine gateway IP"
fi

echo
echo "DNS servers:"
DNS_SERVERS=$(scutil --dns 2>/dev/null | grep 'nameserver\[' | head -6)
if [ -n "$DNS_SERVERS" ]; then
    echo "$DNS_SERVERS"
else
    err "No DNS servers found"
fi

# 2. Check for proxies
header "2. Proxy Settings"
HTTP_PROXY_ENABLED=$(networksetup -getwebproxy Wi-Fi 2>/dev/null | grep "^Enabled:" | awk '{print $2}')
HTTPS_PROXY_ENABLED=$(networksetup -getsecurewebproxy Wi-Fi 2>/dev/null | grep "^Enabled:" | awk '{print $2}')
AUTO_PROXY_ENABLED=$(networksetup -getautoproxyurl Wi-Fi 2>/dev/null | grep "^Enabled:" | awk '{print $2}')

if [ "$HTTP_PROXY_ENABLED" = "Yes" ]; then
    warn "HTTP proxy is ENABLED:"
    networksetup -getwebproxy Wi-Fi 2>/dev/null
else
    ok "HTTP proxy: disabled"
fi

if [ "$HTTPS_PROXY_ENABLED" = "Yes" ]; then
    warn "HTTPS proxy is ENABLED:"
    networksetup -getsecurewebproxy Wi-Fi 2>/dev/null
else
    ok "HTTPS proxy: disabled"
fi

if [ "$AUTO_PROXY_ENABLED" = "Yes" ]; then
    warn "Auto proxy is ENABLED:"
    networksetup -getautoproxyurl Wi-Fi 2>/dev/null
else
    ok "Auto proxy: disabled"
fi

if [ -n "$http_proxy" ] || [ -n "$https_proxy" ] || [ -n "$HTTP_PROXY" ] || [ -n "$HTTPS_PROXY" ]; then
    warn "Environment proxy vars set:"
    [ -n "$http_proxy" ]  && echo "    http_proxy=$http_proxy"
    [ -n "$https_proxy" ] && echo "    https_proxy=$https_proxy"
    [ -n "$HTTP_PROXY" ]  && echo "    HTTP_PROXY=$HTTP_PROXY"
    [ -n "$HTTPS_PROXY" ] && echo "    HTTPS_PROXY=$HTTPS_PROXY"
else
    ok "No environment proxy vars set"
fi

# 3. DNS resolution check
header "3. DNS Resolution"
for host in github.com www.google.com apple.com; do
    RESOLVED=$(dig +short "$host" 2>/dev/null | head -2 | tr '\n' ' ')
    if [ -n "$RESOLVED" ]; then
        ok "$host -> $RESOLVED"
    else
        err "$host -> FAILED TO RESOLVE"
    fi
done

# 4. Certificate checks (the key part)
header "4. Certificate Chain Analysis"
for site in github.com www.google.com apple.com; do
    echo
    echo -e "  ${BOLD}>> $site:443${NC}"
    CERT_OUTPUT=$(ssl_check "$site" 443)

    if ! echo "$CERT_OUTPUT" | grep -q "BEGIN CERTIFICATE"; then
        err "Could not retrieve certificate (connection failed or timed out)"
        continue
    fi

    SUBJECT=$(echo "$CERT_OUTPUT" | grep "subject=" | head -1)
    ISSUER=$(echo "$CERT_OUTPUT" | grep "issuer=" | head -1)
    VERIFY=$(echo "$CERT_OUTPUT" | grep "Verify return code")
    VERIFY_CODE=$(echo "$VERIFY" | grep -o "[0-9]*" | head -1)

    info "$SUBJECT"
    info "$ISSUER"

    # Check if the issuer is suspicious (not a well-known CA)
    if echo "$ISSUER" | grep -qiE "fortinet|fortigate|palo alto|zscaler|bluecoat|symantec web|netgear|asus|tp-link|linksys|ubiquiti|untangle|sophos|watchguard|barracuda|sonicwall|meraki|self.signed"; then
        err "Certificate issuer looks like a network device or proxy!"
        err "Your traffic is being intercepted (MITM)!"
    elif [ "$VERIFY_CODE" = "0" ]; then
        ok "$VERIFY"
    else
        err "$VERIFY"
    fi

    # Show full cert details
    echo "$CERT_OUTPUT" | openssl x509 -noout -dates -fingerprint 2>/dev/null | while read -r line; do
        info "$line"
    done
done

# 5. Compare certificate fingerprints against known good values
header "5. Certificate Fingerprint Comparison"
info "(If these differ from what you see on a trusted network, traffic is being intercepted)"
for site in github.com www.google.com; do
    FP=$(ssl_check "$site" 443 | openssl x509 -noout -fingerprint -sha256 2>/dev/null)
    if [ -n "$FP" ]; then
        info "$site: $FP"
    else
        err "$site: could not get fingerprint"
    fi
done

# 6. TLS version and cipher
header "6. TLS Details"
for site in github.com www.google.com; do
    TLS_INFO=$(ssl_check "$site" 443 | grep -E "Protocol|Cipher" | tr '\n' ' ')
    if echo "$TLS_INFO" | grep -q "TLSv1.3\|TLSv1.2"; then
        ok "$site: $TLS_INFO"
    elif [ -n "$TLS_INFO" ]; then
        warn "$site: $TLS_INFO"
    else
        err "$site: could not determine TLS details"
    fi
done

# 7. Curl verbose test
header "7. HTTPS Connection Tests"
for url in https://github.com https://www.google.com; do
    echo
    RESPONSE=$(curl -sI --connect-timeout 5 "$url" 2>&1 | head -1)
    RESULT=$?
    if [ $RESULT -eq 0 ]; then
        ok "$url -> $RESPONSE"
    else
        err "$url -> FAILED (exit code $RESULT)"
        VERBOSE=$(curl -vI --connect-timeout 5 "$url" 2>&1 | grep -iE "error|certificate|SSL|alert")
        echo -e "     ${RED}$VERBOSE${NC}"
    fi
done

# 8. Check system date
header "8. System Clock"
echo "  Local time: $(date)"
echo "  UTC time:   $(date -u)"
# Quick sanity check: is the year reasonable?
YEAR=$(date +%Y)
if [ "$YEAR" -ge 2024 ] && [ "$YEAR" -le 2030 ]; then
    ok "System clock looks reasonable (year: $YEAR)"
else
    err "System clock year ($YEAR) looks wrong!"
fi

# 9. Check for captive portal
header "9. Captive Portal Check"
PORTAL_CHECK=$(curl -sI --connect-timeout 5 http://captive.apple.com/hotspot-detect.html 2>&1)
PORTAL_STATUS=$(echo "$PORTAL_CHECK" | head -1)
if echo "$PORTAL_CHECK" | grep -q "302\|301\|303"; then
    err "Captive portal detected! You may need to authenticate on this network."
    echo -e "     ${RED}$PORTAL_STATUS${NC}"
elif echo "$PORTAL_CHECK" | grep -q "200"; then
    ok "No captive portal detected"
else
    warn "Unexpected response: $PORTAL_STATUS"
fi

# 10. Git / GitHub Desktop specific
header "10. Git SSL Config"
GIT_SSL_VERIFY=$(git config --global http.sslVerify 2>/dev/null)
GIT_SSL_CA=$(git config --global http.sslCAInfo 2>/dev/null)
GIT_HTTP_PROXY=$(git config --global http.proxy 2>/dev/null)
GIT_HTTPS_PROXY=$(git config --global https.proxy 2>/dev/null)

if [ "$GIT_SSL_VERIFY" = "false" ]; then
    warn "git http.sslVerify is set to FALSE (SSL verification disabled!)"
elif [ -n "$GIT_SSL_VERIFY" ]; then
    ok "git http.sslVerify: $GIT_SSL_VERIFY"
else
    ok "git http.sslVerify: <not set> (defaults to true)"
fi

if [ -n "$GIT_SSL_CA" ]; then
    info "git http.sslCAInfo: $GIT_SSL_CA"
else
    ok "git http.sslCAInfo: <not set> (using system defaults)"
fi

if [ -n "$GIT_HTTP_PROXY" ]; then
    warn "git http.proxy: $GIT_HTTP_PROXY"
else
    ok "git http.proxy: <not set>"
fi

if [ -n "$GIT_HTTPS_PROXY" ]; then
    warn "git https.proxy: $GIT_HTTPS_PROXY"
else
    ok "git https.proxy: <not set>"
fi

# 11. Router Health Check
header "11. Router Health Check"
info "Router IP: $GATEWAY_IP"
echo

# Check if router is reachable
echo "  Ping test (3 packets):"
PING_RESULT=$(ping -c 3 -W 2 "$GATEWAY_IP" 2>&1)
PING_LOSS=$(echo "$PING_RESULT" | grep "packet loss" | grep -o "[0-9.]*%" | head -1)
PING_AVG=$(echo "$PING_RESULT" | grep "avg" | awk -F'/' '{print $5}')
if [ "$PING_LOSS" = "0.0%" ] || [ "$PING_LOSS" = "0%" ]; then
    ok "Router reachable, 0% packet loss, avg ${PING_AVG}ms"
elif [ -n "$PING_LOSS" ]; then
    warn "Router reachable but $PING_LOSS packet loss, avg ${PING_AVG}ms"
else
    err "Router not responding to ping"
fi

# Check router uptime clues via ARP
ARP_ENTRY=$(arp -a 2>/dev/null | grep "($GATEWAY_IP)")
if [ -n "$ARP_ENTRY" ]; then
    info "ARP: $ARP_ENTRY"
else
    warn "No ARP entry for router"
fi

# Try to detect router time by checking its HTTPS certificate dates
echo
echo "  Router admin page certificate check:"
ROUTER_CERT=$(ssl_check "$GATEWAY_IP" 443)
if echo "$ROUTER_CERT" | grep -q "BEGIN CERTIFICATE"; then
    ok "Router has HTTPS admin page on port 443"
    echo "$ROUTER_CERT" | openssl x509 -noout -subject -issuer -dates 2>/dev/null | while read -r line; do
        info "$line"
    done
    NOT_BEFORE=$(echo "$ROUTER_CERT" | openssl x509 -noout -startdate 2>/dev/null | cut -d= -f2)
    NOT_AFTER=$(echo "$ROUTER_CERT" | openssl x509 -noout -enddate 2>/dev/null | cut -d= -f2)
    info "Certificate valid from: $NOT_BEFORE"
    info "Certificate valid to:   $NOT_AFTER"
else
    info "No HTTPS on port 443. Trying port 8443..."
    ROUTER_CERT=$(ssl_check "$GATEWAY_IP" 8443)
    if echo "$ROUTER_CERT" | grep -q "BEGIN CERTIFICATE"; then
        ok "Router has HTTPS admin page on port 8443"
        echo "$ROUTER_CERT" | openssl x509 -noout -subject -issuer -dates 2>/dev/null | while read -r line; do
            info "$line"
        done
    else
        info "No HTTPS admin page found on common ports (443, 8443)"
    fi
fi

# Check if router responds on HTTP (often port 80)
echo
echo "  Router HTTP admin page check:"
ROUTER_HTTP=$(curl -sI --connect-timeout 3 "http://$GATEWAY_IP/" 2>&1)
if [ $? -eq 0 ]; then
    ok "Router HTTP admin page is accessible"
    # Look for server header to identify router brand
    SERVER=$(echo "$ROUTER_HTTP" | grep -i "^server:" | head -1)
    if [ -n "$SERVER" ]; then
        info "Router identified as: $SERVER"
    fi
    # Check for Date header (reveals router's clock!)
    ROUTER_DATE=$(echo "$ROUTER_HTTP" | grep -i "^date:" | head -1)
    if [ -n "$ROUTER_DATE" ]; then
        echo
        echo -e "  ${BOLD}*** ROUTER CLOCK CHECK ***${NC}"
        info "Router says:    $ROUTER_DATE"
        info "Your Mac says:  Date: $(date -u '+%a, %d %b %Y %H:%M:%S GMT')"
        echo
        # Parse and compare
        ROUTER_EPOCH=$(date -j -f "%a, %d %b %Y %H:%M:%S GMT" "$(echo "$ROUTER_DATE" | sed 's/^[Dd]ate: //')" "+%s" 2>/dev/null)
        LOCAL_EPOCH=$(date -u "+%s")
        if [ -n "$ROUTER_EPOCH" ] && [ -n "$LOCAL_EPOCH" ]; then
            DIFF=$(( LOCAL_EPOCH - ROUTER_EPOCH ))
            ABS_DIFF=${DIFF#-}
            if [ "$ABS_DIFF" -gt 86400 ]; then
                DAYS=$(( ABS_DIFF / 86400 ))
                err "Router clock is off by ${DAYS} DAYS (${ABS_DIFF} seconds)!"
                err "This WILL cause certificate validation failures!"
                err "FIX: Log into router admin and enable NTP / set correct time."
            elif [ "$ABS_DIFF" -gt 300 ]; then
                err "Router clock is off by more than 5 minutes (${ABS_DIFF} seconds)!"
                err "This can cause certificate validation failures!"
                err "FIX: Log into router admin and enable NTP / set correct time."
            elif [ "$ABS_DIFF" -gt 60 ]; then
                warn "Minor clock drift detected (${ABS_DIFF} seconds) - probably not an issue"
            else
                ok "Clocks are in sync (${ABS_DIFF}s difference)"
            fi
        else
            warn "Could not parse router date for comparison"
        fi
    else
        warn "Router did not return a Date header - cannot check its clock"
    fi
else
    warn "Router HTTP admin page not reachable on port 80"
fi

# Check common router admin ports (with 2s timeout each)
echo
echo "  Router open ports (common admin ports):"
FOUND_PORT=false
for port in 80 443 8080 8443 8888; do
    (echo >/dev/tcp/$GATEWAY_IP/$port) 2>/dev/null &
    local_pid=$!
    ( sleep 2; kill "$local_pid" 2>/dev/null ) &
    local_wd=$!
    wait "$local_pid" 2>/dev/null
    port_result=$?
    kill "$local_wd" 2>/dev/null
    wait "$local_wd" 2>/dev/null
    if [ $port_result -eq 0 ]; then
        ok "Port $port: OPEN"
        FOUND_PORT=true
    fi
done
if [ "$FOUND_PORT" = false ]; then
    warn "No common admin ports open on router"
fi

# Traceroute to see if traffic goes through unexpected hops
header "12. Path to Internet (first 5 hops)"
info "(Looking for unexpected intermediaries)"
traceroute -m 5 -w 2 github.com 2>&1 | head -7

# 13. Check if certificate errors are date-related
header "13. Certificate Date Sanity Check"
info "Checking if any site cert dates conflict with current time..."
for site in github.com www.google.com apple.com; do
    CERT_DATA=$(ssl_check "$site" 443)
    NOT_BEFORE=$(echo "$CERT_DATA" | openssl x509 -noout -startdate 2>/dev/null | cut -d= -f2)
    NOT_AFTER=$(echo "$CERT_DATA" | openssl x509 -noout -enddate 2>/dev/null | cut -d= -f2)
    VERIFY=$(echo "$CERT_DATA" | grep "Verify return code")
    VERIFY_CODE=$(echo "$VERIFY" | grep -o "[0-9]*" | head -1)

    echo -e "\n  ${BOLD}$site:${NC}"
    info "Valid from: $NOT_BEFORE"
    info "Valid to:   $NOT_AFTER"
    if [ "$VERIFY_CODE" = "0" ]; then
        ok "$VERIFY"
    elif [ -n "$VERIFY_CODE" ]; then
        err "$VERIFY"
    else
        warn "Could not verify certificate"
    fi
done

echo
echo -e "${BOLD}========================================${NC}"
echo -e "${BOLD}  Diagnostics complete.${NC}"
echo -e "  Results saved to: ${BLUE}$OUTPUT_FILE${NC}"
echo
echo -e "${BOLD}  COMMON QUICK FIXES TO TRY:${NC}"
echo -e "  ${YELLOW}1.${NC} Restart your router (unplug for 30 sec)"
echo -e "  ${YELLOW}2.${NC} Log into router admin at ${BLUE}http://$GATEWAY_IP${NC}"
echo "     and check the date/time & NTP settings"
echo -e "  ${YELLOW}3.${NC} Try setting DNS to 8.8.8.8 / 1.1.1.1"
echo "     (System Prefs > Network > Wi-Fi > DNS)"
echo -e "  ${YELLOW}4.${NC} Check for firmware updates for your router"
echo -e "${BOLD}========================================${NC}"
