#!/usr/bin/env python3
"""Build the preserved MTMR customization from pinned, verified upstream files."""
from pathlib import Path
import hashlib
import json
import plistlib
import re
import shutil
import subprocess
import sys
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / '.build'
DIST = ROOT / 'dist'
META = json.loads((ROOT / 'UPSTREAM.json').read_text())


def run(args, **kwargs):
    return subprocess.run([str(x) for x in args], check=True, **kwargs)


def download(name, url, expected_hash):
    folder = BUILD / 'downloads'
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / name
    if not path.exists():
        print('Baixando', name, flush=True)
        temporary = path.with_suffix('.download')
        with urllib.request.urlopen(url, timeout=120) as response, temporary.open('wb') as target:
            shutil.copyfileobj(response, target)
        temporary.replace(path)
    if hashlib.sha256(path.read_bytes()).hexdigest() != expected_hash:
        raise RuntimeError('Arquivo diferente do esperado: ' + str(path))
    return path


def main():
    if sys.platform != 'darwin':
        raise RuntimeError('Este processo precisa ser executado no macOS.')
    BUILD.mkdir(exist_ok=True)
    DIST.mkdir(exist_ok=True)
    source_archive = download('source.tar.gz', META['source_url'], META['source_sha256'])
    base_dmg = download('MTMR.dmg', META['base_app_url'], META['base_app_sha256'])
    source_parent = BUILD / 'source'
    if source_parent.exists():
        shutil.rmtree(source_parent)
    source_parent.mkdir()
    run(['tar', '-xzf', source_archive, '-C', source_parent])
    source = source_parent / ('MTMR-' + META['source_commit'])
    with (ROOT / 'patches/mtmr-personalizado.patch').open('rb') as patch:
        run(['patch', '--batch', '-p1'], cwd=source, stdin=patch)

    sdk = subprocess.check_output(['xcrun', '--show-sdk-path'], text=True).strip()
    cache = BUILD / 'module-cache'
    objects = []
    for path in sorted((source / 'MTMR/CBridge').glob('*')):
        if path.suffix not in ('.m', '.c'):
            continue
        obj = BUILD / (path.stem + '.o')
        objects.append(obj)
        arc = ['-fobjc-arc'] if path.suffix == '.m' else []
        run(['clang', '-c', path, '-o', obj, '-isysroot', sdk, *arc,
             '-fmodules', '-fmodules-cache-path=' + str(cache), '-Wno-deprecated-declarations'])

    binary = BUILD / 'MTMR'
    command = ['swiftc', '-swift-version', '5', '-module-name', 'MTMR',
               '-module-cache-path', cache, '-import-objc-header',
               source / 'MTMR/CBridge/TouchBarPrivateApi-Bridging.h',
               '-F', source, '-F', sdk + '/System/Library/PrivateFrameworks']
    for framework in ['Sparkle', 'MultitouchSupport', 'DFRFoundation', 'CoreDisplay',
                      'CoreBrightness', 'Carbon', 'IOKit', 'ServiceManagement', 'CoreAudio', 'AppKit']:
        command += ['-framework', framework]
    command += ['-Xlinker', '-rpath', '-Xlinker', '@executable_path/../Frameworks', '-o', binary]
    # The original visual editor uses SwiftUI macros unavailable in the installed
    # command-line toolchain. The configuration continues to be edited as JSON.
    command += [p for p in sorted((source / 'MTMR').rglob('*.swift'))
                if 'Customizer' not in p.parts or p.name == 'JSONValue.swift']
    command += objects
    print('Compilando o MTMR personalizado...', flush=True)
    with (BUILD / 'build.log').open('w') as log:
        run(command, stdout=log, stderr=subprocess.STDOUT)

    test_binary = BUILD / 'marquee-tests'
    run(['swiftc', '-module-cache-path', cache, source / 'MTMR/TitleMarqueeMotion.swift',
         ROOT / 'tests/main.swift', '-o', test_binary])
    run([test_binary])

    # Reuse only the app resources from the official, checksum-verified DMG.
    baseline = BUILD / 'base/MTMR.app'
    if not baseline.exists():
        mount = BUILD / 'mount'
        mount.mkdir(exist_ok=True)
        run(['hdiutil', 'attach', '-nobrowse', '-readonly', '-mountpoint', mount, base_dmg],
            stdout=subprocess.DEVNULL)
        try:
            baseline.parent.mkdir(exist_ok=True)
            shutil.copytree(mount / 'MTMR.app', baseline, symlinks=True)
        finally:
            run(['hdiutil', 'detach', mount], stdout=subprocess.DEVNULL)

    app = DIST / 'MTMR.app'
    if app.exists():
        shutil.rmtree(app)
    shutil.copytree(baseline, app, symlinks=True)
    shutil.copyfile(binary, app / 'Contents/MacOS/MTMR')
    sparkle = app / 'Contents/Frameworks/Sparkle.framework'
    if sparkle.exists():
        shutil.rmtree(sparkle)
    shutil.copytree(source / 'Sparkle.framework', sparkle, symlinks=True)
    info_path = app / 'Contents/Info.plist'
    with info_path.open('rb') as file:
        info = plistlib.load(file)
    info['CFBundleShortVersionString'] = META['custom_version']
    # The official app's old minimum system version does not describe this build.
    build_info = subprocess.check_output(['xcrun', 'vtool', '-show-build', binary], text=True)
    minimum = re.search(r'\bminos\s+([0-9.]+)', build_info)
    if not minimum:
        raise RuntimeError('Não foi possível identificar a versão mínima do macOS.')
    info['LSMinimumSystemVersion'] = minimum.group(1)
    with info_path.open('wb') as file:
        plistlib.dump(info, file)
    run(['codesign', '--force', '--deep', '--sign', '-', app])
    run(['codesign', '--verify', '--deep', '--strict', app])
    print('Aplicativo pronto:', app)
    print('Este comando não substitui o aplicativo instalado nem o preset ativo.')


if __name__ == '__main__':
    try:
        main()
    except (RuntimeError, OSError, subprocess.CalledProcessError) as error:
        print('Falha:', error, file=sys.stderr)
        print('Detalhes da compilação, se iniciada: ' + str(BUILD / 'build.log'), file=sys.stderr)
        sys.exit(1)
