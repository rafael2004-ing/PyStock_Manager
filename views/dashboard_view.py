import customtkinter as ctk
from config import COLORS
from views.components.stats_card import StatsCard
from views.components.treeview import CustomTreeview

class DashboardView(ctk.CTkFrame):
    def __init__(self, parent, controller, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        self.controller = controller

        # Grid configuration
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_columnconfigure(3, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # 1. Stats Row (4 Columns)
        self.card_revenue = StatsCard(self, "Ingresos Totales", "$0.00", icon="💸", color=COLORS["success"])
        self.card_revenue.grid(row=0, column=0, padx=(0, 15), pady=(0, 20), sticky="ew")

        self.card_customers = StatsCard(self, "Clientes", "0", icon="👥", color=COLORS["accent"])
        self.card_customers.grid(row=0, column=1, padx=15, pady=(0, 20), sticky="ew")

        self.card_suppliers = StatsCard(self, "Proveedores", "0", icon="🤝", color=COLORS["accent"])
        self.card_suppliers.grid(row=0, column=2, padx=15, pady=(0, 20), sticky="ew")

        self.card_alerts = StatsCard(self, "Alertas Stock", "0", icon="⚠️", color=COLORS["danger"])
        self.card_alerts.grid(row=0, column=3, padx=(15, 0), pady=(0, 20), sticky="ew")

        # 2. Latest Orders Section
        self.table_frame = ctk.CTkFrame(
            self, 
            fg_color=COLORS["bg_light"], 
            border_color=COLORS["border"], 
            border_width=1, 
            corner_radius=12
        )
        self.table_frame.grid(row=1, column=0, columnspan=4, sticky="nsew", pady=(10, 0))
        self.table_frame.grid_rowconfigure(1, weight=1)
        self.table_frame.grid_columnconfigure(0, weight=1)

        # Header of table section
        self.table_title = ctk.CTkLabel(
            self.table_frame,
            text="ÚLTIMAS TRANSACCIONES / FACTURAS",
            font=("Segoe UI", 12, "bold"),
            text_color=COLORS["text_secondary"]
        )
        self.table_title.grid(row=0, column=0, sticky="w", padx=20, pady=(15, 10))

        # Recent Transactions Table
        cols = ("id", "date", "customer", "total")
        headings = ("ID Factura", "Fecha de Emisión", "Cliente", "Monto Total")
        self.treeview = CustomTreeview(self.table_frame, columns=cols, headings=headings)
        self.treeview.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        
        # Configure columns widths
        self.treeview.set_column_width("id", 100)
        self.treeview.set_column_width("date", 180)
        self.treeview.set_column_width("customer", 300)
        self.treeview.set_column_width("total", 150)
        
        self.treeview.set_column_anchor("id", "center")
        self.treeview.set_column_anchor("date", "center")
        self.treeview.set_column_anchor("total", "e")

    def on_show(self):
        """Loads and refreshes dashboard stats and tables."""
        # Refresh KPI figures
        stats = self.controller.get_summary_stats()
        self.card_revenue.update_value(stats["revenue"])
        self.card_customers.update_value(stats["customers"])
        self.card_suppliers.update_value(stats["suppliers"])
        
        # Alert card changes color dynamic based on value
        alert_count = stats["critical_alerts"]
        self.card_alerts.update_value(alert_count)
        if alert_count > 0:
            self.card_alerts.color_strip.configure(fg_color=COLORS["danger"])
            self.card_alerts.icon_label.configure(text_color=COLORS["danger"])
        else:
            self.card_alerts.color_strip.configure(fg_color=COLORS["success"])
            self.card_alerts.icon_label.configure(text_color=COLORS["success"])

        # Refresh table rows
        self.treeview.clear()
        orders = self.controller.get_latest_orders()
        for o in orders:
            self.treeview.insert_row((
                f"FAC-{o.id:04d}",
                o.order_date[:19],  # Trim fractional seconds
                f"{o.customer_name} ({o.customer_rif})",
                f"${o.total:,.2f}"
            ))
