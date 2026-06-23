import sqlite3
import os
from contextlib import contextmanager
import config

class Database:
    @staticmethod
    def get_connection():
        """Creates and returns a connection to SQLite with foreign keys enabled."""
        conn = sqlite3.connect(config.DB_PATH)
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.row_factory = sqlite3.Row  
        return conn

    @classmethod
    @contextmanager
    def transaction(cls):
        """Context manager for database transactions. Commits on success, rolls back on error."""
        conn = cls.get_connection()
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    @classmethod
    def initialize(cls):
        """Initializes the database schema, running auto-migration if outdated."""
        # Check if users table exists, if not, drop tables to recreate with new schema
        conn = sqlite3.connect(config.DB_PATH)
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users';")
            if not cursor.fetchone():
                cursor.execute("DROP TABLE IF EXISTS purchase_items;")
                cursor.execute("DROP TABLE IF EXISTS purchases;")
                cursor.execute("DROP TABLE IF EXISTS order_items;")
                cursor.execute("DROP TABLE IF EXISTS invoices;")
                cursor.execute("DROP TABLE IF EXISTS orders;")
                cursor.execute("DROP TABLE IF EXISTS products;")
                cursor.execute("DROP TABLE IF EXISTS customers;")
                cursor.execute("DROP TABLE IF EXISTS suppliers;")
                conn.commit()
        except Exception:
            pass
        finally:
            conn.close()

        schema = """
        -- Users Table
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL
        );

        -- Customers Table
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rif_cedula TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            phone TEXT,
            email TEXT,
            address TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- Suppliers Table
        CREATE TABLE IF NOT EXISTS suppliers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rif_cedula TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            phone TEXT,
            email TEXT,
            address TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- Products Table (linked to Supplier)
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            stock INTEGER NOT NULL DEFAULT 0 CHECK(stock >= 0),
            purchase_price REAL NOT NULL DEFAULT 0.0 CHECK(purchase_price >= 0),
            sale_price REAL NOT NULL DEFAULT 0.0 CHECK(sale_price >= 0),
            min_stock INTEGER NOT NULL DEFAULT 5 CHECK(min_stock >= 0),
            supplier_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (supplier_id) REFERENCES suppliers(id) ON DELETE RESTRICT
        );

        -- Orders Table (representing a Pedido)
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER NOT NULL,
            order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT NOT NULL DEFAULT 'Pendiente', -- 'Pendiente', 'Autorizado', 'Facturado'
            subtotal REAL NOT NULL DEFAULT 0.0,
            tax REAL NOT NULL DEFAULT 0.0,
            total REAL NOT NULL DEFAULT 0.0,
            FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE RESTRICT
        );

        -- Order Details Table (DetallePedido)
        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL CHECK(quantity > 0),
            price REAL NOT NULL CHECK(price >= 0),
            subtotal REAL NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
            FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE RESTRICT
        );

        -- Invoices Table (Factura, generated from Authorized Order)
        CREATE TABLE IF NOT EXISTS invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER UNIQUE NOT NULL,
            invoice_number TEXT UNIQUE NOT NULL,
            invoice_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            subtotal REAL NOT NULL DEFAULT 0.0,
            tax REAL NOT NULL DEFAULT 0.0,
            total REAL NOT NULL DEFAULT 0.0,
            FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE RESTRICT
        );

        -- Purchases Table (Sourcing from Suppliers)
        CREATE TABLE IF NOT EXISTS purchases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            supplier_id INTEGER NOT NULL,
            purchase_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            total REAL NOT NULL DEFAULT 0.0,
            FOREIGN KEY (supplier_id) REFERENCES suppliers(id) ON DELETE RESTRICT
        );

        -- Purchase Details Table
        CREATE TABLE IF NOT EXISTS purchase_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            purchase_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL CHECK(quantity > 0),
            price REAL NOT NULL CHECK(price >= 0),
            subtotal REAL NOT NULL,
            FOREIGN KEY (purchase_id) REFERENCES purchases(id) ON DELETE CASCADE,
            FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE RESTRICT
        );
        """
        conn = sqlite3.connect(config.DB_PATH)
        try:
            conn.executescript(schema)
            conn.commit()
        finally:
            conn.close()
