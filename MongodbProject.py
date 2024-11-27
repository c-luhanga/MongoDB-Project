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
REVIEW_PROB = 0.06  # Exactly 5% chance per receipt
MIN_AGE = 18
MAX_AGE = 75
DEFAULT_PURCHASE_PROB = 0.1
DEFAULT_MIN_PRODUCTS = 1
DEFAULT_MAX_PRODUCTS = 5
DEFAULT_MIN_QUANTITY = 1
DEFAULT_MAX_QUANTITY = 5
DEFAULT_REVIEW_PROB = 0.01
DEFAULT_AGE = 18
DEFAULT_STREET = ''
DEFAULT_CITY = ''
DEFAULT_STATE = ''

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

        num_receipts = rng.randint(1, 1)
        receipt_bulk = []
        product_updates = {}

        for _ in range(num_receipts):
            if rng.random() <= self.purchaseProb:
                receipt = {
                    "customer_id": str(self.id),
                    "date": date,
                    "lineitems": [],
                    "total": 0,
                    "_internal": []  # Hidden list for validation
                }

                num_products = rng.randint(self.minProducts, self.maxProducts)
                total_amount = 0

                for line_num in range(1, num_products + 1):
                    product = rng.choice(products)
                    quantity = rng.randint(self.minQuantity, self.maxQuantity)
                    price = product['price']
                    extended_price = price * quantity
                    total_amount += extended_price

                    # Visible line item
                    visible_line_item = {
                        "productId": product["_id"],
                        "price": price,
                        "quantity": quantity
                    }
                    receipt["lineitems"].append(visible_line_item)

                    # # Hidden line item for validation
                    # internal_line_item = {
                    #     "extPrice": extended_price
                    # }
                    # receipt["_internal"].append(internal_line_item)

                receipt["total"] = total_amount
                receipt_bulk.append(receipt)

                # Add review at receipt level with exactly 5% probability
                if rng.random() <= REVIEW_PROB:
                    # Pick a random product from this receipt
                    reviewed_item = rng.choice(receipt["lineitems"])
                    product_id = reviewed_item["productId"]
                    
                    if product_id not in product_updates:
                        product_updates[product_id] = []
                    product_updates[product_id].append({
                        "customerId": self.id,
                        "score": rng.randint(1, 5),
                        "comment": "This is a standard review comment."
                    })

        if receipt_bulk:
            receipts.insert_many(receipt_bulk)
            # Update customer's last visit date
            db['customers'].update_one(
                {"_id": self.id},
                {"$set": {"last_visit": date}}
            )

        # Batch update products with ratings
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
            'lastName': customer_data.get('lastName', DEFAULT_STREET),
            'firstName': customer_data.get('firstName', DEFAULT_CITY),
            'purchaseProb': customer_data.get('purchaseProb',
                                               DEFAULT_PURCHASE_PROB),
            'minProducts': customer_data.get('minProducts', 
                                             DEFAULT_MIN_PRODUCTS),
            'maxProducts': customer_data.get('maxProducts', 
                                             DEFAULT_MAX_PRODUCTS),
            'minQuantity': customer_data.get('minQuantity', 
                                             DEFAULT_MIN_QUANTITY),
            'maxQuantity': customer_data.get('maxQuantity', 
                                             DEFAULT_MAX_QUANTITY),
            'reviewProb': customer_data.get('reviewProb', DEFAULT_REVIEW_PROB),
            'age': customer_data.get('age', DEFAULT_AGE),
            'street': customer_data.get('street', DEFAULT_STREET),
            'city': customer_data.get('city', DEFAULT_CITY),
            'state': customer_data.get('state', DEFAULT_STATE),
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

    # drop all collections
    product_collection.drop()
    customer_collection.drop()
    receipt_collection.drop()

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
            'favorites': c.favorites,
            'last_visit': None  # Initialize with None
        } for c in customers])
        print("Customers initialized")

    receipt_collection.drop()
    print("Receipts cleared")

    # Clear ratings from products
    product_collection.update_many({}, {"$set": {"ratings": []}})
    print("Product ratings cleared")
    
    time1 = datetime.now()
    args = parse_arguments()
    start_date = datetime.strptime(args.start_date, "%Y-%m-%d")
    end_date = datetime.strptime(args.end_date, "%Y-%m-%d")
    run_simulation(
        mongo_client, start_date, end_date, customer_collection, 
        product_collection
    )
    time2 = datetime.now()
    duration = (time2 - time1).total_seconds()
    print(f"Simulation took {duration:.2f} seconds")

    # print first product
    print("First product:")
    pprint(product_collection.find_one())

    #print first customer
    print("First customer:")
    pprint(customer_collection.find_one())

    #print first receipt
    print("First receipt:")
    pprint(receipt_collection.find_one(), width=80)
    
    # Validate receipt totals
    for receipt in receipt_collection.find():
        total = sum([
            line["price"] * line["quantity"] 
            for line in receipt["lineitems"]
        ])
        assert abs(total - receipt["total"]) < 0.01  # Use small epsilon for float comparison
    print("All receipts have the correct totals")

    # Validate last visit dates
    for customer in customer_collection.find():
        last_visit = receipt_collection.find_one(
            {"customerId": customer["_id"]},
            sort=[("purchaseDate", pymongo.DESCENDING)]
        )
        if last_visit:
            assert customer.get("last_visit") == last_visit["purchaseDate"]
    print("All customer last_visit dates updated correctly")

    # Calculate line item statistics
    total_lineitems = list(receipt_collection.aggregate([
        {"$unwind": "$lineitems"},
        {"$count": "total"}
    ]))[0]["total"]
    
    rate = total_lineitems / duration
    print(f"Generated {total_lineitems} lineitems in {duration:.2f} seconds "
          f"({rate:.2f} per sec)")

    # Calculate rating statistics
    total_receipts = receipt_collection.count_documents({})
    total_ratings = list(product_collection.aggregate([
        {"$unwind": "$ratings"},
        {"$count": "total"}
    ]))[0]["total"]
    
    rating_percentage = (total_ratings / total_receipts) * 100
    print(f"Generated {total_ratings} ratings over {total_receipts} receipts "
          f"({rating_percentage:.2f}%)")

    # Find customer with most reviews
    pipeline = [
        {"$unwind": "$ratings"},
        {"$group": {
            "_id": "$ratings.customerId",
            "count": {"$sum": 1},
            "avgScore": {"$avg": "$ratings.score"}
        }},
        {"$sort": {"count": -1}},
        {"$limit": 1}
    ]
    top_reviewer = list(product_collection.aggregate(pipeline))[0]
    print(f"Customer {top_reviewer['_id']} left the most reviews "
          f"({top_reviewer['count']}), with an average rating of "
          f"{top_reviewer['avgScore']:.2f}")

    # Customer purchase statistics
    pipeline = [
        {"$group": {
            "_id": "$customer_id",
            "num_receipts": {"$sum": 1},
            "avg_items": {"$avg": {"$size": "$lineitems"}}
        }},
        {"$sort": {"num_receipts": -1}}
    ]

    stats = list(receipt_collection.aggregate(pipeline))
    num_buyers = len(stats)

    print("\nPurchase Statistics:")
    print(f"{num_buyers} out of {NUM_CUSTOMERS} customers made purchases")
    print("\nTop 5 customers by number of receipts:")
    print("CustomerID | Receipts | Avg Items")  # Shortened header
    print("-" * 35)  # Reduced separator length
    for stat in stats[:5]:
        print(
            f"{stat['_id']:10} | "
            f"{stat['num_receipts']:8} | "
            f"{stat['avg_items']:,.1f}"
        )

    total_receipts = sum(s['num_receipts'] for s in stats)
    avg_items = (
        sum(s['avg_items'] * s['num_receipts'] for s in stats) / 
        total_receipts
    )
    print(
        f"\nOverall average items per receipt: "
        f"{avg_items:.1f}"
    )

if __name__ == "__main__":
    main()
