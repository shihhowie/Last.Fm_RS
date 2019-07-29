import pandas as pd
import numpy as np

def process_lastfm_data():
	user_profile_data = pd.read_csv("data/lastfm-dataset-1K/userid-profile.tsv", \
		sep='\t', header=0)
	lastfm_data = pd.read_csv(\
		'data/lastfm-dataset-1K/userid-timestamp-artid-artname-traid-traname.tsv',\
		 sep='\t', header=None, error_bad_lines=False)
	col_names = ["userid", "timestamp", "musicbrainz-artist-id", "artist-name", \
		"musicbrainz-track-id", "track-name"]
	lastfm_data.columns = col_names
	#throw away musicbrainz-artist-id, musicbrainz-track-id, track-name columns
	del lastfm_data["musicbrainz-artist-id"]
	del lastfm_data["musicbrainz-track-id"]
	del lastfm_data["track-name"]
	#convert timestamp to datetime
	lastfm_data["timestamp"] = pd.to_datetime(lastfm_data["timestamp"])
	#convert timestamp to weeks
	lastfm_data["week_of_year"] = lastfm_data["timestamp"].dt.week
	lastfm_data["year"] = lastfm_data["timestamp"].dt.year
	lastfm_data["week"] = (lastfm_data["year"]-lastfm_data["year"].min())*52+lastfm_data["week_of_year"]
	del lastfm_data["week_of_year"]
	del lastfm_data["year"]
	# lastfm_data.to_csv("processed_weekly_data.csv", index=False)
	# test = pd.read_csv("processed_weekly_data.csv")
	artist_listen_count_per_week = lastfm_data.groupby(["userid", "artist-name", "week"]).count().reset_index()
	col_names2 = ["user", "artist", "week", "play_count"]
	artist_listen_count_per_week.columns = col_names2
	# artist_listen_count_per_week.to_csv("processed_weekly_data.csv", index=False)
	weekly_data = pd.read_csv("processed_weekly_data.csv")
	listen_count = weekly_data.groupby(["artist", "user"])["play_count"].count().reset_index()
	listener_count = listen_count.groupby(["artist"])["user"].count().reset_index().\
			sort_values(by=["user"], ascending=False)
	#remove artists that are listened to by fewer than 5 user.  Leaving us with 64095 artists
	kept_artist = listener_count[listener_count["user"]>=5]["artist"]
	weekly_data_trimmed0 = weekly_data[weekly_data["artist"].isin(kept_artist)]
	#remove user-artists entries of whom has only been listened to once in four years
	user_artists_count_total = weekly_data_trimmed0.groupby(["user", "artist"])["play_count"].\
		sum().reset_index()
	#284589 kept user artist entries
	kept_user_artist = user_artists_count_total[user_artists_count_total["play_count"]>=5][["user","artist"]]
	kept_user_artist_pair = kept_user_artist.apply(tuple, axis=1)

	weekly_data_trimmed_copy = weekly_data_trimmed0.copy()
	weekly_data_trimmed1 = weekly_data_trimmed_copy.set_index(["user", "artist"]).\
		loc[list(kept_user_artist_pair)].reset_index()
	#3581989 entries left
	weekly_data_trimmed1.to_csv("weekly_aggregate_trimmed_new.csv", index=False)

#overall data by picking top 50 most listened artists for each user
# overall_user_artist = weekly_data.groupby(["user", "artist"])["play_count"].sum().reset_index()
# top50_artists_per_user = pd.DataFrame()
# for user in set(overall_user_artist["user"]):
# 	artists_listens = overall_user_artist[overall_user_artist["user"]==user]
# 	top_artists = artists_listens.nlargest(50, "play_count")
# 	#throw away 
# 	top50_artists_per_user = top50_artists_per_user.append(top_artists)

# top50_artists_per_user.to_csv("user_artist_data_new.csv", index=False)
# test = pd.read_csv("user_artist_data_new.csv")

# user_week_count = weekly_data.groupby(["user"])["week"].nunique()
# kept_users = user_week_count[user_week_count>=52].index
# weekly_data = weekly_data[weekly_data["user"].isin(kept_users)]



# artists_counts = weekly_data.groupby(["artist"])["play_count"].sum().reset_index()
# artists_sort = artists_counts.sort_values("play_count", ascending=False).reset_index()
# artists_sort.to_csv("top_artists.csv", index=False)

def combine_weekly_data():
	dates = pd.read_csv("chart_dates.csv")
	weekly_data = pd.DataFrame()
	for i in range(len(dates["start"])):
		filename = "data/"+str(dates["start"][i]) +'.csv'
		data = pd.read_csv(filename, header=0, names=["user", "artist", "play_count", "week"])
		weekly_data = weekly_data.append(data)

	weekly_data.to_csv("weekly_aggregate.csv", index=False)

def trim_weekly_data():
	weekly_data = pd.read_csv("weekly_aggregate.csv")

	#number of listens per artists
	listen_count = weekly_data.groupby(["artist", "user"])["play_count"].count().reset_index()
	listener_count = listen_count.groupby(["artist"])["user"].count().reset_index().\
		sort_values(by=["user"], ascending=False)

	#remove artists that are listened to by fewer than 5 user.  Leaving us with 64095 artists
	kept_artist = listener_count[listener_count["user"]>=5]["artist"]
	weekly_data_trimmed0 = weekly_data[weekly_data["artist"].isin(kept_artist)]

	#remove user-artists entries of whom has only been listened to once in two years
	user_artists_count_total = weekly_data_trimmed0.groupby(["user", "artist"])["play_count"].\
		sum().reset_index()
	#174539 artists-user pair have less than 5 total listen combined in all the weeks.  These will be removed
	kept_user_artist = user_artists_count_total[user_artists_count_total["play_count"]>=5][["user","artist"]]
	kept_user_artist_pair = kept_user_artist.apply(tuple, axis=1)

	weekly_data_trimmed_copy = weekly_data_trimmed0.copy()
	weekly_data_trimmed1 = weekly_data_trimmed_copy.set_index(["user", "artist"]).\
		loc[list(kept_user_artist_pair)].reset_index()
	#number of artst has been reduced to 20378

	weekly_data_trimmed1.to_csv("weekly_aggregate_trimmed.csv", index=False)

#this function joins the weekly graphs by sliding windows or width w and stepsize l
def sliding_window(data, w=2, l=1, min_user=5):
	# dates = pd.read_csv("chart_dates.csv")
	# weeks = dates["start"]
	weeks = list(set(data["week"]))
	users = list(set(data["user"]))
	n_frames = int(np.ceil((len(weeks)-w)/l)+1)
	res = pd.DataFrame()
	for i in range(0, n_frames, l):
		week_window = weeks[i:i+w]
		temp = data[data["week"].isin(week_window)].\
			groupby(["user","artist"])["play_count"].agg(["sum", "count"]).reset_index()
		user_count_per_artist = temp.groupby(["artist"])["user"].count().reset_index()	
		kept_artists = user_count_per_artist[user_count_per_artist["user"]>=min_user]["artist"]
		temp = temp[temp["artist"].isin(kept_artists)]
		#keep artists who have been listened to more than once in the window
		temp["window"] = i/l
		res = res.append(temp)
	return(res)

def cumulative_window(data, week):
	dates = pd.read_csv("chart_dates.csv")
	weeks = dates["start"]
	users = list(set(data["user"]))
	week_window = weeks[0:week]
	res = data[data["week"].isin(week_window)].\
		groupby(["user","artist"])["play_count"].agg(["sum", "count"]).reset_index()
	return(res)




