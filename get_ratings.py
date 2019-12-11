import pandas as pd
from sar import demo_reco

def get_ratings(new_ratings_path):
	all_ratings_path = "data/demo/recipes.csv"
	all_ratings_df = pd.read(all_ratings_path)
	new_ratings_df = pd.read_csv(new_ratings_path)


	new_usernames = set(new_ratings_df.username.unique())
	old_usernames = set(all_ratings_df.username.unique())
	username = list(new_usernames - old_usernames)[0]
	
	all_ratings_df = all_ratings_df.append(new_ratings_df) # append new ratings to old
	all_ratings_df = all_ratings_df.drop_duplicates()
	all_ratings_df.to_csv(all_ratings_path) # update the csv with all ratings

	k = 3
	best_k,worst_k = demo_reco(3)

	print("Top {} Recommended Recipes for {}: ".format(k,username))
	for i,recipe in enumerate(best_k):
		print("{}.) {}".format(i,recipe))

	print("Bottom {} Recommended Recipes for {}: ".format(k,username))
	for i,recipe in enumerate(best_k):
		print("{}.) {}".format(i,recipe))

if __name__ == "__main__":
	google_forms_path = "" # TODO: add this path
	get_ratings(google_forms_path)


