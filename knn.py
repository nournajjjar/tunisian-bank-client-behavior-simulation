import joblib
import numpy as np
from sklearn.cluster import SpectralClustering  # Uses KNN internally
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt

# Load embeddings
corporate_embeddings = joblib.load("corporate_embeddings.pkl")
retail_embeddings = joblib.load("retail_embeddings.pkl")

print("Corporate embeddings shape:", np.array(corporate_embeddings).shape)
print("Retail embeddings shape:", np.array(retail_embeddings).shape)

# Corporate clustering with Spectral Clustering (KNN-based)
spectral_corp = SpectralClustering(
    n_clusters=5,
    affinity='nearest_neighbors',  # Uses KNN graph
    n_neighbors=10,               # Number of neighbors for KNN
    random_state=42
)
corporate_labels = spectral_corp.fit_predict(corporate_embeddings)

# Retail clustering with Spectral Clustering (KNN-based)
spectral_retail = SpectralClustering(
    n_clusters=5,
    affinity='nearest_neighbors',  # Uses KNN graph
    n_neighbors=10,                # Number of neighbors for KNN
    random_state=42
)
retail_labels = spectral_retail.fit_predict(retail_embeddings)

# Save clustering results
joblib.dump(corporate_labels, "corporate_knn_clusters.pkl")
joblib.dump(retail_labels, "retail_knn_clusters.pkl")

print("✅ KNN-based clustering done! Saved to corporate_knn_clusters.pkl and retail_knn_clusters.pkl")

# Visualization function (same as before)
def visualize_clusters(embeddings, labels, title):
    pca = PCA(n_components=2)
    reduced = pca.fit_transform(embeddings)
    plt.figure(figsize=(8, 6))
    plt.scatter(reduced[:, 0], reduced[:, 1], c=labels, cmap="tab10", alpha=0.7)
    plt.title(title)
    plt.xlabel("PCA-1")
    plt.ylabel("PCA-2")
    plt.show()

# Visualize Corporate Clusters (KNN-based)
visualize_clusters(corporate_embeddings, corporate_labels, "Corporate Clusters (KNN-based)")

# Visualize Retail Clusters (KNN-based)
visualize_clusters(retail_embeddings, retail_labels, "Retail Clusters (KNN-based)")

# Inspect Cluster Distribution
(unique_corp, counts_corp) = np.unique(corporate_labels, return_counts=True)
print("Corporate cluster distribution (KNN-based):", dict(zip(unique_corp, counts_corp)))

(unique_retail, counts_retail) = np.unique(retail_labels, return_counts=True)
print("Retail cluster distribution (KNN-based):", dict(zip(unique_retail, counts_retail)))