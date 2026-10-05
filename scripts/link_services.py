import os
import shutil

services = [
    'document-intelligence',
    'formation-correlation',
    'physics-validation',
    'rag-engine',
    'risk-engine',
    'risk-fusion',
    'telemetry-ingestion',
    'well-geometry'
]
base = r'c:\Projects\Oil_India\services'

for s in services:
    alias = s.replace('-', '_')
    link_path = os.path.join(base, alias)
    target_path = os.path.join(base, s)
    if os.path.exists(link_path):
        if os.path.islink(link_path):
            os.unlink(link_path)
        else:
            shutil.rmtree(link_path)
    cmd = f'cmd /c mklink /J "{link_path}" "{target_path}"'
    os.system(cmd)
    print(f'Linked {alias} -> {s}')
