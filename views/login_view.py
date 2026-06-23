import customtkinter as ctk
from config import COLORS
from models.user import User

class LoginWindow(ctk.CTk):
    def __init__(self, on_success):
        super().__init__()
        self.on_success = on_success
        
        # Configure window
        self.title("Inicio de Sesión - PyStock_Manager")
        self.geometry("380x480")
        self.resizable(False, False)
        self.configure(fg_color=COLORS["bg_medium"])

        # Center window on the screen
        self.center_window()

        # Build UI layout
        self.build_ui()

    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"+{x}+{y}")

    def build_ui(self):
        # Card container
        card = ctk.CTkFrame(
            self,
            fg_color=COLORS["bg_light"],
            border_color=COLORS["border"],
            border_width=1,
            corner_radius=15
        )
        card.pack(expand=True, fill="both", padx=30, pady=30)
        
        # Title Header
        title_lbl = ctk.CTkLabel(
            card,
            text="PYSTOCK_MANAGER",
            font=("Segoe UI", 24, "bold"),
            text_color=COLORS["accent"]
        )
        title_lbl.pack(pady=(25, 2))

        subtitle_lbl = ctk.CTkLabel(
            card,
            text="Acceso al Sistema",
            font=("Segoe UI", 12),
            text_color=COLORS["text_secondary"]
        )
        subtitle_lbl.pack(pady=(0, 20))

        # Username Input
        user_lbl = ctk.CTkLabel(
            card,
            text="USUARIO:",
            font=("Segoe UI", 10, "bold"),
            text_color=COLORS["text_secondary"]
        )
        user_lbl.pack(anchor="w", padx=30, pady=(10, 2))

        self.user_entry = ctk.CTkEntry(
            card,
            font=("Segoe UI", 12),
            fg_color=COLORS["bg_dark"],
            border_color=COLORS["border"],
            text_color=COLORS["text_primary"],
            height=35
        )
        self.user_entry.pack(fill="x", padx=30)
        self.user_entry.bind("<Return>", lambda e: self.pass_entry.focus())

        # Password Input
        pass_lbl = ctk.CTkLabel(
            card,
            text="CONTRASEÑA:",
            font=("Segoe UI", 10, "bold"),
            text_color=COLORS["text_secondary"]
        )
        pass_lbl.pack(anchor="w", padx=30, pady=(15, 2))

        self.pass_entry = ctk.CTkEntry(
            card,
            font=("Segoe UI", 12),
            show="*",
            fg_color=COLORS["bg_dark"],
            border_color=COLORS["border"],
            text_color=COLORS["text_primary"],
            height=35
        )
        self.pass_entry.pack(fill="x", padx=30)
        self.pass_entry.bind("<Return>", lambda e: self.perform_login())

        # Error notification label
        self.error_lbl = ctk.CTkLabel(
            card,
            text="",
            font=("Segoe UI", 10, "bold"),
            text_color=COLORS["danger"]
        )
        self.error_lbl.pack(pady=(12, 0))

        # Login Button
        self.login_btn = ctk.CTkButton(
            card,
            text="Iniciar Sesión  🔑",
            font=("Segoe UI", 12, "bold"),
            fg_color=COLORS["accent"],
            text_color=COLORS["bg_dark"],
            hover_color=COLORS["accent_hover"],
            height=40,
            command=self.perform_login
        )
        self.login_btn.pack(fill="x", padx=30, pady=(15, 20))

        # Focus username on open
        self.user_entry.focus()

    def perform_login(self):
        username = self.user_entry.get().strip()
        password = self.pass_entry.get()

        if not username or not password:
            self.error_lbl.configure(text="Complete todos los campos.")
            return

        # Attempt authentication via User Model
        user = User.authenticate(username, password)
        if user:
            self.on_success(user)
            self.withdraw()
            self.quit()
        else:
            self.error_lbl.configure(text="Usuario o contraseña incorrectos.")
            self.pass_entry.delete(0, "end")
            self.pass_entry.focus()
