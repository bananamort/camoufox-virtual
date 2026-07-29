import os
import shutil
import pytest
from pathlib import Path
from fastapi.testclient import TestClient

from app.browser import (
    ensure_extensions_unzipped,
    discover_extension_paths,
    run_extension_prelaunch_scripts,
    BASE_DIR,
    EXTENSIONS_DIR,
    UNPACKED_EXTENSIONS_DIR,
)
from app.server import app


def test_source_extensions_has_no_directories():
    dirs = [item for item in EXTENSIONS_DIR.iterdir() if item.is_dir()]
    assert len(dirs) == 0, f"Found unexpected unzipped directory in source extensions: {dirs}"


def test_unzip_and_discover_extensions():
    if UNPACKED_EXTENSIONS_DIR.exists():
        shutil.rmtree(UNPACKED_EXTENSIONS_DIR)

    unpacked_target = ensure_extensions_unzipped(EXTENSIONS_DIR, UNPACKED_EXTENSIONS_DIR)
    assert unpacked_target.exists()

    paths = discover_extension_paths(unpacked_target)
    assert len(paths) >= 2
    ext_names = [p.name for p in paths]
    assert "ublockorigin.firefox" in ext_names
    assert "nopecha_automation.firefox" in ext_names


def test_prelaunch_scripts():
    unpacked_target = ensure_extensions_unzipped(EXTENSIONS_DIR, UNPACKED_EXTENSIONS_DIR)
    run_extension_prelaunch_scripts(EXTENSIONS_DIR)


def test_health_check_endpoint():
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_root_and_instance_endpoints():
    client = TestClient(app)
    res_root = client.get("/")
    assert res_root.status_code == 200
    assert "Camoufox Browser Instance" in res_root.text

    res_inst = client.get("/instance")
    assert res_inst.status_code == 200
    assert "Camoufox Browser Instance" in res_inst.text


def test_instance_status_api():
    client = TestClient(app)
    res = client.get("/api/instance/status")
    assert res.status_code == 200
    data = res.json()
    assert "status" in data
    assert data["status"] in ["stopped", "running", "starting"]
