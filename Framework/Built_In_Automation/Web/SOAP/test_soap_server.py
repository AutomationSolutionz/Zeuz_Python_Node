import logging
from spyne import (
    Application,
    rpc,
    ServiceBase,
    Integer,
    Unicode,
    Float,
    Boolean,
    Iterable,
    ComplexModel,
    Array,
)
from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication
from flask import Flask
from werkzeug.middleware.dispatcher import DispatcherMiddleware


# Define the Item type
class Item(ComplexModel):
    item_id = Unicode
    quantity = Integer
    price = Float


# Define the Order type
class Order(ComplexModel):
    order_id = Unicode
    customer_name = Unicode
    items = Array(Item)
    shipping_address = Unicode


# Define the SOAP service
class ZeuzSoapTestService(ServiceBase):
    @rpc(Integer, Integer, _returns=Integer)
    def add(ctx, num1, num2):
        """Adds two numbers."""
        return num1 + num2

    @rpc(Order, Boolean, _returns=Iterable(Unicode))
    def process_order(ctx, order, priority):
        """Processes an order."""
        # Calculate total cost
        total_cost = sum(item.quantity * item.price for item in order.items)
        # Generate item descriptions
        item_descriptions = [
            f"Item {item.item_id}: {item.quantity} x ${item.price}"
            for item in order.items
        ]

        # Include priority information
        priority_note = (
            "Priority order processing enabled."
            if priority
            else "Standard order processing."
        )
        return [f"Total Cost: ${total_cost:.2f}", *item_descriptions, priority_note]

    @rpc(Unicode, _returns=Array(Order))
    def get_orders_by_customer(ctx, customer_name):
        """Returns a list of orders for a given customer."""
        # Mocking a data source
        orders_data = [
            {
                "order_id": "OID123",
                "customer_name": "Shadow Purr",
                "items": [
                    {"item_id": "ITEM1", "quantity": 2, "price": 15.00},
                    {"item_id": "ITEM2", "quantity": 1, "price": 25.00},
                ],
                "shipping_address": "32/8 Shadow Catties Society, Earth",
            },
            {
                "order_id": "OID124",
                "customer_name": "Mini Tiny",
                "items": [
                    {"item_id": "ITEM3", "quantity": 1, "price": 50.00},
                ],
                "shipping_address": "123 Main St, Cattie Residential area, Earth",
            },
            {
                "order_id": "OID125",
                "customer_name": "Shadow Purr",
                "items": [
                    {"item_id": "ITEM4", "quantity": 3, "price": 10.00},
                    {"item_id": "ITEM5", "quantity": 2, "price": 8.00},
                ],
                "shipping_address": "45/12 Shadow Avenue, Catland",
            },
            {
                "order_id": "OID126",
                "customer_name": "Shadow Purr",
                "items": [
                    {"item_id": "ITEM6", "quantity": 1, "price": 30.00},
                ],
                "shipping_address": "78/2 Moonlight Street, Paradise Cat World",
            },
            {
                "order_id": "OID127",
                "customer_name": "Whiskers McFluff",
                "items": [
                    {"item_id": "ITEM7", "quantity": 5, "price": 12.50},
                ],
                "shipping_address": "89 Catnip Lane, Furry Town",
            },
            {
                "order_id": "OID128",
                "customer_name": "Paws McCuddles",
                "items": [
                    {"item_id": "ITEM8", "quantity": 2, "price": 15.00},
                    {"item_id": "ITEM9", "quantity": 1, "price": 20.00},
                ],
                "shipping_address": "56 Purrfect Road, Catville",
            },
            {
                "order_id": "OID129",
                "customer_name": "Kitty Claws",
                "items": [
                    {"item_id": "ITEM10", "quantity": 4, "price": 5.00},
                ],
                "shipping_address": "34 Meow Street, Feline City",
            },
        ]

        # Filtering orders for the specified customer
        filtered_orders = [
            Order(
                order_id=order["order_id"],
                customer_name=order["customer_name"],
                items=[
                    Item(
                        item_id=item["item_id"],
                        quantity=item["quantity"],
                        price=item["price"],
                    )
                    for item in order["items"]
                ],
                shipping_address=order["shipping_address"],
            )
            for order in orders_data
            if order["customer_name"] == customer_name
        ]

        return filtered_orders


# Create the SOAP application
soap_app = Application(
    [ZeuzSoapTestService],
    tns="zeuz.ai.soap",
    in_protocol=Soap11(validator="lxml"),
    out_protocol=Soap11(),
)

# WSGI Application
soap_wsgi_app = WsgiApplication(soap_app)

# Flask application
app = Flask(__name__)

# Attach the SOAP application to Flask
app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {"/soap": soap_wsgi_app})


@app.route("/", methods=["GET"])
def index():
    return "Welcome to the SOAP API! Use /soap for SOAP requests."


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger("spyne.protocol.xml").setLevel(logging.DEBUG)
    app.run(host="0.0.0.0", port=15000)
