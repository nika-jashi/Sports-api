import os

from pymongo import MongoClient
from django.conf import settings
from functools import lru_cache

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

@lru_cache()
def _get_client():
    return MongoClient(settings.MONGO["URI"])

def mongo(collection_name: str):
    """Returns the specified MongoDB collection."""
    db = _get_client()[settings.MONGO["DB_NAME"]]
    return db[collection_name]
