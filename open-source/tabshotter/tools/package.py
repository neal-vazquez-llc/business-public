#!/usr/bin/env python3
"""Create a deterministic local unpackable extension ZIP; no publication."""
import json
from pathlib import Path
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED
ROOT = Path(__file__).resolve().parents[1]
manifest = json.loads((ROOT / 'extension/manifest.json').read_text())
output = ROOT / 'dist' / f"tabshotter-chromium-{manifest['version']}.zip"
output.parent.mkdir(exist_ok=True)
with ZipFile(output, 'w', compression=ZIP_DEFLATED) as archive:
    for name in ['manifest.json','capture.js','export.js','popup.html','popup.css','popup.js']:
        entry = ZipInfo(name, date_time=(2026,1,1,0,0,0))
        entry.compress_type = ZIP_DEFLATED
        entry.external_attr = 0o100644 << 16
        archive.writestr(entry, (ROOT / 'extension' / name).read_bytes())
print(output)
