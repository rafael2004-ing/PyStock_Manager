import customtkinter as ctk
from datetime import datetime, timedelta
from tkinter import messagebox
from config import COLORS
from views.components.treeview import CustomTreeview
from views.components.stats_card import StatsCard
from views.invoice_detail_view import InvoiceDetailWindow
from models.order import Order
from models.invoice import Invoice


class ReportView(ctk.CTkFrame):
    def __init__(self, parent, controller, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        self.controller = controller

        # Grid configuration
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Tabview
        self.tabview = ctk.CTkTabview(
            self,
            fg_color=COLORS["bg_medium"],
            segmented_button_fg_color=COLORS["bg_dark"],
            segmented_button_selected_color=COLORS["accent"],
            segmented_button_selected_hover_color=COLORS["accent_hover"],
            segmented_button_unselected_color=COLORS["bg_light"],
            segmented_button_unselected_hover_color=COLORS["border"],
            text_color=COLORS["text_primary"]
        )
        self.tabview.grid(row=0, column=0, sticky="nsew")

        self.tab_stock = self.tabview.add("Inventario Crítico")
        self.tab_sales = self.tabview.add("Resumen de Ventas")
        self.tab_invoices = self.tabview.add("Historial de Facturas")

        # Build tabs
        self.build_stock_tab()
        self.build_sales_tab()
        self.build_invoices_tab()

    def on_show(self):
        """Refreshes reports when shown."""
        self.update_idletasks() # Force rendering update to fix Tabview styling/dimensions
        self.refresh_critical_stock()
        self.generate_sales_report()
        self.refresh_invoices()

    # ==========================================
    # TAB: INVENTARIO CRITICO (CRITICAL STOCK)
    # ==========================================
    def build_stock_tab(self):
        self.tab_stock.grid_columnconfigure(0, weight=1)
        self.tab_stock.grid_rowconfigure(1, weight=1)

        # Description Header
        desc_frame = ctk.CTkFrame(self.tab_stock, fg_color="transparent")
        desc_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        desc_frame.grid_columnconfigure(0, weight=1)

        desc_label = ctk.CTkLabel(
            desc_frame,
            text="PRODUCTOS CON STOCK POR DEBAJO DEL MÍNIMO REQUERIDO",
            font=("Segoe UI", 12, "bold"),
            text_color=COLORS["danger"]
        )
        desc_label.grid(row=0, column=0, sticky="w")

        btn_refresh = ctk.CTkButton(
            desc_frame,
            text="Refrescar Lista",
            font=("Segoe UI", 11, "bold"),
            width=120,
            fg_color=COLORS["bg_light"],
            border_color=COLORS["border"],
            border_width=1,
            text_color=COLORS["text_primary"],
            hover_color=COLORS["border"],
            command=self.refresh_critical_stock
        )
        btn_refresh.grid(row=0, column=1, sticky="e", padx=(0, 10))

        btn_export_stock = ctk.CTkButton(
            desc_frame,
            text="Exportar CSV  📥",
            font=("Segoe UI", 11, "bold"),
            width=120,
            fg_color=COLORS["success"],
            text_color=COLORS["bg_dark"],
            hover_color="#8ed189",
            command=self.export_critical_stock
        )
        btn_export_stock.grid(row=0, column=2, sticky="e")

        # Table
        cols = ("id", "code", "name", "stock", "min", "p_price", "s_price")
        headings = ("ID", "Código", "Nombre del Producto", "Stock Actual", "Mínimo Alerta", "P. Compra", "P. Venta")
        self.stock_tree = CustomTreeview(self.tab_stock, columns=cols, headings=headings)
        self.stock_tree.grid(row=1, column=0, sticky="nsew")
        
        self.stock_tree.set_column_width("id", 40)
        self.stock_tree.set_column_width("code", 90)
        self.stock_tree.set_column_width("name", 250)
        self.stock_tree.set_column_width("stock", 80)
        self.stock_tree.set_column_width("min", 80)
        
        self.stock_tree.set_column_anchor("id", "center")
        self.stock_tree.set_column_anchor("code", "center")
        self.stock_tree.set_column_anchor("stock", "center")
        self.stock_tree.set_column_anchor("min", "center")
        self.stock_tree.set_column_anchor("p_price", "e")
        self.stock_tree.set_column_anchor("s_price", "e")

    def refresh_critical_stock(self):
        """Loads critical stock products."""
        self.stock_tree.clear()
        critical_products = self.controller.get_critical_stock()
        for p in critical_products:
            self.stock_tree.insert_row((
                p.id,
                p.code,
                p.name,
                f"⚠️ {p.stock}",
                p.min_stock,
                f"${p.purchase_price:,.2f}",
                f"${p.sale_price:,.2f}"
            ), tags=("warning",))

    # ==========================================
    # TAB: RESUMEN DE VENTAS (SALES REPORT)
    # ==========================================
    def build_sales_tab(self):
        self.tab_sales.grid_columnconfigure(0, weight=1)
        self.tab_sales.grid_rowconfigure(2, weight=1)

        # 1. Filters Header Frame
        filters_frame = ctk.CTkFrame(
            self.tab_sales, 
            fg_color=COLORS["bg_light"], 
            border_color=COLORS["border"], 
            border_width=1, 
            corner_radius=12,
            height=65
        )
        filters_frame.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        filters_frame.grid_propagate(False)

        # Date pickers labels & entries
        # Start Date
        lbl_start = ctk.CTkLabel(filters_frame, text="FECHA INICIO (AAAA-MM-DD):", font=("Segoe UI", 10, "bold"), text_color=COLORS["text_secondary"])
        lbl_start.grid(row=0, column=0, padx=(20, 5), pady=18, sticky="w")
        
        self.start_date_entry = ctk.CTkEntry(
            filters_frame,
            width=100,
            font=("Segoe UI", 11),
            fg_color=COLORS["bg_dark"],
            border_color=COLORS["border"],
            text_color=COLORS["text_primary"]
        )
        self.start_date_entry.grid(row=0, column=1, padx=5, pady=18, sticky="w")
        
        # Default start date: 30 days ago
        default_start = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        self.start_date_entry.insert(0, default_start)

        # End Date
        lbl_end = ctk.CTkLabel(filters_frame, text="FECHA FIN (AAAA-MM-DD):", font=("Segoe UI", 10, "bold"), text_color=COLORS["text_secondary"])
        lbl_end.grid(row=0, column=2, padx=(20, 5), pady=18, sticky="w")
        
        self.end_date_entry = ctk.CTkEntry(
            filters_frame,
            width=100,
            font=("Segoe UI", 11),
            fg_color=COLORS["bg_dark"],
            border_color=COLORS["border"],
            text_color=COLORS["text_primary"]
        )
        self.end_date_entry.grid(row=0, column=3, padx=5, pady=18, sticky="w")
        
        # Default end date: today
        default_end = datetime.now().strftime("%Y-%m-%d")
        self.end_date_entry.insert(0, default_end)

        # Filter Button
        btn_filter = ctk.CTkButton(
            filters_frame,
            text="Generar  📊",
            font=("Segoe UI", 11, "bold"),
            width=100,
            fg_color=COLORS["accent"],
            text_color=COLORS["bg_dark"],
            hover_color=COLORS["accent_hover"],
            command=self.generate_sales_report
        )
        btn_filter.grid(row=0, column=4, padx=(15, 5), pady=18, sticky="e")

        # Export Button
        btn_export = ctk.CTkButton(
            filters_frame,
            text="Exportar  📥",
            font=("Segoe UI", 11, "bold"),
            width=100,
            fg_color=COLORS["success"],
            text_color=COLORS["bg_dark"],
            hover_color="#8ed189",
            command=self.export_sales_report
        )
        btn_export.grid(row=0, column=5, padx=(5, 20), pady=18, sticky="e")

        # 2. Stats cards row (Mini Dashboard inside)
        self.stats_row_frame = ctk.CTkFrame(self.tab_sales, fg_color="transparent")
        self.stats_row_frame.grid(row=1, column=0, sticky="ew", pady=(0, 15))
        self.stats_row_frame.grid_columnconfigure((0, 1, 2), weight=1)

        self.report_card_total = StatsCard(self.stats_row_frame, "Ventas Totales", "$0.00", icon="💰", color=COLORS["success"])
        self.report_card_total.grid(row=0, column=0, padx=(0, 10), sticky="ew")

        self.report_card_qty = StatsCard(self.stats_row_frame, "Nro. de Facturas", "0", icon="🧾", color=COLORS["accent"])
        self.report_card_qty.grid(row=0, column=1, padx=10, sticky="ew")

        self.report_card_avg = StatsCard(self.stats_row_frame, "Promedio Ticket", "$0.00", icon="📈", color=COLORS["accent"])
        self.report_card_avg.grid(row=0, column=2, padx=(10, 0), sticky="ew")

        # 3. Sales Results Table
        sales_cols = ("id", "date", "customer", "subtotal", "tax", "total")
        sales_headings = ("Factura ID", "Fecha Emisión", "Cliente", "Subtotal", "Impuesto (16%)", "Total Facturado")
        self.sales_tree = CustomTreeview(self.tab_sales, columns=sales_cols, headings=sales_headings)
        self.sales_tree.grid(row=2, column=0, sticky="nsew")
        
        self.sales_tree.set_column_width("id", 80)
        self.sales_tree.set_column_width("date", 150)
        self.sales_tree.set_column_width("customer", 250)
        self.sales_tree.set_column_width("subtotal", 100)
        self.sales_tree.set_column_width("tax", 100)
        self.sales_tree.set_column_width("total", 100)

        self.sales_tree.set_column_anchor("id", "center")
        self.sales_tree.set_column_anchor("date", "center")
        self.sales_tree.set_column_anchor("subtotal", "e")
        self.sales_tree.set_column_anchor("tax", "e")
        self.sales_tree.set_column_anchor("total", "e")

    def generate_sales_report(self):
        """Fetches orders in selected date range and updates UI metrics and table."""
        start_date = self.start_date_entry.get().strip()
        end_date = self.end_date_entry.get().strip()

        try:
            report = self.controller.get_sales_report(start_date, end_date)
            
            # Update metric cards
            self.report_card_total.update_value(report["total_revenue"])
            self.report_card_qty.update_value(report["order_count"])
            self.report_card_avg.update_value(report["average_order"])

            # Update Table rows
            self.sales_tree.clear()
            for o in report["orders"]:
                self.sales_tree.insert_row((
                    f"FAC-{o.id:04d}",
                    o.order_date[:19],
                    f"{o.customer_name} ({o.customer_rif})",
                    f"${o.subtotal:,.2f}",
                    f"${o.tax:,.2f}",
                    f"${o.total:,.2f}"
                ))
        except ValueError as ve:
            messagebox.showerror("Error de Rango de Fechas", str(ve))
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo generar el reporte: {str(e)}")

    def export_sales_report(self):
        """Exports the currently displayed sales report to a CSV file."""
        import csv
        from tkinter import filedialog
        
        start_date = self.start_date_entry.get().strip()
        end_date = self.end_date_entry.get().strip()
        
        try:
            report = self.controller.get_sales_report(start_date, end_date)
            if not report["orders"]:
                messagebox.showwarning("Sin Datos", "No hay datos en el reporte para exportar.")
                return
                
            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("Archivos CSV", "*.csv")],
                initialfile=f"reporte_ventas_{start_date}_a_{end_date}.csv",
                title="Guardar Reporte de Ventas"
            )
            if not file_path:
                return
                
            with open(file_path, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f)
                # Write metadata
                writer.writerow(["REPORTE DE VENTAS"])
                writer.writerow([f"Período: {start_date} al {end_date}"])
                writer.writerow([])
                writer.writerow(["Resumen General"])
                writer.writerow(["Facturas Emitidas", report["order_count"]])
                writer.writerow(["Ingreso Total", report["total_revenue"]])
                writer.writerow(["Ticket Promedio", report["average_order"]])
                writer.writerow([])
                # Write headers
                writer.writerow(["Factura ID", "Fecha Emisión", "Cliente", "Subtotal ($)", "Impuesto ($)", "Total ($)"])
                # Write items
                for o in report["orders"]:
                    writer.writerow([
                        f"FAC-{o.id:04d}",
                        o.order_date[:19],
                        f"{o.customer_name} ({o.customer_rif})",
                        f"{o.subtotal:.2f}",
                        f"{o.tax:.2f}",
                        f"{o.total:.2f}"
                    ])
                    
            messagebox.showinfo("Éxito", f"Reporte exportado correctamente a:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo exportar el reporte: {str(e)}")

    def export_critical_stock(self):
        """Exports the current critical stock list to a CSV file."""
        import csv
        from tkinter import filedialog
        
        try:
            critical_products = self.controller.get_critical_stock()
            if not critical_products:
                messagebox.showinfo("Inventario Al Día", "No hay productos con stock crítico para exportar.")
                return
                
            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("Archivos CSV", "*.csv")],
                initialfile="reporte_inventario_critico.csv",
                title="Guardar Reporte de Inventario Crítico"
            )
            if not file_path:
                return
                
            with open(file_path, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f)
                writer.writerow(["REPORTE DE INVENTARIO CRÍTICO"])
                writer.writerow([f"Fecha de Generación: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"])
                writer.writerow([])
                writer.writerow(["ID", "Código", "Nombre del Producto", "Stock Actual", "Mínimo de Alerta", "P. Compra ($)", "P. Venta ($)"])
                for p in critical_products:
                    writer.writerow([
                        p.id,
                        p.code,
                        p.name,
                        p.stock,
                        p.min_stock,
                        f"{p.purchase_price:.2f}",
                        f"{p.sale_price:.2f}"
                    ])
                    
            messagebox.showinfo("Éxito", f"Reporte exportado correctamente a:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo exportar el reporte: {str(e)}")

    # ==========================================
    # TAB: HISTORIAL DE FACTURAS (INVOICE HISTORY)
    # ==========================================
    def build_invoices_tab(self):
        self.tab_invoices.grid_columnconfigure(0, weight=1)
        self.tab_invoices.grid_rowconfigure(1, weight=1)

        # Top Control Frame (Search + View Details Button)
        ctrl_frame = ctk.CTkFrame(
            self.tab_invoices, 
            fg_color=COLORS["bg_light"], 
            border_color=COLORS["border"], 
            border_width=1, 
            corner_radius=12,
            height=60
        )
        ctrl_frame.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        ctrl_frame.grid_propagate(False)

        # Search Entry
        lbl_search = ctk.CTkLabel(ctrl_frame, text="BUSCAR:", font=("Segoe UI", 10, "bold"), text_color=COLORS["text_secondary"])
        lbl_search.grid(row=0, column=0, padx=(20, 5), pady=15, sticky="w")

        self.invoice_search_entry = ctk.CTkEntry(
            ctrl_frame,
            placeholder_text="Nº Factura, Cliente o RIF...",
            font=("Segoe UI", 11),
            fg_color=COLORS["bg_dark"],
            border_color=COLORS["border"],
            text_color=COLORS["text_primary"],
            width=250
        )
        self.invoice_search_entry.grid(row=0, column=1, padx=5, pady=15, sticky="w")
        self.invoice_search_entry.bind("<KeyRelease>", self.filter_invoices)

        # View Details Button
        self.btn_view_invoice = ctk.CTkButton(
            ctrl_frame,
            text="Ver Detalle Factura  🔍",
            font=("Segoe UI", 11, "bold"),
            width=160,
            fg_color=COLORS["accent"],
            text_color=COLORS["bg_dark"],
            hover_color=COLORS["accent_hover"],
            command=self.view_invoice_detail
        )
        self.btn_view_invoice.grid(row=0, column=2, padx=(20, 20), pady=15, sticky="e")
        ctrl_frame.grid_columnconfigure(2, weight=1) # Push button to the right

        # Invoices Table
        inv_cols = ("id", "number", "date", "customer", "subtotal", "tax", "total", "order_id")
        inv_headings = ("ID", "Nº Factura", "Fecha de Emisión", "Cliente", "Subtotal", "Impuesto (16%)", "Total Facturado", "Order ID")
        
        self.invoices_tree = CustomTreeview(self.tab_invoices, columns=inv_cols, headings=inv_headings)
        self.invoices_tree.grid(row=1, column=0, sticky="nsew")
        
        # Configure widths
        self.invoices_tree.set_column_width("id", 40)
        self.invoices_tree.set_column_width("number", 90)
        self.invoices_tree.set_column_width("date", 150)
        self.invoices_tree.set_column_width("customer", 250)
        self.invoices_tree.set_column_width("subtotal", 90)
        self.invoices_tree.set_column_width("tax", 90)
        self.invoices_tree.set_column_width("total", 100)
        self.invoices_tree.set_column_width("order_id", 0) # Hidden / Meta column

        # Alignments
        self.invoices_tree.set_column_anchor("id", "center")
        self.invoices_tree.set_column_anchor("number", "center")
        self.invoices_tree.set_column_anchor("date", "center")
        self.invoices_tree.set_column_anchor("subtotal", "e")
        self.invoices_tree.set_column_anchor("tax", "e")
        self.invoices_tree.set_column_anchor("total", "e")
        
        # Bind double-click
        self.invoices_tree.bind_double_click(lambda sel: self.view_invoice_detail())

        # Raw data cache for client-side search/filtering
        self.all_invoices_data = []

    def refresh_invoices(self):
        """Loads all invoices from database."""
        self.invoices_tree.clear()
        try:
            self.all_invoices_data = self.controller.get_all_invoices()
            self.populate_invoices_table(self.all_invoices_data)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el historial de facturas: {str(e)}")

    def populate_invoices_table(self, data):
        self.invoices_tree.clear()
        for row in data:
            self.invoices_tree.insert_row((
                row["id"],
                row["invoice_number"],
                row["invoice_date"][:19] if row["invoice_date"] else "N/A",
                f"{row['customer_name']} ({row['customer_rif']})",
                f"${row['subtotal']:,.2f}",
                f"${row['tax']:,.2f}",
                f"${row['total']:,.2f}",
                row["order_id"]
            ), item_id=str(row["id"]))

    def filter_invoices(self, event=None):
        query = self.invoice_search_entry.get().strip().lower()
        if not query:
            self.populate_invoices_table(self.all_invoices_data)
            return

        filtered = []
        for row in self.all_invoices_data:
            inv_num = str(row["invoice_number"]).lower()
            cust_name = str(row["customer_name"]).lower()
            cust_rif = str(row["customer_rif"]).lower()
            if query in inv_num or query in cust_name or query in cust_rif:
                filtered.append(row)
        
        self.populate_invoices_table(filtered)

    def view_invoice_detail(self):
        values, item_id = self.invoices_tree.get_selected_item()
        if not values or not item_id:
            messagebox.showwarning("Atención", "Por favor, seleccione una factura de la lista.")
            return

        # Get order_id from index 7 (inv_cols order: id, number, date, customer, subtotal, tax, total, order_id)
        order_id = int(values[7])
        
        try:
            # Load full order
            full_order = Order.get_by_id(order_id)
            
            # Find the invoice details from self.all_invoices_data
            invoice_row = next((r for r in self.all_invoices_data if str(r["id"]) == item_id), None)
            if not invoice_row:
                messagebox.showerror("Error", "No se encontraron los datos de la factura.")
                return
                
            # Construct Invoice object
            invoice = Invoice(
                id=invoice_row["id"],
                order_id=invoice_row["order_id"],
                invoice_number=invoice_row["invoice_number"],
                invoice_date=invoice_row["invoice_date"],
                subtotal=invoice_row["subtotal"],
                tax=invoice_row["tax"],
                total=invoice_row["total"]
            )
            
            # Open the digital invoice window
            InvoiceDetailWindow(self.winfo_toplevel(), full_order, invoice)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el detalle de la factura: {str(e)}")
