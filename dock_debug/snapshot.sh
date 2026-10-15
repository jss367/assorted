#!/bin/zsh
# Usage: ./snapshot.sh [label]   e.g. "good" or "bad"
# Captures Wavlink/DisplayLink dock state for diffing working vs broken.
# Snapshots go to ~/dock-debug/, outside this repo: they contain device
# serial numbers, window titles, and crash reports.
label=${1:-snap}
out=~/dock-debug/$(date +%Y%m%d-%H%M%S)-$label
mkdir -p $out
{
  date; sw_vers
  echo "DisplayLink Manager: $(defaults read '/Applications/DisplayLink Manager.app/Contents/Info' CFBundleShortVersionString 2>/dev/null)"
  echo; echo "== DisplayLink processes"; ps -o pid,lstart,etime,command -p $(pgrep -d, -i displaylink) 2>/dev/null
  echo; echo "== DisplayLink crash reports (newest first)"; ls -lt ~/Library/Logs/DiagnosticReports/ | grep -i displaylink | head
  echo; echo "== Displays"; system_profiler SPDisplaysDataType
  echo; echo "== DisplayLink USB device"; system_profiler SPUSBHostDataType | grep -B3 -A10 -i displaylink
  echo; echo "== Thunderbolt"; system_profiler SPThunderboltDataType
} > $out/summary.txt 2>&1
/usr/bin/log show --last 20m --style compact 2>/dev/null \
  | grep -E 'chimeOnAttach" age:00:00:00|Display:Virtual    \] Will bring display|DisplayLinkUserAgent.* E  |launchd.*displaylink.*(exited|crashed)|ScreenCaptureKit.*ERROR' \
  > $out/timeline.log
/usr/bin/log show --last 20m --style compact 2>/dev/null | grep -i -E 'displaylink|thunderbolt|Display:Virtual' | grep -v -E 'SCRunningApplication|SCWindow|SCDisplay initWith|com.apple.xpc:connection' > $out/full.log
cp $(ls -t ~/Library/Logs/DiagnosticReports/DisplayLinkUserAgent-*.ips 2>/dev/null | head -3) $out/ 2>/dev/null
echo "saved to $out"
