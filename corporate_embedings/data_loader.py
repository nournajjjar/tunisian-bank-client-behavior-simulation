import os
import pandas as pd
from dotenv import load_dotenv
from azure.cosmos import CosmosClient

def load_data(database_name, container_name, batch_size=1000):
    """Charge toutes les données depuis Cosmos DB (générique, sans limite)."""
    load_dotenv()
    endpoint = os.getenv("COSMOS_ENDPOINT")
    key = os.getenv("COSMOS_KEY")

    client = CosmosClient(endpoint, credential=key)
    database = client.get_database_client(database_name)
    container = database.get_container_client(container_name)

    query = "SELECT * FROM c"
    items = []
    continuation_token = None

    while True:
        batch = list(container.query_items(
            query=query,
            enable_cross_partition_query=True,
            max_item_count=batch_size,
            continuation_token=continuation_token
        ))
        if not batch:
            break
        items.extend(batch)

        # Update continuation token
        continuation_token = batch[-1].get("_continuation_token", None)
        if not continuation_token:
            break

    return pd.DataFrame(items)


def load__data(batch_size=1000):
    """Charge toutes les données Retail"""
    return load_data("RetailClient", "Retail", batch_size)


def load_corporate_data(batch_size=1000):
    """Charge toutes les données Corporate"""
    return load_data("CorporateClient", "Corporate", batch_size)
