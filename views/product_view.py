import customtkinter as ctk
from tkinter import messagebox
from config import COLORS
from views.components.treeview import CustomTreeview

class ProductView(ctk.CTkFrame):
    def __init__(self, parent, controller, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        self.controller = controller

        # Layout configuration
        self.grid_columnconfigure(0, weight=3) # Product List
        self.grid_columnconfigure(1, weight=2) # Details Form
        self.grid_rowconfigure(0, weight=1)

        # ---- LEFT COLUMN: Product Catalog ----
        left_frame = ctk.CTkFrame(self, fg_color="transparent")
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        left_frame.grid_rowconfigure(1, weight=1)
        left_frame.grid_columnconfigure(0, weight=1)

        # Search Panel
        search_frame = ctk.CTkFrame(left_frame, fg_color=COLORS["bg_light"], border_color=COLORS["border"], border_width=1, height=60)
        search_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        search_frame.grid_columnconfigure(0, weight=1)
        search_frame.grid_propagate(False)

        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Buscar producto por Nombre o Código...",
            font=("Segoe UI", 11),
            fg_color=COLORS["bg_dark"],
            border_color=COLORS["border"],
            text_color=COLORS["text_primary"]
        )
        self.search_entry.grid(row=0, column=0, sticky="ew", padx=(15, 10), pady=15)
        self.search_entry.bind("<KeyRelease>", self.filter_products)

        btn_clear = ctk.CTkButton(
            search_frame,
            text="Limpiar",
            font=("Segoe UI", 11, "bold"),
            width=80,
            fg_color=COLORS["border"],
            text_color=COLORS["text_primary"],
            hover_color=COLORS["bg_dark"],
            command=self.clear_search
        )
        btn_clear.grid(row=0, column=1, sticky="e", padx=(0, 15), pady=15)

        # Catalog Table
        cols = ("id", "code", "name", "stock", "p_price", "s_price", "min")
        headings = ("ID", "Código", "Nombre del Producto", "Stock", "P. Compra", "P. Venta", "Mínimo")
        self.treeview = CustomTreeview(left_frame, columns=cols, headings=headings)
        self.treeview.grid(row=1, column=0, sticky="nsew")
        
        self.treeview.set_column_width("id", 40)
        self.treeview.set_column_width("code", 90)
        self.treeview.set_column_width("name", 200)
        self.treeview.set_column_width("stock", 60)
        self.treeview.set_column_width("p_price", 90)
        self.treeview.set_column_width("s_price", 90)
        self.treeview.set_column_width("min", 60)

        self.treeview.set_column_anchor("id", "center")
        self.treeview.set_column_anchor("code", "center")
        self.treeview.set_column_anchor("stock", "center")
        self.treeview.set_column_anchor("p_price", "e")
        self.treeview.set_column_anchor("s_price", "e")
        self.treeview.set_column_anchor("min", "center")

        self.treeview.bind_select(self.on_product_selected)

        # ---- RIGHT COLUMN: Details Form ----
        right_frame = ctk.CTkFrame(
            self, 
            fg_color=COLORS["bg_light"], 
            border_color=COLORS["border"], 
            border_width=1, 
            corner_radius=12
        )
        right_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        right_frame.grid_columnconfigure(1, weight=1)

        form_title = ctk.CTkLabel(
            right_frame, 
            text="DETALLES DEL PRODUCTO", 
            font=("Segoe UI", 12, "bold"), 
            text_color=COLORS["accent"]
        )
        form_title.grid(row=0, column=0, columnspan=2, sticky="w", padx=20, pady=(15, 10))

        # Fields definition
        self.inputs = {}
        fields = [
            ("id", "ID (Autogenerado)", True),
            ("code", "Código del Producto *", False),
            ("name", "Nombre del Producto *", False),
            ("description", "Descripción", False),
            ("stock", "Inventario Físico (Stock) *", False),
            ("purchase_price", "Precio de Compra ($) *", False),
            ("sale_price", "Precio de Venta ($) *", False),
            ("min_stock", "Stock de Alerta Mínima *", False)
        ]

        for i, (key, label_text, readonly) in enumerate(fields, start=1):
            lbl = ctk.CTkLabel(
                right_frame, 
                text=label_text, 
                font=("Segoe UI", 10, "bold"), 
                text_color=COLORS["text_secondary"]
            )
            lbl.grid(row=i, column=0, sticky="w", padx=20, pady=4)
            
            entry = ctk.CTkEntry(
                right_frame,
                font=("Segoe UI", 11),
                fg_color=COLORS["bg_dark"] if not readonly else COLORS["border"],
                border_color=COLORS["border"],
                text_color=COLORS["text_primary"]
            )
            if readonly:
                entry.configure(state="readonly")
            entry.grid(row=i, column=1, sticky="ew", padx=(0, 20), pady=4)
            self.inputs[key] = entry

        # Supplier Combobox Field
        lbl_supp = ctk.CTkLabel(
            right_frame,
            text="Proveedor Asociado *",
            font=("Segoe UI", 10, "bold"),
            text_color=COLORS["text_secondary"]
        )
        lbl_supp.grid(row=len(fields)+1, column=0, sticky="w", padx=20, pady=4)

        self.supplier_combo = ctk.CTkComboBox(
            right_frame,
            font=("Segoe UI", 11),
            fg_color=COLORS["bg_dark"],
            border_color=COLORS["border"],
            text_color=COLORS["text_primary"],
            button_color=COLORS["border"],
            dropdown_fg_color=COLORS["bg_light"],
            dropdown_text_color=COLORS["text_primary"]
        )
        self.supplier_combo.grid(row=len(fields)+1, column=1, sticky="ew", padx=(0, 20), pady=4)

        # Action Buttons
        btn_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
        btn_frame.grid(row=len(fields)+2, column=0, columnspan=2, sticky="ew", padx=20, pady=(20, 15))
        btn_frame.grid_columnconfigure((0, 1, 2), weight=1)

        self.btn_save = ctk.CTkButton(
            btn_frame,
            text="Guardar",
            font=("Segoe UI", 11, "bold"),
            fg_color=COLORS["success"],
            text_color=COLORS["bg_dark"],
            hover_color="#8ed189",
            command=self.save_product
        )
        self.btn_save.grid(row=0, column=0, padx=2)

        self.btn_new = ctk.CTkButton(
            btn_frame,
            text="Limpiar",
            font=("Segoe UI", 11, "bold"),
            fg_color=COLORS["border"],
            text_color=COLORS["text_primary"],
            hover_color=COLORS["bg_dark"],
            command=self.clear_form
        )
        self.btn_new.grid(row=0, column=1, padx=2)

        self.btn_delete = ctk.CTkButton(
            btn_frame,
            text="Eliminar",
            font=("Segoe UI", 11, "bold"),
            fg_color=COLORS["danger"],
            text_color=COLORS["bg_dark"],
            hover_color="#e57c96",
            command=self.delete_product
        )
        self.btn_delete.grid(row=0, column=2, padx=2)

    def on_show(self):
        self.load_suppliers()
        self.refresh_product_list()
        self.clear_form()

    def load_suppliers(self):
        """Loads and maps suppliers for the dropdown."""
        self.all_suppliers = self.controller.get_suppliers()
        self.supplier_map = {}
        values = []
        for s in self.all_suppliers:
            display_text = f"{s.name} [RIF: {s.rif_cedula}]"
            self.supplier_map[display_text] = s.id
            values.append(display_text)
        self.supplier_combo.configure(values=values)
        if values:
            self.supplier_combo.set(values[0])
        else:
            self.supplier_combo.set("No hay proveedores registrados")

    def refresh_product_list(self):
        self.treeview.clear()
        self.all_products = self.controller.get_products()
        for p in self.all_products:
            # Highlight with warning if stock is below warning levels
            tags = ()
            if p.stock <= p.min_stock:
                tags = ("warning",)
                stock_display = f"⚠️ {p.stock}"
            else:
                stock_display = str(p.stock)

            self.treeview.insert_row((
                p.id,
                p.code,
                p.name,
                stock_display,
                f"${p.purchase_price:,.2f}",
                f"${p.sale_price:,.2f}",
                p.min_stock
            ), item_id=str(p.id), tags=tags)

    def filter_products(self, event=None):
        query = self.search_entry.get().lower()
        self.treeview.clear()
        for p in self.all_products:
            if query in p.name.lower() or query in p.code.lower():
                tags = ()
                if p.stock <= p.min_stock:
                    tags = ("warning",)
                    stock_display = f"⚠️ {p.stock}"
                else:
                    stock_display = str(p.stock)

                self.treeview.insert_row((
                    p.id,
                    p.code,
                    p.name,
                    stock_display,
                    f"${p.purchase_price:,.2f}",
                    f"${p.sale_price:,.2f}",
                    p.min_stock
                ), item_id=str(p.id), tags=tags)

    def clear_search(self):
        self.search_entry.delete(0, "end")
        self.refresh_product_list()

    def on_product_selected(self, selection):
        values, item_id = selection
        if not values:
            return

        product = next((p for p in self.all_products if str(p.id) == item_id), None)
        if not product:
            return

        self.inputs["id"].configure(state="normal")
        self.inputs["id"].delete(0, "end")
        self.inputs["id"].insert(0, str(product.id))
        self.inputs["id"].configure(state="readonly")

        for key in ("code", "name", "description", "stock", "purchase_price", "sale_price", "min_stock"):
            self.inputs[key].delete(0, "end")
            self.inputs[key].insert(0, str(getattr(product, key) or ""))

        # Highlight supplier
        supplier = next((s for s in self.all_suppliers if s.id == product.supplier_id), None)
        if supplier:
            self.supplier_combo.set(f"{supplier.name} [RIF: {supplier.rif_cedula}]")

    def clear_form(self):
        self.inputs["id"].configure(state="normal")
        for entry in self.inputs.values():
            entry.delete(0, "end")
        self.inputs["id"].configure(state="readonly")
        if self.all_suppliers:
            display_text = f"{self.all_suppliers[0].name} [RIF: {self.all_suppliers[0].rif_cedula}]"
            self.supplier_combo.set(display_text)

    def save_product(self):
        product_id_str = self.inputs["id"].get()
        product_id = int(product_id_str) if product_id_str else None

        selected_supp = self.supplier_combo.get()
        supplier_id = self.supplier_map.get(selected_supp, None)

        try:
            self.controller.save_product(
                product_id=product_id,
                code=self.inputs["code"].get(),
                name=self.inputs["name"].get(),
                description=self.inputs["description"].get(),
                stock=self.inputs["stock"].get(),
                purchase_price=self.inputs["purchase_price"].get(),
                sale_price=self.inputs["sale_price"].get(),
                min_stock=self.inputs["min_stock"].get(),
                supplier_id=supplier_id
            )
            messagebox.showinfo("Éxito", "Producto guardado correctamente.")
            self.refresh_product_list()
            self.clear_form()
        except ValueError as ve:
            messagebox.showerror("Error de Validación", str(ve))
        except Exception as e:
            messagebox.showerror("Error de Base de Datos", f"No se pudo guardar el producto: {str(e)}")

    def delete_product(self):
        product_id_str = self.inputs["id"].get()
        if not product_id_str:
            messagebox.showwarning("Atención", "Seleccione un producto de la lista para eliminar.")
            return

        product_id = int(product_id_str)
        if messagebox.askyesno("Confirmar Eliminación", "¿Está seguro de que desea eliminar este producto?"):
            try:
                self.controller.delete_product(product_id)
                messagebox.showinfo("Éxito", "Producto eliminado correctamente.")
                self.refresh_product_list()
                self.clear_form()
            except ValueError as ve:
                messagebox.showerror("Restricción de Integridad", str(ve))
