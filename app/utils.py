from flask import abort
from products import create_products
from articles import create_articles
import json

def upload_file(formData):
    # Data validation
    if formData.content_type != 'application/json':
        abort(400, 'Uploaded file must have extension .json')
        
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