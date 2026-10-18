"""
DoomScript Standalone Packager (Phase 25)
Bundles a .doom script and the entire DoomScript runtime into a self-contained .pyz zipapp.
Executable anywhere with standard Python 3.10+ without installing DoomScript!
"""

import os
import shutil
import zipapp
from pathlib import Path
from rich.console import Console

from doomscript.compiler.engine import transpile

console = Console()

def pack_script(source_doom: Path, output_pyz: Path) -> Path:
    console.print(f"[bold cyan]Packaging '{source_doom.name}' into standalone bundle...[/bold cyan]")
    
    with open(source_doom, "r", encoding="utf-8") as f:
        doom_source = f.read()

    transpiled_py = transpile(doom_source)

    staging_dir = output_pyz.parent / f"_pack_staging_{source_doom.stem}"
    if staging_dir.exists():
        shutil.rmtree(staging_dir)
    staging_dir.mkdir(parents=True)

    # 1. Copy the doomscript runtime package
    src_doomscript = Path(__file__).parent
    shutil.copytree(src_doomscript, staging_dir / "doomscript", ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))

    # 2. Write __main__.py to staging directory
    main_py_content = f"""# Auto-generated DoomScript Standalone Executable Bundle
import sys
from doomscript import runtime

# Execute the pre-transpiled Python AST code directly
exec_globals = {{}}
for name, obj in vars(runtime).items():
    if not name.startswith("_"):
        exec_globals[name] = obj

compiled = compile({repr(transpiled_py)}, "<doom-app>", "exec")
exec(compiled, exec_globals)
"""
    with open(staging_dir / "__main__.py", "w", encoding="utf-8") as f:
        f.write(main_py_content)

    # 3. Create zipapp
    output_pyz.parent.mkdir(parents=True, exist_ok=True)
    zipapp.create_archive(
        source=staging_dir,
        target=output_pyz,
        interpreter="/usr/bin/env python3"
    )

    # Clean up staging
    shutil.rmtree(staging_dir)

    size_kb = output_pyz.stat().st_size / 1024
    console.print(f"[bold green]Successfully packed standalone bundle:[/bold green] {output_pyz} ({size_kb:.1f} KB)")
    return output_pyz
