import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from progressbar import ProgressBar
import DataProcesser as dps
import networkx as nx
import HelperFunctions as hf
import NbhdMethods as nm
from scipy import stats
from collections import deque 
import RecommenderSystem as rs

def get_indices(artists, all_artists):
	#potentially slow
	indices = [all_artists.index(artist) for artist in artists]
	return(indices)

class User():
	def __init__(self, name, repeat_prob, freq, init_artists_idx, artists, window_size):
		self.name = name
		self.repeat_prob = repeat_prob
		self.freq = freq
		self.artists = artists
		self.window_size = window_size
		init_artists_idx_unique, ct = np.unique(init_artists_idx, return_counts=True)
		self.current_artists = np.zeros(len(artists))
		self.current_artists[init_artists_idx_unique] = ct
		self.artist_history = self.current_artists
		self.previous_artists = deque(np.zeros((window_size,len(artists)))) 
		self.previous_artists.append(self.current_artists)
		self.previous_artists.popleft()

	def get_history(self):
		return(pd.DataFrame({"artist": self.artists, "play_count":self.artist_history}))

	def take_recommendations(self, r_list):
		r_artists = r_list["artist"].values
		n_listens = np.random.poisson(self.freq)
		n_new = int(n_listens*(1-self.repeat_prob))
		n_old = int(n_listens*self.repeat_prob)
		new_artists = np.random.choice(r_artists, p=r_list["p"].values, size=n_new)
		new_artist_unique, ct_new = np.unique(new_artists, return_counts=True)
		print(self.name+" listened to new artists: ", self.artists[new_artist_unique].values)
		old_artists = np.random.choice(np.where(self.current_artists>0)[0], size=n_old)
		old_artist_unique, ct_old = np.unique(old_artists, return_counts=True)
		print(self.name+" listened to old artists:", self.artists[old_artist_unique].values)

		#record in history
		self.artist_history[new_artist_unique] += ct_new
		self.artist_history[old_artist_unique] += ct_old

		temp = np.zeros(len(self.artists))
		temp[new_artist_unique] = ct_new
		temp[old_artist_unique] = ct_old

		self.previous_artists.append(temp)
		self.previous_artists.popleft()

		self.current_artists = np.sum(self.previous_artists, axis=0)

		return(self.current_artists)

class Simulator():
	def __init__(self, n_users, n_artists, repeat_prior=None, freq_prior=None, window_size=4):
		top_artists = pd.read_csv("top_artists.csv")["artist"]
		self.n_users = n_users
		self.n_artists = n_artists
		self.artists = top_artists[:n_artists]
		if repeat_prior == None:
			repeat_prior = [3, 4, 0, 1]
		if freq_prior == None:
			freq_prior = [3, 2, 15]
		self.repeat_probs = stats.beta.rvs(*repeat_prior, size=n_users)
		self.freq_means = stats.gamma.rvs(*freq_prior, size=n_users)
		self.users = {}
		current_window = np.zeros((n_users, n_artists))
		for i in range(n_users):
			user_name = "user"+str(i)
			repeat_prob = self.repeat_probs[i]
			freq = self.freq_means[i]
			init_artists_idx = np.random.randint(0, n_artists, int(freq))
			current_window[i,init_artists_idx] = 1
			self.users[user_name]=User(user_name, repeat_prob, 
				freq, init_artists_idx, self.artists, window_size)
		#use index number instead of artists names to skip conversion
		self.current_window = pd.DataFrame(current_window, index= list(self.users.keys()),\
														columns=np.arange(len(self.artists)))
		self.window_div= []
		self.window_clust= []
		self.window_pct_nb =[]

	def record_behaviour(self):
		div = nm.track_diversity(self.window_data)
		self.window_div.append(div)
		clust = nm.track_clustering(self.window_data)
		self.window_clust.append(clust)
		if len(self.window_pct_nb)==0:
			self.prev_window_data = self.window_data
			pass
		pct_nb = nm.track_pct_nb(self.window_data, self.prev_window_data, 5)
		self.window_pct_nb.append(pct_nb)
		self.prev_window_data = self.window_data

	def plot_behaviour(self, n_samples=None):
		nm.plot_user_behaviour(self, n_samples)

	def simulate(self, n_weeks, weights = None):
		for i in range(n_weeks):
			self.window_data = nm.LDA_rep2(self.current_window)
			r_lists = rs.get_recommendations(self.window_data, weights=weights)
			for user in self.users:
				r_list = r_lists[user]
				top_n = rs.make_recommendations(r_list, 20)
				self.current_window.loc[user] = self.users[user].take_recommendations(top_n)
			self.record_behaviour()




