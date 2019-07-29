import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from progressbar import ProgressBar
import DataProcesser as dps
import networkx as nx
import HelperFunctions as hf
from sklearn.decomposition import LatentDirichletAllocation
from sklearn import cluster

def spectral_clustering(W):
	n = len(W)
	D = np.diag(W.sum(axis=0))
	laplacian = np.linalg.inv(D)**(1/2)@W@np.linalg.inv(D)**(1/2)
	u,s,v = np.linalg.svd(laplacian)
	x = np.linalg.inv(D)**(1/2)@u[:,1]
	cluster_label = zeros(n)
	cluster_label[x<0] = 1
	return(x)

def K_mean(data, nclusters = 10):
	k_means = cluster.KMeans(n_clusters=nclusters)
	k_means.fit(data)
	return(k_means.labels_)

def track_clustering(window_data):
	clustering = hf.LDAClustering(window_data["artist_sim"], window_data["ui"])
	clustering_labeled = dict(zip(window_data["users"], clustering))
	return(clustering_labeled)

def track_pct_nb(current_window, previous_window, n_nbhd=10):
	current_nbhd = K_mean(current_window["ut"], n_nbhd)
	previous_nbhd = K_mean(previous_window["ut"], n_nbhd)
	current_users = current_window["users"]
	previous_users = previous_window["users"]
	common_users = np.intersect1d(current_users, previous_users)
	all_users = np.union1d(current_users, previous_users)
	pct_nb = {}

	for user in all_users:
		if user in common_users:
			nh_current = current_nbhd[np.where(current_users==user)]
			nh_previous = previous_nbhd[np.where(previous_users==user)]
			current_nbs = current_users[np.where(current_nbhd==nh_current)]
			previous_nbs = previous_users[np.where(previous_nbhd==nh_previous)] 
			common_nbs = len(np.intersect1d(current_nbs,previous_nbs))/(len(previous_nbs)+len(current_nbs))
		else:
			common_nbs = 0
		pct_nb[user] = common_nbs
	return(pct_nb)

def track_diversity(window_data):
	entropy = hf.LDADiversity(window_data["ut"])
	entropy_labeled = dict(zip(window_data["users"], entropy))
	return(entropy_labeled)

def LDA_rep2(window_data, n_topics=10, max_iters=20):
	#data is in sliding window form
	ui_matrix = window_data
	iu_matrix = window_data.T
	ui_lda = LatentDirichletAllocation(n_components=n_topics,
		max_iter=max_iters, 
		learning_method='online', 
		learning_offset=5.).fit(ui_matrix)
	iu_lda = LatentDirichletAllocation(n_components=n_topics,
		max_iter=max_iters, 
		learning_method='online', 
		learning_offset=5.).fit(iu_matrix)
	ti_matrix = ui_lda.components_
	ut_matrix = ui_lda.fit_transform(ui_matrix)
	tu_matrix = iu_lda.components_
	it_matrix = iu_lda.fit_transform(iu_matrix)
	res = {"ui": ui_matrix, "ti":ti_matrix, "ut":ut_matrix, "tu": tu_matrix, "it":it_matrix,
		"users": ui_matrix.index, "artists": iu_matrix.index}
	res["user_sim"] = hf.LDASim(res["ut"])
	res["artist_sim"] = hf.LDASim(res["it"])
	return(res)

def LDA_rep(window_data, n_topics=10, max_iters=20):
	#data is in sliding window form
	ui_matrix = window_data[["user", "artist", "sum"]]\
		.pivot(index = "user", columns = "artist", values = "sum").fillna(0)
	iu_matrix = window_data[["user", "artist", "sum"]]\
		.pivot(index = "artist", columns = "user", values = "sum").fillna(0)
	ui_lda = LatentDirichletAllocation(n_components=n_topics,
		max_iter=max_iters, 
		learning_method='online', 
		learning_offset=5.).fit(ui_matrix)
	iu_lda = LatentDirichletAllocation(n_components=n_topics,
		max_iter=max_iters, 
		learning_method='online', 
		learning_offset=5.).fit(iu_matrix)
	ti_matrix = ui_lda.components_
	ut_matrix = ui_lda.fit_transform(ui_matrix)
	tu_matrix = iu_lda.components_
	it_matrix = iu_lda.fit_transform(iu_matrix)
	res = {"ui": ui_matrix, "ti":ti_matrix, "ut":ut_matrix, "tu": tu_matrix, "it":it_matrix,
		"users": ui_matrix.index, "artists": iu_matrix.index}
	res["user_sim"] = hf.LDASim(res["ut"])
	res["artist_sim"] = hf.LDASim(res["it"])
	return(res)

class UserEvolution():
	def __init__(self, raw_data, data=None):
		self.raw_data = raw_data 
		self.data = data
	def process_window(self, window_size, min_user=1):
		self.data = dps.sliding_window(self.raw_data, w=window_size, min_user=min_user)
	def get_window_data(self, i):
		window = self.windows[i]
		window_data = self.data[self.data["window"]==window]
		return(window_data)
	def track_evo(self, n_windows=None):
		self.windows = list(set(self.data["window"]))
		self.window_pct_nb = []
		self.window_div = []
		self.window_clust = []
		if n_windows == None:
			n_windows = len(self.windows)
		pbar = ProgressBar()
		for i in pbar(range(n_windows)):
			LDA_res = LDA_rep(self.get_window_data(i))
			div = track_diversity(LDA_res)
			self.window_div.append(div)
			clust = track_clustering(LDA_res)
			self.window_clust.append(clust)
			if i==0:
				prev = LDA_res
				pass
			pct_nb = track_pct_nb(LDA_res, prev)
			self.window_pct_nb.append(pct_nb)
			prev = LDA_res
	

def plot_user_behaviour(User_evolution_res, n_samples=5):
	window_pct_nb = pd.DataFrame(User_evolution_res.window_pct_nb)
	window_div = pd.DataFrame(User_evolution_res.window_div)
	window_clust = pd.DataFrame(User_evolution_res.window_clust)
	users = window_pct_nb.columns
	weeks = window_pct_nb.index
	random_users = users[np.random.randint(0, window_pct_nb.shape[1], n_samples)]
	plt.subplots(1,3,figsize=(12,4))
	plt.subplot(1,3,1)
	plt.plot(weeks, window_pct_nb[random_users], alpha=0.5)
	plt.title("Percent Repeated Neighbors")
	plt.subplot(1,3,2)
	plt.plot(weeks, window_div[random_users], alpha=0.5)
	plt.title("User Listening Diversity")
	plt.subplot(1,3,3)
	plt.plot(weeks, window_clust[random_users], alpha=0.5)
	plt.title("User's Local Artist Clustering")
	plt.show()





