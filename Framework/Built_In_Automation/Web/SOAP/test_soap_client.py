import json
from zeep import Client
from zeep.helpers import serialize_object
from zeep.cache import SqliteCache
from zeep.transports import Transport
from requests import Session


def create_soap_client():
    # Configure caching and session
    session = Session()
    cache = SqliteCache(path="soap_cache.db", timeout=60)
    transport = Transport(cache=cache, session=session)

    # Create client from WSDL
    client = Client(wsdl="http://localhost:5000/soap?wsdl", transport=transport)
    return client


def sum_two_nums_soap(client, num1, num2):
    try:
        print("making a request")
        response = client.service.add(num1=num1, num2=num2)
        return { "response": response }
    except Exception as e:
        print(f"SOAP Error: {e}")
        return None


# Usage Example
def main():
    client = create_soap_client()

    soap_result = sum_two_nums_soap(client, 10, 5)
    print("SOAP Result:", soap_result)

    order_dict = {
        "order": {
            "order_id": "ORD-1234",
            "customer_name": "Shadow Purr",
            "items": {
                "Item": [
                    {"item_id": "001", "quantity": 1, "price": 5.0},
                    {"item_id": "002", "quantity": 2, "price": 10.0},
                    {"item_id": "003", "quantity": 3, "price": 15.0},
                ]
            },
            "shipping_address": "123 Main St, Cattie Residential area, Earth",
        },
        "priority": True,
    }
    resp = client.service.process_order(**order_dict)
    print(type(resp), resp)

    resp = client.service.get_orders_by_customer("Shadow Purr")
    print(type(resp))
    print(resp)

    serialized_resp = serialize_object(resp)
    print(type(serialized_resp))
    print(serialized_resp)

    to_py_types = json.loads(json.dumps(serialized_resp))
    print(to_py_types)


if __name__ == "__main__":
    main()
