from models.customer import Customer
from models.product import Product
from models.order import Order, OrderItem
from models.invoice import Invoice
from models.database import Database

class OrderController:
    def get_customers(self):
        """Fetches active customers for order billing selection."""
        return Customer.get_all()

    def get_products(self):
        """Fetches active products for order billing selection."""
        return Product.get_all()

    def create_order(self, customer_id, items, tax_rate=0.16):
        """
        Creates a sales order (Pedido) and generates its Invoice (Factura) atomically.
        'items' should be a list of dictionaries:
        [
            {"product_id": 12, "quantity": 3, "price": 150.0},
            ...
        ]
        """
        if not customer_id:
            raise ValueError("Debe seleccionar un cliente para la factura.")
        
        if not items:
            raise ValueError("El pedido debe contener al menos un producto.")

        # Calculate billing figures
        subtotal = 0.0
        order_items = []

        for item_data in items:
            pid = item_data["product_id"]
            qty = int(item_data.get("quantity") if "quantity" in item_data else item_data.get("qty", 0))
            price = float(item_data["price"])
            
            if qty <= 0:
                raise ValueError("La cantidad de cada producto debe ser mayor a 0.")
            
            item_subtotal = qty * price
            subtotal += item_subtotal

            # Create OrderItem object
            order_item = OrderItem(
                product_id=pid,
                quantity=qty,
                price=price,
                subtotal=item_subtotal
            )
            order_items.append(order_item)

        tax = subtotal * tax_rate
        total = subtotal + tax

        # Construct Order with status 'Autorizado'
        order = Order(
            customer_id=customer_id,
            status="Autorizado",
            subtotal=round(subtotal, 2),
            tax=round(tax, 2),
            total=round(total, 2),
            items=order_items
        )

        try:
            # Atomic transaction spanning Order and Invoice creation with stock deduction
            with Database.transaction() as conn:
                # 1. Create Order and OrderItems in database
                order.create(conn=conn)
                # 2. Create Invoice and deduct product stock
                invoice = Invoice.create_from_order(order, conn=conn)
                
            return order, invoice
        except ValueError as ve:
            # Catch stock validation or status errors
            raise ValueError(str(ve))
        except Exception as e:
            raise ValueError(f"Error inesperado al procesar la facturación: {str(e)}")
