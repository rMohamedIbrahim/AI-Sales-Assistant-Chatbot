from motor.motor_asyncio import AsyncIOMotorClient
from src.core.config import settings
from typing import Optional
import logging

class Database:
    client: Optional[AsyncIOMotorClient] = None
    
    @classmethod
    async def connect_db(cls):
        try:
            cls.client = AsyncIOMotorClient(settings.MONGODB_URI)
            logging.info("Connected to MongoDB")
        except Exception as e:
            logging.error(f"Failed to connect to MongoDB: {e}")
            raise e

    @classmethod
    async def close_db(cls):
        if cls.client:
            cls.client.close()
            logging.info("Closed MongoDB connection")

    @classmethod
    def get_db(cls):
        if not cls.client:
            raise ConnectionError("Database not connected")
        return cls.client[settings.DATABASE_NAME]

# Collection names
CUSTOMERS_COLLECTION = "customers"
BOOKINGS_COLLECTION = "bookings"
SERVICES_COLLECTION = "services"
INTERACTIONS_COLLECTION = "interactions"
