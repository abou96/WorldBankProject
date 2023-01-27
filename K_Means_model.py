import pandas as pd
import numpy as np
from dataclasses import dataclass, field
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
from IPython.display import clear_output

def feature_selection(df , feature_selected : list) -> pd.DataFrame :
	return df[feature_selected].copy()

def plot_clusters(data, labels, centroids, iteration):
	pca = PCA(n_components=2)
	data_2d = pca.fit_transform(data)
	centroids_2d = pca.transform(centroids.T)
	clear_output(wait=True)
	plt.title(f'Iteration {iteration}')
	plt.scatter(x=data_2d[:,0], y=data_2d[:,1], c=labels)
	plt.scatter(x=centroids_2d[:,0], y=centroids_2d[:,1])
	plt.show()

@dataclass
class kmeans_model:
	n_cluster : int
	df : pd.DataFrame

	def normalize_data (self) :
		self.df = ((self.df - self.df.min()) / (self.df.max() - self.df.min())) * 10 + 1
		print('describe', self.df.describe)

	def initialize_centroids(self) :
		centroids = []
		for i in range(self.n_cluster):
			centroid = self.df.apply(lambda x: float(x.sample()))
			centroids.append(centroid)
		return pd.concat(centroids, axis=1)

	def get_labels(self, centroids):
		distances = centroids.apply(lambda x: np.sqrt(((self.df - x) ** 2).sum(axis=1)))
		labels = distances.idxmin(axis=1)
		return labels

	def find_new_centroids(self, labels):
		centroids = self.df.groupby(labels).apply(lambda x: np.exp(np.log(x).mean())).T
		return centroids


def main() -> None :
	players = pd.read_csv("players_22.csv")
	features = ["overall", "potential", "wage_eur", "value_eur", "age"]
	players = players.dropna(subset=features)
	data = feature_selection(df = players, feature_selected = features)

	max_iterations = 100
	centroid_count = 3

	knn = knn_model(n_cluster = centroid_count, df = data)
	knn.normalize_data()

	centroids = knn.initialize_centroids()
	old_centroids = pd.DataFrame()
	iteration = 1

	while iteration < max_iterations and not centroids.equals(old_centroids):
		old_centroids = centroids
		labels = knn.get_labels(centroids)
		centroids = knn.find_new_centroids(labels)
		# plot_clusters(data, labels, centroids, iteration)
		iteration += 1

	print(players[labels == 0][["short_name"] + features])
	# print(centroids)
if __name__ == "__main__":
	main()




