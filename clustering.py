import joblib
import numpy as np
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
# Load embeddings (change filename if needed)
corporate_embeddings = joblib.load("corporate_embeddings.pkl")
retail_embeddings = joblib.load("retail_embeddings.pkl")

print("Corporate embeddings shape:", np.array(corporate_embeddings).shape)
print("Retail embeddings shape:", np.array(retail_embeddings).shape)
# Corporate clustering
kmeans_corporate = KMeans(n_clusters=5, random_state=42)
corporate_labels = kmeans_corporate.fit_predict(corporate_embeddings)

# Retail clustering
kmeans_retail = KMeans(n_clusters=5, random_state=42)
retail_labels = kmeans_retail.fit_predict(retail_embeddings)

# Save clustering results
joblib.dump(corporate_labels, "corporate_clusters.pkl")
joblib.dump(retail_labels, "retail_clusters.pkl")

print("✅ Clustering done! Saved to corporate_clusters.pkl and retail_clusters.pkl")
def visualize_clusters(embeddings, labels, title):
    pca = PCA(n_components=2)
    reduced = pca.fit_transform(embeddings)

    plt.figure(figsize=(8, 6))
    plt.scatter(reduced[:, 0], reduced[:, 1], c=labels, cmap="tab10", alpha=0.7)
    plt.title(title)
    plt.xlabel("PCA-1")
    plt.ylabel("PCA-2")
    plt.show()
#Visualize with PCA
# Corporate clusters
visualize_clusters(corporate_embeddings, corporate_labels, "Corporate Client Clusters")

# Retail clusters
visualize_clusters(retail_embeddings, retail_labels, "Retail Client Clusters")
#Inspect Clusters
# Count how many clients per cluster
(unique_corp, counts_corp) = np.unique(corporate_labels, return_counts=True)
print("Corporate cluster distribution:", dict(zip(unique_corp, counts_corp)))

(unique_retail, counts_retail) = np.unique(retail_labels, return_counts=True)
print("Retail cluster distribution:", dict(zip(unique_retail, counts_retail)))
