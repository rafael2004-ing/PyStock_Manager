import unittest
import os
import sys
import sqlite3

# Asegurar que el directorio raíz del proyecto esté en el path de búsqueda de Python
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from models.database import Database
from models.user import User
from models.supplier import Supplier
from models.product import Product
from models.customer import Customer
from models.order import Order, OrderItem
from models.invoice import Invoice

class TestEnterpriseSystem(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Point DB to a separate test database file
        import config
        config.DB_PATH = os.path.join(config.BASE_DIR, "test_empresa.db")
        
        # Ensure clean database state
        if os.path.exists(config.DB_PATH):
            os.remove(config.DB_PATH)
            
        Database.initialize()

    @classmethod
    def tearDownClass(cls):
        # Cleanup test DB file
        import config
        if os.path.exists(config.DB_PATH):
            try:
                os.remove(config.DB_PATH)
            except OSError:
                pass

    def setUp(self):
        # Clear database records between tests to isolate tests cleanly
        with Database.transaction() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM invoices;")
            cursor.execute("DELETE FROM order_items;")
            cursor.execute("DELETE FROM orders;")
            cursor.execute("DELETE FROM purchase_items;")
            cursor.execute("DELETE FROM purchases;")
            cursor.execute("DELETE FROM products;")
            cursor.execute("DELETE FROM suppliers;")
            cursor.execute("DELETE FROM customers;")
            cursor.execute("DELETE FROM users;")
            try:
                cursor.execute("DELETE FROM sqlite_sequence;")
            except sqlite3.OperationalError:
                pass

    def test_user_authentication(self):
        # 1. Create a user
        pwd_hash = User.hash_password("secret123")
        user = User(id=None, username="operator", password_hash=pwd_hash, role="Vendedor")
        user.save()
        self.assertIsNotNone(user.id)

        # 2. Test successful authentication
        authed_user = User.authenticate("operator", "secret123")
        self.assertIsNotNone(authed_user)
        self.assertEqual(authed_user.role, "Vendedor")

        # 3. Test wrong password
        self.assertIsNone(User.authenticate("operator", "wrong_password"))

        # 4. Test non-existent user
        self.assertIsNone(User.authenticate("ghost", "secret123"))

    def test_supplier_product_constraint(self):
        # 1. Create supplier
        supp = Supplier(id=None, rif_cedula="J-1111", name="Supplier A", phone="123", email="a@a.com", address="Addr A")
        supp.save()

        # 2. Create product linked to supplier
        prod = Product(
            id=None, code="P01", name="Product 1", description="Desc",
            stock=10, purchase_price=10.0, sale_price=15.0, min_stock=2,
            supplier_id=supp.id
        )
        prod.save()

        # 3. Try to delete the supplier while linked to a product (should fail due to foreign key RESTRICT)
        with self.assertRaises(sqlite3.IntegrityError):
            with Database.transaction() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM suppliers WHERE id = ?;", (supp.id,))

    def test_invoice_transactional_rollback_on_insufficient_stock(self):
        # 1. Setup entities
        supp = Supplier(id=None, rif_cedula="J-2222", name="Supplier B", phone="123", email="b@b.com", address="Addr B")
        supp.save()

        prod = Product(
            id=None, code="P02", name="Product 2", description="Desc",
            stock=5, purchase_price=10.0, sale_price=20.0, min_stock=1,
            supplier_id=supp.id
        )
        prod.save()

        cust = Customer(id=None, rif_cedula="V-123", name="Customer A", phone="123", email="c@c.com", address="Addr C")
        cust.save()

        # 2. Setup an Order requesting 10 items (stock is only 5!)
        order_item = OrderItem(product_id=prod.id, quantity=10, price=20.0, subtotal=200.00)
        order = Order(
            id=None, customer_id=cust.id, status="Autorizado",
            subtotal=200.0, tax=32.0, total=232.0, items=[order_item]
        )

        # 3. Try to create Order and Invoice in a single atomic transaction
        # Since stock is insufficient, Invoice.create_from_order should fail with ValueError.
        with self.assertRaises(ValueError) as context:
            with Database.transaction() as conn:
                order.create(conn=conn)
                Invoice.create_from_order(order, conn=conn)

        self.assertIn("Stock insuficiente", str(context.exception))

        # 4. Assert Rollback: verify no order or invoice records were persisted
        all_orders = Order.get_all()
        self.assertEqual(len(all_orders), 0)

        # 5. Verify stock was NOT deducted (stays at 5)
        reloaded_prod = Product.get_by_id(prod.id)
        self.assertEqual(reloaded_prod.stock, 5)

    def test_invoice_successful_transaction(self):
        # 1. Setup entities
        supp = Supplier(id=None, rif_cedula="J-3333", name="Supplier C", phone="123", email="c@c.com", address="Addr C")
        supp.save()

        prod = Product(
            id=None, code="P03", name="Product 3", description="Desc",
            stock=15, purchase_price=10.0, sale_price=20.0, min_stock=2,
            supplier_id=supp.id
        )
        prod.save()

        cust = Customer(id=None, rif_cedula="V-456", name="Customer B", phone="123", email="d@d.com", address="Addr D")
        cust.save()

        # 2. Setup Order requesting 5 items (stock is 15)
        order_item = OrderItem(product_id=prod.id, quantity=5, price=20.0, subtotal=100.00)
        order = Order(
            id=None, customer_id=cust.id, status="Autorizado",
            subtotal=100.0, tax=16.0, total=116.0, items=[order_item]
        )

        # 3. Run atomic transaction
        with Database.transaction() as conn:
            order.create(conn=conn)
            invoice = Invoice.create_from_order(order, conn=conn)

        # 4. Verify entities saved successfully
        self.assertIsNotNone(order.id)
        self.assertIsNotNone(invoice.id)
        self.assertEqual(invoice.invoice_number, f"FAC-{invoice.id:04d}")

        # 5. Verify stock was deducted correctly (15 - 5 = 10)
        reloaded_prod = Product.get_by_id(prod.id)
        self.assertEqual(reloaded_prod.stock, 10)

        # 6. Verify order status updated to 'Facturado'
        reloaded_order = Order.get_by_id(order.id)
        self.assertEqual(reloaded_order.status, "Facturado")

if __name__ == "__main__":
    unittest.main()
