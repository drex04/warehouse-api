from config import db, mm

class Product(db.Model):
    __tablename__ = 'product'
    product_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    price = db.Column(db.String)
    
class ProductSchema(mm.SQLAlchemyAutoSchema):
    class Meta:
        model = Product
        load_instance = True
        sqla_session = db.session

class Article(db.Model):
    __tablename__ = 'article'
    article_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    stock = db.Column(db.Integer)
    
class ArticleSchema(mm.SQLAlchemyAutoSchema):
    class Meta:
        model = Article
        load_instance = True
        sqla_session = db.session