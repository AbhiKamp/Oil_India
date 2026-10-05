import sys
import os
import pytest
import importlib.util

def load_mod(name, rel_path):
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    full_path = os.path.join(base_dir, rel_path)
    spec = importlib.util.spec_from_file_location(name, full_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

units_mod = load_mod("units", "normalizers/units.py")
well_names_mod = load_mod("well_names", "normalizers/well_names.py")
table_mod = load_mod("table_parser", "parsers/table_parser.py")

def test_well_name_normalization():
    norm = well_names_mod.WellNameNormalizer
    assert norm.canonicalize("Nahorkatiya #421") == "NHK-421"
    assert norm.canonicalize("MORAN WELL 118") == "MOR-118"
    assert norm.canonicalize("Baghjan 7") == "BGH-07"

def test_unit_conversions():
    norm = units_mod.UnitNormalizer
    bar = norm.psi_to_bar(1000.0)
    assert round(bar, 1) == 68.9
    sg = norm.ppg_to_sg(10.0)
    assert round(sg, 2) == 1.20
    ft = norm.meters_to_feet(1000.0)
    assert round(ft, 0) == 3281.0

def test_table_parser():
    sample_text = '9-5/8" Intermediate Casing set at 2,520.0 m MD (Mud Weight: 1.22 SG)'
    tp = table_mod.TableParser()
    casing = tp.extract_casing_table(sample_text)
    assert len(casing) == 1
    assert casing[0]["setting_depth_md_m"] == 2520.0
    assert casing[0]["mud_weight_sg"] == 1.22
