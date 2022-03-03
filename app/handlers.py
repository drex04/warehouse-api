from flask import abort, jsonify
from config import db
from models import (
    Product,
    ProductSchema,
    Article,
    ArticleSchema,
    Inventory,
    InventorySchema
)
import json
import pandas as pd

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
        components = product.get('contain_articles')
        
        # Check if product already exists
        existing_product = Product.query \
            .filter(Product.name == name) \
            .filter(Product.price == price) \
            .one_or_none()
            
        # If it does not already exist, then add it
        if existing_product is None:
            # Add product to database
            p = Product(name=name, price=price)
            db.session.add(p)
            # Commit changes to add new product  
            db.session.commit()
            # Log which new product was added
            add_log.append(p)
        
            # Get the ID of the newly created Product so that records can be added to Inventory table
            stmt = db.select(Product).where(
                db.and_(
                    Product.name == product['name'],
                    Product.price == product['price']
                )
            )
            result = db.session.execute(stmt)
            product_id = result.fetchone().Product.product_id
            
            # Iterate over component articles and add records to Inventory table    
            for component in components:
                article_id = int(component.get('art_id'))
                required_article_qty = int(component.get('amount_of'))
                
                i = Inventory(product_id=product_id, article_id=article_id, required_article_qty=required_article_qty)
                
                db.session.add(i)
                
            # Commit Inventory db changes
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

def sell_product(productId):
    # TODO:
    # "Sell" a product and decrement the stock of its component articles by the required amount
    select_stmt = db.select(Inventory, Article).join(Inventory.product).join(Inventory.article).where(Inventory.product_id == productId)
    
    with db.engine.connect() as conn:
        results = conn.execute(select_stmt)
        df = pd.DataFrame(data=results)
        
        # if any required_article_quantity is more than current article stock, return an error
        insufficient_articles = df.loc[df['required_article_qty'] > df['stock'], ['product_id', 'article_id', 'required_article_qty', 'stock']]
        
        if len(insufficient_articles) > 0:
            abort(409, 'Insufficient product inventory')
        else:
            # otherwise, remove required_article_quantity from the current article stock
            new_df = df
            new_df['stock'] = new_df['stock'] - new_df['required_article_qty']
            new_stock_df = new_df[['article_id', 'stock']]
            new_stock = new_stock_df.to_dict('records')
            
            for article in new_stock:
                # Add updated stock to database
                update_stmt = (
                    db.update(Article).
                    where(Article.article_id == article['article_id']).
                    values(stock=article['stock'])
                )
                update_result = conn.execute(update_stmt)
        # Then commit all database changes
        db.session.commit()
            
        # Return updated product inventory
        response = read_product_inventory()
        return response

def read_product_inventory():
    # First, find minimum available inventory for each product
    stmt = db.select(Inventory, Product, Article).join(Inventory.product).join(Inventory.article)
        
    with db.engine.connect() as conn:
        results = conn.execute(stmt)
        df= pd.DataFrame(data=results)
        # Calculate hypothetical product stock as if each article was the only component
        df['product_stock'] = df.stock // df.required_article_qty
        
        # Group by the minimum product stock per product ID
        group_df = df.loc[df.groupby('product_id').product_stock.idxmin()]
        prod_inv_df = group_df[['product_id', 'name', 'price', 'product_stock']]
        
        # Convert to JSON format response
        prod_inv = prod_inv_df.to_dict('records')
        prod_inv = {'product_inventory': prod_inv}
        
    return prod_inv

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