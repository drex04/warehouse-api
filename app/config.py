import os
import connexion
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

# Get base directory for Connexion
base_dir = os.path.abspath(os.path.dirname(__file__))

# Create connexion application
conn_app = connexion.App(__name__, specification_dir=base_dir)
app = conn_app.app

# Configure SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////' + os.path.join(base_dir, 'warehouse.db')
app.config['SQLALCHEMY_ECHO'] = True # TODO: change this to False in production
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Create SQLAlchemy db
db = SQLAlchemy(app)

# Initialize Marshmallow
mm = Marshmallow(app)