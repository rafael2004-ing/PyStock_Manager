from models.database import Database
from models.product import Product

class OrderItem:
    def __init__(self, id=None, order_id=None, product_id=None, product_name="", product_code="", quantity=0, price=0.0, subtotal=0.0):
        self.id = id
        self.order_id = order_id
        self.product_id = product_id
        self.product_name = product_name
        self.product_code = product_code
        self.quantity = quantity
        self.price = price
        self.subtotal = subtotal

    @classmethod
    def from_row(cls, row):
        if not row:
            return None
        
        product_name = ""
        product_code = ""
        if "product_name" in row.keys():
            product_name = row["product_name"]
        if "product_code" in row.keys():
            product_code = row["product_code"]

        return cls(
            id=row["id"],
            order_id=row["order_id"],
            product_id=row["product_id"],
            product_name=product_name,
            product_code=product_code,
            quantity=row["quantity"],
            price=row["price"],
            subtotal=row["subtotal"]
        )

class Order:
    def __init__(self, id=None, customer_id=None, customer_name="", customer_rif="", order_date=None, status="Autorizado", subtotal=0.0, tax=0.0, total=0.0, items=None):
        self.id = id
        self.customer_id = customer_id
        self.customer_name = customer_name
        self.customer_rif = customer_rif
        self.order_date = order_date
        self.status = status
        self.subtotal = subtotal
        self.tax = tax
        self.total = total
        self.items = items if items is not None else []

    @classmethod
    def from_row(cls, row):
        if not row:
            return None
        
        customer_name = ""
        customer_rif = ""
        if "customer_name" in row.keys():
            customer_name = row["customer_name"]
        if "customer_rif" in row.keys():
            customer_rif = row["customer_rif"]

        return cls(
            id=row["id"],
            customer_id=row["customer_id"],
            customer_name=customer_name,
            customer_rif=customer_rif,
            order_date=row["order_date"],
            status=row["status"],
            subtotal=row["subtotal"],
            tax=row["tax"],
            total=row["total"]
        )

    @classmethod
    def get_all(cls):
        """Returns all orders with customer names joined."""
        with Database.transaction() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT o.*, c.name AS customer_name, c.rif_cedula AS customer_rif
                FROM orders o
                JOIN customers c ON o.customer_id = c.id
                ORDER BY o.order_date DESC;
                """
            )
            rows = cursor.fetchall()
            return [cls.from_row(row) for row in rows]

    @classmethod
    def get_by_id(cls, order_id):
        """Returns a single order with its items fully loaded."""
        with Database.transaction() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT o.*, c.name AS customer_name, c.rif_cedula AS customer_rif
                FROM orders o
                JOIN customers c ON o.customer_id = c.id
                WHERE o.id = ?;
                """,
                (order_id,)
            )
            row = cursor.fetchone()
            if not row:
                return None
            
            order = cls.from_row(row)
            
            # Load items
            cursor.execute(
                """
                SELECT oi.*, p.name AS product_name, p.code AS product_code
                FROM order_items oi
                JOIN products p ON oi.product_id = p.id
                WHERE oi.order_id = ?;
                """,
                (order_id,)
            )
            item_rows = cursor.fetchall()
            order.items = [OrderItem.from_row(r) for r in item_rows]
            return order

    @classmethod
    def get_by_date_range(cls, start_date, end_date):
        """Returns orders within a date range (for reports) formatted as YYYY-MM-DD."""
        with Database.transaction() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT o.*, c.name AS customer_name, c.rif_cedula AS customer_rif
                FROM orders o
                JOIN customers c ON o.customer_id = c.id
                WHERE date(o.order_date) BETWEEN date(?) AND date(?)
                ORDER BY o.order_date DESC;
                """,
                (start_date, end_date)
            )
            rows = cursor.fetchall()
            return [cls.from_row(row) for row in rows]

    def create(self, conn=None):
        """
        Saves a new order (Pedido) along with its items.
        If 'conn' is provided, executes inside that transaction.
        Otherwise, runs inside a fresh transaction context.
        """
        if not self.items:
            raise ValueError("No se puede registrar un pedido sin productos.")

        def execute_save(c):
            cursor = c.cursor()
            # 1. Insert order header
            cursor.execute(
                """
                INSERT INTO orders (customer_id, status, subtotal, tax, total)
                VALUES (?, ?, ?, ?, ?);
                """,
                (self.customer_id, self.status, self.subtotal, self.tax, self.total)
            )
            self.id = cursor.lastrowid

            # 2. Process items
            for item in self.items:
                # Save the item
                cursor.execute(
                    """
                    INSERT INTO order_items (order_id, product_id, quantity, price, subtotal)
                    VALUES (?, ?, ?, ?, ?);
                    """,
                    (self.id, item.product_id, item.quantity, item.price, item.subtotal)
                )

        if conn is not None:
            execute_save(conn)
        else:
            with Database.transaction() as conn:
                execute_save(conn)
