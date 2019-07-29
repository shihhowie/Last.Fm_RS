import pylast
import pandas as pd
import multiprocessing as mp
from contextlib import closing
from progressbar import ProgressBar
import csv

pbar = ProgressBar()

API_KEY = "92e5065a366659b3cb6940ae714bb41f"
API_SECRET = "9b95e86fe7e4ff114cb2622889f1e37e"
username = "thehowieman"

password_hash = pylast.md5("h#11122")

network = pylast.LastFMNetwork(api_key=API_KEY, api_secret=API_SECRET,
                               username=username, password_hash=password_hash)


sams_profile = network.get_user("BegGsAnator")

#collect data from two most recent years
# num_week = 104
# sams_dates = sams_profile.get_weekly_chart_dates()
# start = [date[0] for date in sams_dates[-num_week:]]
# end = [date[1] for date in sams_dates[-num_week:]]

# pd.DataFrame({"start":start, "end":end}).to_csv("chart_dates.csv", index=False)
# dates = pd.read_csv("chart_dates.csv")

#create empty file to prevent duplicates in writing
# for i in range(len(dates)):
# 	filename = "data/"+str(dates["start"][i]) +'.csv'
# 	pd.DataFrame().to_csv(filename, index=False)

####write weekly top artists to files
def get_artists(username):
	try:
		profile = network.get_user(username)
		artists = profile.get_weekly_artist_charts(dates["start"][i],dates["end"][i])
		artist_names = [artist.item for artist in artists]
		play_count = [artist.weight for artist in artists]
		temp = pd.DataFrame({"user": username, 
			"artists": artist_names,
			"play_count": play_count}).values
	except: 
		temp = []
	return(temp)

# user_names = pd.read_csv("user_names.csv")[:500]

# for i in pbar(range(len(dates))):
# 	filename = "data/"+str(dates["start"][i]) +'.csv'
# 	with closing(mp.Pool()) as pool:
# 		weekly_chart = pool.imap_unordered(get_artists, iter(user_names["user"]))	
# 		with open(filename, 'w') as f:
# 			writer = csv.writer(f)
# 			for user_artist in weekly_chart:
# 				writer.writerows(user_artist)
	
####Get user list from breadth first search
# sams_friends = sams_profile.get_friends()
# user_names = []

# #get a list of sam's friends
# for friend in sams_friends:
# 	if friend.get_name() not in user_names:
# 		user_names.append(friend.get_name())

# #add friends of sam's friends recursively to the list and stop at 50 friends
# for i in range(50):
# 	user = network.get_user(user_names[i])
# 	friends = user.get_friends()
# 	for friend in friends:
# 		if friend.get_name() not in user_names:
# 			user_names.append(friend.get_name())

###Get top artists overall for each user
# pd.DataFrame({"user":user_names}).to_csv("user_names.csv", index=False)
# pool = mp.Pool(mp.cpu_count())

# #for each user in user_names, we get their top 50 artists and store in dataframe
user_names = pd.read_csv("user_names.csv")
user_artist_data = pd.DataFrame()
user_artist_data.to_csv("user_artist_data.csv", index=False)

def get_artists(username):
	try:
		profile = network.get_user(username)
		artists = profile.get_top_artists()
		artist_names = [artist.item for artist in artists]
		play_count = [artist.weight for artist in artists]
		temp = pd.DataFrame({"user": username, 
			"artists": artist_names,
			"play_count": play_count}).values
	except: 
		temp = []
	return(temp)

with closing(mp.Pool()) as pool:
	user_artists = pool.imap_unordered(get_artists, iter(user_names["user"][:500]))
	with open(r'user_artist_data.csv', 'w') as f:
		writer = csv.writer(f)
		for user_artist in user_artists:
			writer.writerows(user_artist)



