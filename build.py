#!/usr/bin/env python3
"""Offline, reproducible universal build. Requires Xcode and Python 3."""
import os
from pathlib import Path
import plistlib
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parent
BUILD = ROOT / 'build'
# Stage signing outside iCloud Documents, where FileProvider adds FinderInfo
# to .app directories concurrently with codesign.
STAGE = Path(tempfile.mkdtemp(prefix='DozerUniversal-sign-'))
APP = STAGE / 'Dozer.app'
VENDOR = ROOT / 'Vendor'
ARCHS = ('arm64', 'x86_64')
os.chdir(ROOT)

def run(*args):
    print('+', ' '.join(map(str, args)), flush=True)
    subprocess.run(list(map(str, args)), check=True)

def plist(path, values):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(plistlib.dumps(values))

BUILD.mkdir(exist_ok=True)
CACHE = BUILD / 'ModuleCache'
SDK = subprocess.check_output(['xcrun', '--show-sdk-path'], text=True).strip()
BASE = ['-swift-version', '5', '-sdk', SDK, '-module-cache-path', str(CACHE), '-O']
run('xcodebuild', '-project', VENDOR / 'MASShortcut/MASShortcut.xcodeproj',
    '-scheme', 'MASShortcut', '-configuration', 'Release', '-derivedDataPath', BUILD / 'MASShortcut',
    'ARCHS=arm64 x86_64', 'ONLY_ACTIVE_ARCH=NO',
    'MACOSX_DEPLOYMENT_TARGET=12.0', 'CODE_SIGNING_ALLOWED=NO', 'GCC_TREAT_WARNINGS_AS_ERRORS=NO', 'build')

if APP.exists():
    shutil.rmtree(APP)
resources = APP / 'Contents/Resources'
frameworks = APP / 'Contents/Frameworks'
macos = APP / 'Contents/MacOS'
for p in (resources, frameworks, macos):
    p.mkdir(parents=True, exist_ok=True)
for name, source in [('MASShortcut', BUILD / 'MASShortcut/Build/Products/Release/MASShortcut.framework'),
                     ('Sparkle', VENDOR / 'Sparkle/Sparkle.framework')]:
    shutil.copytree(source, frameworks / (name + '.framework'), symlinks=True)

info = plistlib.loads((ROOT / 'Dozer/Other/Info.plist').read_bytes())
info.update(CFBundleExecutable='Dozer', CFBundleShortVersionString='4.2.1',
            CFBundleVersion='31', LSMinimumSystemVersion='12.0',
            NSHighResolutionCapable=True,
            NSHumanReadableCopyright='Copyright © Mortennn and Dozer contributors. MPL-2.0.',
            SUEnableAutomaticChecks=False)
plist(APP / 'Contents/Info.plist', info)
(APP / 'Contents/PkgInfo').write_text('APPL????')
for nib in ('Dozer', 'General'):
    run('xcrun', 'ibtool', '--compile', resources / (nib + '.nib'), ROOT / f'Dozer/XIB/{nib}.xib')
run('xcrun', 'actool', ROOT / 'Dozer/Other/Assets.xcassets', '--compile', resources,
    '--platform', 'macosx', '--minimum-deployment-target', '12.0',
    '--app-icon', 'AppIcon', '--output-partial-info-plist', BUILD / 'assets.plist')
info.update(plistlib.loads((BUILD / 'assets.plist').read_bytes()))
plist(APP / 'Contents/Info.plist', info)

helper = APP / 'Contents/Library/LoginItems/Dozer-LaunchAtLoginHelper.app'
helperbin = helper / 'Contents/MacOS/Dozer-LaunchAtLoginHelper'
helperbin.parent.mkdir(parents=True, exist_ok=True)
plist(helper / 'Contents/Info.plist', dict(
    CFBundleExecutable=helperbin.name, CFBundleIdentifier='com.mortennn.Dozer-LaunchAtLoginHelper',
    CFBundleName=helperbin.name, CFBundlePackageType='APPL', CFBundleVersion='31',
    CFBundleShortVersionString='4.2.1', LSBackgroundOnly=True, LSMinimumSystemVersion='12.0',
    NSPrincipalClass='NSApplication'))

for arch in ARCHS:
    out = BUILD / arch
    out.mkdir(exist_ok=True)
    target = f'{arch}-apple-macosx12.0'
    for module, folder in [('Defaults', 'Defaults'), ('Preferences', 'Preferences'), ('LaunchAtLogin', 'LaunchAtLogin')]:
        sources = sorted((VENDOR / folder / 'Sources' / module).glob('*.swift'))
        run('xcrun', 'swiftc', *BASE, '-target', target, '-module-name', module,
            '-emit-library', '-static', '-emit-module', '-emit-module-path', out / (module + '.swiftmodule'),
            '-o', out / ('lib' + module + '.a'), *sources)
    sources = sorted((ROOT / 'Dozer').rglob('*.swift'))
    run('xcrun', 'swiftc', *BASE, '-target', target, '-module-name', 'Dozer',
        '-I', out, '-L', out, '-lDefaults', '-lPreferences', '-lLaunchAtLogin',
        '-F', frameworks, '-framework', 'MASShortcut', '-framework', 'Sparkle',
        '-Xlinker', '-rpath', '-Xlinker', '@executable_path/../Frameworks',
        '-o', out / 'Dozer', *sources)
    run('xcrun', 'swiftc', *BASE, '-target', target, '-o', out / 'Dozer-LaunchAtLoginHelper',
        VENDOR / 'LaunchAtLogin/Sources/LaunchAtLoginHelper/main.swift')
run('xcrun', 'lipo', '-create', *[BUILD / a / 'Dozer' for a in ARCHS], '-output', macos / 'Dozer')
run('xcrun', 'lipo', '-create', *[BUILD / a / helperbin.name for a in ARCHS], '-output', helperbin)

licenses = resources / 'Licenses'
licenses.mkdir(exist_ok=True)
shutil.copy2(ROOT / 'LICENSE', licenses / 'Dozer-MPL-2.0.txt')
for folder, filename in [('Defaults', 'license'), ('Preferences', 'license'),
                         ('LaunchAtLogin', 'license'), ('MASShortcut', 'LICENSE'), ('Sparkle', 'LICENSE')]:
    shutil.copy2(VENDOR / folder / filename, licenses / (folder + '.txt'))

# Ad-hoc signing permits local execution on Apple silicon without a developer account.
# Sign nested Mach-O code and then containing bundles from the inside out.
run('xattr', '-cr', APP)
bundles = [p for p in APP.rglob('*') if p.is_dir() and not p.is_symlink()
           and p.suffix in ('.app', '.framework', '.xpc')]
for p in sorted(bundles, key=lambda p: len(p.parts), reverse=True):
    run('codesign', '--force', '--sign', '-', '--timestamp=none', p)
run('codesign', '--force', '--sign', '-', '--timestamp=none', APP)
run('codesign', '--verify', '--deep', '--strict', '--verbose=2', APP)
destination = BUILD / 'Dozer.app'
if destination.exists():
    shutil.rmtree(destination)
run('ditto', '--norsrc', '--noextattr', APP, destination)
run('codesign', '--verify', '--deep', '--strict', '--verbose=2', destination)
run('ditto', '-c', '-k', '--keepParent', '--norsrc', '--noextattr', APP, BUILD / 'Dozer-Universal.zip')
shutil.rmtree(STAGE)
print(f'Built {destination}')
