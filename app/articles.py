from flask import abort, jsonify
from config import db
from models import (
    Article,
    ArticleSchema,
    )

# Handler function for GET Articles endpoint
def read_all_articles():
    # Query the db to return all articles
    articles = Article.query.order_by(Article.article_id).all()

    if len(articles) < 1:
        abort(404, 'No articles exist in database')
        
    # Serialize the query results to produce a response
    article_schema = ArticleSchema(many=True)
    return article_schema.dump(articles)

# Handler function for POST /api/articles endpoint
def create_articles(body):
    articles = body.get('inventory', None)
    if articles == None:
        abort(400, 'Invalid schema')
        
    add_log = []
    # Loop through list of articles and add each to database if not already in db
    for article in articles:
        name = article.get('name', None)
        stock = article.get('stock', None)
        
        # Data input validation
        if name == None or stock == None:
            abort(400, 'Articles must include a name and stock')
        
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