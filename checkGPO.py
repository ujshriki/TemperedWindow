# hardening_wizard.py
"""
Hardening Wizard - Phase 1
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
        self.root.title("Hardening Wizard - Phase 1")
        self.root.geometry("900x650")
        self.root.minsize(800, 550)

        self.categories = []           # list of dicts: {'name': str, 'description': str, 'rules': list}
        self.category_vars = {}        # name -> BooleanVar for checkbox

        self._build_ui()
        self._create_menu()

        # Initial message
        self.status_var.set("Welcome! Please load a hardening rules file to begin.")

    def _build_ui(self):
        # ── Main container ───────────────────────────────────────────────────────
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # ── Top controls ─────────────────────────────────────────────────────────
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Button(top_frame, text="Load Rules File", command=self.load_rules_file).pack(side=tk.LEFT, padx=5)

        # ── Categories list (left) ───────────────────────────────────────────────
        left_frame = ttk.LabelFrame(main_frame, text="Security Categories", padding="8")
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10), expand=False)

        self.cat_scroll = ttk.Scrollbar(left_frame)
        self.cat_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.cat_listbox = tk.Listbox(
            left_frame,
            width=35,
            height=25,
            yscrollcommand=self.cat_scroll.set,
            selectmode=tk.SINGLE,
            font=("Segoe UI", 10)
        )
        self.cat_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.cat_scroll.config(command=self.cat_listbox.yview)

        # Bind selection to show description
        self.cat_listbox.bind('<<ListboxSelect>>', self.on_category_select)

        # ── Details / description area (right) ───────────────────────────────────
        right_frame = ttk.LabelFrame(main_frame, text="Category Details", padding="8")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.details_text = tk.Text(
            right_frame,
            wrap=tk.WORD,
            font=("Segoe UI", 10),
            height=28,
            state=tk.DISABLED
        )
        self.details_text.pack(fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(right_frame, command=self.details_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.details_text.config(yscrollcommand=scrollbar.set)

        # ── Status bar ───────────────────────────────────────────────────────────
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(
            main_frame,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W,
            padding=(5, 3)
        )
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

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
            "About Hardening Wizard",
            "Hardening Wizard - Phase 1\n\n"
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