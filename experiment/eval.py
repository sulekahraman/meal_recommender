import sys
sys.path.append("../")
import os.path
import pickle
import random
import pandas as pd
import numpy as np
from uuid import uuid3
from random import randint
import itertools
import os
import papermill as pm
from reco_utils.dataset.python_splitters import python_stratified_split
from reco_utils_2.recommender.sar.sar_singlenode import SARSingleNode
from reco_utils_2.evaluation.custom_evaluation import accuracy_metric
import re
import ast

from string import digits
from string import punctuation

DATA_DIR = '../data/'


def evaluate(n_users, n_recipes_per_cuisine, review_ratio, review_ratio_fav, weight_ratings):
    print()
    print('evaluating for:')
    print('n_users =', n_users)
    print('n_recipes_per_cuisine =', n_recipes_per_cuisine)
    print('review_ratio=', review_ratio)
    print('review_ratio_fav =', review_ratio_fav)
    print()

    make_recipe_dataset(n_recipes_per_cuisine)
    write_reviews(n_users, n_recipes_per_cuisine, review_ratio, review_ratio_fav)

    top_k = [1,2,3,5]

    absolute_scores, relative_scores = train_and_score(n_users, n_recipes_per_cuisine, review_ratio, review_ratio_fav, top_k, weight_ratings)

    print('Done!')
    print()
    print('Scores:')
    print('k:\t', top_k)
    print('absolute:\t', absolute_scores)
    print('relative:\t', relative_scores)


def make_recipe_dataset(n_recipes_per_cuisine):

    output_path = DATA_DIR + 'synthetic/recipes/cuisine_size_{}.csv'.format(n_recipes_per_cuisine)
    if os.path.isfile(output_path):
        print("\tfound recipe dataset")
        return

    print("\tcreating recipe dataset")

    original_fn = DATA_DIR + 'original/recipe_final.csv'
    data_final = pd.read_csv(original_fn)

    cuisines = set(data_final['cuisine'])
    cuisines.remove(' garlic')
    cuisines.remove('Cajun & Creole')
    cuisines.remove(' tosted 125 mL 2 tbsp. chopped fresh cilantro 30 mL Directions 1\\xa0In tajine or large saucepan')

    df = pd.DataFrame(columns=data_final.columns)
    for c in cuisines:
        mask = (data_final['cuisine'] == c)
        df = df.append(data_final[mask][:n_recipes_per_cuisine])

    preprocess_ingredients(df, n_recipes_per_cuisine)

def preprocess_ingredients(recipes, n_recipes_per_cuisine):

    print('\tpreprocessing ingredients')

    path = DATA_DIR + 'synthetic/recipes/cuisine_size_{}.csv'.format(n_recipes_per_cuisine)
    recipes = pd.read_csv(path)
        
    common = {"tablespoons", "tablespoon", "teaspoon", "teaspoons", "tbsp", "tsp", "cup", "cups", "ounces",
              "lb", "lbs", "lbs", "box", "pound", "pounds", "whole", "gram", "grams", "g", "ml",
              "oz", "oz.", "parts", "part", "", "/", "-", "the", "and", "into", "cut","fresh", "minced", "chopped", "finely", "or",
              "for", "of", "to","salt", "pepper", "your", "taste", "etc", "sliced", "big", "small", "large", "intact", "flakes", "about", "round",
             "other", "hot", "make", "low", "favorite", "pack", "packed", "recommended", "top", "use", "firmly", "size", "will", "because",
             "in", "is", "inch", "medium", "ounce", "kilo", "kilos", "kg", "so", "plus", "slice", "slices", "as", "drained", "thinly", "halves", "either", 
             "such", "optional", "if", "care", "pride", "per", "it", "got", "have", "want", "on", "be", "all", "very", "with",
             "removed", "approximately", "half", "pieces", "chop", "freshly", "free", "extra", "diced", "recipe", "mix", "halved",
             "each", "a", "an", "what", "i", "thin", "bag", "more", "no", "any", "sauce", "at", "serving", "servings"}

    remove_digits = str.maketrans('', '', digits)
    remove_punctuation = str.maketrans('', '', punctuation)

    def preprocess(cell):
        ingredients = ast.literal_eval(cell)
        long_ing_string = ' '.join(ingredients).lower()
        cleaned_ing_set = set(long_ing_string.translate(remove_digits).translate(remove_punctuation).split(" "))
        cleaned_ing_set.difference_update(common)
        return '+'.join(cleaned_ing_set)

    recipes['clean_ingredients'] = recipes.apply(lambda x: preprocess(x.ingredients), axis=1)
    recipes.to_csv(path)



def write_reviews(n_users, n_recipes_per_cuisine, review_ratio, review_ratio_fav):
    # check if reviews already exist
    path_users_df = DATA_DIR + 'synthetic/users/{}_users_{}_ratio_{}_ratiofav.csv'.format(n_users, review_ratio, review_ratio_fav)
    path_reviews_df = DATA_DIR + 'synthetic/reviews/{}_users_{}_ratio_{}_ratiofav.csv'.format(n_users, review_ratio, review_ratio_fav)
    if os.path.isfile(path_users_df) and os.path.isfile(path_reviews_df):
        print("\tfound review datasets")
        return

    # need to create datasets
    print("\tcreating review datasets")

    path = DATA_DIR + 'synthetic/recipes/cuisine_size_{}.csv'.format(n_recipes_per_cuisine)
    recipe_df = pd.read_csv(path)
    users_df, reviews_df = createUserReviews(n_users, recipe_df, review_ratio, review_ratio_fav)  

    users_df.to_csv(path_users_df)
    reviews_df.to_csv(path_reviews_df)


def createUserReviews(n_users, recipe_df, review_ratio, review_ratio_fav):

    def get_review_ratio(cuisine, fav_cuisine):
        if cuisine == fav_cuisine:
            return review_ratio_fav
        else:
            return review_ratio

    def create_username(fav_cuisine):
        fav_words = ["luver","connoisseur","eatz","finesser","fan"]
        need_words = ["cant_get_enough","cant_live_without","needs","only_eats"]
        names = ['Kathey', 'Silas', 'Cristina', 'Perry', 'Robbi', 'Florentino', 'Elliot', 'Raye',\
                 'Evette', 'Risa', 'Lurline', 'Tashia', 'Danyel', 'Shaun', 'Luciano', 'Trang', \
                 'Summer', 'Martin', 'China', 'Jacob', 'Alenta', 'Sule', 'Quentin', 'Anton']
        food_words = ["food","grub","eatz"]
        
        rand_num = ''.join(random.choice('0123456789') for i in range(3))
        if randint(0,1) == 0:
            return "{}_{}_{}".format(fav_cuisine.lower(),fav_words[randint(0,len(fav_words)-1)],rand_num)
        
        i,j,k = randint(0,len(names)-1),randint(0,len(need_words)-1),randint(0,len(food_words)-1)
        return "{}_{}_{}_{}_{}".format(names[i].lower(), need_words[j], fav_cuisine.lower(),food_words[k],rand_num)

    def get_rating(x):
        if x["cuisine"] == x["fav_cuisine"]:
            return 5
        elif x["cuisine"] == x["least_fav_cuisine"]:
            return 1
        else:
            return cuisine_similarities[x["cuisine"]][x["fav_cuisine"]]*4 + 1  #+ 0.3 * randint(1,5)



    users_df = pd.DataFrame(columns=["username","favorite_cusine","least_fav_cuisine"])
    reviews_df = pd.DataFrame(columns=["username","recipe_id","rating"])
    cuisines = recipe_df.cuisine.unique()
    

    with open(DATA_DIR + 'cuisine_similarities/cuisine_similarities.obj', 'rb') as file_sim:
        cuisine_similarities = pickle.load(file_sim)
    
    for i in range(n_users):
        fav_cuisine_index = randint(0,len(cuisines)-1)
        least_fav_cuisine_index = randint(0,len(cuisines)-1)
        while least_fav_cuisine_index == fav_cuisine_index:
            least_fav_cuisine_index = randint(0,len(cuisines)-1)
        fav_cuisine,least_fav_cuisine = cuisines[fav_cuisine_index],cuisines[least_fav_cuisine_index]
        username = create_username(fav_cuisine)
        user_data = [username,fav_cuisine,least_fav_cuisine]
        users_df.loc[i] = user_data
        
        printed_note = False

        for c in cuisines:
            mask = recipe_df["cuisine"] == c
            recipe_subset = recipe_df[mask]
            rows,cols = recipe_subset.shape
            to_be_reviewed = recipe_subset.sample(int(rows*get_review_ratio(c, fav_cuisine)))
            to_be_reviewed["username"] = username
            to_be_reviewed["fav_cuisine"] = fav_cuisine
            to_be_reviewed["least_fav_cuisine"] = least_fav_cuisine
            if(len(to_be_reviewed) == 0):
                if not printed_note:
                    print('Note: review ratio low, no all users are reviewing a recipe of every cuisine')
                to_be_reviewed["rating"] = 0
            else:
                to_be_reviewed["rating"] = to_be_reviewed.apply(get_rating,axis=1)
            reviewed = to_be_reviewed[["username","recipe_id","rating"]]
            reviews_df = reviews_df.append(reviewed)
            
    return users_df, reviews_df


def train_and_score(n_users, n_recipes_per_cuisine, review_ratio, review_ratio_fav, top_k, weight_ratings):

    data_type = 'synthetic'
    data_path = DATA_DIR + data_type
    
    features_fn = data_path + '/recipes/cuisine_size_{}.csv'.format(n_recipes_per_cuisine)
    review_fn = data_path + '/reviews/{}_users_{}_ratio_{}_ratiofav.csv'.format(n_users, review_ratio, review_ratio_fav)

    data = pd.read_csv(review_fn)
    features = pd.read_csv(features_fn)
    
    # Convert ingredients column to list
    features["clean_ingredients"] = features["clean_ingredients"].apply(lambda a : a.split("+"))
    
    # Convert the float precision to 32-bit in order to reduce memory consumption 
    data.loc[:, 'rating'] = data['rating'].astype(np.float32)


    header = {
        "col_user": "username",
        "col_item": "recipe_id",
        "col_rating": "rating",
        "col_timestamp": "date",
        "col_prediction": "Prediction",
    }

    # split train and test and add dummy user reviewing every recipe in train
    train, test = python_stratified_split(data, ratio=0.80, col_user=header["col_user"], col_item=header["col_item"],seed=42)
    for r in features["recipe_id"]:
        dummy = pd.DataFrame([["dummy",r,3]], columns=['username',"recipe_id","rating"])
        train = train.append(dummy, ignore_index=True)
    

    # build model
    model = SARSingleNode(
        similarity_type="custom", 
        time_decay_coefficient=30, 
        time_now=None, 
        timedecay_formula=False,
        **header
    )
    
    jaccard = lambda a,b: len(set(a).intersection(set(b)))/len(set(a).union(set(b)))
    
    print('\ttraining model')

    model.fit(train, features, "recipe_id", {"ratings" : weight_ratings, "clean_ingredients" : (1, jaccard)})
    
    print('\tscoring')

    # get score
    absolute_scores = []
    relative_scores = []
    for i in top_k:
        absolute, relative = accuracy_metric(model, test, i)
        absolute_scores.append(absolute)
        relative_scores.append(relative)

    return absolute_scores, relative_scores






# python3 eval.py <n_users> <n_recipes_per_cuisine> <review_ratio> <review_ratio_fav> <weight_ratings>
if __name__ == "__main__":
    evaluate(int(sys.argv[1]), int(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4]), float(sys.argv[5]))






