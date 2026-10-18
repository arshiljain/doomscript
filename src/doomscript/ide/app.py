"""
DoomScript Studio 2026.1 - Professional Desktop IDE
A JetBrains-inspired IDE tailored specifically for DoomScript.
"""

import os
import sys
import re
import sqlite3
import threading
import urllib.request
import json
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

import customtkinter as ctk

from doomscript.compiler.engine import transpile, compile_to_ast, execute
from doomscript.runtime import Record


class LineNumbers(tk.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.textwidget = None

    def attach(self, textwidget):
        self.textwidget = textwidget

    def redraw(self, *args):
        self.delete("all")
        if not self.textwidget:
            return

        i = self.textwidget.index("@0,0")
        while True:
            dline = self.textwidget.dlineinfo(i)
            if dline is None:
                break
            y = dline[1]
            linenum = str(i).split(".")[0]
            self.create_text(
                32, y,
                anchor="ne",
                text=linenum,
                font=("JetBrains Mono", 10),
                fill="#5A5D63"
            )
            i = self.textwidget.index(f"{i}+1line")


class DoomScriptStudio(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("DoomScript Studio 2026.1 - Professional Edition")
        self.geometry("1280x820")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.current_file = None
        self.workspace_dir = Path.cwd()
        self.repl_env = {}

        self._init_theme_colors()
        self._build_header_toolbar()
        self._build_main_split_layout()
        self._build_status_bar()

        # Load initial example if available
        initial_sample = self.workspace_dir / "examples" / "doom_citadel_server.doom"
        if initial_sample.exists():
            self.open_file_path(initial_sample)
        else:
            self._set_default_editor_content()

    def _init_theme_colors(self):
        self.c_bg = "#1E1F22"
        self.c_sidebar = "#2B2D30"
        self.c_header = "#26282B"
        self.c_accent = "#3574F0"
        self.c_text = "#BCBEC4"
        self.c_comment = "#7A7E85"
        self.c_keyword = "#CF8E6D"
        self.c_verb = "#C792EA"
        self.c_string = "#6AAB73"
        self.c_number = "#2AACB8"

    def _build_header_toolbar(self):
        self.toolbar = ctk.CTkFrame(self, height=48, fg_color=self.c_header, corner_radius=0)
        self.toolbar.pack(side="top", fill="x")

        # Brand / Title
        logo_lbl = ctk.CTkLabel(
            self.toolbar,
            text="⚡ DOOMSCRIPT STUDIO",
            font=("Segoe UI", 13, "bold"),
            text_color="#FF4757"
        )
        logo_lbl.pack(side="left", padx=(16, 12), pady=8)

        pro_badge = ctk.CTkLabel(
            self.toolbar,
            text="PRO",
            font=("Segoe UI", 9, "bold"),
            fg_color="#3574F0",
            text_color="white",
            corner_radius=4,
            width=36,
            height=18
        )
        pro_badge.pack(side="left", padx=(0, 20), pady=12)

        # File actions
        ctk.CTkButton(
            self.toolbar, text="New", width=60, height=28, fg_color="#3E4247",
            hover_color="#4E5257", command=self.action_new_file
        ).pack(side="left", padx=4)

        ctk.CTkButton(
            self.toolbar, text="Open", width=60, height=28, fg_color="#3E4247",
            hover_color="#4E5257", command=self.action_open_file_dialog
        ).pack(side="left", padx=4)

        ctk.CTkButton(
            self.toolbar, text="Save", width=60, height=28, fg_color="#3E4247",
            hover_color="#4E5257", command=self.action_save_file
        ).pack(side="left", padx=4)

        # Run Widgets
        self.run_btn = ctk.CTkButton(
            self.toolbar,
            text="▶  Run",
            width=80,
            height=28,
            fg_color="#368244",
            hover_color="#2E6D38",
            command=self.action_run_script
        )
        self.run_btn.pack(side="left", padx=(20, 6))

        self.transpile_btn = ctk.CTkButton(
            self.toolbar,
            text="⚡  Transpile",
            width=90,
            height=28,
            fg_color="#3574F0",
            hover_color="#2758BA",
            command=self.action_transpile
        )
        self.transpile_btn.pack(side="left", padx=6)

        self.check_btn = ctk.CTkButton(
            self.toolbar,
            text="🔍  Check",
            width=70,
            height=28,
            fg_color="#8F6B20",
            hover_color="#7A5A18",
            command=self.action_check_syntax
        )
        self.check_btn.pack(side="left", padx=6)

        self.build_btn = ctk.CTkButton(
            self.toolbar,
            text="📦  Build EXE",
            width=90,
            height=28,
            fg_color="#A33B3B",
            hover_color="#872E2E",
            command=self.action_build_exe
        )
        self.build_btn.pack(side="left", padx=6)

        # Current file label
        self.file_title_lbl = ctk.CTkLabel(
            self.toolbar,
            text="[No File]",
            font=("Segoe UI", 11, "italic"),
            text_color="#9AA0A6"
        )
        self.file_title_lbl.pack(side="right", padx=16)

    def _build_main_split_layout(self):
        self.main_container = ctk.CTkFrame(self, fg_color=self.c_bg, corner_radius=0)
        self.main_container.pack(fill="both", expand=True)

        # Left Tool Windows (Tabs: Project, Database, Web Tester)
        self.left_sidebar = ctk.CTkTabview(
            self.main_container,
            width=280,
            fg_color=self.c_sidebar,
            segmented_button_fg_color="#1E1F22",
            segmented_button_selected_color="#3574F0"
        )
        self.left_sidebar.pack(side="left", fill="y", padx=(0, 2), pady=0)

        self.tab_files = self.left_sidebar.add("Project")
        self.tab_db = self.left_sidebar.add("Database")
        self.tab_http = self.left_sidebar.add("HTTP Client")

        self._build_project_tree()
        self._build_db_explorer()
        self._build_http_client()

        # Right / Center Area (Editor + Bottom Tool Windows)
        self.center_split = tk.PanedWindow(
            self.main_container,
            orient=tk.VERTICAL,
            bg=self.c_sidebar,
            sashrelief=tk.FLAT,
            sashwidth=4
        )
        self.center_split.pack(side="right", fill="both", expand=True)

        # Editor Area
        self._build_editor_area()

        # Bottom Tool Windows (Run, Transpiled, REPL)
        self._build_bottom_tool_windows()

        self.center_split.add(self.editor_frame, minsize=300)
        self.center_split.add(self.bottom_tabs, minsize=180)

    def _build_project_tree(self):
        lbl = ctk.CTkLabel(self.tab_files, text="Project Explorer", font=("Segoe UI", 11, "bold"))
        lbl.pack(anchor="w", padx=6, pady=4)

        self.file_listbox = tk.Listbox(
            self.tab_files,
            bg=self.c_bg,
            fg=self.c_text,
            selectbackground=self.c_accent,
            selectforeground="white",
            relief=tk.FLAT,
            font=("Segoe UI", 10),
            highlightthickness=0
        )
        self.file_listbox.pack(fill="both", expand=True, padx=4, pady=4)
        self.file_listbox.bind("<Double-Button-1>", self._on_file_select)

        self._refresh_project_files()

    def _refresh_project_files(self):
        self.file_listbox.delete(0, tk.END)
        self.discovered_files = []
        for p in sorted(self.workspace_dir.rglob("*.doom")):
            rel = p.relative_to(self.workspace_dir)
            self.discovered_files.append(p)
            self.file_listbox.insert(tk.END, f"  📄 {rel}")

    def _on_file_select(self, event):
        sel = self.file_listbox.curselection()
        if sel:
            idx = sel[0]
            if idx < len(self.discovered_files):
                self.open_file_path(self.discovered_files[idx])

    def _build_db_explorer(self):
        # Database Tool Window (PyCharm Pro style)
        ctk.CTkLabel(self.tab_db, text="SQLite Database Explorer", font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=6, pady=4)

        refresh_btn = ctk.CTkButton(
            self.tab_db, text="🔄 Refresh DBs", height=24, fg_color="#3E4247", command=self._refresh_databases
        )
        refresh_btn.pack(fill="x", padx=6, pady=4)

        self.db_dropdown = ctk.CTkOptionMenu(self.tab_db, values=["(No .db found)"], command=self._on_db_selected)
        self.db_dropdown.pack(fill="x", padx=6, pady=4)

        self.table_listbox = tk.Listbox(
            self.tab_db,
            bg=self.c_bg,
            fg=self.c_text,
            selectbackground=self.c_accent,
            font=("Segoe UI", 10),
            relief=tk.FLAT,
            height=6
        )
        self.table_listbox.pack(fill="x", padx=6, pady=4)
        self.table_listbox.bind("<Double-Button-1>", self._view_table_data)

        # Table rows display
        self.db_output = tk.Text(
            self.tab_db,
            bg=self.c_bg,
            fg="#6AAB73",
            font=("JetBrains Mono", 9),
            relief=tk.FLAT
        )
        self.db_output.pack(fill="both", expand=True, padx=6, pady=4)

        self._refresh_databases()

    def _refresh_databases(self):
        dbs = list(self.workspace_dir.rglob("*.db"))
        vals = [str(d.relative_to(self.workspace_dir)) for d in dbs] or ["(No .db found)"]
        self.db_dropdown.configure(values=vals)
        if dbs:
            self.db_dropdown.set(vals[0])
            self._on_db_selected(vals[0])

    def _on_db_selected(self, val):
        self.table_listbox.delete(0, tk.END)
        p = self.workspace_dir / val
        if not p.exists() or not p.is_file():
            return
        try:
            conn = sqlite3.connect(str(p))
            cur = conn.cursor()
            cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [row[0] for row in cur.fetchall()]
            conn.close()
            for t in tables:
                self.table_listbox.insert(tk.END, f"  📊 {t}")
        except Exception:
            pass

    def _view_table_data(self, event):
        sel = self.table_listbox.curselection()
        if not sel:
            return
        t_name = self.table_listbox.get(sel[0]).replace("📊", "").strip()
        db_rel = self.db_dropdown.get()
        p = self.workspace_dir / db_rel
        try:
            conn = sqlite3.connect(str(p))
            cur = conn.cursor()
            cur.execute(f'SELECT * FROM "{t_name}" LIMIT 20')
            rows = cur.fetchall()
            col_names = [desc[0] for desc in cur.description] if cur.description else []
            conn.close()

            self.db_output.delete("1.0", tk.END)
            self.db_output.insert(tk.END, f"Table: {t_name}\n")
            self.db_output.insert(tk.END, " | ".join(col_names) + "\n" + ("-" * 30) + "\n")
            for r in rows:
                self.db_output.insert(tk.END, " | ".join(str(c) for c in r) + "\n")
        except Exception as e:
            self.db_output.delete("1.0", tk.END)
            self.db_output.insert(tk.END, f"Error reading table: {e}\n")

    def _build_http_client(self):
        # HTTP / Endpoints Tester (PyCharm Pro style)
        ctk.CTkLabel(self.tab_http, text="HTTP / REST Client", font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=6, pady=4)

        row = ctk.CTkFrame(self.tab_http, fg_color="transparent")
        row.pack(fill="x", padx=6, pady=4)

        self.http_method = ctk.CTkOptionMenu(row, values=["GET", "POST", "PUT", "DELETE"], width=70)
        self.http_method.pack(side="left", padx=(0, 4))
        self.http_url = ctk.CTkEntry(row, placeholder_text="http://localhost:8088/api/status")
        self.http_url.pack(side="left", fill="x", expand=True)

        ctk.CTkButton(
            self.tab_http, text="Send Request", fg_color="#3574F0", height=28, command=self._send_http_request
        ).pack(fill="x", padx=6, pady=4)

        self.http_response = tk.Text(
            self.tab_http, bg=self.c_bg, fg=self.c_text, font=("JetBrains Mono", 9), relief=tk.FLAT
        )
        self.http_response.pack(fill="both", expand=True, padx=6, pady=4)

    def _send_http_request(self):
        url = self.http_url.get().strip() or "http://localhost:8088/api/status"
        method = self.http_method.get()

        def req_worker():
            try:
                req = urllib.request.Request(url, method=method, headers={"User-Agent": "DoomScriptStudio/1.0"})
                with urllib.request.urlopen(req, timeout=5) as resp:
                    status = resp.status
                    body = resp.read().decode("utf-8")
                    try:
                        formatted = json.dumps(json.loads(body), indent=2)
                    except Exception:
                        formatted = body

                    out = f"Status: {status} OK\n\n{formatted}"
            except Exception as e:
                out = f"Connection Error:\n{e}"

            self.after(0, lambda: self._update_http_output(out))

        threading.Thread(target=req_worker, daemon=True).start()

    def _update_http_output(self, text):
        self.http_response.delete("1.0", tk.END)
        self.http_response.insert(tk.END, text)

    def _build_editor_area(self):
        self.editor_frame = ctk.CTkFrame(self.center_split, fg_color=self.c_bg, corner_radius=0)

        # Tab bar
        self.editor_tab_bar = ctk.CTkFrame(self.editor_frame, height=28, fg_color="#2B2D30", corner_radius=0)
        self.editor_tab_bar.pack(fill="x")

        self.tab_title = ctk.CTkLabel(
            self.editor_tab_bar, text="  main.doom  ✕", font=("Segoe UI", 10, "bold"), text_color="#FFFFFF"
        )
        self.tab_title.pack(side="left", padx=8, pady=4)

        # Text container with line numbers
        text_container = tk.Frame(self.editor_frame, bg=self.c_bg)
        text_container.pack(fill="both", expand=True)

        self.line_numbers = LineNumbers(text_container, width=40, bg=self.c_bg, highlightthickness=0)
        self.line_numbers.pack(side="left", fill="y")

        self.editor = tk.Text(
            text_container,
            bg=self.c_bg,
            fg=self.c_text,
            insertbackground="white",
            font=("JetBrains Mono", 11),
            relief=tk.FLAT,
            undo=True,
            wrap="none",
            highlightthickness=0
        )
        self.editor.pack(side="left", fill="both", expand=True)

        scrollbar_y = ttk.Scrollbar(text_container, orient=tk.VERTICAL, command=self._on_scroll)
        scrollbar_y.pack(side="right", fill="y")
        self.editor.configure(yscrollcommand=scrollbar_y.set)

        self.line_numbers.attach(self.editor)

        # Bindings
        self.editor.bind("<KeyRelease>", self._on_editor_key)
        self.editor.bind("<MouseWheel>", lambda e: self.after(10, self.line_numbers.redraw))

        self._configure_syntax_tags()

    def _configure_syntax_tags(self):
        self.editor.tag_configure("comment", foreground="#7A7E85", font=("JetBrains Mono", 11, "italic"))
        self.editor.tag_configure("string", foreground="#6AAB73")
        self.editor.tag_configure("keyword", foreground="#CF8E6D", font=("JetBrains Mono", 11, "bold"))
        self.editor.tag_configure("verb", foreground="#C792EA", font=("JetBrains Mono", 11, "bold"))
        self.editor.tag_configure("number", foreground="#2AACB8")
        self.editor.tag_configure("possessive", foreground="#E5C07B")

    def _on_scroll(self, *args):
        self.editor.yview(*args)
        self.line_numbers.redraw()

    def _on_editor_key(self, event=None):
        self.line_numbers.redraw()
        self._highlight_syntax()

    def _highlight_syntax(self):
        content = self.editor.get("1.0", tk.END)

        for tag in ["comment", "string", "keyword", "verb", "number", "possessive"]:
            self.editor.tag_remove(tag, "1.0", tk.END)

        # Highlight Strings
        for match in re.finditer(r'(".*?"|\'.*?\')', content):
            start = f"1.0 + {match.start()} chars"
            end = f"1.0 + {match.end()} chars"
            self.editor.tag_add("string", start, end)

        # Highlight Comments
        for match in re.finditer(r'#.*$', content, re.MULTILINE):
            start = f"1.0 + {match.start()} chars"
            end = f"1.0 + {match.end()} chars"
            self.editor.tag_add("comment", start, end)

        # Highlight Keywords
        kw_pattern = r'\b(if|else|repeat while|repeat until|repeat|times|time|for each|in|return|stop|attempt|if it fails|to|with|and|or|not|otherwise|verify that|verify|true|false|nothing|none)\b'
        for match in re.finditer(kw_pattern, content):
            start = f"1.0 + {match.start()} chars"
            end = f"1.0 + {match.end()} chars"
            self.editor.tag_add("keyword", start, end)

        # Highlight Verbs
        verb_pattern = r'\b(say|set|increase|decrease|by|to|ask choice|ask|into|write|read|append|copy file|delete file|create directory|list files in|check if file|file|exists|replace|split|join|convert|to uppercase|to lowercase|capitalize|trim|spawn|wait for|route|start server|stop server|display colored|pause|round|decimals|clamp|roll|between|pick random from|shuffle|save record|into database|table|load records from database|sum of|average of|highest in|lowest in|first item of|last item of|beep|play sound|open window|draw circle|draw rectangle|draw text|clear screen|refresh screen|add|remove|from|wait|call|count of)\b'
        for match in re.finditer(verb_pattern, content):
            start = f"1.0 + {match.start()} chars"
            end = f"1.0 + {match.end()} chars"
            self.editor.tag_add("verb", start, end)

        # Highlight Numbers
        for match in re.finditer(r'\b\d+(\.\d+)?%?\b', content):
            start = f"1.0 + {match.start()} chars"
            end = f"1.0 + {match.end()} chars"
            self.editor.tag_add("number", start, end)

        # Possessives
        for match in re.finditer(r"(\w+)('s)\b", content):
            start = f"1.0 + {match.start(2)} chars"
            end = f"1.0 + {match.end(2)} chars"
            self.editor.tag_add("possessive", start, end)

    def _build_bottom_tool_windows(self):
        self.bottom_tabs = ctk.CTkTabview(
            self.center_split,
            fg_color="#1E1F22",
            segmented_button_fg_color="#2B2D30",
            segmented_button_selected_color="#3574F0",
            height=200
        )

        self.tab_run = self.bottom_tabs.add("Console (Run)")
        self.tab_transpiled = self.bottom_tabs.add("Transpiled Python")
        self.tab_repl = self.bottom_tabs.add("Terminal REPL")

        # Run output console
        self.console_output = tk.Text(
            self.tab_run, bg="#18181A", fg="#BCBEC4", font=("JetBrains Mono", 10), relief=tk.FLAT
        )
        self.console_output.pack(fill="both", expand=True)

        # Transpiled output
        self.transpiled_output = tk.Text(
            self.tab_transpiled, bg="#18181A", fg="#6AAB73", font=("JetBrains Mono", 10), relief=tk.FLAT
        )
        self.transpiled_output.pack(fill="both", expand=True)

        # Interactive REPL Tab
        repl_frame = ctk.CTkFrame(self.tab_repl, fg_color="transparent")
        repl_frame.pack(fill="both", expand=True)

        self.repl_history = tk.Text(
            repl_frame, bg="#18181A", fg="#BCBEC4", font=("JetBrains Mono", 10), relief=tk.FLAT, height=8
        )
        self.repl_history.pack(fill="both", expand=True)
        self.repl_history.insert(tk.END, "DOOMSCRIPT REPL v0.2.0 (Type English statements and press Enter)\n")

        repl_input_row = ctk.CTkFrame(repl_frame, height=32, fg_color="#2B2D30")
        repl_input_row.pack(fill="x", side="bottom")

        ctk.CTkLabel(repl_input_row, text=" DOOM> ", font=("JetBrains Mono", 10, "bold"), text_color="#FF4757").pack(side="left")
        self.repl_input = ctk.CTkEntry(repl_input_row, font=("JetBrains Mono", 10), fg_color="#1E1F22")
        self.repl_input.pack(side="left", fill="x", expand=True, padx=4, pady=2)
        self.repl_input.bind("<Return>", self._on_repl_submit)

    def _build_status_bar(self):
        self.status_bar = ctk.CTkFrame(self, height=22, fg_color="#2B2D30", corner_radius=0)
        self.status_bar.pack(side="bottom", fill="x")

        self.status_lbl = ctk.CTkLabel(
            self.status_bar, text="Ready", font=("Segoe UI", 9), text_color="#9AA0A6"
        )
        self.status_lbl.pack(side="left", padx=12)

        ver_lbl = ctk.CTkLabel(
            self.status_bar, text="DoomScript v0.2.0 • Python 3.14.7 • UTF-8", font=("Segoe UI", 9), text_color="#9AA0A6"
        )
        ver_lbl.pack(side="right", padx=16)

    def _set_default_editor_content(self):
        demo = """# DoomScript Studio Demo
say "========================================"
say "   WELCOME TO DOOMSCRIPT STUDIO IDE     "
say "========================================"

player = {name: "Doom Slayer", health: 100, score: 0}
increase player's score by 500

say "Hero: {player's name} | Score: {player's score}"

# Clamp and assertions
clamp player's health between 0 and 100 into actual_hp
verify actual_hp is at most 100 otherwise "Overflow"

display colored "SYSTEMS VERIFIED & OPERATIONAL!" in "green"
"""
        self.editor.insert("1.0", demo)
        self.tab_title.configure(text="  demo.doom  ")
        self.file_title_lbl.configure(text="demo.doom")
        self._on_editor_key()

    def open_file_path(self, filepath: Path):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            self.editor.delete("1.0", tk.END)
            self.editor.insert("1.0", content)
            self.current_file = filepath
            self.tab_title.configure(text=f"  {filepath.name}  ")
            self.file_title_lbl.configure(text=str(filepath))
            self._on_editor_key()
            self.status_lbl.configure(text=f"Opened: {filepath.name}")
        except Exception as e:
            messagebox.showerror("Error opening file", str(e))

    def action_new_file(self):
        self.editor.delete("1.0", tk.END)
        self.current_file = None
        self.tab_title.configure(text="  untitled.doom  ")
        self.file_title_lbl.configure(text="[Untitled]")
        self.line_numbers.redraw()

    def action_open_file_dialog(self):
        f = filedialog.askopenfilename(
            initialdir=str(self.workspace_dir),
            title="Open DoomScript Source",
            filetypes=[("DoomScript Files", "*.doom"), ("All Files", "*.*")]
        )
        if f:
            self.open_file_path(Path(f))

    def action_save_file(self):
        if not self.current_file:
            f = filedialog.asksaveasfilename(
                initialdir=str(self.workspace_dir),
                title="Save DoomScript Source",
                defaultextension=".doom",
                filetypes=[("DoomScript Files", "*.doom")]
            )
            if not f:
                return
            self.current_file = Path(f)

        try:
            with open(self.current_file, "w", encoding="utf-8") as f:
                f.write(self.editor.get("1.0", tk.END))
            self.status_lbl.configure(text=f"Saved: {self.current_file.name}")
            self._refresh_project_files()
        except Exception as e:
            messagebox.showerror("Error saving file", str(e))

    def action_run_script(self):
        self.action_save_file()
        code = self.editor.get("1.0", tk.END)
        self.bottom_tabs.set("Console (Run)")
        self.console_output.delete("1.0", tk.END)
        self.console_output.insert(tk.END, "[Running DoomScript...]\n")

        import io
        from contextlib import redirect_stdout, redirect_stderr

        def run_thread():
            f_out = io.StringIO()
            f_err = io.StringIO()
            success = True
            err_msg = ""
            with redirect_stdout(f_out), redirect_stderr(f_err):
                try:
                    execute(code)
                except Exception as e:
                    success = False
                    err_msg = str(e)

            output = f_out.getvalue() + f_err.getvalue()
            if not success:
                output += f"\n[Runtime Error]: {err_msg}"
            output += "\n[Process finished]\n"

            self.after(0, lambda: self._update_console(output))

        threading.Thread(target=run_thread, daemon=True).start()

    def _update_console(self, text):
        self.console_output.delete("1.0", tk.END)
        self.console_output.insert(tk.END, text)
        self.status_lbl.configure(text="Execution finished.")

    def action_transpile(self):
        code = self.editor.get("1.0", tk.END)
        self.bottom_tabs.set("Transpiled Python")
        try:
            py = transpile(code)
            self.transpiled_output.delete("1.0", tk.END)
            self.transpiled_output.insert(tk.END, py)
            self.status_lbl.configure(text="Transpiled successfully.")
        except Exception as e:
            self.transpiled_output.delete("1.0", tk.END)
            self.transpiled_output.insert(tk.END, f"# Transpilation Error:\n# {e}")
            self.status_lbl.configure(text="Transpile error.")

    def action_check_syntax(self):
        code = self.editor.get("1.0", tk.END)
        try:
            compile_to_ast(code)
            messagebox.showinfo("Syntax OK", "Syntax is 100% valid DoomScript code!")
            self.status_lbl.configure(text="Syntax OK.")
        except Exception as e:
            messagebox.showerror("Syntax Error", f"DoomScript Syntax Error:\n{e}")
            self.status_lbl.configure(text="Syntax Error detected.")

    def action_build_exe(self):
        self.action_save_file()
        if not self.current_file:
            return

        self.bottom_tabs.set("Console (Run)")
        self.console_output.delete("1.0", tk.END)
        self.console_output.insert(tk.END, f"Building standalone executable for {self.current_file.name}...\n")

        import subprocess
        target_f = self.current_file

        def build_thread():
            cmd = [sys.executable, "-m", "doomscript.cli", "build", str(target_f)]
            res = subprocess.run(cmd, capture_output=True, text=True)
            out = res.stdout + res.stderr
            self.after(0, lambda: self._update_console(out))

        threading.Thread(target=build_thread, daemon=True).start()

    def _on_repl_submit(self, event=None):
        line = self.repl_input.get().strip()
        if not line:
            return
        self.repl_input.delete(0, tk.END)
        self.repl_history.insert(tk.END, f"\nDOOM> {line}\n")

        import io
        from contextlib import redirect_stdout, redirect_stderr

        f_out = io.StringIO()
        with redirect_stdout(f_out), redirect_stderr(f_out):
            try:
                execute(line, custom_globals=self.repl_env)
            except Exception as e:
                f_out.write(f"Error: {e}\n")

        res_text = f_out.getvalue()
        if res_text:
            self.repl_history.insert(tk.END, res_text)
        self.repl_history.see(tk.END)


def launch_ide():
    """Launch the DoomScript Studio desktop IDE."""
    app = DoomScriptStudio()
    app.mainloop()


if __name__ == "__main__":
    launch_ide()
