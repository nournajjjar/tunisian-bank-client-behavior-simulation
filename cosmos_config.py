import os
from dotenv import load_dotenv

load_dotenv()

# Azure Cosmos DB Configuration
COSMOS_CONFIG = {
    "endpoint": os.getenv("COSMOS_ENDPOINT", "https://your-account.documents.azure.com:443/"),
    "primary_key": os.getenv("COSMOS_PRIMARY_KEY", ""),
    "database_name": os.getenv("COSMOS_DATABASE_NAME", "client"),
    "container_name": os.getenv("COSMOS_CONTAINER_NAME", "scraping-results")
}