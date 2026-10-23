"""
DoomScript CLI
Provides commands: doom run, doom transpile, doom check, doom explain, doom suggest, doom fmt, doom new, doom repl.
"""

from pathlib import Path
from typing import Optional
import sys
import traceback
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.syntax import Syntax

from doomscript.compiler.engine import compile_to_ast, transpile, export_to_python, execute
from doomscript.errors import format_syntax_error, find_closest_phrasings, translate_runtime_error
from doomscript.explainer import explain_source
from doomscript.formatter import format_code
from lark.exceptions import UnexpectedToken, UnexpectedCharacters, VisitError
from doomscript.exceptions import DoomError, DoomIndentationError

app = typer.Typer(
    name="doom",
    help="DoomScript: The English-first programming language for mortals.",
    add_completion=False
)
console = Console()


def handle_cli_error(file_path: str, source: str, err: Exception, theatrical: bool = False):
    """Formats and prints syntax or runtime error in plain English with caret and suggestions."""
    if isinstance(err, (UnexpectedToken, UnexpectedCharacters, VisitError, DoomError)):
        msg = format_syntax_error(source, err, file_path=file_path, theatrical=theatrical)
        console.print(msg)
    else:
        # Runtime error: inspect traceback for line in source
        tb = err.__traceback__
        matched_lineno = None
        while tb:
            frame = tb.tb_frame
            fn = frame.f_code.co_filename
            if fn in ("<doom>", file_path):
                matched_lineno = tb.tb_lineno
            tb = tb.tb_next

        lines = source.splitlines()
        console.print(Panel(f"[bold red]DoomScript Runtime Error[/bold red] in [yellow]{file_path}[/yellow]", border_style="red"))
        if matched_lineno and 1 <= matched_lineno <= len(lines):
            line_text = lines[matched_lineno - 1]
            prefix = f"{matched_lineno:4d} | "
            console.print(f"[bold red]{prefix}{line_text}[/bold red]")
            console.print(" " * len(prefix) + "[bold red]^[/bold red]")
        plain_msg = translate_runtime_error(err)
        console.print(f"\n[bold white]Problem:[/bold white] {plain_msg}")


@app.command()
def run(
    file: Path = typer.Argument(..., help="Path to .doom script"),
    theatrical: bool = typer.Option(False, "--theatrical", help="Enable villain-voice errors")
):
    """Run a DoomScript file directly."""
    if not file.exists():
        console.print(f"[bold red]Error:[/bold red] File '{file}' not found.")
        raise typer.Exit(code=1)

    with open(file, "r", encoding="utf-8") as f:
        source = f.read()

    try:
        execute(source, filename=str(file))
    except Exception as e:
        handle_cli_error(str(file), source, e, theatrical=theatrical)
        raise typer.Exit(code=1)


@app.command("transpile")
def transpile_cmd(
    file: Path = typer.Argument(..., help="Path to .doom script"),
    output: Path = typer.Option(None, "--output", "-o", help="Optional output .py file path")
):
    """Transpile a DoomScript file to standard Python code."""
    if not file.exists():
        console.print(f"[bold red]Error:[/bold red] File '{file}' not found.")
        raise typer.Exit(code=1)

    with open(file, "r", encoding="utf-8") as f:
        source = f.read()

    try:
        py_code = transpile(source)
        if output:
            with open(output, "w", encoding="utf-8") as out_f:
                out_f.write(py_code + "\n")
            console.print(f"[green]Successfully transpiled to[/green] [bold]{output}[/bold]")
        else:
            syntax = Syntax(py_code, "python", theme="monokai", line_numbers=True)
            console.print(Panel(syntax, title="Transpiled Python", border_style="cyan"))
    except Exception as e:
        handle_cli_error(str(file), source, e)
        raise typer.Exit(code=1)


@app.command("export")
def export_cmd(
    file: Path = typer.Argument(..., help="Path to .doom script"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Target .py file path")
):
    """Export a DoomScript file to a standalone, runnable Python script."""
    if not file.exists():
        console.print(f"[bold red]Error:[/bold red] File '{file}' not found.")
        raise typer.Exit(code=1)

    target_path = output if output is not None else file.with_suffix(".py")

    with open(file, "r", encoding="utf-8") as f:
        source = f.read()

    try:
        py_code = export_to_python(source)
        with open(target_path, "w", encoding="utf-8") as out_f:
            out_f.write(py_code)
        console.print(f"[green]Successfully exported standalone script to[/green] [bold]{target_path}[/bold]")
    except Exception as e:
        handle_cli_error(str(file), source, e)
        raise typer.Exit(code=1)


@app.command()
def check(
    file: Path = typer.Argument(..., help="Path to .doom script"),
    theatrical: bool = typer.Option(False, "--theatrical", help="Enable villain-voice errors"),
    strict: bool = typer.Option(False, "--strict", help="Enable strict static contract and type checking")
):
    """Check syntax of a DoomScript file."""
    if not file.exists():
        console.print(f"[bold red]Error:[/bold red] File '{file}' not found.")
        raise typer.Exit(code=1)

    with open(file, "r", encoding="utf-8") as f:
        source = f.read()

    try:
        compile_to_ast(source)
        if strict:
            from doomscript.contracts import analyze_contracts
            violations = analyze_contracts(source)
            if violations:
                for v in violations:
                    console.print(f"[bold red]Strict Error (Line {v.line}):[/bold red] {v.message}")
                raise typer.Exit(code=1)
            console.print(f"[bold green][OK] Strict Type & Contract Checks Passed:[/bold green] [dim]{file}[/dim]")
        else:
            console.print(f"[bold green][OK] Syntax Valid:[/bold green] [dim]{file}[/dim]")
    except typer.Exit:
        raise
    except Exception as e:
        handle_cli_error(str(file), source, e, theatrical=theatrical)
        raise typer.Exit(code=1)


@app.command()
def explain(file: Path = typer.Argument(..., help="Path to .doom script")):
    """Print each DoomScript line with the exact Python it becomes and a plain English explanation."""
    if not file.exists():
        console.print(f"[bold red]Error:[/bold red] File '{file}' not found.")
        raise typer.Exit(code=1)

    with open(file, "r", encoding="utf-8") as f:
        source = f.read()

    items = explain_source(source)

    table = Table(title=f"DoomScript Explanation: {file.name}", border_style="cyan", show_lines=True)
    table.add_column("Line", justify="right", style="dim", width=6)
    table.add_column("DoomScript", style="bold green", width=36)
    table.add_column("Transpiled Python", style="cyan", width=36)
    table.add_column("Plain English Meaning", style="white")

    for item in items:
        if not item["is_code"]:
            continue
        table.add_row(
            str(item["line_no"]),
            item["doom"].strip(),
            item["python"],
            item["explanation"]
        )

    console.print(table)


@app.command()
def suggest(
    sentence: str = typer.Argument(..., help="Sentence to test or find closest supported phrasings for"),
    theatrical: bool = typer.Option(False, "--theatrical", help="Enable villain-voice suggestions")
):
    """Test a sentence or suggest closest supported DoomScript phrasings if it fails."""
    try:
        py_ast = compile_to_ast(sentence)
        py_code = transpile(sentence)
        console.print("[bold green][VALID DOOMSCRIPT][/bold green]")
        console.print(f"[bold white]Sentence:[/bold white] \"{sentence}\"")
        console.print(f"[bold cyan]Transpiles to:[/bold cyan] `{py_code}`")
    except Exception as e:
        if theatrical:
            console.print("[bold red]FOOLISH MORTAL! That sentence is an abomination to the compiler![/bold red]")
        else:
            console.print(f"[bold red]Sentence not understood:[/bold red] \"{sentence}\"")

        closest = find_closest_phrasings(sentence, n=3, cutoff=0.3)
        if not closest:
            closest = [
                'say "Hello, world!"',
                'set score to 100',
                'repeat 5 times:'
            ]
        if closest:
            console.print("\n[bold green]Supported phrasings you can use:[/bold green]")
            for match in closest:
                console.print(f"  * [bold cyan]{match}[/bold cyan]")
        else:
            console.print("\n[dim]No close match found in common templates. Try simpler subject-verb-object phrasing.[/dim]")


@app.command()
def fmt(
    file: Path = typer.Argument(..., help="Path to .doom script"),
    write: bool = typer.Option(False, "--write", "-w", help="Overwrite file in-place with formatted output")
):
    """Format a DoomScript file to canonical style (4-space indent, canonical verbs, cleaned fillers)."""
    if not file.exists():
        console.print(f"[bold red]Error:[/bold red] File '{file}' not found.")
        raise typer.Exit(code=1)

    with open(file, "r", encoding="utf-8") as f:
        source = f.read()

    try:
        formatted = format_code(source)
    except DoomIndentationError as e:
        console.print(f"[bold red]Indentation Error:[/bold red] {e}")
        raise typer.Exit(code=1)

    if write:
        with open(file, "w", encoding="utf-8") as f:
            f.write(formatted)
        console.print(f"[bold green]Formatted and updated:[/bold green] [cyan]{file}[/cyan]")
    else:
        console.print(formatted, end="")


@app.command()
def new(project_name: str = typer.Argument(..., help="Name of the new DoomScript project directory")):
    """Create a new starter DoomScript project with idiomatic examples."""
    target_dir = Path(project_name)
    if target_dir.exists():
        console.print(f"[bold red]Error:[/bold red] Directory '{project_name}' already exists.")
        raise typer.Exit(code=1)

    target_dir.mkdir(parents=True)
    data_dir = target_dir / "data"
    data_dir.mkdir()

    # Create sample.csv
    sample_csv = data_dir / "sales.csv"
    sample_csv.write_text(
        "item,price,quantity\nWidget,15,4\nGadget,30,2\nDoomHelm,150,1\n",
        encoding="utf-8"
    )

    # Create main.doom
    main_doom = target_dir / "main.doom"
    main_code = """# Welcome to DoomScript!
# The English-first programming language for everyday automation.

say "=== DoomScript Sales Summary ==="

# Read CSV data
read csv file "data/sales.csv" into orders

# Compute metrics
order_count is the count of orders
say "Loaded {order_count} orders."

for each order in orders
    total_price = order.price * order.quantity
    say "Order item:", order.item, "Total:", total_price

say "Done! Happy English scripting."
"""
    main_doom.write_text(main_code, encoding="utf-8")

    # Create README.md
    readme = target_dir / "README.md"
    readme.write_text(
        f"# {project_name}\n\nA DoomScript automation project.\n\n## Running\n```bash\ndoom run main.doom\n```\n",
        encoding="utf-8"
    )

    console.print(Panel(
        f"[bold green]Project '{project_name}' created successfully![/bold green]\n\n"
        f"  1. [cyan]cd {project_name}[/cyan]\n"
        f"  2. [cyan]doom run main.doom[/cyan]\n"
        f"  3. [cyan]doom explain main.doom[/cyan]",
        border_style="green"
    ))


@app.command()
def build(
    file: Path = typer.Argument(..., help="Path to .doom script"),
    output: Path = typer.Option(None, "--output", "-o", help="Optional output executable name or path"),
    onefile: bool = typer.Option(True, "--onefile/--dir", help="Create a single-file executable")
):
    """Compile a DoomScript file into a standalone native executable (.exe)."""
    import subprocess

    if not file.exists():
        console.print(f"[bold red]Error:[/bold red] File '{file}' not found.")
        raise typer.Exit(code=1)

    with open(file, "r", encoding="utf-8") as f:
        source = f.read()

    try:
        console.print(f"[bold cyan]Transpiling[/bold cyan] [yellow]{file}[/yellow]...")
        py_code = transpile(source)

        bundled_code = f'''# Standalone DoomScript Executable
from doomscript.runtime import *

{py_code}
'''
        build_dir = Path("build_cache")
        build_dir.mkdir(exist_ok=True)
        temp_py = build_dir / f"{file.stem}_runner.py"
        with open(temp_py, "w", encoding="utf-8") as tf:
            tf.write(bundled_code)

        console.print("[bold cyan]Compiling standalone binary with PyInstaller...[/bold cyan]")
        out_stem = output.stem if output else file.stem
        cmd = [
            sys.executable, "-m", "PyInstaller",
            "--noconfirm",
            "--clean",
            "--name", out_stem,
            str(temp_py)
        ]
        if onefile:
            cmd.append("--onefile")

        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode != 0:
            console.print(f"[bold red]Build error:[/bold red]\n{res.stderr}")
            raise typer.Exit(code=1)

        dist_path = Path("dist") / (f"{out_stem}.exe" if sys.platform == "win32" else out_stem)
        console.print(Panel(f"[bold green]Standalone binary built successfully![/bold green]\nExecutable: [cyan]{dist_path}[/cyan]", border_style="green"))
    except Exception as e:
        handle_cli_error(str(file), source, e)
        raise typer.Exit(code=1)


@app.command()
def repl():
    """Start an interactive real-time DoomScript shell (REPL) with multi-line block buffering."""
    from doomscript.kernel import is_block_continuation_needed
    console.print(Panel("[bold red]DOOMSCRIPT REPL v0.6.0[/bold red]\n[dim]The English-first programming shell. Type 'exit' or 'quit' to close.[/dim]", border_style="red"))

    session_env = {}
    while True:
        try:
            line = console.input("[bold red]DOOM>[/bold red] ")
            if not line.strip():
                continue
            if line.strip().lower() in ("exit", "quit"):
                console.print("[dim]Exiting DoomScript.[/dim]")
                break

            buffer = [line]
            while is_block_continuation_needed("\n".join(buffer)):
                cont = console.input("[dim]... [/dim]")
                if not cont.strip():
                    break
                buffer.append(cont)

            full_code = "\n".join(buffer)
            try:
                execute(full_code, custom_globals=session_env)
            except Exception as first_e:
                from doomscript.exceptions import DoomScriptSyntaxError
                retried = False
                # Only retry as 'say <expr>' if it was a syntax error on a single expression
                if isinstance(first_e, DoomScriptSyntaxError) and not re.search(r"^\s*[A-Za-z_]\w*\s*=", full_code):
                    try:
                        execute(f"say {full_code}", custom_globals=session_env)
                        retried = True
                    except Exception:
                        pass
                if not retried:
                    handle_cli_error("<repl>", full_code, first_e)
        except (KeyboardInterrupt, EOFError):
            console.print("\n[dim]Session closed.[/dim]")
            break


@app.command()
def ide():
    """Launch DoomScript Studio - Professional Desktop IDE."""
    console.print(Panel("[bold red]DOOMSCRIPT STUDIO 2026.1[/bold red]\n[green]Launching Desktop IDE...[/green]", border_style="red"))
    from doomscript.ide.app import launch_ide
    launch_ide()


@app.command()
def idle():
    """Launch DoomScript Studio (IDLE) - Professional Desktop IDE."""
    ide()


@app.command()
def lsp():
    """Start the DoomScript Language Server (LSP) over stdio for IDE integration."""
    from doomscript.lsp.server import start_lsp_server
    start_lsp_server()


@app.command("init")
def pkg_init(name: str = typer.Option(None, "--name", "-n", help="Project name")):
    """Initialize a new doom.toml package manifest in the current directory."""
    from doomscript.package import init_manifest
    try:
        manifest_path = init_manifest(Path.cwd(), name=name)
        console.print(f"[bold green]Initialized manifest:[/bold green] [cyan]{manifest_path}[/cyan]")
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(code=1)


@app.command("add")
def pkg_add(
    package: str = typer.Argument(..., help="Package name or specifier"),
    python: bool = typer.Option(False, "--python", "-p", help="Add as external PyPI python dependency")
):
    """Add a dependency to doom.toml."""
    from doomscript.package import add_dependency
    try:
        add_dependency(Path.cwd(), package, is_python=python)
        console.print(f"[bold green]Added dependency:[/bold green] [cyan]{package}[/cyan]")
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(code=1)


@app.command("install")
def pkg_install():
    """Install all dependencies declared in doom.toml."""
    from doomscript.package import install_dependencies
    try:
        console.print("[bold cyan]Installing dependencies from doom.toml...[/bold cyan]")
        res = install_dependencies(Path.cwd())
        console.print(f"[bold green]Dependencies installed successfully![/bold green] Installed: {res['python_installed']}")
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(code=1)


@app.command("test")
def run_tests(
    path: Optional[Path] = typer.Argument(None, help="Path to test file or directory")
):
    """Run native DoomScript tests written with 'test' and 'expect'."""
    from doomscript.tester import run_doom_tests
    success = run_doom_tests(path)
    if not success:
        raise typer.Exit(code=1)


@app.command("doc")
def generate_docs(
    path: Optional[Path] = typer.Argument(None, help="Directory to inspect for .doom files"),
    output: Path = typer.Option(Path("docs/site/index.html"), "--output", "-o", help="Output HTML file path")
):
    """Generate static HTML API documentation from DoomScript source files (Phase 16)."""
    from doomscript.docgen import build_docs
    target_dir = path or Path.cwd()
    res = build_docs(target_dir, output)
    console.print(f"[bold green]Documentation generated successfully at:[/bold green] [cyan]{res}[/cyan]")


@app.command("watch")
def watch_daemon(
    file: Path = typer.Argument(..., help="Path to .doom file or directory to monitor"),
    action: str = typer.Option("run", "--action", "-a", help="Action to execute on change: 'run' or 'test'")
):
    """Watch a .doom file or directory and auto-reload on modification (Phase 18)."""
    from doomscript.watcher import watch_path
    watch_path(file, action=action)


@app.command("bench")
def benchmark_cmd(
    file: Path = typer.Argument(..., help="Path to .doom script to benchmark"),
    iterations: int = typer.Option(10, "--iterations", "-i", help="Number of benchmark iterations")
):
    """Benchmark script execution latency, throughput, and memory consumption (Phase 24)."""
    from doomscript.bench import benchmark_script
    benchmark_script(file, iterations=iterations)


@app.command("pack")
def pack_cmd(
    file: Path = typer.Argument(..., help="Path to .doom script to package"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output .pyz bundle path")
):
    """Package a .doom script and runtime into a zero-dependency standalone zipapp bundle (Phase 25)."""
    from doomscript.pack import pack_script
    out = output or file.with_suffix(".pyz")
    pack_script(file, out)


@app.command("playground")
def playground_cmd(
    port: int = typer.Option(8000, "--port", "-p", help="Port to serve the playground on"),
    no_browser: bool = typer.Option(False, "--no-browser", help="Do not open browser automatically")
):
    """Launch the interactive web playground in your browser."""
    from doomscript.playground import launch_playground
    launch_playground(port=port, open_browser=not no_browser)


if __name__ == "__main__":
    app()
