import customtkinter as ctk
from config import COLORS

class StatsCard(ctk.CTkFrame):
    def __init__(self, parent, title, value, icon="📊", color=COLORS["accent"], **kwargs):
        super().__init__(parent, fg_color=COLORS["bg_light"], border_color=COLORS["border"], border_width=1, corner_radius=12, **kwargs)
        
        # Grid layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Left color strip
        self.color_strip = ctk.CTkFrame(
            self,
            width=6,
            fg_color=color,
            corner_radius=0
        )
        self.color_strip.grid(row=0, column=0, rowspan=2, sticky="nsw", padx=(0, 10))

        # Text Frame
        self.text_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.text_frame.grid(row=0, column=1, sticky="w", pady=15)

        # Icon Label
        self.icon_label = ctk.CTkLabel(
            self,
            text=icon,
            font=("Segoe UI", 36),
            text_color=color
        )
        self.icon_label.grid(row=0, column=2, sticky="e", padx=(0, 20), pady=15)

        # Title Label
        self.title_label = ctk.CTkLabel(
            self.text_frame,
            text=title.upper(),
            font=("Segoe UI", 11, "bold"),
            text_color=COLORS["text_secondary"]
        )
        self.title_label.pack(anchor="w")

        # Value Label
        self.value_label = ctk.CTkLabel(
            self.text_frame,
            text=value,
            font=("Segoe UI", 24, "bold"),
            text_color=COLORS["text_primary"]
        )
        self.value_label.pack(anchor="w", pady=(2, 0))

    def update_value(self, new_value):
        """Dynamic updater for stats values."""
        self.value_label.configure(text=str(new_value))
