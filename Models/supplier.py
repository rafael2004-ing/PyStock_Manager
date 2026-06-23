from models.database import Database

class Supplier:
    def __init__(self, id=None, rif_cedula="", name="", phone="", email="", address="", created_at=None):
        self.id = id
        self.rif_cedula = rif_cedula
        self.name = name
        self.phone = phone
        self.email = email
        self.address = address
        self.created_at = created_at

    @classmethod
    def from_row(cls, row):
        """Helper to create a Supplier instance from a sqlite3.Row."""
        if not row:
            return None
        return cls(
            id=row["id"],
            rif_cedula=row["rif_cedula"],
            name=row["name"],
            phone=row["phone"],
            email=row["email"],
            address=row["address"],
            created_at=row["created_at"]
        )

    @classmethod
    def get_all(cls):
        """Returns all suppliers ordered by name."""
        with Database.transaction() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM suppliers ORDER BY name ASC;")
            rows = cursor.fetchall()
            return [cls.from_row(row) for row in rows]

    @classmethod
    def get_by_id(cls, supplier_id):
        """Finds a supplier by ID."""
        with Database.transaction() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM suppliers WHERE id = ?;", (supplier_id,))
            row = cursor.fetchone()
            return cls.from_row(row) if row else None

    @classmethod
    def get_by_rif(cls, rif_cedula):
        """Finds a supplier by RIF/Cédula."""
        with Database.transaction() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM suppliers WHERE rif_cedula = ?;", (rif_cedula,))
            row = cursor.fetchone()
            return cls.from_row(row) if row else None

    def save(self):
        """Inserts a new supplier or updates an existing one."""
        with Database.transaction() as conn:
            cursor = conn.cursor()
            if self.id is None:
                # Insert
                cursor.execute(
                    """
                    INSERT INTO suppliers (rif_cedula, name, phone, email, address)
                    VALUES (?, ?, ?, ?, ?);
                    """,
                    (self.rif_cedula, self.name, self.phone, self.email, self.address)
                )
                self.id = cursor.lastrowid
            else:
                # Update
                cursor.execute(
                    """
                    UPDATE suppliers 
                    SET rif_cedula = ?, name = ?, phone = ?, email = ?, address = ?
                    WHERE id = ?;
                    """,
                    (self.rif_cedula, self.name, self.phone, self.email, self.address, self.id)
                )

    def delete(self):
        """Deletes a supplier from the database. Will fail if they have purchase records (RESTRICT constraint)."""
        if self.id is None:
            return
        with Database.transaction() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM suppliers WHERE id = ?;", (self.id,))

    def get_purchase_history(self):
        """Fetches the operational purchases history for this supplier."""
        if self.id is None:
            return []
        with Database.transaction() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, purchase_date, total 
                FROM purchases 
                WHERE supplier_id = ? 
                ORDER BY purchase_date DESC;
                """,
                (self.id,)
            )
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
