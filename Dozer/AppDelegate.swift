/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/. */

import Cocoa
import MASShortcut
import Sparkle
import Defaults
import Preferences


final class AppDelegate: NSObject, NSApplicationDelegate {
    lazy var updaterController = SPUStandardUpdaterController(
        startingUpdater: true, updaterDelegate: nil, userDriverDelegate: nil
    )

    func applicationDidFinishLaunching(_: Notification) {
        _ = updaterController
        MASShortcutBinder.shared()?.bindShortcut(withDefaultsKey: UserDefaultKeys.Shortcuts.ToggleMenuItems) { () in
            DozerIcons.shared.toggle()
        }

        // Initalize Dozer Icons
        _ = DozerIcons.shared

        // If enabled hide menu bar icons at launch
        DozerIcons.shared.hideAtLaunch()

        _ = DozerIcons.toggleDockIcon(showIcon: false)
        installMainMenu()
    }

    private func installMainMenu() {
        let menu = NSMenu()
        let appItem = NSMenuItem()
        let appMenu = NSMenu(title: "Dozer")
        let settings = appMenu.addItem(withTitle: "Preferences…", action: #selector(showPreferences), keyEquivalent: ",")
        settings.target = self
        let updates = appMenu.addItem(withTitle: "Check for updates…", action: #selector(SPUStandardUpdaterController.checkForUpdates(_:)), keyEquivalent: "u")
        updates.target = updaterController
        appMenu.addItem(.separator())
        appMenu.addItem(withTitle: "Quit Dozer", action: #selector(NSApplication.terminate(_:)), keyEquivalent: "q")
        appItem.submenu = appMenu
        menu.addItem(appItem)
        NSApp.mainMenu = menu
    }

    @objc private func showPreferences() {
        preferencesWindowController.show(preferencePane: .general)
    }

    // Show all Dozer icons when opening Dozer from Finder etc.
    func applicationOpenUntitledFile(_ sender: NSApplication) -> Bool {
        DozerIcons.shared.showAll()
        return true
    }

    lazy var preferences: [PreferencePane] = [
        Dozer(),
        General()
    ]

    lazy var preferencesWindowController = PreferencesWindowController(
        preferencePanes: preferences,
        style: .toolbarItems,
        animated: true,
        hidesToolbarForSingleItem: true
    )
}
