from pymongo.mongo_client import MongoClient
import os
from dotenv import load_dotenv
import logging

if os.getenv('FLASK_ENV') == 'development':
    logging.basicConfig(filename='app.log', level=logging.ERROR, format='%(asctime)s [%(levelname)s] : %(message)s')

load_dotenv()

# FLASK
SECRET_KEY = os.getenv('SECRET_KEY')
FLASK_ENV = os.getenv('FLASK_ENV')

DB_URL = os.getenv('DB_URL')

# POSTGRES CONFIG
POSTGRES_URL = os.getenv('POSTGRES_URL')


# mongo db config
client = MongoClient(os.getenv('MONGO_URL'))
mongo_db = client['AmazonKlone']
products = mongo_db['amazon_products']
categories = mongo_db['amazon_categories']
orders=mongo_db['amazon_orders']

# choosing to put cart in mongo db sunce product info is already there
carts = mongo_db['amazon_carts']

