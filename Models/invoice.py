from models.database import Database
from models.product import Product

class Invoice:
    def __init__(self, id=None, order_id=None, invoice_number="", invoice_date=None, subtotal=0.0, tax=0.0, total=0.0):
        self.id = id
        self.order_id = order_id
        self.invoice_number = invoice_number
        self.invoice_date = invoice_date
        self.subtotal = subtotal
        self.tax = tax
        self.total = total

    @classmethod
    def from_row(cls, row):
        if not row:
            return None
        return cls(
            id=row["id"],
            order_id=row["order_id"],
            invoice_number=row["invoice_number"],
            invoice_date=row["invoice_date"],
            subtotal=row["subtotal"],
            tax=row["tax"],
            total=row["total"]
        )

    @classmethod
    def get_all(cls):
        """Returns all invoices ordered by date."""
        with Database.transaction() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM invoices ORDER BY invoice_date DESC;")
            rows = cursor.fetchall()
            return [cls.from_row(row) for row in rows]

    @classmethod
    def generate_next_number(cls, conn):
        """Generates next invoice number (e.g. FAC-0001)."""
        cursor = conn.cursor()
        cursor.execute("SELECT COALESCE(MAX(id), 0) + 1 as next_id FROM invoices;")
        next_id = cursor.fetchone()["next_id"]
        return f"FAC-{next_id:04d}"

    @classmethod
    def create_from_order(cls, order, conn):
        """
        Generates an Invoice (Factura) from an authorized Order (Pedido).
        Executes within the provided 'conn' transaction.
        Checks inventory stock levels, deducts stock, creates invoice, updates order status to 'Facturado'.
        Raises ValueError if stock is insufficient.
        """
        if order.status != "Autorizado":
            raise ValueError(f"El pedido ID {order.id} no puede ser facturado porque su estado es '{order.status}' y requiere estar 'Autorizado'.")

        cursor = conn.cursor()

        # 1. Strict stock validation before database modification
        for item in order.items:
            # We query the product using the transaction connection 'conn' to avoid dirty reads
            cursor.execute("SELECT name, stock FROM products WHERE id = ?;", (item.product_id,))
            row = cursor.fetchone()
            if not row:
                raise ValueError(f"Producto ID {item.product_id} no existe en catálogo.")
            
            avail_stock = row["stock"]
            if item.quantity > avail_stock:
                # Interrumpir transacción: This exception bubbles up to trigger Rollback in context manager
                raise ValueError(
                    f"Operación rechazada: Stock insuficiente para el producto '{row['name']}'. "
                    f"Disponible: {avail_stock}, Solicitado: {item.quantity}. Saldo remanente negativo no permitido."
                )

        # 2. Deduct stocks
        for item in order.items:
            product = Product.get_by_id(item.product_id)
            product.update_stock(-item.quantity, conn=conn)

        # 3. Generate invoice number
        invoice_num = cls.generate_next_number(conn)

        # 4. Insert Invoice record
        cursor.execute(
            """
            INSERT INTO invoices (order_id, invoice_number, subtotal, tax, total)
            VALUES (?, ?, ?, ?, ?);
            """,
            (order.id, invoice_num, order.subtotal, order.tax, order.total)
        )
        invoice_id = cursor.lastrowid

        # 5. Update Order status to 'Facturado'
        cursor.execute(
            "UPDATE orders SET status = 'Facturado' WHERE id = ?;",
            (order.id,)
        )
        
        # Save invoice id to object
        invoice = cls(
            id=invoice_id,
            order_id=order.id,
            invoice_number=invoice_num,
            subtotal=order.subtotal,
            tax=order.tax,
            total=order.total
        )
        return invoice
