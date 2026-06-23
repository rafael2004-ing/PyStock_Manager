import customtkinter as ctk
from config import APP_TITLE, WINDOW_WIDTH, WINDOW_HEIGHT, COLORS, CTK_THEME
from controllers.dashboard_controller import DashboardController
from controllers.customer_supplier_controller import CustomerSupplierController
from controllers.product_controller import ProductController
from controllers.order_controller import OrderController
from controllers.report_controller import ReportController

# View imports (to be created next)
from views.dashboard_view import DashboardView
from views.customer_supplier_view import CustomerSupplierView
from views.product_view import ProductView
from views.order_view import OrderView
from views.report_view import ReportView

class MainWindow(ctk.CTk):
    def __init__(self, user):
        super().__init__()
        self.current_user = user
        
        # Window settings
        self.title(APP_TITLE)
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.minsize(1000, 650)
        
        # Center the window on screen
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (WINDOW_WIDTH // 2)
        y = (screen_height // 2) - (WINDOW_HEIGHT // 2)
        self.geometry(f"+{x}+{y}")

        # Set default theme
        ctk.set_appearance_mode(CTK_THEME)

        # Initialize Controllers
        self.dashboard_ctrl = DashboardController()
        self.contacts_ctrl = CustomerSupplierController()
        self.product_ctrl = ProductController()
        self.order_ctrl = OrderController()
        self.report_ctrl = ReportController()

        # Layout configuration
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Build Sidebar
        self.build_sidebar()

        # Build Content Area
        self.content_container = ctk.CTkFrame(
            self, 
            fg_color=COLORS["bg_medium"], 
            corner_radius=0
        )
        self.content_container.grid(row=0, column=1, sticky="nsew")
        self.content_container.grid_rowconfigure(1, weight=1)
        self.content_container.grid_columnconfigure(0, weight=1)

        # Content Header
        self.header_label = ctk.CTkLabel(
            self.content_container,
            text="Dashboard",
            font=("Segoe UI", 24, "bold"),
            text_color=COLORS["text_primary"]
        )
        self.header_label.grid(row=0, column=0, sticky="w", padx=30, pady=(25, 15))

        # Instantiate Views
        self.views = {
            "dashboard": DashboardView(self.content_container, self.dashboard_ctrl),
            "contacts": CustomerSupplierView(self.content_container, self.contacts_ctrl),
            "products": ProductView(self.content_container, self.product_ctrl),
            "billing": OrderView(self.content_container, self.order_ctrl),
            "reports": ReportView(self.content_container, self.report_ctrl)
        }

        # Show initial view (Dashboard)
        self.current_view_name = None
        self.show_view("dashboard")

        # Run critical stock check on startup (delay briefly to let GUI display)
        self.after(500, lambda: self.check_critical_stock(show_popup=True))

    def build_sidebar(self):
        """Creates the navigation sidebar."""
        self.sidebar_frame = ctk.CTkFrame(
            self,
            width=220,
            fg_color=COLORS["bg_dark"],
            corner_radius=0,
            border_width=0
        )
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_propagate(False)

        # App Logo
        self.logo_label = ctk.CTkLabel(
            self.sidebar_frame,
            text="PyStock_Manager",
            font=("Segoe UI", 22, "bold"),
            text_color=COLORS["accent"]
        )
        self.logo_label.pack(pady=(25, 15))

        # User Profile Frame
        profile_frame = ctk.CTkFrame(
            self.sidebar_frame,
            fg_color=COLORS["bg_light"],
            border_color=COLORS["border"],
            border_width=1,
            corner_radius=8,
            height=60
        )
        profile_frame.pack(fill="x", padx=15, pady=(0, 20))
        profile_frame.pack_propagate(False)

        usr_lbl = ctk.CTkLabel(
            profile_frame,
            text=f"👤 {self.current_user.username.capitalize()}",
            font=("Segoe UI", 12, "bold"),
            text_color=COLORS["text_primary"]
        )
        usr_lbl.pack(anchor="w", padx=12, pady=(10, 0))

        role_lbl = ctk.CTkLabel(
            profile_frame,
            text=self.current_user.role,
            font=("Segoe UI", 10, "bold"),
            text_color=COLORS["accent"]
        )
        role_lbl.pack(anchor="w", padx=12, pady=(0, 5))

        # Navigation Buttons definitions
        self.nav_buttons = {}
        nav_items = [
            ("dashboard", "📊  Inicio", "dashboard"),
            ("contacts", "👥  Clientes & Prov.", "contacts"),
            ("products", "📦  Inventario", "products"),
            ("billing", "🧾  Facturación", "billing"),
            ("reports", "📈  Reportes", "reports")
        ]

        # Render nav buttons
        for key, text, view_name in nav_items:
            # If user is not Admin, do not render or enable the Reports view
            if key == "reports" and self.current_user.role != "Administrador":
                continue

            btn = ctk.CTkButton(
                self.sidebar_frame,
                text=text,
                font=("Segoe UI", 13, "bold"),
                anchor="w",
                height=42,
                corner_radius=8,
                fg_color="transparent",
                text_color=COLORS["text_secondary"],
                hover_color=COLORS["bg_light"],
                command=lambda vn=view_name: self.show_view(vn)
            )
            btn.pack(fill="x", padx=15, pady=6)
            self.nav_buttons[key] = btn



    def check_critical_stock(self, show_popup=False):
        """Queries products for critical stock alert levels and warns user if needed."""
        critical_items = self.report_ctrl.get_critical_stock()
        if not critical_items:
            return

        if show_popup:
            import tkinter.messagebox as messagebox
            lines = [f"- {p.name} (Stock actual: {p.stock}, Alerta: {p.min_stock})" for p in critical_items]
            msg = "Los siguientes productos están por debajo del stock mínimo de seguridad:\n\n" + "\n".join(lines)
            messagebox.showwarning("Alerta de Stock Crítico", msg)

    def show_view(self, view_name):
        """Switches the active frame in the content area."""
        if view_name == self.current_view_name:
            return

        # Hide current view
        if self.current_view_name:
            self.views[self.current_view_name].grid_forget()
            # Reset button state
            if self.current_view_name in self.nav_buttons:
                self.nav_buttons[self.current_view_name].configure(
                    fg_color="transparent",
                    text_color=COLORS["text_secondary"]
                )

        # Show new view
        self.views[view_name].grid(row=1, column=0, sticky="nsew", padx=30, pady=(0, 30))
        self.views[view_name].on_show() # Trigger refresh/onload logic

        # Highlight new button
        if view_name in self.nav_buttons:
            self.nav_buttons[view_name].configure(
                fg_color=COLORS["accent"],
                text_color=COLORS["bg_dark"]
            )

        # Update header title
        titles = {
            "dashboard": "Dashboard / Resumen",
            "contacts": "Clientes y Proveedores",
            "products": "Inventario / Productos",
            "billing": "Facturación y Pedidos",
            "reports": "Reportes y Gerencia"
        }
        self.header_label.configure(text=titles[view_name])
        self.current_view_name = view_name


