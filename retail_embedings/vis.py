import umap
import matplotlib.pyplot as plt
import seaborn as sns
import joblib

# Load embeddings
embeddings = joblib.load("retail_embeddings.pkl")

# Reduce to 2D
reducer = umap.UMAP(n_neighbors=15, min_dist=0.1, random_state=42)
embedding_2d = reducer.fit_transform(embeddings)

# Plot
plt.figure(figsize=(10, 7))
sns.scatterplot(x=embedding_2d[:,0], y=embedding_2d[:,1])
plt.title("2D visualization of retail embeddings")
plt.xlabel("UMAP-1")
plt.ylabel("UMAP-2")
plt.show()
