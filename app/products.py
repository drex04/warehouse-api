from flask import abort, jsonify
from config import db
from models import (
    Product,
    ProductSchema,
    Article,
    Inventory
    )
import pandas as pd

# Handler function for GET Products endpoint
def read_all_products():
    # Query the db to return all products
    products = Product.query.order_by(Product.product_id).all()

    if len(products) < 1:
        abort(404, 'No products exist in database')
        
    # Serialize the query results to produce a response
    product_schema = ProductSchema(many=True)
    return product_schema.dump(products)

# Handler function for POST /api/products endpoint
def create_products(body):
    products = body.get('products', None)
    if products == None:
        abort(400, 'Invalid schema')
    
    add_log = []
    # Loop through list of products and add each to database if not exists
    for product in products:
        name = product.get('name', None)
        price = product.get('price', None)
        components = product.get('contain_articles', None)
        
        # Data input validation
        if name == None or price == None:
            abort(400, 'Products must include a name and price')
            
        if len(components) < 1:
            abort(400, 'Each product must be composed of at least one article')
        else:
            for component in components:
                article_id = component.get('art_id', None)
                required_article_qty = component.get('amount_of', None)
                if article_id == None or required_article_qty == None:
                    abort(400, 'Each component article must include a numerical ID and a required quantity')
        
        
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
                    Product.name == name,
                    Product.price == price
                )
            )
            result = db.session.execute(stmt)
            product_id = result.fetchone().Product.product_id
            
            # Iterate over component articles and add records to Inventory table                
            for component in components:
                article_id = component.get('art_id', None)
                required_article_qty = component.get('amount_of', None)
                
                if isinstance(article_id, str):
                    article_id = int(article_id)
                if isinstance(required_article_qty, str):
                    required_article_qty = int(required_article_qty)
                                
                i = Inventory(product_id=product_id, article_id=article_id, required_article_qty=required_article_qty)
                
                db.session.add(i)
                
            # Commit Inventory table db changes
            db.session.commit()
    
    # Return serialized version of the products added to db
    product_schema = ProductSchema(many=True)
    if len(add_log) > 0:
        added_products = jsonify(product_schema.dump(add_log))
        return added_products, 201
    else:
        abort(409, 'All products already exist in database')

def sell_product(productId):
    # "Sell" a product and decrement the stock of its component articles by the required amount    
    select_stmt = db.select(Inventory, Article).join(Inventory.product).join(Inventory.article).where(Inventory.product_id == productId)
    
    with db.engine.connect() as conn:
        results = conn.execute(select_stmt)
        df = pd.DataFrame(data=results)
 
        if len(df) < 1:
            abort(404, 'Requested product not found in database')
        
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
        if len(df) < 1:
            abort(404, 'No products found in database')
        # Calculate hypothetical product stock as if each article was the only component
        df['product_stock'] = df.stock // df.required_article_qty
        
        # Group by the minimum product stock per product ID
        group_df = df.loc[df.groupby('product_id').product_stock.idxmin()]
        prod_inv_df = group_df[['product_id', 'name', 'price', 'product_stock']]
        
        # Convert to JSON format response
        prod_inv = prod_inv_df.to_dict('records')
        prod_inv = {'product_inventory': prod_inv}
        
    return prod_inv