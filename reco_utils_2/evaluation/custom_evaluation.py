import pandas as pd

def accuracy_metric(model, test, top_k, remove_seen=True):
    TOP_K = top_k
    NO_OF_RECIPES_OR_HIGH_NUMBER = 10000

    ground_truth_test = test
    predicted_on_test = model.recommend_k_items(test, top_k=NO_OF_RECIPES_OR_HIGH_NUMBER, remove_seen=remove_seen)

    min_number_of_ratings_per_user = min(ground_truth_test.groupby('username').count()['rating'])
    max_number_of_ratings_per_user = max(ground_truth_test.groupby('username').count()['rating'])

    if min_number_of_ratings_per_user < TOP_K:
        print('IMPORTANT WARNING: score will be artificially lower, as not enough ground truth ratings exist for certain users. Use a lower TOP_K value.')

    if min_number_of_ratings_per_user != max_number_of_ratings_per_user:
        print('IMPORTANT WARNING: discard relative score, only use absolute score because number of ground truth ratings varies across users')

    merged = pd.merge(predicted_on_test, ground_truth_test, on=['username','recipe_id'])
    top_by_rating = merged.groupby('username').apply(lambda x: x.nlargest(TOP_K, 'rating')).reset_index(drop=True)
    top_by_prediction = merged.groupby('username').apply(lambda x: x.nlargest(TOP_K, 'Prediction')).reset_index(drop=True)

    common_tops = top_by_rating.merge(right=top_by_prediction, how='inner', on=['username', 'recipe_id'])

    absolute_score = len(common_tops)/len(top_by_prediction)
    chance_lower_bound = (TOP_K/min_number_of_ratings_per_user)
    relative_score = absolute_score/chance_lower_bound

    return absolute_score, relative_score