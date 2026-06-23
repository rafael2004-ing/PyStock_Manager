from models.database import Database

class Product:
    def __init__(self, id=None, code="", name="", description="", stock=0, purchase_price=0.0, sale_price=0.0, min_stock=5, supplier_id=1, created_at=None):
        self.id = id
        self.code = code
        self.name = name
        self.description = description
        self.stock = stock
        self.purchase_price = purchase_price
        self.sale_price = sale_price
        self.min_stock = min_stock
        self.supplier_id = supplier_id
        self.created_at = created_at

    @classmethod
    def from_row(cls, row):
        """Helper to create a Product instance from a sqlite3.Row."""
        if not row:
            return None
        return cls(
            id=row["id"],
            code=row["code"],
            name=row["name"],
            description=row["description"],
            stock=row["stock"],
            purchase_price=row["purchase_price"],
            sale_price=row["sale_price"],
            min_stock=row["min_stock"],
            supplier_id=row["supplier_id"],
            created_at=row["created_at"]
        )

    @classmethod
    def get_all(cls):
        """Returns all products ordered by name."""
        with Database.transaction() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM products ORDER BY name ASC;")
            rows = cursor.fetchall()
            return [cls.from_row(row) for row in rows]

    @classmethod
    def get_by_id(cls, product_id):
        """Finds a product by ID."""
        with Database.transaction() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM products WHERE id = ?;", (product_id,))
            row = cursor.fetchone()
            return cls.from_row(row) if row else None

    @classmethod
    def get_by_code(cls, code):
        """Finds a product by Code."""
        with Database.transaction() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM products WHERE code = ?;", (code,))
            row = cursor.fetchone()
            return cls.from_row(row) if row else None

    @classmethod
    def get_critical_stock(cls):
        """Returns products whose stock is less than or equal to their min_stock warning level."""
        with Database.transaction() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM products WHERE stock <= min_stock ORDER BY stock ASC;")
            rows = cursor.fetchall()
            return [cls.from_row(row) for row in rows]

    def save(self):
        """Inserts a new product or updates an existing one."""
        with Database.transaction() as conn:
            cursor = conn.cursor()
            if self.id is None:
                # Insert
                cursor.execute(
                    """
                    INSERT INTO products (code, name, description, stock, purchase_price, sale_price, min_stock, supplier_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?);
                    """,
                    (self.code, self.name, self.description, self.stock, self.purchase_price, self.sale_price, self.min_stock, self.supplier_id)
                )
                self.id = cursor.lastrowid
            else:
                # Update
                cursor.execute(
                    """
                    UPDATE products 
                    SET code = ?, name = ?, description = ?, stock = ?, purchase_price = ?, sale_price = ?, min_stock = ?, supplier_id = ?
                    WHERE id = ?;
                    """,
                    (self.code, self.name, self.description, self.stock, self.purchase_price, self.sale_price, self.min_stock, self.supplier_id, self.id)
                )

    def delete(self):
        """Deletes a product from the database. Will fail if it is referenced in any invoice/purchase."""
        if self.id is None:
            return
        with Database.transaction() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM products WHERE id = ?;", (self.id,))

    def update_stock(self, quantity, conn=None):
        """
        Adjusts the product stock. 
        If 'conn' is provided, runs inside that connection context.
        Raises ValueError if stock drops below zero.
        """
        if self.id is None:
            raise ValueError("Cannot adjust stock of an unsaved product.")
            
        def execute_update(connection):
            cursor = connection.cursor()
            cursor.execute("SELECT stock, name FROM products WHERE id = ?;", (self.id,))
            row = cursor.fetchone()
            if not row:
                raise ValueError(f"Product ID {self.id} not found.")
            
            current_stock = row["stock"]
            new_stock = current_stock + quantity
            
            if new_stock < 0:
                raise ValueError(f"Stock insuficiente para '{row['name']}'. Disponible: {current_stock}, Requerido: {abs(quantity)}.")
                
            cursor.execute("UPDATE products SET stock = ? WHERE id = ?;", (new_stock, self.id))
            self.stock = new_stock

        if conn is not None:
            execute_update(conn)
        else:
            with Database.transaction() as conn:
                execute_update(conn)
