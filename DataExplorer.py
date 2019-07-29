import pandas as pd
import numpy as np
import DataProcesser as dps
import matplotlib.pyplot as plt
from progressbar import ProgressBar
from sklearn.decomposition import NMF, LatentDirichletAllocation

user_names = pd.read_csv("user_names.csv")[:500]
dates = pd.read_csv("chart_dates.csv")

weekly_data_trimmed1 = pd.read_csv("weekly_aggregate_trimmed.csv")

#How many times does each user listen to music every week, how many artists does each user listen to every week
play_count_summary = weekly_data_trimmed1.groupby(["week","user"])["play_count"].agg(["sum", "count"]).reset_index()
play_count_summary_dist = play_count_summary.groupby(["user"])[["sum","count"]].agg(["mean", "var"])

#Historgram plot of mean user play count per week(10 highest removed for better binning)
plt.hist(np.sort(play_count_summary_dist["count"]["mean"])[:-10], density=True)
plt.title("Mean user weekly play count")
plt.show()

#Aggregating for how many repeated artist per user every week,
weekly_data_sliding = dps.sliding_window(weekly_data_trimmed1, w=2)
repeated_per_window = weekly_data_sliding[weekly_data_sliding["count"]>1].\
	groupby(["user", "window"]).agg({"count": "count", "sum": "sum"})
total_per_window = weekly_data_sliding.groupby(["user", "window"])\
	.agg({"count": "count", "sum": "sum"})
summary_per_window = pd.merge(total_per_window, repeated_per_window, how="outer", on=["user","window"]).fillna(0)
summary_per_window["count_pct"] = summary_per_window["count_y"]/summary_per_window["count_x"]
summary_per_window["sum_pct"] = summary_per_window["sum_y"]/summary_per_window["sum_x"]
fig, ax = plt.subplots(1,2)
plt.subplot(1,2,1)
plt.hist(summary_per_window["count_pct"])
plt.title("weekly repeated artist count")
plt.subplot(1,2,2)
plt.hist(summary_per_window["sum_pct"])
plt.title("weekly repeated artist listen")
plt.show()

#Repeat procedure for monthly window
weekly_data_sliding = dps.sliding_window(weekly_data_trimmed1, w=4)
repeated_per_window = weekly_data_sliding[weekly_data_sliding["count"]>1].\
	groupby(["user", "window"]).agg({"count": "count", "sum": "sum"})
total_per_window = weekly_data_sliding.groupby(["user", "window"])\
	.agg({"count": "count", "sum": "sum"})
summary_per_window = pd.merge(total_per_window, repeated_per_window, how="outer", on=["user","window"]).fillna(0)

summary_per_window["count_pct"] = summary_per_window["count_y"]/summary_per_window["count_x"]
summary_per_window["sum_pct"] = summary_per_window["sum_y"]/summary_per_window["sum_x"]

summary_per_window.groupby(["user"])["count_pct"].mean()
summary_per_window.groupby(["user"])["sum_pct"].mean()




	