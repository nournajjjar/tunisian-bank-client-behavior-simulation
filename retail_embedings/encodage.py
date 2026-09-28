# encodage_local.py
from sentence_transformers import SentenceTransformer
from data_loader import load_retail_data
import joblib

# Load retail data directly
retail_df = load_retail_data()  # you can increase the limit later

# Print columns to verify
print("Columns in retail_df:", retail_df.columns.tolist())

# Select columns to encode
columns_to_use = [
    "gender",
    "age",
    "civil_status",
    "sector_activity",
    "region",
    "occupation",
    "annual_salary"
]

# Combine text features into a single string per row
retail_df["text_to_encode"] = retail_df[columns_to_use].astype(str).agg(" | ".join, axis=1)

# Load the local sentence-transformers model (free)
model = SentenceTransformer("all-MiniLM-L6-v2")

# Encode the text into embeddings
print("Encoding in progress...")
embeddings = model.encode(retail_df["text_to_encode"].tolist(), show_progress_bar=True)

# Save embeddings locally
joblib.dump(embeddings, "retail_embeddings.pkl")

print("✅ Embeddings saved successfully to retail_embeddings.pkl")

