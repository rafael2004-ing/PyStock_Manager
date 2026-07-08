import sys
import os

# Asegurar que el directorio raíz del proyecto esté en el path de búsqueda de Python
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from models.database import Database
from models.user import User
from views.main_window import MainWindow
from views.login_view import LoginWindow

def seed_database_if_empty():
    """Inserts mock sample data on a fresh install to demonstrate the application's premium look."""
    with Database.transaction() as conn:
        cursor = conn.cursor()
        
        # Check if database has already been seeded
        cursor.execute("SELECT COUNT(*) as cnt FROM customers;")
        row = cursor.fetchone()
        if row["cnt"] > 0:
            # Ensure default users exist in pre-existing databases
            for username, pwd_hash, role in [
                ("admin", User.hash_password("admin"), "Administrador"),
                ("vendedor", User.hash_password("vendedor"), "Vendedor")
            ]:
                cursor.execute("SELECT COUNT(*) as cnt FROM users WHERE username = ?;", (username,))
                if cursor.fetchone()["cnt"] == 0:
                    cursor.execute(
                        "INSERT OR IGNORE INTO users (username, password_hash, role) VALUES (?, ?, ?);",
                        (username, pwd_hash, role)
                    )
            return # Database already populated
            
        print("Fresh database detected. Seeding sample records...")

        # 1. Insert sample users (passwords: admin, vendedor hashed)
        users = [
            ("admin", User.hash_password("admin"), "Administrador"),
            ("vendedor", User.hash_password("vendedor"), "Vendedor")
        ]
        cursor.executemany(
            "INSERT OR IGNORE INTO users (username, password_hash, role) VALUES (?, ?, ?);",
            users
        )

        # 2. Insert sample customers
        customers = [
            ("V-12345678", "José Rodríguez", "+58 412-5551234", "jose.rod@gmail.com", "Av. Bolívar, Local 12, Valencia"),
            ("V-87654321", "María Delgado", "+58 424-9876543", "maria_del@yahoo.com", "C.C. Metrópolis, Nivel 1, Local 4, San Diego"),
            ("J-31415926", "Tecnología Global C.A.", "+58 241-8889900", "contacto@tecglobal.com", "Zona Industrial Castillito, Galpón B5")
        ]
        cursor.executemany(
            "INSERT OR IGNORE INTO customers (rif_cedula, name, phone, email, address) VALUES (?, ?, ?, ?, ?);",
            customers
        )

        # 3. Insert sample suppliers
        suppliers = [
            ("J-99887766", "Distribuidora Nacional de Hardware", "+58 212-3334455", "ventas@distrihardware.com", "Av. Francisco de Miranda, Edif. Centro, Caracas"),
            ("J-11223344", "Suministros del Centro C.A.", "+58 241-7776655", "pedidos@sumicentro.com", "Calle Urdaneta, Galpón 9, Valencia")
        ]
        cursor.executemany(
            "INSERT OR IGNORE INTO suppliers (rif_cedula, name, phone, email, address) VALUES (?, ?, ?, ?, ?);",
            suppliers
        )

        # 4. Insert sample products (linked to supplier_id)
        products = [
            ("LAP-001", "Laptop Dell Vostro 15", "Laptop de oficina Intel i5 8GB RAM 256GB SSD", 12, 450.00, 599.99, 3, 1),
            ("MOU-002", "Mouse Óptico Logitech M170", "Mouse inalámbrico ergonómico color negro", 2, 8.50, 15.00, 5, 1),   # Critical stock (2 <= 5)
            ("KEY-003", "Teclado Mecánico Redragon", "Teclado RGB switch azul distribución español", 18, 28.00, 45.00, 4, 2),
            ("MON-004", "Monitor LG 24'' Full HD", "Monitor IPS con bordes ultrafinos y 75Hz", 4, 95.00, 139.99, 5, 2),    # Critical stock (4 <= 5)
            ("AUD-005", "Auriculares Corsair HS50", "Auriculares gamer estéreo con micrófono extraíble", 15, 32.00, 49.99, 3, 1)
        ]
        cursor.executemany(
            "INSERT OR IGNORE INTO products (code, name, description, stock, purchase_price, sale_price, min_stock, supplier_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?);",
            products
        )

        # 5. Insert sample purchases (Supplier supply history)
        cursor.execute("INSERT INTO purchases (supplier_id, total) VALUES (1, 5400.00);")
        p_id = cursor.lastrowid
        cursor.execute("INSERT INTO purchase_items (purchase_id, product_id, quantity, price, subtotal) VALUES (?, 1, 12, 450.00, 5400.00);", (p_id,))

        cursor.execute("INSERT INTO purchases (supplier_id, total) VALUES (2, 504.00);")
        p_id2 = cursor.lastrowid
        cursor.execute("INSERT INTO purchase_items (purchase_id, product_id, quantity, price, subtotal) VALUES (?, 3, 18, 28.00, 504.00);", (p_id2,))

        # 6. Insert sample sales orders (Customer orders) in status 'Facturado'
        cursor.execute("INSERT INTO orders (customer_id, status, subtotal, tax, total) VALUES (1, 'Facturado', 614.99, 98.40, 713.39);")
        o_id = cursor.lastrowid
        cursor.execute("INSERT INTO order_items (order_id, product_id, quantity, price, subtotal) VALUES (?, 1, 1, 599.99, 599.99);", (o_id,))
        cursor.execute("INSERT INTO order_items (order_id, product_id, quantity, price, subtotal) VALUES (?, 2, 1, 15.00, 15.00);", (o_id,))

        cursor.execute("INSERT INTO orders (customer_id, status, subtotal, tax, total) VALUES (2, 'Facturado', 279.98, 44.80, 324.78);")
        o_id2 = cursor.lastrowid
        cursor.execute("INSERT INTO order_items (order_id, product_id, quantity, price, subtotal) VALUES (?, 4, 2, 139.99, 279.98);", (o_id2,))

        # 7. Insert Invoice records (corresponding to orders)
        cursor.execute("INSERT INTO invoices (order_id, invoice_number, subtotal, tax, total) VALUES (?, 'FAC-0001', ?, ?, ?);", (o_id, 614.99, 98.40, 713.39))
        cursor.execute("INSERT INTO invoices (order_id, invoice_number, subtotal, tax, total) VALUES (?, 'FAC-0002', ?, ?, ?);", (o_id2, 279.98, 44.80, 324.78))

        print("Database seeding completed.")

def main():
    try:
        # Set global appearance mode to dark
        import customtkinter as ctk
        from config import CTK_THEME, CTK_COLOR_THEME
        ctk.set_appearance_mode(CTK_THEME)
        ctk.set_default_color_theme(CTK_COLOR_THEME)

        # Initialize SQLite database structures
        Database.initialize()
        
        # Populate with sample data if first run
        seed_database_if_empty()
        
        # Start authentication window
        print("Launching Authentication...")
        
        authenticated_user = None

        def handle_auth_success(user):
            nonlocal authenticated_user
            authenticated_user = user

        login_win = LoginWindow(on_success=handle_auth_success)
        login_win.mainloop()
        
        try:
            login_win.destroy()
        except Exception:
            pass

        if authenticated_user:
            print(f"User '{authenticated_user.username}' authenticated successfully as '{authenticated_user.role}'. Launching GUI...")
            app = MainWindow(authenticated_user)
            app.mainloop()
    except Exception as e:
        print(f"Error fatal al arrancar la aplicación: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
