"""Expose hyphenated service directories under their Python import names."""

import importlib.util
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[3] / "services"
for _path in _ROOT.iterdir():
    if _path.is_dir() and "-" in _path.name and (_path / "__init__.py").exists():
        _name = f"services.{_path.name.replace('-', '_')}"
        _spec = importlib.util.spec_from_file_location(
            _name, _path / "__init__.py", submodule_search_locations=[str(_path)]
        )
        _module = importlib.util.module_from_spec(_spec)
        sys.modules[_name] = _module
        _spec.loader.exec_module(_module)
