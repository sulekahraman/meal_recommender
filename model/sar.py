# set the environment path to find Recommenders
import sys
sys.path.append("../")

import itertools

import logging
import os

import numpy as np
import pandas as pd
import papermill as pm

#from reco_utils.dataset import movielens
from reco_utils.dataset.python_splitters import python_stratified_split
from reco_utils.evaluation.python_evaluation import map_at_k, ndcg_at_k, precision_at_k, recall_at_k
from reco_utils_2.recommender.sar.sar_singlenode import SARSingleNode

#print("System version: {}".format(sys.version))
#print("Pandas version: {}".format(pd.__version__))

def demo_reco(): 
    #LOAD DATA
    data_dir = '../data'
    data_type = '/demo'
    data_path = data_dir + data_type
    
    review_fn = '/reviews.csv'
    features_fn = '/recipes.csv'
    
    data = pd.read_csv(data_path + review_fn)# encoding = "ISO-8859-1",delimiter="|")
    features = pd.read_csv(data_path + features_fn)#,encoding = "ISO-8859-1",delimiter="|")
    
    # only keep recipes with reviews
    features = pd.merge(features, data, left_on='recipe_id', right_on='recipe_id', how="inner")
    features = features[["recipe_id", "cuisine", "clean_ingredients", "big_image"]]
    features = features.drop_duplicates().reset_index()
#    features = features[["recipe_id", "cuisine", "clean_ingredients"]]
    
    # Convert ingredients column to list
    features["clean_ingredients"] = features["clean_ingredients"].apply(lambda a : a.split("+"))
    
    # Convert the float precision to 32-bit in order to reduce memory consumption 
    data.loc[:, 'rating'] = data['rating'].astype(np.float32)
    
    # set log level to INFO
    logging.basicConfig(level=logging.DEBUG, 
                        format='%(asctime)s %(levelname)-8s %(message)s')
    header = {
        "col_user": "username",
        "col_item": "recipe_id",
        "col_rating": "rating",
        "col_timestamp": "date",
        "col_prediction": "Prediction",
    } 
    
    model = SARSingleNode(
        similarity_type="custom", 
        time_decay_coefficient=30, 
        time_now=None, 
        timedecay_formula=False, #add recipes to node CAN SET THIS TO TRUE LATER BUT LETS LEAVE IT FOR NOW
        **header
    )
    
    jaccard = lambda a,b: len(set(a).intersection(set(b)))/len(set(a).union(set(b)))
    train = data
    model.fit(train, features, "recipe_id", {"ratings" : 0.5, "clean_ingredients" : (1.0, jaccard)}, demo=True)
    top_k = model.recommend_k_items(train, remove_seen=True)
    
    top_k_with_titles = (top_k.join(data[['recipe_id']].drop_duplicates().set_index('recipe_id'), 
                                    on='recipe_id', 
                                    how='inner').sort_values(by=['username', 'Prediction'], ascending=False))

    return top_k_with_titles
    

