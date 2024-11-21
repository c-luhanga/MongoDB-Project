import pymongo
import random
from datetime import datetime, timedelta
from faker import Faker
import argparse
from pprint import pprint

# Constants
NUM_CUSTOMERS = 30
MIN_PURCHASE_PROB = 0.1
MAX_PURCHASE_PROB = 0.9
MIN_PRODUCTS = 1
MAX_PRODUCTS = 5
MIN_REPEAT = 1
MAX_REPEAT = 5
REVIEW_PROB = 0.01  # Reduced to 1% to achieve around 5% of receipts
MIN_AGE = 18
MAX_AGE = 75

class Customer:

    def __init__(
        self, _id, lastName, firstName, purchaseProb, minProducts, 
        maxProducts, minQuantity, maxQuantity, reviewProb, age, 
        street, city, state, favorites
    ):
        self.id = _id
        self.lastName = lastName
        self.firstName = firstName
        self.purchaseProb = purchaseProb
        self.minProducts = minProducts
        self.maxProducts = maxProducts
        self.minQuantity = minQuantity
        self.maxQuantity = maxQuantity
        self.reviewProb = reviewProb
        self.age = age
        self.street = street
        self.city = city
        self.state = state
        self.favorites = favorites

    def do_one_day(self, connection, date, products, rng):
        db = connection['Bakery4']
        receipts = db['receipts']
        products_collection = db['products']

        num_receipts = rng.randint(1, 5)
        receipt_bulk = []
        product_updates = {}

        for _ in range(num_receipts):
            if rng.random() <= self.purchaseProb:
                receipt = {
                    "customerId": self.id,
                    "purchaseDate": date,
                    "total": 0,
                    "lineItems": []
                }

                num_products = rng.randint(self.minProducts, self.maxProducts)
                total_amount = 0

                for line_num in range(1, num_products + 1):
                    product = rng.choice(products)
                    quantity = rng.randint(self.minQuantity, self.maxQuantity)
                    price = product['price']
                    extended_price = price * quantity
                    total_amount += extended_price

                    line_item = {
                        "lineNum": line_num,
                        "productId": product["_id"],
                        "qty": quantity,
                        "extPrice": extended_price
                    }
                    receipt["lineItems"].append(line_item)

                    if rng.random() <= self.reviewProb:
                        if product["_id"] not in product_updates:
                            product_updates[product["_id"]] = []
                        product_updates[product["_id"]].append({
                            "customerId": self.id,
                            "score": rng.randint(1, 5),
                            "comment": "This is a standard review comment."
                        })

                receipt["total"] = total_amount
                receipt_bulk.append(receipt)

        if receipt_bulk:
            receipts.insert_many(receipt_bulk)

        for product_id, ratings in product_updates.items():
            products_collection.update_one(
                {"_id": product_id},
                {"$push": {"ratings": {"$each": ratings}}}
            )

def generate_random_customer(i, product_collection):
    fake = Faker()
    purchase_prob = random.uniform(MIN_PURCHASE_PROB, MAX_PURCHASE_PROB)
    review_prob = REVIEW_PROB
    age = random.randint(MIN_AGE, MAX_AGE)
    min_products = random.randint(MIN_PRODUCTS, MAX_PRODUCTS)
    max_products = random.randint(min_products, MAX_PRODUCTS)
    min_quantity = random.randint(MIN_REPEAT, MAX_REPEAT)
    max_quantity = random.randint(min_quantity, MAX_REPEAT)
    favorites = [
        random.choice(list(product_collection.find({}, {"_id": 1})))["_id"] 
        for _ in range(random.randint(1, 3))
    ]
    return Customer(
        _id=i,
        lastName=fake.last_name(),
        firstName=fake.first_name(),
        purchaseProb=purchase_prob,
        minProducts=min_products,
        maxProducts=max_products,
        minQuantity=min_quantity,
        maxQuantity=max_quantity,
        reviewProb=review_prob,
        age=age,
        street=fake.street_address(),
        city=fake.city(),
        state=fake.state_abbr(),
        favorites=favorites
    )

def add_products(product_collection):
    product_collection.drop()

    products = [
        {"_id": "20-BC-C-10", "flavor": "Chocolate", "type": "Cake", 
         "price": 8.95, "ratings": []},
        {"_id": "20-BC-L-10", "flavor": "Lemon", "type": "Cake", 
         "price": 8.95, "ratings": []},
        {"_id": "20-CA-7.5", "flavor": "Casino", "type": "Cake", 
         "price": 15.95, "ratings": []},
        {"_id": "24-8x10", "flavor": "Opera", "type": "Cake", 
         "price": 15.95, "ratings": []},
        {"_id": "25-STR-9", "flavor": "Strawberry", "type": "Cake", 
         "price": 11.95, "ratings": []},
        {"_id": "26-8x10", "flavor": "Truffle", "type": "Cake", 
         "price": 15.95, "ratings": []},
        {"_id": "45-CH", "flavor": "Chocolate", "type": "Eclair", 
         "price": 3.25, "ratings": []},
        {"_id": "45-CO", "flavor": "Coffee", "type": "Eclair", 
         "price": 3.5, "ratings": []},
        {"_id": "45-VA", "flavor": "Vanilla", "type": "Eclair", 
         "price": 3.25, "ratings": []},
        {"_id": "46-11", "flavor": "Napoleon", "type": "Cake", 
         "price": 13.49, "ratings": []},
        {"_id": "90-ALM-I", "flavor": "Almond", "type": "Tart", 
         "price": 3.75, "ratings": []},
        {"_id": "90-APIE-10", "flavor": "Apple", "type": "Pie", 
         "price": 5.25, "ratings": []},
        {"_id": "90-APP-11", "flavor": "Apple", "type": "Tart", 
         "price": 3.25, "ratings": []},
        {"_id": "90-APR-PF", "flavor": "Apricot", "type": "Tart", 
         "price": 3.25, "ratings": []},
        {"_id": "90-BER-11", "flavor": "Berry", "type": "Tart", 
         "price": 3.25, "ratings": []},
        {"_id": "90-BLK-PF", "flavor": "Blackberry", "type": "Tart", 
         "price": 3.25, "ratings": []},
        {"_id": "90-BLU-11", "flavor": "Blueberry", "type": "Tart", 
         "price": 3.25, "ratings": []},
        {"_id": "90-CH-PF", "flavor": "Chocolate", "type": "Tart", 
         "price": 3.75, "ratings": []},
        {"_id": "90-CHR-11", "flavor": "Cherry", "type": "Tart", 
         "price": 3.25, "ratings": []},
        {"_id": "90-LEM-11", "flavor": "Lemon", "type": "Tart", 
         "price": 3.25, "ratings": []},
        {"_id": "90-PEC-11", "flavor": "Pecan", "type": "Tart", 
         "price": 3.75, "ratings": []},
        {"_id": "70-GA", "flavor": "Ganache", "type": "Cookie", 
         "price": 1.15, "ratings": []},
        {"_id": "70-GON", "flavor": "Gongolais", "type": "Cookie", 
         "price": 1.15, "ratings": []},
        {"_id": "70-R", "flavor": "Raspberry", "type": "Cookie", 
         "price": 1.09, "ratings": []},
        {"_id": "70-LEM", "flavor": "Lemon", "type": "Cookie", 
         "price": 0.79, "ratings": []},
        {"_id": "70-M-CH-DZ", "flavor": "Chocolate", "type": "Meringue", 
         "price": 1.25, "ratings": []},
        {"_id": "70-M-VA-SM-DZ", "flavor": "Vanilla", "type": "Meringue", 
         "price": 1.15, "ratings": []},
        {"_id": "70-MAR", "flavor": "Marzipan", "type": "Cookie", 
         "price": 1.25, "ratings": []},
        {"_id": "70-TU", "flavor": "Tuile", "type": "Cookie", 
         "price": 1.25, "ratings": []},
        {"_id": "70-W", "flavor": "Walnut", "type": "Cookie", 
         "price": 0.79, "ratings": []},
        {"_id": "50-ALM", "flavor": "Almond", "type": "Croissant", 
         "price": 1.45, "ratings": []},
        {"_id": "50-APP", "flavor": "Apple", "type": "Croissant", 
         "price": 1.45, "ratings": []},
        {"_id": "50-APR", "flavor": "Apricot", "type": "Croissant", 
         "price": 1.45, "ratings": []},
        {"_id": "50-CHS", "flavor": "Cheese", "type": "Croissant", 
         "price": 1.75, "ratings": []},
        {"_id": "50-CH", "flavor": "Chocolate", "type": "Croissant", 
         "price": 1.75, "ratings": []},
        {"_id": "51-APR", "flavor": "Apricot", "type": "Danish", 
         "price": 1.15, "ratings": []},
        {"_id": "51-APP", "flavor": "Apple", "type": "Danish", 
         "price": 1.15, "ratings": []},
        {"_id": "51-ATW", "flavor": "Almond", "type": "Twist", 
         "price": 1.15, "ratings": []},
        {"_id": "51-BC", "flavor": "Almond", "type": "Bear Claw", 
         "price": 1.95, "ratings": []},
        {"_id": "51-BLU", "flavor": "Blueberry", "type": "Danish", 
         "price": 1.15, "ratings": []}
    ]

    product_collection.insert_many(products)

def run_simulation(
    mongo_client, start_date, end_date, customer_collection, 
    product_collection
):
    print(f"Running simulation from {start_date} to {end_date}")
    rng = random.Random()
    current_date = start_date

    customers = []
    for customer_data in customer_collection.find():
        customer_dict = {
            '_id': customer_data['_id'],
            'lastName': customer_data.get('lastName', ''),
            'firstName': customer_data.get('firstName', ''),
            'purchaseProb': customer_data.get('purchaseProb', 0.5),
            'minProducts': customer_data.get('minProducts', 1),
            'maxProducts': customer_data.get('maxProducts', 5),
            'minQuantity': customer_data.get('minQuantity', 1),
            'maxQuantity': customer_data.get('maxQuantity', 5),
            'reviewProb': customer_data.get('reviewProb', 0.05),
            'age': customer_data.get('age', 25),
            'street': customer_data.get('street', ''),
            'city': customer_data.get('city', ''),
            'state': customer_data.get('state', ''),
            'favorites': customer_data.get('favorites', [])
        }
        customers.append(Customer(**customer_dict))

    products = list(product_collection.find())

    count = 0
    while current_date <= end_date:
        for customer in customers:
            customer.do_one_day(mongo_client, current_date, products, rng)
            count += 1
        current_date += timedelta(days=1)

    print("Simulation completed successfully")
    print(f"Number of line items: {count}")

def parse_arguments():
    parser = argparse.ArgumentParser(description="Run a full simulation.")
    parser.add_argument(
        "start_date", type=str, help="Start date in YYYY-MM-DD format"
    )
    parser.add_argument(
        "end_date", type=str, help="End date in YYYY-MM-DD format"
    )
    return parser.parse_args()

def main():
    MONGODB_URI = open("uri.txt").read()

    mongo_client = pymongo.MongoClient(
        MONGODB_URI, tlsAllowInvalidCertificates=True
    )
    mongo_db = mongo_client["Bakery4"]
    
    product_collection = mongo_db["products"]
    customer_collection = mongo_db["customers"]
    receipt_collection = mongo_db["receipts"]

    if product_collection.count_documents({}) == 0:
        add_products(product_collection)
        print("Products initialized")

    if customer_collection.count_documents({}) == 0:
        customers = [
            generate_random_customer(i, product_collection) 
            for i in range(NUM_CUSTOMERS)
        ]
        customer_collection.insert_many([{
            '_id': c.id,
            'lastName': c.lastName,
            'firstName': c.firstName,
            'purchaseProb': c.purchaseProb,
            'minProducts': c.minProducts,
            'maxProducts': c.maxProducts,
            'minQuantity': c.minQuantity,
            'maxQuantity': c.maxQuantity,
            'reviewProb': c.reviewProb,
            'age': c.age,
            'street': c.street,
            'city': c.city,
            'state': c.state,
            'favorites': c.favorites
        } for c in customers])
        print("Customers initialized")

    receipt_collection.drop()
    print("Receipts cleared")

    # Clear ratings from products
    product_collection.update_many({}, {"$set": {"ratings": []}})
    print("Product ratings cleared")

    args = parse_arguments()
    start_date = datetime.strptime(args.start_date, "%Y-%m-%d")
    end_date = datetime.strptime(args.end_date, "%Y-%m-%d")
    run_simulation(
        mongo_client, start_date, end_date, customer_collection, 
        product_collection
    )
    
    print("Number of receipts: ", receipt_collection.count_documents({}))

    pipeline = [
        {"$unwind": "$lineItems"},
        {"$count": "totalLineItems"}
    ]
    print(
        "Number of line items: ", 
        list(receipt_collection.aggregate(pipeline))[0]["totalLineItems"]
    )

    pipeline2 = [
        {"$unwind": "$ratings"},
        {"$count": "totalRatings"}
    ]
    total_ratings = list(product_collection.aggregate(pipeline2))[0]["totalRatings"]
    total_receipts = receipt_collection.count_documents({})
    print(
        "Number of ratings: ", total_ratings,
        " ratings make up", 
        f"{(total_ratings / total_receipts) * 100:.2f}% of the number of receipts."
    )

    pipeline3 = [
        {"$unwind": "$ratings"},
        {"$group": {"_id": "$ratings.customerId", "avgScore": {"$avg": "$ratings.score"}}},
        {"$sort": {"avgScore": -1}},
        {"$limit": 1}
    ]
    print(
        "Average score given by the customer who gave the most ratings: ", 
        list(product_collection.aggregate(pipeline3))[0]["avgScore"]
    )

    print("Data generation and insertion complete.")

if __name__ == "__main__":
    main()
