from pymongo.mongo_client import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()


# FLASK
SECRET_KEY = os.getenv('SECRET_KEY')

# SQL LITE CONFIG
SQL_LITE = os.getenv('SQL_LITE_URL')


# mongo db config
client = MongoClient(os.getenv('MONGO_URL'))
mongo_db = client['AmazonKlone']
products = mongo_db['products']
categories = mongo_db['categories']

# choosing to put cart in mongo db sunce product info is already there
carts = mongo_db['carts']

# LOCATION_API
LOCATION_API = os.getenv('SECRET_KEY')
