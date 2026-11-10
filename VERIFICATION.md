# Verification — Dozer Universal 4.2.1 (31)

Built on 9 November 2026 with Xcode 27.2 / Swift 6.4.2, Swift 5 language mode, macOS SDK 27.2, deployment target macOS 12.0.

## Passed

- Release compilation for arm64 and x86_64; merged into a universal application.
- All 8 embedded Mach-O executables/libraries contain both architectures: Dozer, MASShortcut, Sparkle, Sparkle Autoupdate, Updater, Downloader, Installer, and the macOS 12 login helper.
- Deep, strict codesign verification of the final app and its nested frameworks, helpers, and services.
- ZIP integrity; framework symbolic links and executable permissions retained.
- Native arm64 app executable launches and remains running without runtime errors in its captured log.
- 34 AppKit integration checks passed on native Apple silicon.
- The same 34 checks passed for x86_64 using the already-installed Rosetta runtime.
- Isolated tests cover first/second groups, optional-icon removal, option-click behavior, no-icon shortcut gating and recovery, icon size/width, auto-hide, hide-at-launch, all original preference controls/nibs, updater initialization, global shortcut registration/unregistration, preferences window visibility/tab selection, and original preference keys.

## Practical limits

- Intel execution was tested through Rosetta, not on physical Intel hardware.
- macOS 12 and reboot/login behavior were not exercised on separate installations. Launch at login uses SMAppService on macOS 13+ and a universal legacy helper on macOS 12.
- Updater initialization was verified; installing an upstream update was not performed. The app retains the upstream appcast and its signing public key. No separate universal-fork update service is hosted.
- The local UI automation tool timed out when selecting the menu-bar-only application; UI control presence, nib loading and preference-window behavior were checked in the isolated AppKit test harness. A complete visual/manual pass on individual menu-bar arrangements remains unperformed.
- The app has a valid ad-hoc signature. Developer ID signing and Apple notarization were not possible because no signing identity is installed. A downloaded copy may need the standard Open Anyway action in Privacy & Security.

The source archive includes test.py and Tests/main.swift. Tests use the dedicated com.mortennn.Dozer.UniversalTests preferences domain and do not change the user's Dozer preferences or login-item configuration. To repeat the Intel checks on Apple silicon with Rosetta already installed: `DOZER_TEST_ARCH=x86_64 python3 test.py`.
