import customtkinter as ctk
from tkinter import messagebox
from config import COLORS
from views.components.treeview import CustomTreeview

class CustomerSupplierView(ctk.CTkFrame):
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

        # Create tabs
        self.tab_customers = self.tabview.add("Clientes")
        self.tab_suppliers = self.tabview.add("Proveedores")

        # Build each tab's UI
        self.build_customers_tab()
        self.build_suppliers_tab()

    def on_show(self):
        """Called when this view is selected. Refreshes lists and clears forms."""
        self.update_idletasks() # Force rendering update to fix Tabview styling/dimensions
        self.refresh_customer_list()
        self.clear_customer_form()
        self.refresh_supplier_list()
        self.clear_supplier_form()

    # ==========================================
    # CLIENTES (CUSTOMERS) TAB
    # ==========================================
    def build_customers_tab(self):
        # Grid layout for customers tab
        self.tab_customers.grid_columnconfigure(0, weight=3) # List
        self.tab_customers.grid_columnconfigure(1, weight=2) # Form + History
        self.tab_customers.grid_rowconfigure(0, weight=1)

        # ---- LEFT FRAME (List + Search) ----
        left_frame = ctk.CTkFrame(self.tab_customers, fg_color="transparent")
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        left_frame.grid_rowconfigure(1, weight=1)
        left_frame.grid_columnconfigure(0, weight=1)

        # Search Panel
        search_frame = ctk.CTkFrame(left_frame, fg_color=COLORS["bg_light"], border_color=COLORS["border"], border_width=1, height=60)
        search_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        search_frame.grid_columnconfigure(0, weight=1)
        search_frame.grid_propagate(False)

        self.cust_search_entry = ctk.CTkEntry(
            search_frame, 
            placeholder_text="Buscar cliente por Nombre o RIF...",
            font=("Segoe UI", 11),
            fg_color=COLORS["bg_dark"],
            border_color=COLORS["border"],
            text_color=COLORS["text_primary"]
        )
        self.cust_search_entry.grid(row=0, column=0, sticky="ew", padx=(15, 10), pady=15)
        self.cust_search_entry.bind("<KeyRelease>", self.filter_customers)

        btn_cust_clear = ctk.CTkButton(
            search_frame,
            text="Limpiar",
            font=("Segoe UI", 11, "bold"),
            width=80,
            fg_color=COLORS["border"],
            text_color=COLORS["text_primary"],
            hover_color=COLORS["bg_dark"],
            command=self.clear_customer_search
        )
        btn_cust_clear.grid(row=0, column=1, sticky="e", padx=(0, 15), pady=15)

        # Customer List
        cols = ("id", "rif", "name", "phone", "email")
        headings = ("ID", "RIF/Cédula", "Nombre", "Teléfono", "Correo Electrónico")
        self.cust_tree = CustomTreeview(left_frame, columns=cols, headings=headings)
        self.cust_tree.grid(row=1, column=0, sticky="nsew")
        self.cust_tree.set_column_width("id", 40)
        self.cust_tree.set_column_width("rif", 100)
        self.cust_tree.set_column_width("name", 180)
        self.cust_tree.set_column_width("phone", 110)
        
        self.cust_tree.set_column_anchor("id", "center")
        self.cust_tree.bind_select(self.on_customer_selected)

        # ---- RIGHT FRAME (Form + History) ----
        right_frame = ctk.CTkFrame(self.tab_customers, fg_color="transparent")
        right_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        right_frame.grid_rowconfigure(0, weight=0) # Form
        right_frame.grid_rowconfigure(1, weight=1) # History
        right_frame.grid_columnconfigure(0, weight=1)

        # Form Frame
        form_frame = ctk.CTkFrame(right_frame, fg_color=COLORS["bg_light"], border_color=COLORS["border"], border_width=1, corner_radius=12)
        form_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 10))
        form_frame.grid_columnconfigure(1, weight=1)

        form_title = ctk.CTkLabel(form_frame, text="DATOS DEL CLIENTE", font=("Segoe UI", 12, "bold"), text_color=COLORS["accent"])
        form_title.grid(row=0, column=0, columnspan=2, sticky="w", padx=20, pady=(15, 10))

        # Fields
        self.cust_inputs = {}
        fields = [
            ("id", "ID (Autogenerado)", True),
            ("rif", "RIF / Cédula *", False),
            ("name", "Nombre / Razón Social *", False),
            ("phone", "Teléfono", False),
            ("email", "Correo Electrónico", False),
            ("address", "Dirección", False)
        ]

        for i, (key, label_text, readonly) in enumerate(fields, start=1):
            lbl = ctk.CTkLabel(form_frame, text=label_text, font=("Segoe UI", 10, "bold"), text_color=COLORS["text_secondary"])
            lbl.grid(row=i, column=0, sticky="w", padx=20, pady=4)
            
            entry = ctk.CTkEntry(
                form_frame,
                font=("Segoe UI", 11),
                fg_color=COLORS["bg_dark"] if not readonly else COLORS["border"],
                border_color=COLORS["border"],
                text_color=COLORS["text_primary"]
            )
            if readonly:
                entry.configure(state="readonly")
            entry.grid(row=i, column=1, sticky="ew", padx=(0, 20), pady=4)
            self.cust_inputs[key] = entry

        # Form Buttons
        btn_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        btn_frame.grid(row=len(fields)+1, column=0, columnspan=2, sticky="ew", padx=20, pady=(15, 15))
        btn_frame.grid_columnconfigure((0, 1, 2), weight=1)

        self.btn_cust_save = ctk.CTkButton(
            btn_frame, text="Guardar", font=("Segoe UI", 11, "bold"), fg_color=COLORS["success"], text_color=COLORS["bg_dark"], hover_color="#8ed189", command=self.save_customer
        )
        self.btn_cust_save.grid(row=0, column=0, padx=2)

        self.btn_cust_new = ctk.CTkButton(
            btn_frame, text="Limpiar", font=("Segoe UI", 11, "bold"), fg_color=COLORS["border"], text_color=COLORS["text_primary"], hover_color=COLORS["bg_dark"], command=self.clear_customer_form
        )
        self.btn_cust_new.grid(row=0, column=1, padx=2)

        self.btn_cust_delete = ctk.CTkButton(
            btn_frame, text="Eliminar", font=("Segoe UI", 11, "bold"), fg_color=COLORS["danger"], text_color=COLORS["bg_dark"], hover_color="#e57c96", command=self.delete_customer
        )
        self.btn_cust_delete.grid(row=0, column=2, padx=2)

        # History Frame
        hist_frame = ctk.CTkFrame(right_frame, fg_color=COLORS["bg_light"], border_color=COLORS["border"], border_width=1, corner_radius=12)
        hist_frame.grid(row=1, column=0, sticky="nsew", pady=(10, 0))
        hist_frame.grid_rowconfigure(1, weight=1)
        hist_frame.grid_columnconfigure(0, weight=1)

        hist_title = ctk.CTkLabel(hist_frame, text="HISTORIAL OPERATIVO (VENTAS)", font=("Segoe UI", 11, "bold"), text_color=COLORS["text_secondary"])
        hist_title.grid(row=0, column=0, sticky="w", padx=20, pady=(15, 5))

        self.cust_hist_tree = CustomTreeview(hist_frame, columns=("id", "date", "total"), headings=("Factura", "Fecha", "Monto"))
        self.cust_hist_tree.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 15))
        self.cust_hist_tree.set_column_width("id", 80)
        self.cust_hist_tree.set_column_width("date", 120)
        self.cust_hist_tree.set_column_anchor("id", "center")
        self.cust_hist_tree.set_column_anchor("total", "e")

    # ==========================================
    # PROVEEDORES (SUPPLIERS) TAB
    # ==========================================
    def build_suppliers_tab(self):
        # Grid layout for suppliers tab
        self.tab_suppliers.grid_columnconfigure(0, weight=3) # List
        self.tab_suppliers.grid_columnconfigure(1, weight=2) # Form + History
        self.tab_suppliers.grid_rowconfigure(0, weight=1)

        # ---- LEFT FRAME (List + Search) ----
        left_frame = ctk.CTkFrame(self.tab_suppliers, fg_color="transparent")
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        left_frame.grid_rowconfigure(1, weight=1)
        left_frame.grid_columnconfigure(0, weight=1)

        # Search Panel
        search_frame = ctk.CTkFrame(left_frame, fg_color=COLORS["bg_light"], border_color=COLORS["border"], border_width=1, height=60)
        search_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        search_frame.grid_columnconfigure(0, weight=1)
        search_frame.grid_propagate(False)

        self.supp_search_entry = ctk.CTkEntry(
            search_frame, 
            placeholder_text="Buscar proveedor por Nombre o RIF...",
            font=("Segoe UI", 11),
            fg_color=COLORS["bg_dark"],
            border_color=COLORS["border"],
            text_color=COLORS["text_primary"]
        )
        self.supp_search_entry.grid(row=0, column=0, sticky="ew", padx=(15, 10), pady=15)
        self.supp_search_entry.bind("<KeyRelease>", self.filter_suppliers)

        btn_supp_clear = ctk.CTkButton(
            search_frame,
            text="Limpiar",
            font=("Segoe UI", 11, "bold"),
            width=80,
            fg_color=COLORS["border"],
            text_color=COLORS["text_primary"],
            hover_color=COLORS["bg_dark"],
            command=self.clear_supplier_search
        )
        btn_supp_clear.grid(row=0, column=1, sticky="e", padx=(0, 15), pady=15)

        # Supplier List
        cols = ("id", "rif", "name", "phone", "email")
        headings = ("ID", "RIF/Cédula", "Nombre", "Teléfono", "Correo Electrónico")
        self.supp_tree = CustomTreeview(left_frame, columns=cols, headings=headings)
        self.supp_tree.grid(row=1, column=0, sticky="nsew")
        self.supp_tree.set_column_width("id", 40)
        self.supp_tree.set_column_width("rif", 100)
        self.supp_tree.set_column_width("name", 180)
        self.supp_tree.set_column_width("phone", 110)
        
        self.supp_tree.set_column_anchor("id", "center")
        self.supp_tree.bind_select(self.on_supplier_selected)

        # ---- RIGHT FRAME (Form + History) ----
        right_frame = ctk.CTkFrame(self.tab_suppliers, fg_color="transparent")
        right_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        right_frame.grid_rowconfigure(0, weight=0) # Form
        right_frame.grid_rowconfigure(1, weight=1) # History
        right_frame.grid_columnconfigure(0, weight=1)

        # Form Frame
        form_frame = ctk.CTkFrame(right_frame, fg_color=COLORS["bg_light"], border_color=COLORS["border"], border_width=1, corner_radius=12)
        form_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 10))
        form_frame.grid_columnconfigure(1, weight=1)

        form_title = ctk.CTkLabel(form_frame, text="DATOS DEL PROVEEDOR", font=("Segoe UI", 12, "bold"), text_color=COLORS["accent"])
        form_title.grid(row=0, column=0, columnspan=2, sticky="w", padx=20, pady=(15, 10))

        # Fields
        self.supp_inputs = {}
        fields = [
            ("id", "ID (Autogenerado)", True),
            ("rif", "RIF / Cédula *", False),
            ("name", "Nombre / Razón Social *", False),
            ("phone", "Teléfono", False),
            ("email", "Correo Electrónico", False),
            ("address", "Dirección", False)
        ]

        for i, (key, label_text, readonly) in enumerate(fields, start=1):
            lbl = ctk.CTkLabel(form_frame, text=label_text, font=("Segoe UI", 10, "bold"), text_color=COLORS["text_secondary"])
            lbl.grid(row=i, column=0, sticky="w", padx=20, pady=4)
            
            entry = ctk.CTkEntry(
                form_frame,
                font=("Segoe UI", 11),
                fg_color=COLORS["bg_dark"] if not readonly else COLORS["border"],
                border_color=COLORS["border"],
                text_color=COLORS["text_primary"]
            )
            if readonly:
                entry.configure(state="readonly")
            entry.grid(row=i, column=1, sticky="ew", padx=(0, 20), pady=4)
            self.supp_inputs[key] = entry

        # Form Buttons
        btn_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        btn_frame.grid(row=len(fields)+1, column=0, columnspan=2, sticky="ew", padx=20, pady=(15, 15))
        btn_frame.grid_columnconfigure((0, 1, 2), weight=1)

        self.btn_supp_save = ctk.CTkButton(
            btn_frame, text="Guardar", font=("Segoe UI", 11, "bold"), fg_color=COLORS["success"], text_color=COLORS["bg_dark"], hover_color="#8ed189", command=self.save_supplier
        )
        self.btn_supp_save.grid(row=0, column=0, padx=2)

        self.btn_supp_new = ctk.CTkButton(
            btn_frame, text="Limpiar", font=("Segoe UI", 11, "bold"), fg_color=COLORS["border"], text_color=COLORS["text_primary"], hover_color=COLORS["bg_dark"], command=self.clear_supplier_form
        )
        self.btn_supp_new.grid(row=0, column=1, padx=2)

        self.btn_supp_delete = ctk.CTkButton(
            btn_frame, text="Eliminar", font=("Segoe UI", 11, "bold"), fg_color=COLORS["danger"], text_color=COLORS["bg_dark"], hover_color="#e57c96", command=self.delete_supplier
        )
        self.btn_supp_delete.grid(row=0, column=2, padx=2)

        # History Frame
        hist_frame = ctk.CTkFrame(right_frame, fg_color=COLORS["bg_light"], border_color=COLORS["border"], border_width=1, corner_radius=12)
        hist_frame.grid(row=1, column=0, sticky="nsew", pady=(10, 0))
        hist_frame.grid_rowconfigure(1, weight=1)
        hist_frame.grid_columnconfigure(0, weight=1)

        hist_title = ctk.CTkLabel(hist_frame, text="HISTORIAL DE COMPRAS (SURTIDO)", font=("Segoe UI", 11, "bold"), text_color=COLORS["text_secondary"])
        hist_title.grid(row=0, column=0, sticky="w", padx=20, pady=(15, 5))

        self.supp_hist_tree = CustomTreeview(hist_frame, columns=("id", "date", "total"), headings=("Compra ID", "Fecha de Surtido", "Total"))
        self.supp_hist_tree.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 15))
        self.supp_hist_tree.set_column_width("id", 80)
        self.supp_hist_tree.set_column_width("date", 120)
        self.supp_hist_tree.set_column_anchor("id", "center")
        self.supp_hist_tree.set_column_anchor("total", "e")

    # ==========================================
    # LOGIC - CUSTOMERS
    # ==========================================
    def refresh_customer_list(self):
        self.cust_tree.clear()
        self.all_customers = self.controller.get_customers()
        for c in self.all_customers:
            self.cust_tree.insert_row((c.id, c.rif_cedula, c.name, c.phone, c.email), item_id=str(c.id))

    def filter_customers(self, event=None):
        query = self.cust_search_entry.get().lower()
        self.cust_tree.clear()
        for c in self.all_customers:
            if query in c.name.lower() or query in c.rif_cedula.lower():
                self.cust_tree.insert_row((c.id, c.rif_cedula, c.name, c.phone, c.email), item_id=str(c.id))

    def clear_customer_search(self):
        self.cust_search_entry.delete(0, "end")
        self.refresh_customer_list()

    def on_customer_selected(self, selection):
        values, item_id = selection
        if not values:
            return
        
        # Load form
        # values index: 0=id, 1=rif, 2=name, 3=phone, 4=email
        # We need to find the address as well, so we query or read from all_customers
        customer = next((c for c in self.all_customers if str(c.id) == item_id), None)
        if not customer:
            return

        self.cust_inputs["id"].configure(state="normal")
        self.cust_inputs["id"].delete(0, "end")
        self.cust_inputs["id"].insert(0, str(customer.id))
        self.cust_inputs["id"].configure(state="readonly")

        for key in ("rif", "name", "phone", "email", "address"):
            self.cust_inputs[key].delete(0, "end")
            attr = "rif_cedula" if key == "rif" else key
            self.cust_inputs[key].insert(0, getattr(customer, attr) or "")

        # Load history
        self.cust_hist_tree.clear()
        history = self.controller.get_customer_history(customer.id)
        for h in history:
            self.cust_hist_tree.insert_row((
                f"FAC-{h['id']:04d}",
                h["order_date"][:10],
                f"${h['total']:,.2f}"
            ))

    def clear_customer_form(self):
        self.cust_inputs["id"].configure(state="normal")
        for entry in self.cust_inputs.values():
            entry.delete(0, "end")
        self.cust_inputs["id"].configure(state="readonly")
        self.cust_hist_tree.clear()

    def save_customer(self):
        customer_id_str = self.cust_inputs["id"].get()
        customer_id = int(customer_id_str) if customer_id_str else None
        
        try:
            self.controller.save_customer(
                customer_id=customer_id,
                rif=self.cust_inputs["rif"].get(),
                name=self.cust_inputs["name"].get(),
                phone=self.cust_inputs["phone"].get(),
                email=self.cust_inputs["email"].get(),
                address=self.cust_inputs["address"].get()
            )
            messagebox.showinfo("Éxito", "Cliente guardado correctamente.")
            self.refresh_customer_list()
            self.clear_customer_form()
        except ValueError as ve:
            messagebox.showerror("Error de Validación", str(ve))
        except Exception as e:
            messagebox.showerror("Error de Base de Datos", f"No se pudo guardar el cliente: {str(e)}")

    def delete_customer(self):
        customer_id_str = self.cust_inputs["id"].get()
        if not customer_id_str:
            messagebox.showwarning("Atención", "Seleccione un cliente de la lista para eliminar.")
            return
            
        customer_id = int(customer_id_str)
        if messagebox.askyesno("Confirmar Eliminación", "¿Está seguro de que desea eliminar este cliente?"):
            try:
                self.controller.delete_customer(customer_id)
                messagebox.showinfo("Éxito", "Cliente eliminado correctamente.")
                self.refresh_customer_list()
                self.clear_customer_form()
            except ValueError as ve:
                messagebox.showerror("Restricción de Integridad", str(ve))

    # ==========================================
    # LOGIC - SUPPLIERS
    # ==========================================
    def refresh_supplier_list(self):
        self.supp_tree.clear()
        self.all_suppliers = self.controller.get_suppliers()
        for s in self.all_suppliers:
            self.supp_tree.insert_row((s.id, s.rif_cedula, s.name, s.phone, s.email), item_id=str(s.id))

    def filter_suppliers(self, event=None):
        query = self.supp_search_entry.get().lower()
        self.supp_tree.clear()
        for s in self.all_suppliers:
            if query in s.name.lower() or query in s.rif_cedula.lower():
                self.supp_tree.insert_row((s.id, s.rif_cedula, s.name, s.phone, s.email), item_id=str(s.id))

    def clear_supplier_search(self):
        self.supp_search_entry.delete(0, "end")
        self.refresh_supplier_list()

    def on_supplier_selected(self, selection):
        values, item_id = selection
        if not values:
            return
        
        supplier = next((s for s in self.all_suppliers if str(s.id) == item_id), None)
        if not supplier:
            return

        self.supp_inputs["id"].configure(state="normal")
        self.supp_inputs["id"].delete(0, "end")
        self.supp_inputs["id"].insert(0, str(supplier.id))
        self.supp_inputs["id"].configure(state="readonly")

        for key in ("rif", "name", "phone", "email", "address"):
            self.supp_inputs[key].delete(0, "end")
            attr = "rif_cedula" if key == "rif" else key
            self.supp_inputs[key].insert(0, getattr(supplier, attr) or "")

        # Load history
        self.supp_hist_tree.clear()
        history = self.controller.get_supplier_history(supplier.id)
        for h in history:
            self.supp_hist_tree.insert_row((
                f"COM-{h['id']:04d}",
                h["purchase_date"][:10],
                f"${h['total']:,.2f}"
            ))

    def clear_supplier_form(self):
        self.supp_inputs["id"].configure(state="normal")
        for entry in self.supp_inputs.values():
            entry.delete(0, "end")
        self.supp_inputs["id"].configure(state="readonly")
        self.supp_hist_tree.clear()

    def save_supplier(self):
        supplier_id_str = self.supp_inputs["id"].get()
        supplier_id = int(supplier_id_str) if supplier_id_str else None
        
        try:
            self.controller.save_supplier(
                supplier_id=supplier_id,
                rif=self.supp_inputs["rif"].get(),
                name=self.supp_inputs["name"].get(),
                phone=self.supp_inputs["phone"].get(),
                email=self.supp_inputs["email"].get(),
                address=self.supp_inputs["address"].get()
            )
            messagebox.showinfo("Éxito", "Proveedor guardado correctamente.")
            self.refresh_supplier_list()
            self.clear_supplier_form()
        except ValueError as ve:
            messagebox.showerror("Error de Validación", str(ve))
        except Exception as e:
            messagebox.showerror("Error de Base de Datos", f"No se pudo guardar el proveedor: {str(e)}")

    def delete_supplier(self):
        supplier_id_str = self.supp_inputs["id"].get()
        if not supplier_id_str:
            messagebox.showwarning("Atención", "Seleccione un proveedor de la lista para eliminar.")
            return
            
        supplier_id = int(supplier_id_str)
        if messagebox.askyesno("Confirmar Eliminación", "¿Está seguro de que desea eliminar este proveedor?"):
            try:
                self.controller.delete_supplier(supplier_id)
                messagebox.showinfo("Éxito", "Proveedor eliminado correctamente.")
                self.refresh_supplier_list()
                self.clear_supplier_form()
            except ValueError as ve:
                messagebox.showerror("Restricción de Integridad", str(ve))
