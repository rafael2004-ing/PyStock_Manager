import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
from config import COLORS

class CustomTreeview(ctk.CTkFrame):
    def __init__(self, parent, columns, headings, selectmode="browse", show="headings", **kwargs):
        super().__init__(parent, **kwargs)
        self.columns = columns
        
        # Configure ttk style to match dark mode theme
        self.style = ttk.Style()
        
        # Ensure we use 'clam' theme as it is highly customizable
        self.style.theme_use("clam")
        
        # Configure global treeview style
        self.style.configure(
            "Treeview",
            background=COLORS["bg_light"],
            foreground=COLORS["text_primary"],
            fieldbackground=COLORS["bg_light"],
            rowheight=35,
            bordercolor=COLORS["border"],
            borderwidth=0,
            font=("Segoe UI", 10)
        )
        
        # Configure headers style
        self.style.configure(
            "Treeview.Heading",
            background=COLORS["bg_dark"],
            foreground=COLORS["text_primary"],
            relief="flat",
            font=("Segoe UI", 10, "bold"),
            bordercolor=COLORS["border"],
            borderwidth=1
        )
        
        # Map colors for active/selected states
        self.style.map(
            "Treeview",
            background=[("selected", COLORS["accent"])],
            foreground=[("selected", COLORS["bg_dark"])]
        )
        
        self.style.map(
            "Treeview.Heading",
            background=[("active", COLORS["border"])]
        )

        # Create Treeview inside this frame
        self.tree = ttk.Treeview(
            self, 
            columns=self.columns, 
            show=show, 
            selectmode=selectmode
        )
        
        # Configure warning tag to display in bright danger color
        self.tree.tag_configure("warning", foreground=COLORS["danger"])
        
        # Add scrollbars
        self.scrollbar_y = ctk.CTkScrollbar(self, orientation="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.scrollbar_y.set)
        
        # Grid layout
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        self.tree.grid(row=0, column=0, sticky="nsew", padx=(5, 0), pady=5)
        self.scrollbar_y.grid(row=0, column=1, sticky="ns", padx=(0, 5), pady=5)

        # Configure columns and headings
        for col, heading in zip(self.columns, headings):
            self.tree.heading(col, text=heading, anchor="w")
            self.tree.column(col, anchor="w", width=120)

        # Bind events
        self.tree.bind("<Motion>", self._on_mouse_over_header)

    def _on_mouse_over_header(self, event):
        # Trick to change cursor when hovering headings
        region = self.tree.identify_region(event.x, event.y)
        current = self.tree.cget("cursor")
        if region == "heading":
            if current != "hand2":
                self.tree.configure(cursor="hand2")
        else:
            if current != "":
                self.tree.configure(cursor="")

    def set_column_width(self, column, width):
        self.tree.column(column, width=width)

    def set_column_anchor(self, column, anchor):
        self.tree.column(column, anchor=anchor)

    def clear(self):
        """Clears all records in the treeview."""
        for item in self.tree.get_children():
            self.tree.delete(item)

    def insert_row(self, values, item_id=None, tags=()):
        """Inserts a new row of data."""
        if item_id:
            return self.tree.insert("", "end", iid=item_id, values=values, tags=tags)
        return self.tree.insert("", "end", values=values, tags=tags)

    def get_selected_item(self):
        """Returns the values and IID of the selected row."""
        selected = self.tree.selection()
        if not selected:
            return None, None
        item_id = selected[0]
        return self.tree.item(item_id, "values"), item_id

    def select_item_by_id(self, item_id):
        """Highlights a specific item by its IID."""
        if self.tree.exists(item_id):
            self.tree.selection_set(item_id)
            self.tree.see(item_id)

    def bind_double_click(self, callback):
        """Binds double click on row to a function."""
        self.tree.bind("<Double-1>", lambda event: callback(self.get_selected_item()))

    def bind_select(self, callback):
        """Binds item selection to a function."""
        self.tree.bind("<<TreeviewSelect>>", lambda event: callback(self.get_selected_item()))
