# Source provenance and modifications

This personal universal rebuild is based on the supplied Dozer-master source, identifying itself as Dozer 4.2.0 (30). Upstream: https://github.com/Mortennn/Dozer (Mozilla Public License 2.0).

The port modifies AppDelegate.swift, DozerIcons.swift, Util.swift, HelperStatusIcon.swift, RemoveStatusIcon.swift, DozerVC.swift, and GeneralVC.swift; adds the offline build/test scripts and integration suite; and replaces the build instructions/Makefile. Changes are described in README.md. Original source copyright/license notices are retained.

Vendored dependencies:
- Defaults v4.2.2 — MIT — https://github.com/sindresorhus/Defaults
- Preferences v2.2.1 (repository now named Settings) — MIT — https://github.com/sindresorhus/Settings
- LaunchAtLogin v4.1.0 (repository now named LaunchAtLogin-Legacy) — MIT — https://github.com/sindresorhus/LaunchAtLogin-Legacy
- MASShortcut 2.4.0 — BSD 2-Clause — https://github.com/shpakovski/MASShortcut
- Sparkle 2.10.1 official universal binary distribution — Sparkle license and third-party notices in Vendor/Sparkle/LICENSE — https://github.com/sparkle-project/Sparkle

LaunchAtLogin's isEnabled implementation is modified to use SMAppService on macOS 13+. MASShortcut's shared scheme is modified to build only the framework instead of also building its old test target. Other dependency sources are unchanged. Sparkle is re-signed ad-hoc when the app is built; its distributed library/helper binaries are otherwise unmodified.
