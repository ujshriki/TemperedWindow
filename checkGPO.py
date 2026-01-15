# checkGPO.py
"""
Tempered Windows: a Hardening Wizard - Phase 1
Focus: Admin elevation + Basic GUI + Load & display categories from JSON
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import os
import sys
import ctypes
from pathlib import Path


def is_admin() -> bool:
    """Check if the current process is running with administrator privileges"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except:
        return False


def relaunch_as_admin():
    """Relaunch the script with admin rights (Windows only)"""
    if not is_admin():
        # Re-run the program with admin rights
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1
        )
        sys.exit(0)  # Important: exit current non-admin instance


class HardeningWizard:
    def __init__(self, root):
        self.root = root
        self.category_vars = {}

        # ── Window setup ───────────────────────────────────────────────────────
        self.root.title("Tempered Windows – System Hardening Tool")
        self.root.geometry("960x680")
        self.root.minsize(860, 580)

        # set icon (tempered.ico in folder)
        try:
            self.root.iconbitmap("tempered.ico")
        except:
            pass  # silent fail if file missing

        # ── Modern-ish theme attempt ───────────────────────────────────────────
        style = ttk.Style()
        style.theme_use('clam')  # or 'vista', 'xpnative' - depending on OS look

        # Some color tweaks (Windows 11-ish feeling)
        accent = '#0066cc'  # nice blue
        bg = '#f8f9fa'
        fg = '#212529'
        status_bg = '#e9ecef'

        style.configure('.', background=bg, foreground=fg, font=('Segoe UI', 10))
        style.configure('TButton', padding=8, font=('Segoe UI', 10, 'bold'))
        style.map('TButton',
                  background=[('active', '#005bb5')],
                  foreground=[('active', 'white')])
        style.configure('TLabelFrame', background=bg, foreground='#343a40')
        style.configure('TLabelFrame.Label', font=('Segoe UI', 11, 'bold'))

        self._build_ui()
        self._create_menu()

        self.status_var.set("Ready • Load a hardening rules file to begin")

    def _build_ui(self):
        main_frame = ttk.Frame(self.root, padding="12 10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Top controls
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill=tk.X, pady=(0, 12))

        load_btn = ttk.Button(top_frame, text="Load Rules File", command=self.load_rules_file)
        load_btn.pack(side=tk.LEFT, padx=4)
        # Optional: make first button stand out more
        load_btn.state(['!disabled'])  # just in case...

        # ── Content area ─────────────────────────────────────────────────────
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)

        # Left - Categories
        left_frame = ttk.LabelFrame(content_frame, text=" Security Categories ", padding="10")
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10), expand=False)

        # Small header above list
        ttk.Label(
            left_frame,
            text="Select categories to harden:",
            font=('Segoe UI', 10, 'bold'),
            foreground='#495057'
        ).pack(anchor='w', pady=(0, 6))

        self.cat_scroll = ttk.Scrollbar(left_frame)
        self.cat_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.cat_listbox = tk.Listbox(
            left_frame,
            width=38,
            height=26,
            yscrollcommand=self.cat_scroll.set,
            selectmode=tk.SINGLE,
            font=('Segoe UI', 10),
            bg='#ffffff',
            relief='flat',
            highlightthickness=1,
            highlightbackground='#ced4da',
            highlightcolor='#80bdff'
        )
        self.cat_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.cat_scroll.config(command=self.cat_listbox.yview)

        self.cat_listbox.bind('<<ListboxSelect>>', self.on_category_select)

        # Right - Details
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

        # ── Status bar ───────────────────────────────────────────────────────
        status_container = ttk.Frame(main_frame)
        status_container.pack(side=tk.BOTTOM, fill=tk.X, pady=(8, 0))

        self.status_var = tk.StringVar(value="Ready • Load a hardening rules file to begin")
        status_label = ttk.Label(
            status_container,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W,
            padding=(12, 6),
            font=('Segoe UI', 9)
        )
        status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Tiny version tag on right
        ttk.Label(
            status_container,
            text="Tempered Windows • Phase 1 • 2026",
            foreground='#6c757d',
            font=('Segoe UI', 8)
        ).pack(side=tk.RIGHT, padx=12)

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
            "About Tempered Windows",
            "Tempered Windows: a Hardening Wizard - Phase 1\n\n"
            "A simple GUI for applying Windows hardening rules\n"
            "Currently supports: loading & displaying categories\n\n"
            "Next phases will add apply/revert functionality"
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

            self.status_var.set(f"Loaded {len(self.categories)} categories from {Path(file_path).name}")

        except json.JSONDecodeError:
            messagebox.showerror("Error", "Invalid JSON format")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load file:\n{str(e)}")

    def _refresh_category_list(self):
        self.cat_listbox.delete(0, tk.END)
        self.category_vars.clear()

        for cat in self.categories:
            name = cat.get("name", "Unnamed")
            self.cat_listbox.insert(tk.END, name)

            # We don't show checkboxes in phase 1 - just list
            # Checkboxes will come in next phase

    def on_category_select(self, event):
        selection = self.cat_listbox.curselection()
        if not selection:
            return

        index = selection[0]
        if index >= len(self.categories):
            return

        cat = self.categories[index]

        self.details_text.config(state=tk.NORMAL)
        self.details_text.delete("1.0", tk.END)

        name = cat.get("name", "Unnamed")
        desc = cat.get("description", "No description provided")
        rules_count = len(cat.get("rules", []))

        content = f"Category: {name}\n\n"
        content += f"{desc}\n\n"
        content += f"Number of rules: {rules_count}\n\n"

        if rules_count > 0:
            content += "Rules preview (first few):\n"
            for i, rule in enumerate(cat.get("rules", [])[:5], 1):
                rname = rule.get("name", "Unnamed rule")
                rdesc = rule.get("description", "").strip()
                method = rule.get("method", "?")
                content += f"  {i}. {rname}  ({method})\n"
                if rdesc:
                    content += f"     {rdesc[:120]}{'...' if len(rdesc) > 120 else ''}\n"

        self.details_text.insert(tk.END, content)
        self.details_text.config(state=tk.DISABLED)


def main():
    # Step 1: Make sure we're running as admin
    relaunch_as_admin()

    root = tk.Tk()
    app = HardeningWizard(root)
    root.mainloop()


if __name__ == "__main__":
    main()