# Chrome Keychain

Notes on the macOS dialog "A keychain cannot be found to store 'Chrome'", first seen on 2026-10-16.

## What was checked

All of these came back healthy at about 17:25 on 2026-10-16 (macOS 27.0.1, Chrome 155.0.8059.82):

- `~/Library/Keychains/login.keychain-db` exists and is the default, login, and only user keychain.
- The login keychain is unlocked (`no-timeout`).
- The `Chrome Safe Storage` item (account `Chrome`) is present. It was created on 2025-12-07 and hasn't been modified since.

So the keychain wasn't missing or corrupt.

## Likely cause

Chrome auto-updated to 155.0.8059.82 on 2026-10-15 (the `Info.plist` timestamp is 22:09 that day). The Chrome process running on 2026-10-16 was started by the updater at 17:20:11 with `--restart --restart`. The login keychain file was modified at 17:20, the same minute.

A process relaunched by the updater can start in a context that can't reach the login keychain. macOS then shows this dialog even though the keychain is fine. That's an inference: the unified log didn't record the failed keychain lookup.

macOS had already been on 27.0.1 since 2026-10-02, so the OS update is an unlikely trigger.

## What to do

1. Click **Cancel** on the dialog.
2. Quit Chrome fully with Cmd-Q, then reopen it from the Dock.
3. If the dialog comes back after a clean launch, reboot.

**Don't click "Reset To Defaults."** It creates a new, empty login keychain. Chrome would then generate a new Safe Storage key and could no longer decrypt its existing cookies or locally saved passwords. You'd be logged out of every site, and passwords that aren't synced to your Google account would be lost.

## Rechecking

These commands only read state:

```bash
security default-keychain
security list-keychains -d user
security show-keychain-info ~/Library/Keychains/login.keychain-db
security find-generic-password -s "Chrome Safe Storage" | grep -E 'acct|cdat|mdat'
defaults read "/Applications/Google Chrome.app/Contents/Info.plist" CFBundleShortVersionString
ps -axo pid,lstart,command | grep "Google Chrome.app/Contents/MacOS" | grep -v grep
```

If the dialog persists after a reboot, record here whether `show-keychain-info` reports the keychain as locked and whether the `Chrome Safe Storage` dates changed.
