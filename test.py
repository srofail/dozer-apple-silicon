#!/usr/bin/env python3
"""Run AppKit integration tests in a separate bundle and preference domain."""
from pathlib import Path
import plistlib
import shutil
import subprocess
import tempfile
import os

root = Path(__file__).resolve().parent
build = root / 'build'
stage = Path(tempfile.mkdtemp(prefix='DozerUniversal-tests-'))
app = stage / 'DozerTests.app'
if app.exists():
    shutil.rmtree(app)
shutil.copytree(build / 'Dozer.app', app, symlinks=True)
info = plistlib.loads((app / 'Contents/Info.plist').read_bytes())
info['CFBundleIdentifier'] = 'com.mortennn.Dozer.UniversalTests'
(app / 'Contents/Info.plist').write_bytes(plistlib.dumps(info))
sdk = subprocess.check_output(['xcrun', '--show-sdk-path'], text=True).strip()
arch = os.environ.get('DOZER_TEST_ARCH') or ('arm64' if __import__('platform').machine() == 'arm64' else 'x86_64')
assert arch in ('arm64', 'x86_64')
sources = sorted(p for p in (root / 'Dozer').rglob('*.swift') if p.name != 'main.swift')
subprocess.run(['xcrun', 'swiftc', '-swift-version', '5', '-sdk', sdk,
    '-module-cache-path', str(build / 'ModuleCache'), '-target', f'{arch}-apple-macosx12.0',
    '-module-name', 'Dozer', '-I', str(build / arch), '-L', str(build / arch),
    '-lDefaults', '-lPreferences', '-lLaunchAtLogin', '-F', str(app / 'Contents/Frameworks'),
    '-framework', 'MASShortcut', '-framework', 'Sparkle', '-Xlinker', '-rpath', '-Xlinker',
    '@executable_path/../Frameworks', '-o', str(app / 'Contents/MacOS/Dozer'),
    *map(str, sources), str(root / 'Tests/main.swift')], check=True)
subprocess.run(['xattr', '-cr', str(app)], check=True)
subprocess.run(['codesign', '--force', '--sign', '-', str(app)], check=True)
subprocess.run([str(app / 'Contents/MacOS/Dozer')], check=True)
shutil.rmtree(stage)
