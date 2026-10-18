"""
Tests for Phase 7: Package Management & Project Manifest
Validates doom.toml creation, reading, dependency additions, and CLI commands.
"""

from pathlib import Path
from typer.testing import CliRunner
from doomscript.cli import app
from doomscript.package import init_manifest, read_manifest, add_dependency

runner = CliRunner()


def test_manifest_init_and_read(tmp_path):
    manifest = init_manifest(tmp_path, name="test_app", entrypoint="app.doom")
    assert manifest.exists()

    data = read_manifest(tmp_path)
    assert data["package"]["name"] == "test_app"
    assert data["package"]["entrypoint"] == "app.doom"


def test_add_dependency(tmp_path):
    init_manifest(tmp_path, name="my_app")
    add_dependency(tmp_path, "github:user/doom-tools", is_python=False)

    data = read_manifest(tmp_path)
    deps = data.get("dependencies", {})
    assert any("doom-tools" in k or "doom-tools" in str(v) for k, v in deps.items())


def test_cli_pkg_init_and_add(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    res_init = runner.invoke(app, ["init", "--name", "cli_project"])
    assert res_init.exit_code == 0
    assert (tmp_path / "doom.toml").exists()

    res_add = runner.invoke(app, ["add", "sample-lib"])
    assert res_add.exit_code == 0
    content = (tmp_path / "doom.toml").read_text(encoding="utf-8")
    assert "sample-lib" in content
