# Dozer Apple Silicon — Universal 4.2.1 (31)

Native universal macOS application for Apple silicon (`arm64`) and Intel (`x86_64`). Requires macOS 12 or later. Based on the Mortennn/Dozer source (4.2.0, build 30), retaining the original AppKit preference panes, assets, settings keys, and interactions.

[Releases](https://github.com/srofail/dozer-apple-silicon/releases/latest) · [Verification notes](VERIFICATION.md)

## Install and use

Get the app from [Releases](https://github.com/srofail/dozer-apple-silicon/releases/latest) and extract the archive. Quit any running Dozer instance, then copy `Dozer.app` to Applications and open it. The app runs in the menu bar. Hold Command and drag icons to arrange them. Click either large Dozer dot to hide/show icons left of the left dot. Right-click a dot to open Preferences. Enable the smaller third dot for a second group, revealed with Option-click. Reopening the app from Finder reveals all groups if needed.

All original settings are present: launch at login, automatic update checking, hide at launch, auto-hide after 3/5/10/15/20/30 seconds, hide both Dozer icons when a shortcut is configured, optional second group, use the full screen width, dot size 4–10 px, item width 10–40 px, and a global keyboard shortcut. The original preference domain `com.mortennn.Dozer` is preserved so existing settings carry over.

This build is ad-hoc signed, not Developer ID signed or notarized. If macOS blocks opening it after download, use System Settings > Privacy & Security > Open Anyway. No security settings need to be disabled. Launch at login may require approval under System Settings > General > Login Items; install the app in Applications before enabling it.

If a shortcut is reported as already used, check System Settings > Keyboard > Keyboard Shortcuts. Control–Option–Space is reserved by the Input Sources option “Select next source in Input menu” when that option is enabled. Disable or change that system binding before assigning the combination to Dozer.

## Build offline

With Xcode 27.2 (or a compatible newer Xcode) and Python 3 installed:

```sh
python3 build.py
python3 test.py
```

To test the Intel build on Apple silicon with Rosetta already installed: `DOZER_TEST_ARCH=x86_64 python3 test.py`.

Outputs: `build/Dozer.app` and `build/Dozer-Universal.zip`. All dependencies are vendored. No Homebrew, Carthage, SwiftGen, or XcodeGen installation is required. The historical project.yml/Cartfile/scripts describe the old upstream build and are not used by this build. Signing stages in a temporary directory to avoid iCloud FileProvider metadata interfering with codesign.

## Port changes

- All app code, statically linked Swift libraries, MASShortcut, the login helper, and Sparkle components include both architectures.
- Updated Sparkle 1 to Sparkle 2.10.1 with its supported updater API.
- Use SMAppService on macOS 13+, keeping the rebuilt login helper for macOS 12.
- Preserve Defaults 4.2.2, Preferences 2.2.1, and MASShortcut 2.4.0 behavior; compile their sources using the current toolchain.
- Remove status items from the menu bar when disabled; avoid duplicate optional icons and position collisions; copy images before resizing; handle variable menu-bar heights; avoid an unsafe frontmost-app force unwrap; supply an app menu and accessibility labels.

Update checking retains the original upstream appcast URL and public verification key. It checks upstream Dozer releases, not a separate update service for this build. There is no hosted universal-fork update feed. This version/build is greater than the currently published upstream version so the old Intel release will not replace it. Future upstream releases are outside this build's control.

## Verification

See VERIFICATION.md for the delivered build's checks and limits. Integration tests use a separate app bundle and preferences domain; they do not change your Dozer preferences or login items.

## Source and licenses

Original source: https://github.com/Mortennn/Dozer — MPL-2.0. Original copyright/license headers and LICENSE are retained. Modified source files are part of this universal port. Dependencies and their license texts are in Vendor; license copies are embedded in the app. This is a community rebuild, not an official upstream release.
