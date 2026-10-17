# Chrome Keychain

Notes on the macOS dialog "A keychain cannot be found to store 'Chrome'", first seen on 2026-10-16.

## What was checked

These observations were recorded at about 17:25 on 2026-10-16 (macOS 27.0.1, Chrome 155.0.8059.82):

- `~/Library/Keychains/login.keychain-db` exists and is the default, login, and only user keychain.
- The login keychain reports `no-timeout`, an automatic-lock setting. This does not establish whether it is currently unlocked.
- The `Chrome Safe Storage` item (account `Chrome`) is present. It was created on 2025-12-07 and hasn't been modified since.

These checks established that the keychain file and the item's metadata were present. They did not establish the current lock state, verify that Chrome could read the secret, or rule out corruption. [`show-keychain-info` reports settings](https://github.com/apple-oss-distributions/Security/blob/main/SecurityTool/macOS/keychain_show_info.c), and the metadata lookup below does not retrieve the secret.

## Possible cause (unverified)

The installed Chrome bundle reported version 155.0.8059.82, and its `Info.plist` modification timestamp was 22:09 on 2026-10-15. The Chrome process observed on 2026-10-16 started at 17:20:11 with `--restart --restart`. The login keychain file was modified at 17:20, the same minute. These timestamps and arguments do not identify the launcher or establish when or how Chrome was updated.

An updater-related relaunch leaving Chrome unable to reach the login keychain is one unverified hypothesis. [`--restart` is not updater-specific](https://chromium.googlesource.com/chromium/src/+/refs/tags/133.0.6928.0/chrome/common/chrome_switches.cc#543): Chromium also uses it for restarts after flag changes. No process ancestry or updater logs were recorded here, and the unified log didn't record the failed keychain lookup, so neither the updater's involvement nor the failure mechanism was established.

macOS had already been on 27.0.1 since 2026-10-02, so the OS update is an unlikely trigger.

## What to do

1. Click **Cancel** on the dialog.
2. Quit Chrome fully with Cmd-Q, then reopen it from the Dock.
3. If the dialog comes back after a clean launch, reboot.

**Don't click "Reset To Defaults."** Resetting replaces the login keychain and affects more than Chrome: unrelated application and network passwords, certificates, identities, private keys, and secure notes in that keychain can become unavailable. [Apple warns that resetting deletes saved keychain passwords and recommends doing it only when advised by Apple Support](https://support.apple.com/guide/keychain-access/kyca2429/mac). Losing Chrome's existing Safe Storage key can also prevent decryption of existing cookies or locally saved passwords, causing sign-outs or loss of unsynced data. Recovery depends on what was synced or backed up.

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

If the dialog persists after a reboot, record the exact dialog and whether the `Chrome Safe Storage` metadata dates changed. `show-keychain-info` reports settings, not the current lock state; leave that state unverified unless it is checked separately.
