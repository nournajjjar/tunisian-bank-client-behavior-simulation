# encodage_local_corporate.py
from sentence_transformers import SentenceTransformer
from data_loader import load_corporate_data
import joblib

# Load corporate data directly
corporate_df = load_corporate_data()

# Print columns to verify
print("Columns in corporate_df:", corporate_df.columns.tolist())

# Select the most relevant columns for text encoding
columns_to_use = [
    "short_name",
    "company_name",
    "certification",
    "manager",
    "activities",
    "products",
    "factory_address",
    "gouvernorate",
    "delegation",
    "market",
    "foreign_participant_country",
    "share_capital_dt",
    "employees",
    "size",
    "credit_needs",
    "digital_maturity"
]

# Combine text features into a single string per row
corporate_df["text_to_encode"] = corporate_df[columns_to_use].astype(str).agg(" | ".join, axis=1)

# Load the sentence-transformers model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Encode the text into embeddings
print("Encoding corporate data in progress...")
embeddings = model.encode(corporate_df["text_to_encode"].tolist(), show_progress_bar=True)

# Save embeddings locally
joblib.dump(embeddings, "corporate_embeddings.pkl")

print("✅ Corporate embeddings saved successfully to corporate_embeddings.pkl")
