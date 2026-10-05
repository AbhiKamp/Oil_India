import sys
import os
import pytest

# Ensure services directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

# Import using dynamic loader if folder has hyphen
import importlib.util

def load_module_from_path(module_name, file_path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
depth_mod = load_module_from_path("depth_extractor", os.path.join(base_dir, "extractors", "depth_extractor.py"))
formation_mod = load_module_from_path("formation_extractor", os.path.join(base_dir, "extractors", "formation_extractor.py"))
event_mod = load_module_from_path("event_extractor", os.path.join(base_dir, "extractors", "event_extractor.py"))

def test_depth_extractor():
    text = "Depth: 2,848.0 m MD (2,724.0 m TVD) was reached."
    extractor = depth_mod.DepthExtractor()
    depths = extractor.extract_depths(text)
    assert len(depths) >= 1
    assert depths[0]["md"] == 2848.0
    assert depths[0]["tvd"] == 2724.0

def test_formation_extractor():
    text = "- Tipam Sandstone: 610 m to 1,820 m MD (Massive porous water sands)"
    extractor = formation_mod.FormationExtractor()
    tops = extractor.extract_formation_tops(text)
    assert len(tops) == 1
    assert tops[0]["formation_name"] == "Tipam Sandstone"
    assert tops[0]["md_top"] == 610.0
    assert tops[0]["md_bottom"] == 1820.0

def test_event_extractor():
    text = "Incident Type: MECHANICAL HOLE PACK-OFF & STUCK PIPE"
    extractor = event_mod.EventExtractor()
    events = extractor.extract_events(text)
    assert len(events) == 1
    assert events[0]["categorized_type"] == "STUCK_PIPE_PACKOFF"
    assert events[0]["severity"] == "CRITICAL"
