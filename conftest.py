"""Repository checks must never read or mutate the operator's local knowledge store."""

import pytest


@pytest.fixture(autouse=True)
def isolated_local_store(tmp_path, monkeypatch):
    monkeypatch.setenv("NWIS_DATA_DIR", str(tmp_path / "nwis"))
