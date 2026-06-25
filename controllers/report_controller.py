from models.product import Product
from models.order import Order
from datetime import datetime

class ReportController:
    def get_critical_stock(self):
        """Fetches products that are running low on stock."""
        return Product.get_critical_stock()

    def get_sales_report(self, start_date_str, end_date_str):
        """
        Retrieves sales orders within a date range and compiles summary metrics.
        Dates are passed as 'YYYY-MM-DD'.
        """
        # Validate date formats
        try:
            datetime.strptime(start_date_str, "%Y-%m-%d")
            datetime.strptime(end_date_str, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Las fechas deben tener el formato AAAA-MM-DD.")

        # Query database via Order Model
        orders = Order.get_by_date_range(start_date_str, end_date_str)

        # Calculate metrics
        order_count = len(orders)
        total_revenue = sum(order.total for order in orders)
        avg_order = (total_revenue / order_count) if order_count > 0 else 0.0

        return {
            "orders": orders,
            "total_revenue": f"${total_revenue:,.2f}",
            "order_count": order_count,
            "average_order": f"${avg_order:,.2f}"
        }

    def get_all_invoices(self):
        """Fetches all invoices with customer name and RIF."""
        from models.database import Database
        with Database.transaction() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT i.*, c.name AS customer_name, c.rif_cedula AS customer_rif
                FROM invoices i
                JOIN orders o ON i.order_id = o.id
                JOIN customers c ON o.customer_id = c.id
                ORDER BY i.invoice_date DESC;
                """
            )
            return cursor.fetchall()
