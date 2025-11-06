from faker import Faker
import random
import uuid
import datetime

fake = Faker('pt_BR')


def generate_customer():
    return {
        "_id": str(uuid.uuid4()),
        "name": fake.name(),
        "email": fake.email(),
        "phone": fake.phone_number(),
        "address": {
            "street": fake.street_name(),
            "number": fake.building_number(),
            "city": fake.city(),
            "state": fake.state_abbr(),
            "zip": fake.postcode()
        },
        "created_at": datetime.datetime.utcnow()
    }


def generate_product():
    categories = ["Eletrônicos", "Moda", "Casa", "Esporte", "Beleza"]
    return {
        "_id": str(uuid.uuid4()),
        "sku": "SKU-" + str(random.randint(100000, 999999)),
        "name": fake.word().title() + " " + fake.word().title(),
        "category": random.choice(categories),
        "price": round(random.uniform(10, 2000), 2),
        "stock": random.randint(0, 500),
        "attributes": {
            "color": random.choice(["preto", "branco", "azul", "vermelho", "verde"]),
            "size": random.choice(["P", "M", "G", "Único"])
        }
    }


def generate_order(customers, products):
    cust = random.choice(customers)
    items = []
    total = 0.0
    for _ in range(random.randint(1, 4)):
        p = random.choice(products)
        qty = random.randint(1, 3)
        items.append(
            {"product_id": p["_id"], "sku": p["sku"], "price": p["price"], "qty": qty})
        total += p["price"] * qty
    return {
        "_id": str(uuid.uuid4()),
        "order_number": random.randint(1000000, 9999999),
        "customer_id": cust["_id"],
        "items": items,
        "total": round(total, 2),
        "status": random.choice(["pending", "confirmed", "shipped", "delivered", "cancelled"]),
        "created_at": datetime.datetime.utcnow()
    }
