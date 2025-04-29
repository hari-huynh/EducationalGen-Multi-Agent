import os
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from urllib.parse import quote_plus
from dotenv import load_dotenv

load_dotenv()

def get_mongo_client():
    db_password = quote_plus(os.getenv('DB_PASSWORD'))
    # uri = f"mongodb+srv://{os.getenv('DB_USER')}:{db_password}@{os.getenv('DB_HOST')}?retryWrites=true&w=majority&appName={os.getenv('DB_APP_NAME')}"
    uri = f"mongodb+srv://quangtruongairline:{db_password}@chatbotdb.pzsqjdr.mongodb.net/?retryWrites=true&w=majority&appName=chatbotdb"

    # Create a new client and connect to the server
    client = MongoClient(uri, tls=True, server_api=ServerApi('1'))

    try:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(e)

    return client
