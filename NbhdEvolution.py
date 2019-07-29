import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from progressbar import ProgressBar
import DataProcesser as dps
import networkx as nx
import HelperFunctions as hf
from sklearn.decomposition import NMF, LatentDirichletAllocation

weekly_data_trimmed1 = pd.read_csv("weekly_aggregate_trimmed.csv")
weekly_data_sliding = dps.sliding_window(weekly_data_trimmed1, 4)

#Generating user-artist matrix for LDA and other topic modeling analysis
windows = list(set(weekly_data_sliding["window"]))
artists = list(set(weekly_data_sliding["artist"]))
users = list(set(weekly_data_sliding["user"]))
user_artist_matrix = np.matrix((len(users),len(artists)))
sample_window = weekly_data_sliding[weekly_data_sliding["window"]==windows[0]]

def window_diversity(window, n_topics, iters, thresh):
	artist_count = window.groupby(["artist"])["user"].count().reset_index()
	window = window[window["artist"].\
		isin(artist_count[artist_count["user"]>=thresh]["artist"])]
	ui_matrix = window[["user", "artist", "sum"]]\
	.pivot(index = "user", columns = "artist", values = "sum")
	users = ui_matrix.index
	ui_matrix = ui_matrix.fillna(0)
	ui_matrix_tfidf = np.multiply(tf, idf)
	ui_lda = LatentDirichletAllocation(n_topics=n_topics,
	 max_iter=iters, 
	 learning_method='online', 
	 learning_offset=50.,
	 random_state=0).fit(ui_matrix_tfidf)
	ti_matrix = ui_lda.components_	
	ut_matrix = ui_lda.fit_transform(ui_matrix_tfidf)
	diversity = hf.LDADiversity(ut_matrix)
	user_diversity = pd.DataFrame({"diversity":diversity}, index=users)
	return(user_diversity)

pbar = ProgressBar()
diversity_evolution2 = pd.DataFrame(index = users, columns = windows)
for i in pbar(range(len(windows))):
	window = windows[i]
	window_data = weekly_data_sliding[weekly_data_sliding["window"]==window]
	window_div = window_diversity(window_data, 30, 10, 2)
	diversity_evolution2.iloc[:,i].loc[window_div.index] = window_div["diversity"]

diversity_evolution2
#filter out artists that appear in fewer than 5 users' list
artist_count = sample_window.groupby(["artist"])["user"].count().reset_index()
sample_window = sample_window[sample_window["artist"].\
	isin(artist_count[artist_count["user"]>=5]["artist"])]

ui_matrix = sample_window[["user", "artist", "sum"]]\
	.pivot(index = "user", columns = "artist", values = "sum")

ui_matrix = ui_matrix.fillna(0)
#process matrix to resemble tf-idf


#testing LDA 
n_topics = 20
iters = 10
n_top_artist = 10

#transform user_item matrix to user_topic and topic_item matrix.
ui_lda = LatentDirichletAllocation(n_topics=n_topics,
 max_iter=iters, 
 learning_method='online', 
 learning_offset=50.,
 random_state=0).fit(ui_matrix_tfidf)

# for topic_idx, topic in enumerate(ui_lda.components_):
# 	print("Topic %d:" % (topic_idx))
# 	proportion = topic/sum(topic)
# 	print([(artists[i],np.round(proportion[i],3)) for i in topic.argsort()[:-n_top_artist-1:-1]])
	
ti_matrix = ui_lda.components_	
ut_matrix = ui_lda.fit_transform(ui_matrix_tfidf)

#Same process for item user matrix
iu_matrix = sample_window[["user", "artist", "sum"]]\
	.pivot(index = "artist", columns = "user", values = "sum")
iu_matrix = iu_matrix.fillna(0)

tf = iu_matrix/(iu_matrix.sum(axis=1)[:,np.newaxis])
idf = (iu_matrix>0)/(iu_matrix>0).sum(axis=0)
iu_matrix_tfidf = np.multiply(tf, idf)

#transform item_user matrix to item_topic and topic_user matrix
iu_lda = LatentDirichletAllocation(n_topics=n_topics,
 max_iter=iters, 
 learning_method='online', 
 learning_offset=50.,
 random_state=0).fit(iu_matrix_tfidf)

tu_matrix = iu_lda.components_	
it_matrix = iu_lda.fit_transform(iu_matrix_tfidf)


user_sim = hf.LDASim(ut_matrix)
item_sim = hf.LDASim(it_matrix)

user_div = hf.LDADiversity(ut_matrix)

hf.LDAClustering(item_sim, ui_matrix)

hf.draw_graph(graph)

#Clustering bipartite graph
#forming bipartite graph W
m,n = ui_matrix.shape
axis_label = np.concatenate((ui_matrix.index, ui_matrix.columns))
W  = np.block([
	[np.zeros((m,m)), ui_matrix],
	[ui_matrix.T, np.zeros((n,n))]])
D = np.diag(W.sum(axis=0))
W_scaled = np.linalg.inv(D)**(1/2)@W@np.linalg.inv(D)**(1/2)

u,s,v = np.linalg.svd(W_scaled)
x = np.linalg.inv(D)**(1/2)@u[:,1]



