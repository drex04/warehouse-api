from config import db, mm

class Product(db.Model):
    __tablename__ = 'product'
    __table_args__ = (db.UniqueConstraint('name', 'price'),)
    product_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    price = db.Column(db.String)
    articles = db.relationship("Inventory", back_populates="product")

class Article(db.Model):
    __tablename__ = 'article'
    article_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    stock = db.Column(db.Integer)
    products = db.relationship("Inventory", back_populates="article")

# Association object to track which articles compose each products and current product inventory
class Inventory(db.Model):
    __tablename__ = 'inventory'
    product_id = db.Column(db.Integer, db.ForeignKey('product.product_id'), primary_key=True)
    article_id = db.Column(db.Integer, db.ForeignKey('article.article_id'), primary_key=True)
    required_article_qty = db.Column(db.Integer)
    product = db.relationship("Product", back_populates="articles")
    article = db.relationship("Article", back_populates="products")



class ProductSchema(mm.SQLAlchemyAutoSchema):
    class Meta:
        model = Product
        load_instance = True
        sqla_session = db.session
        
class ArticleSchema(mm.SQLAlchemyAutoSchema):
    class Meta:
        model = Article
        load_instance = True
        sqla_session = db.session
        
class InventorySchema(mm.SQLAlchemyAutoSchema):
    class Meta:
        model = Inventory
        load_instance = True
        sqla_session = db.session