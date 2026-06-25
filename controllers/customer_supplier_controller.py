from models.customer import Customer
from models.supplier import Supplier

class CustomerSupplierController:
    def get_customers(self):
        """Fetches all customers."""
        return Customer.get_all()

    def get_suppliers(self):
        """Fetches all suppliers."""
        return Supplier.get_all()

    def save_customer(self, customer_id, rif, name, phone, email, address):
        """Creates or updates a customer with safety checks."""
        rif = rif.strip().upper()
        name = name.strip()
        phone = phone.strip()
        email = email.strip()
        address = address.strip()

        if not rif or not name:
            raise ValueError("El RIF/Cédula y el Nombre son obligatorios.")

        # Check duplicate RIF if new customer or changed RIF
        existing = Customer.get_by_rif(rif)
        if existing and (customer_id is None or existing.id != customer_id):
            raise ValueError(f"El RIF/Cédula '{rif}' ya está registrado con el cliente '{existing.name}'.")

        customer = Customer(
            id=customer_id,
            rif_cedula=rif,
            name=name,
            phone=phone,
            email=email,
            address=address
        )
        customer.save()
        return customer

    def save_supplier(self, supplier_id, rif, name, phone, email, address):
        """Creates or updates a supplier with safety checks."""
        rif = rif.strip().upper()
        name = name.strip()
        phone = phone.strip()
        email = email.strip()
        address = address.strip()

        if not rif or not name:
            raise ValueError("El RIF/Cédula y el Nombre son obligatorios.")

        # Check duplicate RIF
        existing = Supplier.get_by_rif(rif)
        if existing and (supplier_id is None or existing.id != supplier_id):
            raise ValueError(f"El RIF/Cédula '{rif}' ya está registrado con el proveedor '{existing.name}'.")

        supplier = Supplier(
            id=supplier_id,
            rif_cedula=rif,
            name=name,
            phone=phone,
            email=email,
            address=address
        )
        supplier.save()
        return supplier

    def delete_customer(self, customer_id):
        """Deletes a customer by ID."""
        customer = Customer.get_by_id(customer_id)
        if not customer:
            raise ValueError("Cliente no encontrado.")
        try:
            customer.delete()
        except Exception as e:
            raise ValueError("No se puede eliminar el cliente porque posee historial de compras/facturas.")

    def delete_supplier(self, supplier_id):
        """Deletes a supplier by ID."""
        supplier = Supplier.get_by_id(supplier_id)
        if not supplier:
            raise ValueError("Proveedor no encontrado.")
        try:
            supplier.delete()
        except Exception as e:
            raise ValueError("No se puede eliminar el proveedor porque posee registros de compras/abastecimiento asociadas.")

    def get_customer_history(self, customer_id):
        """Gets sales orders associated with this customer."""
        customer = Customer.get_by_id(customer_id)
        if not customer:
            return []
        return customer.get_order_history()

    def get_supplier_history(self, supplier_id):
        """Gets purchase orders associated with this supplier."""
        supplier = Supplier.get_by_id(supplier_id)
        if not supplier:
            return []
        return supplier.get_purchase_history()
