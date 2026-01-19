# app.py
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
from pathlib import Path

from constants import (
    APP_TITLE, WINDOW_GEOMETRY, MIN_WINDOW_SIZE,
    ACCENT_COLOR, BG_COLOR, STATUS_BG_COLOR
)


class TemperedWindows:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry(WINDOW_GEOMETRY)
        self.root.minsize(*MIN_WINDOW_SIZE)

        try:
            self.root.iconbitmap("tempered.ico")
        except:
            pass

        self.categories = []
        self.category_vars = {}                 # name → BooleanVar
        self.category_widgets = {}              # name → row_frame
        self.selected_category_name = None

        self.categories_canvas = None
        self.categories_inner_frame = None
        self.no_categories_label = None

        self._setup_style()
        self._build_ui()
        self._create_menu()

        self.status_var.set("Welcome! Please load a hardening rules file to begin.")

    def _setup_style(self):
        style = ttk.Style()
        try:
            style.theme_use('clam')
        except:
            pass

        style.configure('.', background=BG_COLOR, foreground='#212529', font=('Segoe UI', 10))
        style.configure('TButton', padding=8, font=('Segoe UI', 10, 'bold'))
        style.map('TButton', background=[('active', '#005bb5')], foreground=[('active', 'white')])
        style.configure('TLabelFrame', background=BG_COLOR, foreground='#343a40')
        style.configure('TLabelFrame.Label', font=('Segoe UI', 11, 'bold'))

        # Selected category row style
        style.configure('SelectedCategory.TFrame', background='#e6f0ff')

    def _build_ui(self):
        main_frame = ttk.Frame(self.root, padding="12 10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=0)   # top
        main_frame.rowconfigure(1, weight=1)   # content
        main_frame.rowconfigure(2, weight=0)   # status

        # Top controls
        top_frame = ttk.Frame(main_frame)
        top_frame.grid(row=0, column=0, sticky="ew", pady=(0, 12))

        ttk.Button(top_frame, text="Load Rules File", command=self.load_rules_file).pack(side=tk.LEFT, padx=4)

        # Content area
        content_frame = ttk.Frame(main_frame)
        content_frame.grid(row=1, column=0, sticky="nsew")
        content_frame.columnconfigure(1, weight=1)
        content_frame.rowconfigure(0, weight=1)

        # Left: Categories
        left_container = ttk.Frame(content_frame, width=360)
        left_container.grid(row=0, column=0, sticky="ns", padx=(0, 10))

        self.categories_canvas = tk.Canvas(left_container)
        scrollbar = ttk.Scrollbar(left_container, orient="vertical", command=self.categories_canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.categories_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.categories_canvas.configure(yscrollcommand=scrollbar.set)

        self.categories_inner_frame = ttk.Frame(self.categories_canvas)
        self.categories_canvas.create_window((0, 0), window=self.categories_inner_frame, anchor="nw")

        self.categories_inner_frame.bind("<Configure>", lambda e: self.categories_canvas.configure(
            scrollregion=self.categories_canvas.bbox("all")))

        ttk.Label(
            self.categories_inner_frame,
            text="Select categories to harden:",
            font=('Segoe UI', 10, 'bold'),
            foreground='#495057'
        ).pack(anchor='w', pady=(10, 12), padx=10)

        self.no_categories_label = ttk.Label(
            self.categories_inner_frame,
            text="(No categories loaded yet)",
            foreground='#6c757d',
            font=('Segoe UI', 9, 'italic')
        )
        self.no_categories_label.pack(anchor='w', padx=16, pady=30)

        # Right: Details
        right_frame = ttk.LabelFrame(content_frame, text=" Category Details ", padding="10")
        right_frame.grid(row=0, column=1, sticky="nsew")

        self.details_text = tk.Text(
            right_frame,
            wrap=tk.WORD,
            font=('Segoe UI', 10),
            bg='#ffffff',
            relief='flat',
            highlightthickness=1,
            highlightbackground='#ced4da'
        )
        self.details_text.pack(fill=tk.BOTH, expand=True)

        details_scroll = ttk.Scrollbar(right_frame, command=self.details_text.yview)
        details_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.details_text.config(yscrollcommand=details_scroll.set)

        # Status bar
        status_container = ttk.Frame(main_frame)
        status_container.grid(row=2, column=0, sticky="ew", pady=(8, 0))

        self.status_var = tk.StringVar(value="Ready")
        status_label = ttk.Label(
            status_container,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W,
            padding=(12, 6),
            font=('Segoe UI', 9)
        )
        status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        ttk.Label(
            status_container,
            text="Tempered Windows • Phase 2",
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
            "Tempered Windows – Phase 2\n\n"
            "• Load & display categorized hardening rules\n"
            "• Checkbox selection + live status\n"
            "• Category details on click\n"
            "Next: Backup → Apply → Revert"
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
            self.status_var.set(f"Loaded {len(self.categories)} categories successfully")

        except json.JSONDecodeError:
            messagebox.showerror("Error", "Invalid JSON format")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load file:\n{str(e)}")

    def _refresh_category_list(self):
        for widget in self.categories_inner_frame.winfo_children():
            if widget != self.no_categories_label:
                widget.destroy()

        self.category_vars.clear()
        self.category_widgets.clear()
        self.selected_category_name = None

        if not self.categories:
            self.no_categories_label.pack(anchor='w', padx=16, pady=30)
            self._clear_details()
            return

        self.no_categories_label.pack_forget()

        for cat in self.categories:
            name = cat.get("name", "Unnamed")
            desc = cat.get("description", "").strip()
            short_desc = (desc[:90] + "...") if len(desc) > 90 else desc

            row_frame = ttk.Frame(self.categories_inner_frame)
            row_frame.pack(fill='x', padx=6, pady=3)

            var = tk.BooleanVar(value=False)
            self.category_vars[name] = var

            chk = ttk.Checkbutton(
                row_frame,
                variable=var,
                command=self._update_selection_status
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

            row_frame.bind("<Button-1>", lambda e, n=name: self._select_category(n))
            for child in text_frame.winfo_children():
                child.bind("<Button-1>", lambda e, n=name: self._select_category(n))

            self.category_widgets[name] = row_frame

        self._update_selection_status()

        if self.categories:
            self._select_category(self.categories[0].get("name", "Unnamed"))

    def _select_category(self, category_name):
        self.selected_category_name = category_name

        for name, row_frame in self.category_widgets.items():
            if name == category_name:
                row_frame.configure(style='SelectedCategory.TFrame')
            else:
                row_frame.configure(style='')

        self._show_category_details(category_name)

    def _show_category_details(self, category_name):
        self.details_text.config(state=tk.NORMAL)
        self.details_text.delete("1.0", tk.END)

        category = next((c for c in self.categories if c.get("name") == category_name), None)
        if not category:
            self.details_text.insert(tk.END, "Category not found.\n")
        else:
            name = category.get("name", "Unnamed")
            desc = category.get("description", "No description provided.")
            rules = category.get("rules", [])

            content = f"Category: {name}\n\n"
            content += f"{desc}\n\n"
            content += f"Total rules: {len(rules)}\n\n"

            if rules:
                content += "Rules preview (first few):\n"
                for i, rule in enumerate(rules[:8], 1):
                    r_name = rule.get("name", "Unnamed rule")
                    r_desc = rule.get("description", "").strip()
                    method = rule.get("method", "—")
                    content += f"{i}. {r_name}  ({method})\n"
                    if r_desc:
                        content += f"   {r_desc[:140]}{'...' if len(r_desc) > 140 else ''}\n\n"
            else:
                content += "(No rules defined in this category yet)\n"

            self.details_text.insert(tk.END, content)

        self.details_text.config(state=tk.DISABLED)

    def _clear_details(self):
        self.details_text.config(state=tk.NORMAL)
        self.details_text.delete("1.0", tk.END)
        self.details_text.insert(tk.END, "Select a category to view details\n")
        self.details_text.config(state=tk.DISABLED)

    def _update_selection_status(self):
        selected = sum(1 for v in self.category_vars.values() if v.get())
        total = len(self.category_vars)

        if total == 0:
            msg = "No categories loaded"
        elif selected == 0:
            msg = f"No categories selected ({total} available)"
        elif selected == total:
            msg = f"All {total} categories selected"
        else:
            msg = f"{selected} of {total} categories selected"

        self.status_var.set(msg + " • Ready")

