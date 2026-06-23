from models.database import Database
from models.product import Product

class PurchaseItem:
    def __init__(self, id=None, purchase_id=None, product_id=None, product_name="", product_code="", quantity=0, price=0.0, subtotal=0.0):
        self.id = id
        self.purchase_id = purchase_id
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
        return cls(
            id=row["id"],
            purchase_id=row["purchase_id"],
            product_id=row["product_id"],
            product_name=row.get("product_name", ""),
            product_code=row.get("product_code", ""),
            quantity=row["quantity"],
            price=row["price"],
            subtotal=row["subtotal"]
        )

class Purchase:
    def __init__(self, id=None, supplier_id=None, supplier_name="", supplier_rif="", purchase_date=None, total=0.0, items=None):
        self.id = id
        self.supplier_id = supplier_id
        self.supplier_name = supplier_name
        self.supplier_rif = supplier_rif
        self.purchase_date = purchase_date
        self.total = total
        self.items = items if items is not None else []

    @classmethod
    def from_row(cls, row):
        if not row:
            return None
        return cls(
            id=row["id"],
            supplier_id=row["supplier_id"],
            supplier_name=row.get("supplier_name", ""),
            supplier_rif=row.get("supplier_rif", ""),
            purchase_date=row["purchase_date"],
            total=row["total"]
        )

    @classmethod
    def get_all(cls):
        """Returns all purchases with supplier names joined."""
        with Database.transaction() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT p.*, s.name AS supplier_name, s.rif_cedula AS supplier_rif
                FROM purchases p
                JOIN suppliers s ON p.supplier_id = s.id
                ORDER BY p.purchase_date DESC;
                """
            )
            rows = cursor.fetchall()
            return [cls.from_row(row) for row in rows]

    @classmethod
    def get_by_id(cls, purchase_id):
        """Returns a single purchase with its items fully loaded."""
        with Database.transaction() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT p.*, s.name AS supplier_name, s.rif_cedula AS supplier_rif
                FROM purchases p
                JOIN suppliers s ON p.supplier_id = s.id
                WHERE p.id = ?;
                """,
                (purchase_id,)
            )
            row = cursor.fetchone()
            if not row:
                return None
            
            purchase = cls.from_row(row)
            
            # Load items
            cursor.execute(
                """
                SELECT pi.*, pr.name AS product_name, pr.code AS product_code
                FROM purchase_items pi
                JOIN products pr ON pi.product_id = pr.id
                WHERE pi.purchase_id = ?;
                """,
                (purchase_id,)
            )
            item_rows = cursor.fetchall()
            purchase.items = [PurchaseItem.from_row(r) for r in item_rows]
            return purchase

    def create(self):
        """
        Saves a new supplier purchase, adding quantity back to the inventory stock.
        This entire process is run inside a single SQLite transaction context.
        """
        if not self.items:
            raise ValueError("No se puede registrar una compra sin productos.")

        with Database.transaction() as conn:
            cursor = conn.cursor()
            
            # 1. Insert purchase header
            cursor.execute(
                """
                INSERT INTO purchases (supplier_id, total)
                VALUES (?, ?);
                """,
                (self.supplier_id, self.total)
            )
            self.id = cursor.lastrowid

            # 2. Process items
            for item in self.items:
                product = Product.get_by_id(item.product_id)
                if not product:
                    raise ValueError(f"Producto ID {item.product_id} no existe.")

                # Increase stock (update_stock with positive quantity)
                product.update_stock(item.quantity, conn=conn)

                # Save the item
                cursor.execute(
                    """
                    INSERT INTO purchase_items (purchase_id, product_id, quantity, price, subtotal)
                    VALUES (?, ?, ?, ?, ?);
                    """,
                    (self.id, item.product_id, item.quantity, item.price, item.subtotal)
                )
