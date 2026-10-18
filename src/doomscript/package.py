"""
DoomScript Package Management & Project Manifest Engine
Manages doom.toml, project dependencies, and PyPI bridge.
"""

from pathlib import Path
import subprocess
import sys
import os
from typing import Dict, Any, Optional

try:
    import tomllib  # Python 3.11+ standard library
except ImportError:
    try:
        import tomli as tomllib
    except ImportError:
        tomllib = None


def generate_manifest_content(name: str, version: str = "0.1.0", entrypoint: str = "main.doom") -> str:
    """Generates standard doom.toml manifest text."""
    return f"""[package]
name = "{name}"
version = "{version}"
description = "A DoomScript automation project"
entrypoint = "{entrypoint}"

[dependencies]
# doom-http = "github:doomscript/doom-http"

[python_dependencies]
# requests = ">=2.28"
"""


def init_manifest(project_dir: Path, name: Optional[str] = None, entrypoint: str = "main.doom") -> Path:
    """Initializes a new doom.toml manifest in project_dir."""
    project_dir = Path(project_dir)
    project_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = project_dir / "doom.toml"
    if manifest_path.exists():
        raise FileExistsError(f"Manifest 'doom.toml' already exists in {project_dir}")

    pkg_name = name or project_dir.resolve().name
    manifest_path.write_text(generate_manifest_content(pkg_name, entrypoint=entrypoint), encoding="utf-8")
    return manifest_path


def read_manifest(project_dir: Path) -> Dict[str, Any]:
    """Reads and parses doom.toml using standard library tomllib."""
    manifest_path = Path(project_dir) / "doom.toml"
    if not manifest_path.exists():
        raise FileNotFoundError(f"No 'doom.toml' found in {project_dir}")

    text = manifest_path.read_text(encoding="utf-8")
    if tomllib:
        return tomllib.loads(text)

    # Minimal fallback parser if tomllib is unavailable
    data = {"package": {}, "dependencies": {}, "python_dependencies": {}}
    curr_section = None
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("[") and line.endswith("]"):
            curr_section = line[1:-1].strip()
            data.setdefault(curr_section, {})
        elif "=" in line and curr_section:
            k, v = line.split("=", 1)
            data[curr_section][k.strip()] = v.strip().strip('"\'')
    return data


def add_dependency(project_dir: Path, package_spec: str, is_python: bool = False):
    """Adds a dependency to doom.toml."""
    manifest_path = Path(project_dir) / "doom.toml"
    if not manifest_path.exists():
        init_manifest(project_dir)

    text = manifest_path.read_text(encoding="utf-8")
    section = "[python_dependencies]" if is_python else "[dependencies]"

    short_name = package_spec.split("/")[-1].split(":")[-1].split("==")[0].split(">=")[0].split("<=")[0].strip()
    pkg_entry = f'{short_name} = "{package_spec}"\n'

    if section in text:
        text = text.replace(section, f"{section}\n{pkg_entry}", 1)
    else:
        text += f"\n{section}\n{pkg_entry}\n"

    manifest_path.write_text(text, encoding="utf-8")

    if is_python:
        # Install via pip
        subprocess.run([sys.executable, "-m", "pip", "install", package_spec], check=True, capture_output=True)


def install_dependencies(project_dir: Path) -> Dict[str, Any]:
    """Installs all dependencies declared in doom.toml."""
    manifest = read_manifest(project_dir)
    py_deps = manifest.get("python_dependencies", {})
    installed_py = []
    for pkg, spec in py_deps.items():
        arg = spec if any(op in spec for op in ("=", ">", "<")) else f"{pkg}=={spec}"
        res = subprocess.run([sys.executable, "-m", "pip", "install", arg], capture_output=True, text=True)
        if res.returncode == 0:
            installed_py.append(pkg)

    return {
        "python_installed": installed_py,
        "doom_dependencies": list(manifest.get("dependencies", {}).keys())
    }
