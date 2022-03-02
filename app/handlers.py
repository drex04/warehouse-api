from flask import abort, jsonify
from config import db
from models import (
    Product,
    ProductSchema,
    Article,
    ArticleSchema
)
import json

# Handler function for GET PRODUCTS endpoint
def read_all_products():
    # Query the db to return all products
    products = Product.query.order_by(Product.product_id).all()
    # Serialize the query results to produce a response
    product_schema = ProductSchema(many=True)
    return product_schema.dump(products)

def read_all_articles():
    # Query the db to return all articles
    articles = Article.query.order_by(Article.article_id).all()
    # Serialize the query results to produce a response
    article_schema = ArticleSchema(many=True)
    return article_schema.dump(articles)

# Handler function for POST /api/products endpoint
def create_products(body):
    products = body['products']
    add_log = []
    # Loop through list of products and add each to database if not exists
    for product in products:
        name = product.get('name')
        price = product.get('price')
        
        # Check if product already exists
        existing_product = Product.query \
            .filter(Product.name == name) \
            .filter(Product.price == price) \
            .one_or_none()
            
        # If it does not already exist, then add it
        if existing_product is None:
            # Add product to database
            p = Product(name=name, price=price)
            
            # TODO: add Product-Article relations to database
            
            db.session.add(p)
            # Log which new products were added
            add_log.append(p)
            
    # Then commit all database changes
    db.session.commit()
    
    # Return serialized version of the products added to db
    product_schema = ProductSchema(many=True)
    if len(add_log) > 0:
        added_products = jsonify(product_schema.dump(add_log))
        return added_products, 201
    else:
        abort(409, 'All products already exist in database')
        
# Handler function for POST /api/articles endpoint
def create_articles(body):
    articles = body['inventory']
    add_log = []

    # Loop through list of articles and add each to database if not already in db
    for article in articles:
        name = article.get('name')
        stock = article.get('stock')
        
        # Check if article already exists
        existing_article = Article.query \
            .filter(Article.name == name) \
            .one_or_none()
        
        # If it does not already exist, then add the article with provided stock
        if existing_article is None:
       
            # Add article to database
            a = Article(name=name, stock=stock)
            db.session.add(a)
            # Add new article to the log tracking which articles were added
            add_log.append(a)
            
        # If the article does already exist, then add the new stock to existing stock
        else: 
            new_stock = int(stock)
            existing_article.stock += new_stock
            # Add updated article to the log tracking which articles were added
            add_log.append(existing_article)
            
    # Then commit all database changes
    db.session.commit()
    
    # Return serialized version of the articles added to db
    article_schema = ArticleSchema(many=True)
    if len(add_log) > 0:
        added_articles = jsonify(article_schema.dump(add_log))
        return added_articles, 201
    else:
        abort(409, 'Article addition failed')

def delete_product_inventory():
    # TODO:
    return None

def read_product_inventory():
    #TODO:
    
    # join product, bom, article, add calculated column
    return None

def upload_file(formData):
    # parse file and upload products to DB
    body = json.load(formData)
    if (body.get('products')):
        response = create_products(body)
        return response
    elif (body.get('inventory')):
        response = create_articles(body)
        return response
    else:
        return 'File does not match required JSON schema', 400