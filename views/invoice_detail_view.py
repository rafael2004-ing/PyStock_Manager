import customtkinter as ctk
from tkinter import filedialog, messagebox
from config import COLORS
from utils.pdf_generator import generate_invoice_pdf

class InvoiceDetailWindow(ctk.CTkToplevel):
    def __init__(self, parent, order, invoice, **kwargs):
        super().__init__(parent, **kwargs)
        self.order = order
        self.invoice = invoice

        # Configure window
        self.title(f"Factura Digital - {self.invoice.invoice_number}")
        self.geometry("450x650")
        self.resizable(False, False)
        self.configure(fg_color=COLORS["bg_medium"])

        # Make modal and handle window close
        self.transient(parent)
        self.grab_set()
        self.focus_set()

        # Center window relative to parent
        self.center_window(parent)

        self.build_ui()

    def center_window(self, parent):
        self.update_idletasks()
        width = 450
        height = 650
        
        # Try to center relative to parent window
        try:
            px = parent.winfo_rootx()
            py = parent.winfo_rooty()
            pw = parent.winfo_width()
            ph = parent.winfo_height()
            x = px + (pw // 2) - (width // 2)
            y = py + (ph // 2) - (height // 2)
        except Exception:
            # Fallback to screen center
            x = (self.winfo_screenwidth() // 2) - (width // 2)
            y = (self.winfo_screenheight() // 2) - (height // 2)
            
        self.geometry(f"{width}x{height}+{x}+{y}")

    def build_ui(self):
        # Master scrollable frame to ensure everything fits perfectly
        container = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            corner_radius=0
        )
        container.pack(expand=True, fill="both", padx=10, pady=10)

        # Receipt Container Frame
        receipt = ctk.CTkFrame(
            container,
            fg_color=COLORS["bg_light"],
            border_color=COLORS["border"],
            border_width=1,
            corner_radius=16
        )
        receipt.pack(fill="x", padx=10, pady=10)

        # 1. Header (Brand / Logo)
        brand_label = ctk.CTkLabel(
            receipt,
            text="PyStock_Manager",
            font=("Segoe UI", 24, "bold"),
            text_color=COLORS["accent"]
        )
        brand_label.pack(pady=(20, 2))

        tagline_label = ctk.CTkLabel(
            receipt,
            text="SISTEMA DE GESTIÓN & INVENTARIO",
            font=("Segoe UI", 9, "bold"),
            text_color=COLORS["text_secondary"]
        )
        tagline_label.pack(pady=(0, 15))

        # Divider
        self.create_divider(receipt)

        # 2. Invoice Metadata (Number, Date)
        meta_frame = ctk.CTkFrame(receipt, fg_color="transparent")
        meta_frame.pack(fill="x", padx=20, pady=10)

        invoice_lbl = ctk.CTkLabel(
            meta_frame,
            text=f"FACTURA: {self.invoice.invoice_number}",
            font=("Segoe UI", 13, "bold"),
            text_color=COLORS["text_primary"]
        )
        invoice_lbl.pack(anchor="w")

        date_lbl = ctk.CTkLabel(
            meta_frame,
            text=f"Fecha: {self.invoice.invoice_date or self.order.order_date or 'Hoy'}",
            font=("Segoe UI", 11),
            text_color=COLORS["text_secondary"]
        )
        date_lbl.pack(anchor="w")

        # Divider
        self.create_divider(receipt)

        # 3. Customer Information
        customer_frame = ctk.CTkFrame(receipt, fg_color="transparent")
        customer_frame.pack(fill="x", padx=20, pady=10)

        cust_title = ctk.CTkLabel(
            customer_frame,
            text="CLIENTE / RECEPTOR",
            font=("Segoe UI", 10, "bold"),
            text_color=COLORS["accent"]
        )
        cust_title.pack(anchor="w", pady=(0, 4))

        cust_name = ctk.CTkLabel(
            customer_frame,
            text=f"Nombre: {self.order.customer_name}",
            font=("Segoe UI", 12, "bold"),
            text_color=COLORS["text_primary"]
        )
        cust_name.pack(anchor="w")

        cust_rif = ctk.CTkLabel(
            customer_frame,
            text=f"RIF / Cédula: {self.order.customer_rif}",
            font=("Segoe UI", 11),
            text_color=COLORS["text_secondary"]
        )
        cust_rif.pack(anchor="w")

        # Divider
        self.create_divider(receipt)

        # 4. Itemized List (Receipt Style Table Header)
        items_frame = ctk.CTkFrame(receipt, fg_color="transparent")
        items_frame.pack(fill="x", padx=20, pady=10)

        table_header = ctk.CTkFrame(items_frame, fg_color="transparent")
        table_header.pack(fill="x", pady=(0, 5))

        lbl_hdr_desc = ctk.CTkLabel(table_header, text="PRODUCTO", font=("Segoe UI", 10, "bold"), text_color=COLORS["text_secondary"])
        lbl_hdr_desc.pack(side="left")

        lbl_hdr_total = ctk.CTkLabel(table_header, text="TOTAL", font=("Segoe UI", 10, "bold"), text_color=COLORS["text_secondary"])
        lbl_hdr_total.pack(side="right")

        # Loop through items
        for item in self.order.items:
            item_row = ctk.CTkFrame(items_frame, fg_color="transparent")
            item_row.pack(fill="x", pady=4)

            # Left side: Product name & Qty x Unit Price
            left_sub_frame = ctk.CTkFrame(item_row, fg_color="transparent")
            left_sub_frame.pack(side="left", fill="y")

            prod_title = ctk.CTkLabel(
                left_sub_frame,
                text=item.product_name,
                font=("Segoe UI", 12, "bold"),
                text_color=COLORS["text_primary"]
            )
            prod_title.pack(anchor="w")

            qty_desc = ctk.CTkLabel(
                left_sub_frame,
                text=f"{item.quantity} x ${item.price:,.2f}",
                font=("Segoe UI", 10),
                text_color=COLORS["text_secondary"]
            )
            qty_desc.pack(anchor="w")

            # Right side: Item subtotal
            prod_subtotal = ctk.CTkLabel(
                item_row,
                text=f"${item.subtotal:,.2f}",
                font=("Segoe UI", 12, "bold"),
                text_color=COLORS["text_primary"]
            )
            prod_subtotal.pack(side="right", anchor="n")

        # Divider
        self.create_divider(receipt)

        # 5. Totals
        totals_frame = ctk.CTkFrame(receipt, fg_color=COLORS["bg_dark"], corner_radius=8)
        totals_frame.pack(fill="x", padx=20, pady=15)

        # Subtotal
        self.add_total_line(totals_frame, "Subtotal", f"${self.invoice.subtotal:,.2f}", is_bold=False)
        # Tax
        self.add_total_line(totals_frame, "I.V.A. (16%)", f"${self.invoice.tax:,.2f}", is_bold=False)
        # Grand Total
        self.add_total_line(totals_frame, "TOTAL FACTURA", f"${self.invoice.total:,.2f}", is_bold=True, is_accent=True)

        # Action Buttons (Export PDF & Close)
        actions_frame = ctk.CTkFrame(container, fg_color="transparent")
        actions_frame.pack(fill="x", padx=20, pady=(10, 20))
        actions_frame.grid_columnconfigure((0, 1), weight=1)

        btn_pdf = ctk.CTkButton(
            actions_frame,
            text="Exportar PDF 📄",
            font=("Segoe UI", 13, "bold"),
            fg_color=COLORS["accent"],
            text_color=COLORS["bg_dark"],
            hover_color=COLORS["accent_hover"],
            height=40,
            command=self.export_to_pdf
        )
        btn_pdf.grid(row=0, column=0, padx=(0, 5), sticky="ew")

        btn_close = ctk.CTkButton(
            actions_frame,
            text="Aceptar  ✓",
            font=("Segoe UI", 13, "bold"),
            fg_color=COLORS["success"],
            text_color=COLORS["bg_dark"],
            hover_color="#8ed189",
            height=40,
            command=self.destroy
        )
        btn_close.grid(row=0, column=1, padx=(5, 0), sticky="ew")

    def export_to_pdf(self):
        try:
            # Let the user select the save location
            file_path = filedialog.asksaveasfilename(
                parent=self,
                defaultextension=".pdf",
                filetypes=[("Archivos PDF", "*.pdf")],
                initialfile=f"factura_{self.invoice.invoice_number}.pdf",
                title="Guardar Factura como PDF"
            )
            
            if not file_path:
                return # User cancelled
                
            generate_invoice_pdf(file_path, self.order, self.invoice)
            messagebox.showinfo(
                parent=self,
                title="Exportación Exitosa",
                message=f"La factura se ha guardado correctamente como PDF en:\n{file_path}"
            )
        except Exception as e:
            messagebox.showerror(
                parent=self,
                title="Error de Exportación",
                message=f"No se pudo generar el archivo PDF:\n{str(e)}"
            )

    def create_divider(self, parent):
        divider = ctk.CTkFrame(
            parent,
            height=1,
            fg_color=COLORS["border"]
        )
        divider.pack(fill="x", padx=20, pady=5)

    def add_total_line(self, parent, label, value, is_bold=False, is_accent=False):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=15, pady=6)

        font_size = 14 if is_bold else 11
        font_weight = "bold" if is_bold else "normal"
        text_color = COLORS["accent"] if is_accent else (COLORS["text_primary"] if is_bold else COLORS["text_secondary"])

        lbl = ctk.CTkLabel(
            row,
            text=label,
            font=("Segoe UI", font_size, font_weight),
            text_color=text_color
        )
        lbl.pack(side="left")

        val = ctk.CTkLabel(
            row,
            text=value,
            font=("Segoe UI", font_size, "bold" if is_bold else font_weight),
            text_color=text_color
        )
        val.pack(side="right")
