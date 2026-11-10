import Cocoa
import Defaults
import MASShortcut
import Preferences

let app = NSApplication.shared
setbuf(stdout, nil)
let appDelegate = AppDelegate()
app.delegate = appDelegate
app.setActivationPolicy(.accessory)
let domain = Bundle.main.bundleIdentifier!
precondition(domain == "com.mortennn.Dozer.UniversalTests")
UserDefaults.standard.removePersistentDomain(forName: domain)
defer { UserDefaults.standard.removePersistentDomain(forName: domain) }
var passed = 0
func check(_ condition: @autoclosure () -> Bool, _ message: String) {
    guard condition() else { fatalError("FAIL: \(message)") }
    passed += 1
    print("PASS: \(message)")
}
func settle(_ seconds: Double = 0.15) {
    RunLoop.main.run(until: Date().addingTimeInterval(seconds))
}
let icons = DozerIcons.shared
func items() -> [HelperstatusIcon] {
    // Inspect actual AppKit status-item lengths without exposing test-only app APIs.
    Mirror(reflecting: icons).children.first { $0.label == "dozerIcons" }!.value as! [HelperstatusIcon]
}
func normals() -> [HelperstatusIcon] { items().filter { $0.type == .normal } }
settle()
check(normals().count == 2, "two movable normal icons at startup")
icons.hide()
check(normals().filter { $0.isHidden }.count == 1, "hide leaves the interaction icon visible")
icons.toggle()
check(normals().allSatisfy { $0.isShown }, "toggle restores the first group")
icons.enableRemoveDozerIcon = true
settle()
check(items().filter { $0.type == .remove }.count == 1, "optional third icon is created")
icons.enableRemoveDozerIcon = true
check(items().filter { $0.type == .remove }.count == 1, "reapplying settings does not duplicate icons")
icons.hide()
check(items().filter { $0.isHidden }.count == 2, "hide collapses both groups")
icons.handleOptionClick()
check(items().allSatisfy { $0.isShown }, "option-click reveals both groups")
icons.handleOptionClick()
check(items().first { $0.type == .remove }!.isHidden, "option-click hides only the second group")
icons.toggleRemove()
check(items().first { $0.type == .remove }!.isShown, "third icon toggles its group")
icons.iconFontSize = 6
check(normals().allSatisfy { $0.statusIcon.button?.image?.size.width == 6 }, "icon size changes immediately")
check(items().first { $0.type == .remove }!.statusIcon.button!.image!.size.width == 3, "third icon retains half-size dot")
icons.buttonPadding = 35
check(items().allSatisfy { $0.statusIcon.length == 35 }, "icon width changes immediately")
icons.hideBothDozerIcons = true
check(normals().count == 2, "no-icon mode requires a shortcut")
Defaults[.isShortcutSet] = true
settle()
check(normals().count == 1, "shortcut enables no-icon mode")
icons.hide()
check(items().allSatisfy { $0.isHidden }, "no-icon mode hides all icons")
icons.showAll()
check(items().allSatisfy { $0.isShown }, "reopening can recover all icons")
Defaults[.isShortcutSet] = false
settle()
check(normals().count == 2, "removing shortcut restores the interaction icon")
icons.hideBothDozerIcons = false
icons.enableRemoveDozerIcon = false
check(items().count == 2, "disabling third icon removes it")
icons.handleOptionClick()
check(normals().allSatisfy { $0.isShown }, "option-click is safe with third icon disabled")
Defaults[.hideAfterDelay] = 0.3
icons.hideStatusBarIconsAfterDelay = true
icons.show()
settle(0.5)
check(normals().filter { $0.isHidden }.count == 1, "auto-hide timer collapses the first group")
icons.hideStatusBarIconsAfterDelay = false
icons.show()
settle(0.5)
check(normals().allSatisfy { $0.isShown }, "disabling auto-hide cancels timer")
icons.hideStatusBarIconsAtLaunch = true
icons.hideAtLaunch()
settle(0.3)
check(normals().filter { $0.isHidden }.count == 1, "hide-at-launch works after menu-bar layout")
icons.showAll()
icons.hideStatusBarIconsAtLaunch = false
let about = Dozer()
let general = General()
_ = about.view
_ = general.view
check(about.view.bounds.width > 0, "Dozer preference nib loads")
check(appDelegate.updaterController.updater.canCheckForUpdates, "Sparkle updater starts with valid configuration")
check(general.view.bounds.size == NSSize(width: 405, height: 415), "General preference nib loads at original dimensions")
func descendants(_ view: NSView) -> [NSView] { [view] + view.subviews.flatMap(descendants) }
let controls = descendants(general.view)
let checkboxes = controls.compactMap { $0 as? NSButton }.filter { !($0 is NSPopUpButton) }
check(checkboxes.count == 7, "all seven original preference checkboxes are present")
check(controls.compactMap { $0 as? NSPopUpButton }.count == 3, "all delay, size, and width selectors are present")
check(controls.contains { $0 is MASShortcutView }, "native shortcut recorder loads")
let shortcut = MASShortcut(keyCode: 2, modifierFlags: [.command, .option, .control])!
let monitor = MASShortcutMonitor.shared()!
check(monitor.register(shortcut, withAction: {}), "global Carbon shortcut registers")
check(monitor.isShortcutRegistered(shortcut), "shortcut registration is active")
monitor.unregisterShortcut(shortcut)
check(!monitor.isShortcutRegistered(shortcut), "global shortcut unregisters cleanly")
appDelegate.preferencesWindowController.show(preferencePane: .general)
settle()
check(appDelegate.preferencesWindowController.window?.isVisible == true, "preferences window opens")
appDelegate.preferencesWindowController.show(preferencePane: .dozer)
settle()
check(appDelegate.preferencesWindowController.window?.isVisible == true, "toolbar switches to Dozer pane")
appDelegate.preferencesWindowController.close()
check(Defaults[.iconSize] == 6 && Defaults[.buttonPadding] == 35, "original preference keys persist values")
print("\(passed) integration checks passed")
