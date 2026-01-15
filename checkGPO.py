# tempered_windows.py
"""
Tempered Windows - Phase 2
Admin elevation + GUI + Load & display categories with checkboxes
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import os
import sys
import ctypes
from pathlib import Path


def is_admin() -> bool:
    """Check if running with administrator privileges"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except:
        return False


def relaunch_as_admin():
    """Relaunch script with admin rights"""
    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1
        )
        sys.exit(0)


class TemperedWindows:
    def __init__(self, root):
        self.root = root
        self.root.title("Tempered Windows – System Hardening Tool")
        self.root.geometry("960x680")
        self.root.minsize(860, 580)

        # Try to set icon (optional - place tempered.ico in same folder)
        try:
            self.root.iconbitmap("tempered.ico")
        except:
            pass

        self.categories = []                    # list of category dicts
        self.category_vars = {}                 # name → tk.BooleanVar
        self.category_widgets = {}              # name → widgets (for future reference)

        self.categories_canvas = None
        self.categories_inner_frame = None
        self.no_categories_label = None

        # Style setup
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('.', font=('Segoe UI', 10))
        style.configure('TButton', padding=8)
        style.map('TButton', background=[('active', '#005bb5')])

        self._build_ui()
        self._create_menu()

        self.status_var.set("Ready • Load a hardening rules file to begin")

    def _build_ui(self):
        main_frame = ttk.Frame(self.root, padding="12 10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Top controls
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill=tk.X, pady=(0, 12))

        ttk.Button(
            top_frame,
            text="Load Rules File",
            command=self.load_rules_file
        ).pack(side=tk.LEFT, padx=4)

        # Content area
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)

        # ── Left: Scrollable categories with checkboxes ───────────────────────
        left_container = ttk.Frame(content_frame, width=380)
        left_container.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10), expand=False)
        left_container.pack_propagate(False)

        self.categories_canvas = tk.Canvas(left_container, bg='#ffffff')
        scrollbar = ttk.Scrollbar(left_container, orient="vertical", command=self.categories_canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.categories_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.categories_canvas.configure(yscrollcommand=scrollbar.set)

        self.categories_inner_frame = ttk.Frame(self.categories_canvas)
        self.categories_canvas.create_window((0, 0), window=self.categories_inner_frame, anchor="nw")

        self.categories_inner_frame.bind("<Configure>", self._update_scrollregion)

        # Header
        ttk.Label(
            self.categories_inner_frame,
            text="Select categories to harden:",
            font=('Segoe UI', 11, 'bold'),
            foreground='#343a40'
        ).pack(anchor='w', pady=(10, 12), padx=10)

        # Placeholder
        self.no_categories_label = ttk.Label(
            self.categories_inner_frame,
            text="(No categories loaded yet)",
            foreground='#6c757d',
            font=('Segoe UI', 10, 'italic')
        )

        # ── Right: Details ────────────────────────────────────────────────────
        right_frame = ttk.LabelFrame(content_frame, text=" Category Details ", padding="10")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.details_text = tk.Text(
            right_frame,
            wrap=tk.WORD,
            font=('Segoe UI', 10),
            height=28,
            bg='#ffffff',
            relief='flat',
            highlightthickness=1,
            highlightbackground='#ced4da'
        )
        self.details_text.pack(fill=tk.BOTH, expand=True)

        details_scroll = ttk.Scrollbar(right_frame, command=self.details_text.yview)
        details_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.details_text.config(yscrollcommand=details_scroll.set)

        # ── Status bar ────────────────────────────────────────────────────────
        status_container = ttk.Frame(main_frame)
        status_container.pack(side=tk.BOTTOM, fill=tk.X, pady=(8, 0))

        self.status_var = tk.StringVar()
        status_label = ttk.Label(
            status_container,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W,
            padding=(12, 6)
        )
        status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        ttk.Label(
            status_container,
            text="Phase 2 • 2026",
            foreground='#6c757d',
            font=('Segoe UI', 8)
        ).pack(side=tk.RIGHT, padx=12)

    def _update_scrollregion(self, event=None):
        self.categories_canvas.configure(scrollregion=self.categories_canvas.bbox("all"))

    def _create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Load Rules...", command=self.load_rules_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)

    def show_about(self):
        messagebox.showinfo(
            "Tempered Windows",
            "Tempered Windows – Phase 2\n\n"
            "A safe, reversible way to harden Windows systems\n\n"
            "Current features:\n"
            "• Load hardening rules from JSON\n"
            "• Category selection with checkboxes\n"
            "• Live selection feedback"
        )

    def load_rules_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Hardening Rules JSON",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if not file_path:
            return

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            if "categories" not in data:
                raise ValueError("Invalid format: 'categories' key not found")

            self.categories = data["categories"]
            self._refresh_category_list()

            self.status_var.set(f"Loaded {len(self.categories)} categories • {Path(file_path).name}")

        except json.JSONDecodeError:
            messagebox.showerror("Error", "Invalid JSON format")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load:\n{str(e)}")

    def _refresh_category_list(self):
        # Clear old content (except header & placeholder)
        for widget in self.categories_inner_frame.winfo_children():
            if widget != self.no_categories_label:
                widget.destroy()

        self.category_vars.clear()
        self.category_widgets.clear()

        self.no_categories_label.pack_forget()

        if not self.categories:
            self.no_categories_label.pack(anchor='w', padx=12, pady=20)
            return

        for cat in self.categories:
            name = cat.get("name", "Unnamed")
            desc = cat.get("description", "").strip()
            short_desc = desc[:90] + ("..." if len(desc) > 90 else "")

            row_frame = ttk.Frame(self.categories_inner_frame)
            row_frame.pack(fill='x', padx=6, pady=3)

            var = tk.BooleanVar(value=False)
            self.category_vars[name] = var

            chk = ttk.Checkbutton(
                row_frame,
                variable=var,
                command=self._on_selection_changed
            )
            chk.pack(side='left', padx=(4, 8))

            text_frame = ttk.Frame(row_frame)
            text_frame.pack(side='left', fill='x', expand=True)

            ttk.Label(
                text_frame,
                text=name,
                font=('Segoe UI', 10, 'bold')
            ).pack(anchor='w')

            if short_desc:
                ttk.Label(
                    text_frame,
                    text=short_desc,
                    foreground='#6c757d',
                    font=('Segoe UI', 9)
                ).pack(anchor='w')

            self.category_widgets[name] = row_frame

        self._update_scrollregion()
        self._on_selection_changed()

    def _on_selection_changed(self, *args):
        selected = sum(1 for v in self.category_vars.values() if v.get())
        total = len(self.category_vars)

        if selected == 0:
            msg = f"No categories selected"
        elif selected == total:
            msg = f"All {total} categories selected"
        else:
            msg = f"{selected} of {total} categories selected"

        self.status_var.set(f"{msg} • Ready")

    def run(self):
        self.root.mainloop()


def main():
    relaunch_as_admin()
    root = tk.Tk()
    app = TemperedWindows(root)
    root.mainloop()


if __name__ == "__main__":
    main()