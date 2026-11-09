#!/usr/bin/env python3
"""Install only the preset, preserving an existing configuration."""
from datetime import datetime
from pathlib import Path
import shutil

root = Path(__file__).resolve().parents[1]
source = root / 'items.json'
target = Path.home() / 'Library/Application Support/MTMR/items.json'
if source.resolve() == target.resolve():
    print('O preset já está na pasta usada pelo MTMR.')
else:
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        folder = target.parent / 'backups'
        folder.mkdir(exist_ok=True)
        backup = folder / ('items-' + datetime.now().strftime('%Y%m%d-%H%M%S-%f') + '.json')
        shutil.copy2(target, backup)
        print('Cópia anterior:', backup)
    shutil.copy2(source, target)
    print('Preset instalado:', target)
print('Use a versão personalizada do MTMR para habilitar todas as funções.')
