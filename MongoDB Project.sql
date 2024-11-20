import pymongo
import sqlite3
import os

# Establish a connection to MongoDB
mongo_client = pymongo.MongoClient("mongodb://localhost:27017/")
mongo_db = mongo_client["Bakery4"]
product_collection = mongo_db["products"]
customer_collection = mongo_db["customers"]
receipt_collection = mongo_db["receipts"]

# Create a SQLite in-memory database and load the SQL file to process the data
sqlite_conn = sqlite3.connect(":memory:")
sqlite_cursor = sqlite_conn.cursor()

# Load SQL schema and data
sqlite_cursor.executescript(sql_content)

# Extract data from SQLite tables and prepare for MongoDB
# 1. Extract Customers
sqlite_cursor.execute("SELECT * FROM Customer;")
customers = [
    {
        "_id": idx + 1,  # Incrementing ID for MongoDB
        "lastName": row[1],
        "firstName": row[2],
        "age": row[3],
        "gender": row[4],
        "street": row[5],
        "city": row[6],
        "state": row[7],
        "favorites": row[8],
        "lastVisit": row[9].isoformat() if row[9] else None,
    }
    for idx, row in enumerate(sqlite_cursor.fetchall())
]

# Insert into MongoDB
customer_collection.insert_many(customers)

# 2. Extract Products
sqlite_cursor.execute("SELECT * FROM Product;")
products = [
    {
        "_id": row[0],  # Use unique IDs from Product table
        "flavor": row[1],
        "kind": row[2],
        "price": float(row[3]) if row[3] else None,
        "ratings": [],  # Placeholder for ratings
    }
    for row in sqlite_cursor.fetchall()
]

# Insert into MongoDB
product_collection.insert_many(products)

# 3. Extract Receipts
sqlite_cursor.execute("SELECT * FROM Receipt;")
receipts = []
for row in sqlite_cursor.fetchall():
    receipt_id, purchase_date, customer_id, total = row
    sqlite_cursor.execute(
        "SELECT * FROM LineItem WHERE receiptId = ?;", (receipt_id,)
    )
    lineitems = [
        {"productId": item[1], "quantity": item[2], "price": float(item[3])}
        for item in sqlite_cursor.fetchall()
    ]
    receipts.append(
        {
            "purchaseDate": purchase_date.isoformat() if purchase_date else None,
            "customerId": customer_id,
            "total": float(total) if total else None,
            "lineItems": lineitems,
        }
    )

# Insert into MongoDB
receipt_collection.insert_many(receipts)

# Close SQLite connection
sqlite_conn.close()

# Confirm data insertion summary
{
    "customers": customer_collection.count_documents({}),
    "products": product_collection.count_documents({}),
    "receipts": receipt_collection.count_documents({}),
}
