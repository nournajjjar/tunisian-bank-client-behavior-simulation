import os
import pandas as pd
import joblib
import json
from collections import Counter
from dotenv import load_dotenv
from azure.cosmos import CosmosClient


# === Load Retail Data from Cosmos DB ===
def load_retail_data():
    """Load all retail data from Cosmos DB"""
    load_dotenv()
    endpoint = os.getenv("COSMOS_ENDPOINT")
    key = os.getenv("COSMOS_KEY")
    database_name = "RetailClient"
    container_name = "Retail"

    if not endpoint or not key:
        raise ValueError("❌ COSMOS_ENDPOINT or COSMOS_KEY not found in .env file")

    client = CosmosClient(endpoint, credential=key)
    database = client.get_database_client(database_name)
    container = database.get_container_client(container_name)

    query = "SELECT * FROM c"
    items = []

    for item in container.query_items(query=query, enable_cross_partition_query=True):
        items.append(item)

    return pd.DataFrame(items)


# === Load Corporate Data from Cosmos DB ===
def load_corporate_data(batch_size=1000):
    """Load all corporate data from Cosmos DB"""
    load_dotenv()
    endpoint = os.getenv("COSMOS_ENDPOINT")
    key = os.getenv("COSMOS_KEY")
    database_name = "CorporareClient"
    container_name = "corporate1"

    if not endpoint or not key:
        raise ValueError("❌ COSMOS_ENDPOINT or COSMOS_KEY not found in .env file")

    client = CosmosClient(endpoint, credential=key)
    database = client.get_database_client(database_name)
    container = database.get_container_client(container_name)

    query = "SELECT * FROM c"
    items = []

    for item in container.query_items(
        query=query,
        enable_cross_partition_query=True,
        max_item_count=batch_size
    ):
        items.append(item)

    return pd.DataFrame(items)


# === Profiling Function ===
def profile_clusters(df, cluster_col, num_features, cat_features, dataset_name):
    profiles = {}
    for cluster_id in sorted(df[cluster_col].unique()):
        cluster_data = df[df[cluster_col] == cluster_id]
        profile = {"size": len(cluster_data)}

        # Numerical averages
        for col in num_features:
            if col in cluster_data.columns:
                try:
                    profile[f"avg_{col}"] = cluster_data[col].astype(float).mean(skipna=True)
                except Exception:
                    profile[f"avg_{col}"] = None
            else:
                profile[f"avg_{col}"] = None

        # Categorical most common
        for col in cat_features:
            if col in cluster_data.columns:
                most_common = Counter(cluster_data[col].dropna()).most_common(1)
                profile[f"top_{col}"] = most_common[0][0] if most_common else None
            else:
                profile[f"top_{col}"] = None

        profiles[int(cluster_id)] = profile  # ✅ force en int natif pour JSON

    # Print nicely
    print(f"\n=== {dataset_name} Cluster Profiles ===")
    for cid, prof in profiles.items():
        print(f"\nCluster {cid}:")
        for k, v in prof.items():
            print(f"  {k}: {v}")

    # Save to JSON
    with open(f"{dataset_name.lower()}_profiles.json", "w", encoding="utf-8") as f:
        json.dump(profiles, f, indent=4, ensure_ascii=False)

    return profiles


# === MAIN SCRIPT ===
if __name__ == "__main__":

    # === Retail ===
    print("📥 Loading retail data from Cosmos DB...")
    retail_df = load_retail_data()
    print(f"✅ Retail data loaded: {len(retail_df)} rows")

    retail_labels = joblib.load("retail_clusters.pkl")
    retail_df["cluster"] = [int(c) for c in retail_labels]  # ✅ convertir labels numpy → int

    retail_profiles = profile_clusters(
        retail_df,
        cluster_col="cluster",
        num_features=["age", "annual_salary"],  # 👉 adapte selon ton vrai dataset
        cat_features=["gender", "civil_status", "occupation", "region"],
        dataset_name="Retail"
    )

    # === Corporate ===
    print("\n📥 Loading corporate data from Cosmos DB...")
    corporate_df = load_corporate_data()
    print(f"✅ Corporate data loaded: {len(corporate_df)} rows")

    corporate_labels = joblib.load("corporate_clusters.pkl")
    corporate_df["cluster"] = [int(c) for c in corporate_labels]  # ✅ convertir labels numpy → int

    corporate_profiles = profile_clusters(
        corporate_df,
        cluster_col="cluster",
        num_features=["employees", "share_capital_dt"],  # 👉 adapte selon ton vrai dataset
        cat_features=["market", "digital_maturity", "credit_needs", "gouvernorate"],
        dataset_name="Corporate"
    )

    print("\n🎉 Profiling completed! JSON files saved.")
