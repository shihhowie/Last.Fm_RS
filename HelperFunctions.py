import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from progressbar import ProgressBar
import DataProcesser as dps
import networkx as nx

def LDASim(xt_matrix):
	normalized_xt_matrix = xt_matrix/(np.linalg.norm(xt_matrix, axis=1))[:,np.newaxis]
	return(normalized_xt_matrix@normalized_xt_matrix.T)

def Sim(ui_matrix):
	nonzero_indicator = np.nonzero(np.array(ui_matrix))
	ui_matrix_indicator = np.zeros(ui_matrix.shape)
	ui_matrix_indicator[nonzero_indicator] = 1
	ui_matrix_indicator = ui_matrix_indicator/(np.linalg.norm(ui_matrix_indicator, axis=1))[:,np.newaxis]
	user_user_similarity = ui_matrix_indicator@ui_matrix_indicator.T
	return(user_user_similarity)

def LDADiversity(xt_matrix):
	entropy = np.multiply(xt_matrix, np.log(xt_matrix))
	return(-entropy.sum(axis=1))

def triangle_pct(graph):
	#counts the number of triangles in a graph
	n_triangle = 0
	n_pairs = 0
	n = len(graph)
	np.fill_diagonal(graph, 0)
	degree_index = graph.sum(axis=1).argsort()
	for i in range(len(degree_index)):
		idx = degree_index[i]
		subgraph_idx = np.intersect1d(np.where(graph[idx])[0],degree_index[i:])
		subgraph = graph[subgraph_idx,:][:,subgraph_idx]
		n_triangle += len(np.argwhere(subgraph))
		n_pairs += len(subgraph)*(len(subgraph)-1)
	if n_pairs==0:
		return(0)
	else:
		return(n_triangle/n_pairs)


def LDAClustering(item_sim, ui_matrix, min_sim = 0.7):
	n,m = ui_matrix.shape
	triangle_counts = []
	item_sim_adjusted = item_sim - min_sim
	item_link = np.multiply(np.ones(item_sim.shape),item_sim_adjusted>0)
	for user_idx in range(n): 
		subgraph_idx = np.where(ui_matrix.iloc[user_idx]>0)[0]
		subgraph = item_link[subgraph_idx,:][:,subgraph_idx]
		triangle_counts.append(triangle_pct(subgraph))
	return(triangle_counts)

def ClusteringScore(user_subgraph_idx, full_graph, candidate_list):
	for candidate in candidate_list:
		subgraph_idx = user_subgraph_idx

def draw_graph(graph):
	G = nx.Graph()
	for node in range(len(graph)):
		G.add_node(node)
	for i in range(len(graph)):
		for j in range(len(graph)):
			if graph[i,j] ==1:
				G.add_edge(i,j)
	pos = nx.layout.circular_layout(G)
	nx.draw_networkx_nodes(G, pos)
	nx.draw_networkx_edges(G, pos)
	nx.draw_networkx_labels(G, pos)
	plt.show()
