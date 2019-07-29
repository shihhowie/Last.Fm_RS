import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from progressbar import ProgressBar
import DataProcesser as dps
import networkx as nx
import HelperFunctions as hf


def top_sim(artists, current_artists_idx, artist_sim):
	candidate_artists = np.delete(artists, current_artists_idx)
	candidate_scores = artist_sim[current_artists_idx].sum(axis=0)
	#remove artists that have already been seen by user
	candidate_scores = np.delete(candidate_scores, current_artists_idx)
	candidate_rank_idx = np.argsort(candidate_scores)[::-1]
	candidate_ranks = np.empty_like(candidate_rank_idx)
	candidate_ranks[candidate_rank_idx] = np.arange(1,len(candidate_rank_idx)+1)
	r_list = pd.DataFrame({"artist": candidate_artists, "sim_score": candidate_scores, "sim_rank": candidate_ranks})
	return(r_list)

def top_clustering(artists, current_artists_idx, item_sim):
	candidate_artists = np.delete(artists, current_artists_idx)
	candidate_nodes_idx = np.delete(np.arange(len(item_sim)), current_artists_idx)
	avg_sim = np.mean(item_sim[current_artists_idx,:][:,current_artists_idx])
	triangle_pcts = []
	for node in candidate_nodes_idx:
		#candidate node will be at the first row/column
		graph_idx = np.append(node, current_artists_idx)
		graph = item_sim[graph_idx,:][:,graph_idx]
		np.fill_diagonal(graph, 0)
		graph_link = np.multiply(np.ones(graph.shape),graph>avg_sim)
		subgraph_idx = np.where(graph_link[0])[0]
		subgraph = graph_link[subgraph_idx,:][:,subgraph_idx] 
		n_triangles = len(np.argwhere(subgraph))
		n_pairs = len(subgraph)*(len(subgraph)-1)
		if n_pairs ==0:
			triangle_pcts.append(1)
		else:
			triangle_pcts.append((n_triangles+1)/(n_pairs+1))
	candidate_rank_idx = np.argsort(triangle_pcts)
	candidate_ranks = np.empty_like(candidate_rank_idx)
	candidate_ranks[candidate_rank_idx] = np.arange(1,len(candidate_rank_idx)+1)
	r_list = pd.DataFrame({"artist": candidate_artists, "clust_score": triangle_pcts, "clust_rank": candidate_ranks})
	return(r_list)

def top_div(artists, current_artists_idx, entropy, popularity):
	candidate_artists = np.delete(artists, current_artists_idx)
	candidate_entropy = np.delete(entropy, current_artists_idx)
	candidate_popularity = np.delete(popularity, current_artists_idx)
	diversity = candidate_entropy-candidate_popularity
	candidate_rank_idx = np.argsort(diversity)[::-1]
	candidate_ranks = np.empty_like(candidate_rank_idx)
	candidate_ranks[candidate_rank_idx] = np.arange(1,len(candidate_rank_idx)+1)
	r_list = pd.DataFrame({"artist": candidate_artists, "diversity": diversity, "div_rank": candidate_ranks})
	return(r_list)

def weighted_recommendations(rec_summary, weights):
	weights = weights/np.sum(weights)
	weighted_score = rec_summary[["sim_rank", "div_rank", "clust_rank"]]@weights
	candidate_rank_idx = np.argsort(weighted_score)
	candidate_ranks = np.empty_like(candidate_rank_idx)
	candidate_ranks[candidate_rank_idx] = np.arange(1,len(candidate_rank_idx)+1)
	r_list = rec_summary[["artist", "sim_rank", "div_rank", "clust_rank"]].copy()
	r_list["score"] = weighted_score
	r_list["rank"] = candidate_ranks
	return(r_list)

def get_recommendations(window_data, n_users=None, weights=None):
	entropy = hf.LDADiversity(window_data["it"])
	popularity = (window_data["ui"]>0).sum(axis=0)
	users = window_data["users"]
	if weights == None:
		weights = np.array([10,1,1])
	if n_users == None:
		n_users = len(users)
	r_weighted_all = {}
	for i in range(n_users):
		user = users[i]
		current_artists_idx = np.where(window_data["ui"].loc[user]>0)[0]
		sim_rec = top_sim(window_data["artists"], current_artists_idx, window_data["artist_sim"])
		div_rec = top_div(window_data["artists"], current_artists_idx, entropy, popularity.values)
		clust_rec = top_clustering(window_data["artists"], current_artists_idx, window_data["artist_sim"])
		rec_sum = pd.merge(sim_rec, div_rec, on="artist")
		rec_sum = pd.merge(rec_sum, clust_rec, on="artist")
		r_weighted = weighted_recommendations(rec_sum, weights)
		r_weighted_all[user] = r_weighted
	return(r_weighted_all)

def make_recommendations(r_list, n_rec, beta=0.5):
	top_n = r_list.nsmallest(n_rec,"rank")
	top_n["p"] = (np.exp(-top_n["rank"])**beta)/((np.exp(-top_n["rank"])**beta).sum())
	return(top_n[["artist", "p"]].copy())


