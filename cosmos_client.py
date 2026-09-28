import azure.cosmos.exceptions as exceptions
from azure.cosmos import CosmosClient, PartitionKey
from cosmos_config import COSMOS_CONFIG
import json
from datetime import datetime

class CosmosDBClient:
    def __init__(self):
        self.client = CosmosClient(
            COSMOS_CONFIG["endpoint"], 
            credential=COSMOS_CONFIG["primary_key"]
        )
        self.database = self.client.create_database_if_not_exists(
            id=COSMOS_CONFIG["database_name"]
        )
        self.container = self.database.create_container_if_not_exists(
            id=COSMOS_CONFIG["container_name"],
            partition_key=PartitionKey(path="/bank")
        )
    
    def save_result(self, result):
        """Save a scraping result to Cosmos DB"""
        try:
            # Add timestamp and id if not present
            if "id" not in result:
                result["id"] = f"{result['bank']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            if "timestamp" not in result:
                result["timestamp"] = datetime.now().isoformat()
            
            # Insert the document
            self.container.upsert_item(body=result)
            print(f"✅ Successfully saved result for {result['bank']} to Cosmos DB")
            return True
            
        except exceptions.CosmosHttpResponseError as e:
            print(f"❌ Error saving to Cosmos DB: {e.message}")
            return False
    
    def save_batch_results(self, results):
        """Save multiple results to Cosmos DB"""
        success_count = 0
        for result in results:
            if self.save_result(result):
                success_count += 1
        return success_count
    
    def query_results(self, query="SELECT * FROM c"):
        """Query results from Cosmos DB"""
        try:
            items = list(self.container.query_items(
                query=query,
                enable_cross_partition_query=True
            ))
            return items
        except exceptions.CosmosHttpResponseError as e:
            print(f"❌ Error querying Cosmos DB: {e.message}")
            return []