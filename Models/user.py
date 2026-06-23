import hashlib
from models.database import Database

class User:
    def __init__(self, id=None, username="", password_hash="", role="", created_at=None):
        self.id = id
        self.username = username
        self.password_hash = password_hash
        self.role = role
        self.created_at = created_at

    @classmethod
    def from_row(cls, row):
        if not row:
            return None
        return cls(
            id=row["id"],
            username=row["username"],
            password_hash=row["password_hash"],
            role=row["role"]
        )

    @staticmethod
    def hash_password(password):
        """Generates SHA-256 hash for raw password."""
        return hashlib.sha256(password.encode()).hexdigest()

    @classmethod
    def get_by_username(cls, username):
        """Finds user by username."""
        with Database.transaction() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = ?;", (username.strip().lower(),))
            row = cursor.fetchone()
            return cls.from_row(row) if row else None

    @classmethod
    def authenticate(cls, username, password):
        """Authenticates user and returns User instance if valid."""
        user = cls.get_by_username(username)
        if not user:
            return None
        
        hashed = cls.hash_password(password)
        if user.password_hash == hashed:
            return user
        return None

    def save(self):
        """Inserts or updates a user record."""
        with Database.transaction() as conn:
            cursor = conn.cursor()
            if self.id is None:
                cursor.execute(
                    "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?);",
                    (self.username.strip().lower(), self.password_hash, self.role)
                )
                self.id = cursor.lastrowid
            else:
                cursor.execute(
                    "UPDATE users SET username = ?, password_hash = ?, role = ? WHERE id = ?;",
                    (self.username.strip().lower(), self.password_hash, self.role, self.id)
                )
