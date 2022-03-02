import os
from config import db
import json
from models import Article, Product, Inventory

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
    db.session.add(p)
    
# Commit changes to add products and articles   
db.session.commit()

# Iterate over each new product and get its product_id
for product in PRODUCTS:
    stmt = db.select(Product).where(
                db.and_(
                    Product.name == product['name'],
                    Product.price == product['price']
                )
            )
    result = db.session.execute(stmt)
    product_id = result.fetchone().Product.product_id
    
    # Iterate over component articles and add to Inventory table
    components = product['contain_articles']
    
    for component in components:
        print(component)
        article_id = int(component.get('art_id'))
        print(article_id)
        required_article_qty = int(component.get('amount_of'))
        print(required_article_qty)
        i = Inventory(product_id=product_id, article_id=article_id, required_article_qty=required_article_qty)
        
        db.session.add(i)
        
# Commit changes to add relationships between products and articles   
db.session.commit()
