import os
from config import db
import json
from models import Product, Article

# Initialize database with test data
file_p = open('initial_products.json')
data_p = json.load(file_p)
file_p.close()
PRODUCTS = data_p['products']

file_a = open('initial_articles.json')
data_a = json.load(file_a)
file_a.close()
ARTICLES = data_a['inventory']

# Delete database file if it already exists
if os.path.exists('warehouse.db'):
    os.remove('warehouse.db')

# Create db
db.create_all()

for article in ARTICLES:
    a = Article(name=article['name'], stock=article['stock'])
    db.session.add(a)

# Iterate over the PRODUCTS dict & add to database
for product in PRODUCTS:
    p = Product(name=product['name'], price=product['price'])
    # TODO: add Product-Article relationship
    db.session.add(p)

db.session.commit()
