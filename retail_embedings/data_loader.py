import os
import pandas as pd
from dotenv import load_dotenv
from azure.cosmos import CosmosClient

def load_retail_data():
    """Charge toutes les données Retail depuis Cosmos DB"""
    load_dotenv()
    endpoint = os.getenv("COSMOS_ENDPOINT")
    key = os.getenv("COSMOS_KEY")
    database_name = "RetailClient"
    container_name = "Retail"

    cosmos_client = CosmosClient(endpoint, credential=key)
    database = cosmos_client.get_database_client(database_name)
    container = database.get_container_client(container_name)

    query = "SELECT * FROM c"
    items = []

    for item in container.query_items(
        query=query,
        enable_cross_partition_query=True
    ):
        items.append(item)

    return pd.DataFrame(items)
