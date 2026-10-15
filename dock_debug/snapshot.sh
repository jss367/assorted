#!/bin/zsh
# Usage: ./snapshot.sh [label]   e.g. "good" or "bad"
# Captures Wavlink/DisplayLink dock state for diffing working vs broken.
# Snapshots go to ~/dock-debug/, outside this repo: they contain device
# serial numbers, window titles, and crash reports.
setopt pipefail
umask 077

label=${1:-snap}
if [[ $label == */* || $label == .* ]]; then
  echo "label must be a plain name (no '/' or leading '.'): $label" >&2
  exit 2
fi

root=~/dock-debug
out=$root/$(date +%Y%m%d-%H%M%S)-$label
if ! mkdir -p $out || ! chmod 700 $root $out; then
  echo "could not create $out" >&2
  exit 1
fi

failed=()
{
  date; sw_vers
  echo "DisplayLink Manager: $(defaults read '/Applications/DisplayLink Manager.app/Contents/Info' CFBundleShortVersionString 2>/dev/null)"
  echo; echo "== DisplayLink processes"; ps -o pid,lstart,etime,command -p $(pgrep -d, -i displaylink) 2>/dev/null
  echo; echo "== DisplayLink crash reports (newest first)"; ls -lt ~/Library/Logs/DiagnosticReports/ | grep -i displaylink | head
  echo; echo "== Displays"; system_profiler SPDisplaysDataType
  echo; echo "== DisplayLink USB device"; system_profiler SPUSBHostDataType | grep -B3 -A10 -i displaylink
  echo; echo "== Thunderbolt"; system_profiler SPThunderboltDataType
} > $out/summary.txt 2>&1 || failed+=(summary.txt)

# capture <file> <include-regex> [exclude-regex]: filter $logs into <file>.
# The file is opened first so an open failure isn't mistaken for grep's
# "no matches" (exit 1), which is a valid empty capture.
capture() {
  local f=$out/$1
  : > $f || { failed+=($1); return }
  print -r -- $logs | grep -E $2 | grep -v -E ${3:-'^$'} >> $f
  (( $? > 1 )) && failed+=($1)
}

# One log read feeds both files.
logs=$(/usr/bin/log show --last 20m --style compact) || failed+=("log show")
capture timeline.log 'chimeOnAttach" age:00:00:00|Display:Virtual    \] Will bring display|DisplayLinkUserAgent.* E  |launchd.*displaylink.*(exited|crashed)|ScreenCaptureKit.*ERROR'
capture full.log '[Dd]isplay[Ll]ink|[Tt]hunderbolt|Display:Virtual' 'SCRunningApplication|SCWindow|SCDisplay initWith|com.apple.xpc:connection'

reports=(~/Library/Logs/DiagnosticReports/DisplayLinkUserAgent-*.ips(N.om[1,3]))
(( $#reports )) && { cp -- $reports $out/ || failed+=("crash reports"); }

if (( $#failed )); then
  echo "partial snapshot in $out; failed: ${(j:, :)failed}" >&2
  exit 1
fi
echo "saved to $out (${#reports} crash reports)"
