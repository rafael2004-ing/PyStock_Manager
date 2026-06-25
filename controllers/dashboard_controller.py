from models.database import Database
from models.customer import Customer
from models.supplier import Supplier
from models.product import Product
from models.order import Order

class DashboardController:
    def get_summary_stats(self):
        """Calculates global summary figures for the dashboard."""
        with Database.transaction() as conn:
            cursor = conn.cursor()
            
            # Total revenue (Sales sum)
            cursor.execute("SELECT SUM(total) as revenue FROM orders;")
            row = cursor.fetchone()
            revenue = row["revenue"] if row and row["revenue"] is not None else 0.0
            
            # Total stock items
            cursor.execute("SELECT SUM(stock) as total_stock FROM products;")
            row_stock = cursor.fetchone()
            total_stock = row_stock["total_stock"] if row_stock and row_stock["total_stock"] is not None else 0
            
        # Counts using models
        customers_count = len(Customer.get_all())
        suppliers_count = len(Supplier.get_all())
        critical_count = len(Product.get_critical_stock())
        
        return {
            "revenue": f"${revenue:,.2f}",
            "customers": customers_count,
            "suppliers": suppliers_count,
            "stock": total_stock,
            "critical_alerts": critical_count
        }

    def get_latest_orders(self):
        """Fetches the 5 most recent orders."""
        orders = Order.get_all()
        return orders[:5]
