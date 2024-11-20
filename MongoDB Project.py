import pymongo
import random
from datetime import datetime, timedelta
from faker import Faker 
import argparse
from pprint import pprint

#Constants
NUM_CUSTOMERS = 20
MIN_PURCHASE_PROB = 0.1
MAX_PURCHASE_PROB = 0.9
MIN_PRODUCTS = 1
MAX_PRODUCTS = 3
MIN_REPEAT = 1
MAX_REPEAT = 5
MIN_REVIEW_PROB = 0.1
MAX_REVIEW_PROB = 0.9
MIN_AGE = 25
MAX_AGE = 75
EXPIRATION_DAYS = 5
VARCHAR_LENGTH = 30

class Customer:

    def __init__(self, lastName, firstName, purchaseProb, minProducts, 
                 maxProducts, minQuantity, maxQuantity, reviewProb, age, 
                 street, city, state):
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

    def parse_arguments():
        parser = argparse.ArgumentParser(description="Run a full simulation.")
        parser.add_argument("start_date", type=str, 
                            help="Start date in YYYY-MM-DD format")
        parser.add_argument("end_date", type=str, 
                            help="End date in YYYY-MM-DD format")
        return parser.parse_args()

    # Generate sample customers
    def generate_random_customer(i, product_collection):
        fake = Faker()
        purchase_prob = random.uniform(MIN_PURCHASE_PROB, MAX_PURCHASE_PROB)
        review_prob = random.uniform(MIN_REVIEW_PROB, MAX_REVIEW_PROB)
        age = random.randint(MIN_AGE, MAX_AGE)
        min_products = random.randint(MIN_PRODUCTS, MAX_PRODUCTS)
        max_products = random.randint(min_products, MAX_PRODUCTS)
        min_quantity = random.randint(MIN_REPEAT, MAX_REPEAT)
        max_quantity = random.randint(min_quantity, MAX_REPEAT)
        return {
            "_id": i,
            "lastName": fake.last_name(),
            "firstName": fake.first_name(),
            "purchaseProb": purchase_prob,
            "minProducts": min_products,
            "maxProducts": max_products,
            "minQuantity": min_quantity,
            "maxQuantity": max_quantity,
            "reviewProb": review_prob,
            "age": age,
            "street": fake.street_address(),
            "city": fake.city(),
            "state": fake.state_abbr()
        }
    
    def add_products(product_collection):
        # Generate sample products
        products = [
        { _id: "20-BC-C-10", flavor: "Chocolate", type: "Cake", price: 8.95 },
        { _id: "20-BC-L-10", flavor: "Lemon", type: "Cake", price: 8.95 },
        { _id: "20-CA-7.5", flavor: "Casino", type: "Cake", price: 15.95 },
        { _id: "24-8x10", flavor: "Opera", type: "Cake", price: 15.95 },
        { _id: "25-STR-9", flavor: "Strawberry", type: "Cake", price: 11.95 },
        { _id: "26-8x10", flavor: "Truffle", type: "Cake", price: 15.95 },
        { _id: "45-CH", flavor: "Chocolate", type: "Eclair", price: 3.25 },
        { _id: "45-CO", flavor: "Coffee", type: "Eclair", price: 3.5 },
        { _id: "45-VA", flavor: "Vanilla", type: "Eclair", price: 3.25 },
        { _id: "46-11", flavor: "Napoleon", type: "Cake", price: 13.49 },
        { _id: "90-ALM-I", flavor: "Almond", type: "Tart", price: 3.75 },
        { _id: "90-APIE-10", flavor: "Apple", type: "Pie", price: 5.25 },
        { _id: "90-APP-11", flavor: "Apple", type: "Tart", price: 3.25 },
        { _id: "90-APR-PF", flavor: "Apricot", type: "Tart", price: 3.25 },
        { _id: "90-BER-11", flavor: "Berry", type: "Tart", price: 3.25 },
        { _id: "90-BLK-PF", flavor: "Blackberry", type: "Tart", price: 3.25 },
        { _id: "90-BLU-11", flavor: "Blueberry", type: "Tart", price: 3.25 },
        { _id: "90-CH-PF", flavor: "Chocolate", type: "Tart", price: 3.75 },
        { _id: "90-CHR-11", flavor: "Cherry", type: "Tart", price: 3.25 },
        { _id: "90-LEM-11", flavor: "Lemon", type: "Tart", price: 3.25 },
        { _id: "90-PEC-11", flavor: "Pecan", type: "Tart", price: 3.75 },
        { _id: "70-GA", flavor: "Ganache", type: "Cookie", price: 1.15 },
        { _id: "70-GON", flavor: "Gongolais", type: "Cookie", price: 1.15 },
        { _id: "70-R", flavor: "Raspberry", type: "Cookie", price: 1.09 },
        { _id: "70-LEM", flavor: "Lemon", type: "Cookie", price: 0.79 },
        { _id: "70-M-CH-DZ", flavor: "Chocolate", type: "Meringue", price: 1.25 },
        { _id: "70-M-VA-SM-DZ", flavor: "Vanilla", type: "Meringue", price: 1.15 },
        { _id: "70-MAR", flavor: "Marzipan", type: "Cookie", price: 1.25 },
        { _id: "70-TU", flavor: "Tuile", type: "Cookie", price: 1.25 },
        { _id: "70-W", flavor: "Walnut", type: "Cookie", price: 0.79 },
        { _id: "50-ALM", flavor: "Almond", type: "Croissant", price: 1.45 },
        { _id: "50-APP", flavor: "Apple", type: "Croissant", price: 1.45 },
        { _id: "50-APR", flavor: "Apricot", type: "Croissant", price: 1.45 },
        { _id: "50-CHS", flavor: "Cheese", type: "Croissant", price: 1.75 },
        { _id: "50-CH", flavor: "Chocolate", type: "Croissant", price: 1.75 },
        { _id: "51-APR", flavor: "Apricot", type: "Danish", price: 1.15 },
        { _id: "51-APP", flavor: "Apple", type: "Danish", price: 1.15 },
        { _id: "51-ATW", flavor: "Almond", type: "Twist", price: 1.15 },
        { _id: "51-BC", flavor: "Almond", type: "Bear Claw", price: 1.95 },
        { _id: "51-BLU", flavor: "Blueberry", type: "Danish", price: 1.15 }
            # Add more products as needed
        ]

        # Insert products into MongoDB
        product_collection.insert_many(products)
        
    #simulate a single day of activity for a customer
    def do_one_day(self, connection, date, products, rng):
        db = connection['Bakery4']
        receipts = db['receipts']
        customers = db['customers']
        products_collection = db['products']

        if rng.random() <= self.purchaseProb:
            receipt = {
                "customerId": self.id,
                "purchaseDate": date,
                "total": 0,
                "lineItems": []
            }
            receipt_id = receipts.insert_one(receipt).inserted_id

            customers.update_one(
                {"_id": self.id},
                {"$set": {"lastVisit": date}}
            )

            num_products = rng.randint(self.minProducts, self.maxProducts)
            total_amount = 0

            for line_num in range(1, num_products + 1):
                product = rng.choice(products)
                quantity = rng.randint(self.minQuantity, self.maxQuantity)

                product_info = products_collection.find_one({"_id": product["_id"]}, {"price": 1})
                price = product_info['price']
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
                    product_rating = {
                        "customerId": self.id,
                        "score": rng.randint(1, 5),
                        "comment": "This is a standard review comment."
                    }
                    products_collection.update_one(
                        {"_id": product["_id"]},
                        {"$push": {"ratings": product_rating}}
                    )

            receipts.update_one(
                {"_id": receipt_id},
                {"$set": {"total": total_amount, "lineItems": receipt["lineItems"]}}
            )

    # Run simulation
    def run_simulation( start_date, end_date, customers, products):
        print(f"Running simulation from {start_date} to {end_date}")
        rng = random.Random()
        current_date = start_date

        count = 0
        while current_date <= end_date:
            for customer in customers:
                customer.do_one_day( current_date, products, rng)
                count += 1
            current_date += timedelta(days=1)
        
       
        print("Simulation completed successfully")
        print(f"Number of line items: {count}")

    # Generate and insert receipts

    print("Data generation and insertion complete.")

    def main():
        # Establish a connection to MongoDB
        MONGODB_URI = open("uri.txt").read()

        # Connect to your MongoDB cluster:
        mongo_client = pymongo.MongoClient(MONGODB_URI)
        mongo_db = mongo_client["Bakery4"]
        product_collection = mongo_db["products"]
        customer_collection = mongo_db["customers"]

        # Add products to the product collection
        Customer.add_products(product_collection)
        #print all the products
        for product in product_collection.find():
            pprint(product)

        # drop the bakery4 database to start fresh check if the database is dropped after running the code
        # mongo_client.drop_database("Bakery4")
        # if "Bakery4" in mongo_client.list_database_names():
        #     print("Database not dropped")
        #     print(mongo_client.list_database_names())

        # # Generate sample customers
        # customers = [Customer.generate_random_customer(i, product_collection) for i in range(NUM_CUSTOMERS)]
        # customer_collection.insert_many(customers)

        # Run simulation
        # args = Customer.parse_arguments()
        # start_date = datetime.strptime(args.start_date, "%Y-%m-%d")
        # end_date = datetime.strptime(args.end_date, "%Y-%m-%d")
        # Customer.run_simulation(start_date, end_date, customers, product_collection)

        print("Data generation and insertion complete.")

    if __name__ == "__main__":
        main()
