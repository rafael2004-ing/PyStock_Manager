from models.product import Product
from models.supplier import Supplier

class ProductController:
    def get_products(self):
        """Fetches all products."""
        return Product.get_all()

    def get_suppliers(self):
        """Fetches all suppliers for product assignment."""
        return Supplier.get_all()

    def save_product(self, product_id, code, name, description, stock, purchase_price, sale_price, min_stock, supplier_id):
        """Inserts or updates a product with validation."""
        code = code.strip().upper()
        name = name.strip()
        description = description.strip()

        if not code or not name:
            raise ValueError("El Código y el Nombre son obligatorios.")

        if not supplier_id:
            raise ValueError("Debe seleccionar un Proveedor para el producto.")

        # Parse and validate numeric inputs
        try:
            stock = int(stock)
            if stock < 0:
                raise ValueError()
        except ValueError:
            raise ValueError("El stock debe ser un número entero mayor o igual a 0.")

        try:
            purchase_price = float(purchase_price)
            if purchase_price < 0:
                raise ValueError()
        except ValueError:
            raise ValueError("El precio de compra debe ser un número decimal mayor o igual a 0.")

        try:
            sale_price = float(sale_price)
            if sale_price < 0:
                raise ValueError()
        except ValueError:
            raise ValueError("El precio de venta debe ser un número decimal mayor o igual a 0.")

        try:
            min_stock = int(min_stock)
            if min_stock < 0:
                raise ValueError()
        except ValueError:
            raise ValueError("El stock mínimo debe ser un número entero mayor o igual a 0.")

        # Check unique code
        existing = Product.get_by_code(code)
        if existing and (product_id is None or existing.id != product_id):
            raise ValueError(f"El código de producto '{code}' ya está asignado al producto '{existing.name}'.")

        # Verify supplier exists
        supplier = Supplier.get_by_id(supplier_id)
        if not supplier:
            raise ValueError("El Proveedor seleccionado no existe.")

        product = Product(
            id=product_id,
            code=code,
            name=name,
            description=description,
            stock=stock,
            purchase_price=purchase_price,
            sale_price=sale_price,
            min_stock=min_stock,
            supplier_id=supplier_id
        )
        product.save()
        return product

    def delete_product(self, product_id):
        """Deletes a product by ID."""
        product = Product.get_by_id(product_id)
        if not product:
            raise ValueError("Producto no encontrado.")
        try:
            product.delete()
        except Exception as e:
            raise ValueError("No se puede eliminar el producto porque está referenciado en el historial de facturas o compras.")
