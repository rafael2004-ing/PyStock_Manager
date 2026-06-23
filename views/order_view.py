import customtkinter as ctk
from tkinter import messagebox
from config import COLORS
from views.components.treeview import CustomTreeview
from views.invoice_detail_view import InvoiceDetailWindow
from models.order import Order

class OrderView(ctk.CTkFrame):
    def __init__(self, parent, controller, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        self.controller = controller
        
        # State variables
        self.cart_items = {}       # product_id -> { 'code', 'name', 'qty', 'price', 'subtotal' }
        self.all_customers = []
        self.customer_map = {}     # Display text -> Customer ID
        self.selected_product = None

        # Layout configuration
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=4) # Customer + Product Catalog
        self.grid_columnconfigure(1, weight=5) # Shopping Cart + Totals

        # ==========================================
        # TOP FRAME: Customer Selector
        # ==========================================
        cust_frame = ctk.CTkFrame(
            self, 
            fg_color=COLORS["bg_light"], 
            border_color=COLORS["border"], 
            border_width=1, 
            corner_radius=12,
            height=80
        )
        cust_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 15))
        cust_frame.grid_columnconfigure(1, weight=1)
        cust_frame.grid_propagate(False)

        cust_label = ctk.CTkLabel(
            cust_frame, 
            text="SELECCIONAR CLIENTE:", 
            font=("Segoe UI", 11, "bold"), 
            text_color=COLORS["text_secondary"]
        )
        cust_label.grid(row=0, column=0, padx=(20, 10), pady=25, sticky="w")

        self.cust_combobox = ctk.CTkComboBox(
            cust_frame,
            font=("Segoe UI", 12),
            fg_color=COLORS["bg_dark"],
            border_color=COLORS["border"],
            text_color=COLORS["text_primary"],
            button_color=COLORS["border"],
            button_hover_color=COLORS["accent"],
            dropdown_fg_color=COLORS["bg_light"],
            dropdown_text_color=COLORS["text_primary"],
            dropdown_hover_color=COLORS["border"],
            values=[]
        )
        self.cust_combobox.grid(row=0, column=1, sticky="ew", padx=(0, 20), pady=25)

        # ==========================================
        # LEFT COLUMN: Product Catalog & Item Add
        # ==========================================
        left_frame = ctk.CTkFrame(self, fg_color="transparent")
        left_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 10))
        left_frame.grid_rowconfigure(1, weight=1)
        left_frame.grid_rowconfigure(2, weight=0)
        left_frame.grid_columnconfigure(0, weight=1)

        # Catalog Search
        prod_search_frame = ctk.CTkFrame(left_frame, fg_color=COLORS["bg_light"], border_color=COLORS["border"], border_width=1, height=55)
        prod_search_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        prod_search_frame.grid_columnconfigure(0, weight=1)
        prod_search_frame.grid_propagate(False)

        self.prod_search_entry = ctk.CTkEntry(
            prod_search_frame,
            placeholder_text="Buscar producto por Código/Nombre...",
            font=("Segoe UI", 11),
            fg_color=COLORS["bg_dark"],
            border_color=COLORS["border"],
            text_color=COLORS["text_primary"]
        )
        self.prod_search_entry.grid(row=0, column=0, sticky="ew", padx=(15, 15), pady=12)
        self.prod_search_entry.bind("<KeyRelease>", self.filter_products)

        # Catalog Grid
        cols = ("id", "code", "name", "stock", "price")
        headings = ("ID", "Código", "Producto", "Stock", "Precio")
        self.prod_tree = CustomTreeview(left_frame, columns=cols, headings=headings)
        self.prod_tree.grid(row=1, column=0, sticky="nsew")
        self.prod_tree.set_column_width("id", 35)
        self.prod_tree.set_column_width("code", 80)
        self.prod_tree.set_column_width("name", 160)
        self.prod_tree.set_column_width("stock", 50)
        self.prod_tree.set_column_width("price", 75)
        self.prod_tree.set_column_anchor("id", "center")
        self.prod_tree.set_column_anchor("code", "center")
        self.prod_tree.set_column_anchor("stock", "center")
        self.prod_tree.set_column_anchor("price", "e")

        self.prod_tree.bind_select(self.on_product_selected)

        # Item Cart Form (Below Catalog)
        add_frame = ctk.CTkFrame(
            left_frame, 
            fg_color=COLORS["bg_light"], 
            border_color=COLORS["border"], 
            border_width=1, 
            corner_radius=12
        )
        add_frame.grid(row=2, column=0, sticky="ew", pady=(10, 0))
        add_frame.grid_columnconfigure((1, 3), weight=1)

        # Labels & Fields
        lbl_prod = ctk.CTkLabel(add_frame, text="PROD. SELECCIONADO:", font=("Segoe UI", 10, "bold"), text_color=COLORS["text_secondary"])
        lbl_prod.grid(row=0, column=0, padx=(15, 5), pady=12, sticky="w")
        
        self.lbl_selected_prod_name = ctk.CTkLabel(add_frame, text="Ninguno", font=("Segoe UI", 11, "bold"), text_color=COLORS["text_primary"])
        self.lbl_selected_prod_name.grid(row=0, column=1, padx=5, pady=12, sticky="w")

        lbl_qty = ctk.CTkLabel(add_frame, text="CANTIDAD:", font=("Segoe UI", 10, "bold"), text_color=COLORS["text_secondary"])
        lbl_qty.grid(row=0, column=2, padx=10, pady=12, sticky="w")

        self.qty_entry = ctk.CTkEntry(
            add_frame,
            width=70,
            font=("Segoe UI", 11),
            fg_color=COLORS["bg_dark"],
            border_color=COLORS["border"],
            text_color=COLORS["text_primary"]
        )
        self.qty_entry.grid(row=0, column=3, padx=5, pady=12, sticky="w")

        self.btn_add_to_cart = ctk.CTkButton(
            add_frame,
            text="Añadir  🛒",
            font=("Segoe UI", 11, "bold"),
            width=90,
            fg_color=COLORS["success"],
            text_color=COLORS["bg_dark"],
            hover_color="#8ed189",
            command=self.add_item_to_cart
        )
        self.btn_add_to_cart.grid(row=0, column=4, padx=(10, 15), pady=12, sticky="e")

        # ==========================================
        # RIGHT COLUMN: Cart Summary & Checkout
        # ==========================================
        right_frame = ctk.CTkFrame(
            self, 
            fg_color=COLORS["bg_light"], 
            border_color=COLORS["border"], 
            border_width=1, 
            corner_radius=12
        )
        right_frame.grid(row=1, column=1, sticky="nsew", padx=(10, 0))
        right_frame.grid_rowconfigure(1, weight=1)
        right_frame.grid_columnconfigure(0, weight=1)

        # Title / Buttons
        cart_title_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
        cart_title_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(15, 10))
        cart_title_frame.grid_columnconfigure(0, weight=1)

        cart_title = ctk.CTkLabel(cart_title_frame, text="DETALLE DEL PEDIDO (CARRITO)", font=("Segoe UI", 12, "bold"), text_color=COLORS["accent"])
        cart_title.grid(row=0, column=0, sticky="w")

        self.btn_remove_item = ctk.CTkButton(
            cart_title_frame,
            text="Quitar Item",
            font=("Segoe UI", 10, "bold"),
            width=80,
            height=26,
            fg_color=COLORS["danger"],
            text_color=COLORS["bg_dark"],
            hover_color="#e57c96",
            command=self.remove_item_from_cart
        )
        self.btn_remove_item.grid(row=0, column=1, sticky="e")

        # Cart Table
        cart_cols = ("pid", "code", "name", "qty", "price", "subtotal")
        cart_headings = ("PID", "Código", "Producto", "Cant.", "Precio U.", "Subtotal")
        self.cart_tree = CustomTreeview(right_frame, columns=cart_cols, headings=cart_headings)
        self.cart_tree.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 10))
        
        self.cart_tree.set_column_width("pid", 35)
        self.cart_tree.set_column_width("code", 80)
        self.cart_tree.set_column_width("name", 150)
        self.cart_tree.set_column_width("qty", 50)
        self.cart_tree.set_column_width("price", 70)
        self.cart_tree.set_column_width("subtotal", 80)
        
        self.cart_tree.set_column_anchor("pid", "center")
        self.cart_tree.set_column_anchor("code", "center")
        self.cart_tree.set_column_anchor("qty", "center")
        self.cart_tree.set_column_anchor("price", "e")
        self.cart_tree.set_column_anchor("subtotal", "e")

        # Totals Panel
        totals_frame = ctk.CTkFrame(right_frame, fg_color=COLORS["bg_dark"], corner_radius=8)
        totals_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=10)
        totals_frame.grid_columnconfigure(1, weight=1)

        # Subtotal
        lbl_sub = ctk.CTkLabel(totals_frame, text="Subtotal:", font=("Segoe UI", 11, "bold"), text_color=COLORS["text_secondary"])
        lbl_sub.grid(row=0, column=0, padx=15, pady=(8, 2), sticky="w")
        self.lbl_subtotal_val = ctk.CTkLabel(totals_frame, text="$0.00", font=("Segoe UI", 12, "bold"), text_color=COLORS["text_primary"])
        self.lbl_subtotal_val.grid(row=0, column=1, padx=15, pady=(8, 2), sticky="e")

        # IVA (16%)
        lbl_iva = ctk.CTkLabel(totals_frame, text="I.V.A. (16%):", font=("Segoe UI", 11, "bold"), text_color=COLORS["text_secondary"])
        lbl_iva.grid(row=1, column=0, padx=15, pady=2, sticky="w")
        self.lbl_iva_val = ctk.CTkLabel(totals_frame, text="$0.00", font=("Segoe UI", 12, "bold"), text_color=COLORS["text_primary"])
        self.lbl_iva_val.grid(row=1, column=1, padx=15, pady=2, sticky="e")

        # Grand Total
        lbl_tot = ctk.CTkLabel(totals_frame, text="TOTAL FACTURA:", font=("Segoe UI", 13, "bold"), text_color=COLORS["accent"])
        lbl_tot.grid(row=2, column=0, padx=15, pady=(4, 10), sticky="w")
        self.lbl_total_val = ctk.CTkLabel(totals_frame, text="$0.00", font=("Segoe UI", 18, "bold"), text_color=COLORS["accent"])
        self.lbl_total_val.grid(row=2, column=1, padx=15, pady=(4, 10), sticky="e")

        # Checkout Button
        self.btn_checkout = ctk.CTkButton(
            right_frame,
            text="Confirmar y Registrar Factura 💳",
            font=("Segoe UI", 13, "bold"),
            fg_color=COLORS["accent"],
            text_color=COLORS["bg_dark"],
            hover_color=COLORS["accent_hover"],
            height=45,
            command=self.process_checkout
        )
        self.btn_checkout.grid(row=3, column=0, sticky="ew", padx=20, pady=(0, 20))

    def on_show(self):
        """Refreshes available customers and catalog on load."""
        self.load_customers()
        self.refresh_catalog()
        self.clear_item_selection()
        
        # Reset cart if empty
        if not self.cart_items:
            self.clear_cart()

    def load_customers(self):
        """Loads and maps customers for combobox selection."""
        self.all_customers = self.controller.get_customers()
        self.customer_map = {}
        values = []
        for c in self.all_customers:
            display_text = f"{c.name} [RIF: {c.rif_cedula}]"
            self.customer_map[display_text] = c.id
            values.append(display_text)
        self.cust_combobox.configure(values=values)
        if values:
            self.cust_combobox.set(values[0])
        else:
            self.cust_combobox.set("No hay clientes registrados")

    def refresh_catalog(self):
        """Refreshes product list treeview."""
        self.prod_tree.clear()
        self.all_products = self.controller.get_products()
        for p in self.all_products:
            stock_str = f"⚠️ {p.stock}" if p.stock <= p.min_stock else str(p.stock)
            tags = ("warning",) if p.stock <= p.min_stock else ()
            self.prod_tree.insert_row((
                p.id,
                p.code,
                p.name,
                stock_str,
                f"${p.sale_price:,.2f}"
            ), item_id=str(p.id), tags=tags)

    def filter_products(self, event=None):
        query = self.prod_search_entry.get().lower()
        self.prod_tree.clear()
        for p in self.all_products:
            if query in p.name.lower() or query in p.code.lower():
                stock_str = f"⚠️ {p.stock}" if p.stock <= p.min_stock else str(p.stock)
                tags = ("warning",) if p.stock <= p.min_stock else ()
                self.prod_tree.insert_row((
                    p.id,
                    p.code,
                    p.name,
                    stock_str,
                    f"${p.sale_price:,.2f}"
                ), item_id=str(p.id), tags=tags)

    def clear_search(self):
        self.prod_search_entry.delete(0, "end")
        self.refresh_catalog()

    def on_product_selected(self, selection):
        values, item_id = selection
        if not values:
            return
            
        self.selected_product = next((p for p in self.all_products if str(p.id) == item_id), None)
        if not self.selected_product:
            return
            
        self.lbl_selected_prod_name.configure(text=self.selected_product.name)
        self.qty_entry.delete(0, "end")
        self.qty_entry.insert(0, "1")
        self.qty_entry.focus()

    def clear_item_selection(self):
        self.selected_product = None
        self.lbl_selected_prod_name.configure(text="Ninguno")
        self.qty_entry.delete(0, "end")

    # ==========================================
    # CART ACTIONS
    # ==========================================
    def add_item_to_cart(self):
        if not self.selected_product:
            messagebox.showwarning("Atención", "Debe seleccionar un producto del catálogo.")
            return

        qty_str = self.qty_entry.get().strip()
        try:
            qty = int(qty_str)
            if qty <= 0:
                raise ValueError()
        except ValueError:
            messagebox.showerror("Error", "La cantidad debe ser un número entero mayor a 0.")
            return

        # Check local stock limit before adding to UI cart
        pid = self.selected_product.id
        current_in_cart = self.cart_items.get(pid, {}).get("quantity", 0)
        requested_qty = current_in_cart + qty

        if requested_qty > self.selected_product.stock:
            messagebox.showerror(
                "Stock Insuficiente", 
                f"No se puede agregar al carrito.\n\nDisponibles: {self.selected_product.stock}\nEn Carrito: {current_in_cart}\nRequeridos: {qty}"
            )
            return

        subtotal = requested_qty * self.selected_product.sale_price

        # Update cart dict
        self.cart_items[pid] = {
            "product_id": pid,
            "code": self.selected_product.code,
            "name": self.selected_product.name,
            "quantity": requested_qty,
            "price": self.selected_product.sale_price,
            "subtotal": subtotal
        }

        self.refresh_cart_treeview()
        self.clear_item_selection()
        self.refresh_catalog() # Reselect/update stock warnings

    def remove_item_from_cart(self):
        values, item_id = self.cart_tree.get_selected_item()
        if not item_id:
            messagebox.showwarning("Atención", "Seleccione un producto en el carrito para quitar.")
            return
            
        pid = int(item_id)
        if pid in self.cart_items:
            del self.cart_items[pid]
            
        self.refresh_cart_treeview()

    def refresh_cart_treeview(self):
        self.cart_tree.clear()
        
        subtotal = 0.0
        for pid, item in self.cart_items.items():
            self.cart_tree.insert_row((
                pid,
                item["code"],
                item["name"],
                item["quantity"],
                f"${item['price']:,.2f}",
                f"${item['subtotal']:,.2f}"
            ), item_id=str(pid))
            subtotal += item["subtotal"]

        # Calculate totals
        iva = subtotal * 0.16
        total = subtotal + iva

        self.lbl_subtotal_val.configure(text=f"${subtotal:,.2f}")
        self.lbl_iva_val.configure(text=f"${iva:,.2f}")
        self.lbl_total_val.configure(text=f"${total:,.2f}")

    def clear_cart(self):
        self.cart_items = {}
        self.refresh_cart_treeview()

    def process_checkout(self):
        # 1. Validate customer selection
        selected_cust_str = self.cust_combobox.get()
        if selected_cust_str not in self.customer_map:
            messagebox.showerror("Error", "Seleccione un cliente válido.")
            return
            
        customer_id = self.customer_map[selected_cust_str]

        # 2. Validate cart not empty
        if not self.cart_items:
            messagebox.showwarning("Carrito Vacío", "No se han añadido productos al pedido.")
            return

        # 3. Compile checkout list
        items_list = list(self.cart_items.values())

        # 4. Trigger creation via controller
        if messagebox.askyesno("Confirmar Cobro", "¿Está seguro de que desea registrar esta factura y descontar el inventario?"):
            try:
                order, invoice = self.controller.create_order(
                    customer_id=customer_id,
                    items=items_list
                )
                
                # Fetch full order details with loaded customer & items
                full_order = Order.get_by_id(invoice.order_id)
                
                # Show digital invoice window modal
                InvoiceDetailWindow(self.winfo_toplevel(), full_order, invoice)
                
                # Success cleanup
                self.clear_cart()
                self.on_show()

                # Trigger real-time critical stock check & visual alert dialogs
                self.winfo_toplevel().check_critical_stock(show_popup=True)
            except ValueError as ve:
                messagebox.showerror("Operación Cancelada", str(ve))
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo procesar la factura: {str(e)}")
