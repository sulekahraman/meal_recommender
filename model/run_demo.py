import pandas as pd
from sar import demo_reco
from gsheets import Sheets

def pull_from_sheets(url, new_ratings_path):
    sheets = Sheets.from_files('~/client_secrets.json', '~/storage.json')    
    s = sheets.get(url)
    p = s.sheets[0]
    df = p.to_frame() 
    last_row = df.iloc[-1]
    new_df = pd.DataFrame(columns=['username', 'recipe_id', 'rating'])
    username = last_row['username']
    for i, col in enumerate(df.columns):
        if col[1] == '[':
            new_df.loc[i] = [username, col[2:-1], last_row[col]]
    new_df.to_csv(new_ratings_path) # encoding='utf-8', dialect='excel')
    return 1

def run_demo(new_ratings_path):
    all_ratings_path = "../data/demo/reviews.csv"
    all_ratings_df = pd.read_csv(all_ratings_path)
    new_ratings_df = pd.read_csv(new_ratings_path)
    features = pd.read_csv('../data/demo/recipes.csv')
    
    all_ratings_df = all_ratings_df.append(new_ratings_df) # append new ratings to old
    all_ratings_df = all_ratings_df.drop_duplicates()
    all_ratings_df.to_csv(all_ratings_path) # update the csv with all ratings
    username = all_ratings_df.iloc[-1]['username']
    k = 3
    all_ranking = demo_reco()
    user_all = all_ranking[all_ranking['username'] == username]
    best_k, worst_k = user_all.head(k), user_all.tail(k)
    #print(best_k)
    print("Top {} Recommended Recipes for {}: ".format(k,username))
    with open('../data/demo/most_recent_reco.csv','w') as f: 
        for i, recipe in enumerate(best_k['recipe_id']):
            recipe_img = features.loc[(features['recipe_id'] == recipe), 'big_image'].item()
            f.write(username + ',' + recipe + ',' + recipe_img)
            f.write('\n')    
            print("{}.) {}".format(i+1, recipe))
        print('\n')
        print("Bottom {} Recommended Recipes for {}: ".format(k,username))
        for i,recipe in enumerate(worst_k['recipe_id']):
            recipe_img = features.loc[(features['recipe_id'] == recipe), 'big_image'].item()
            f.write(username + ',' + recipe + ',' + recipe_img)
            f.write('\n')
            print("{}.) {}".format(i+1, recipe))
        
if __name__ == "__main__":
    google_forms_path = "../data/demo_survey/survey_results.csv" # TODO: add this path
    key = '1T8Htp9LGFYePzdsejs9sxXCHp7UAE76v3nSdYm6EASU'
    url = 'https://docs.google.com/spreadsheets/d/'+key
    #pulled = pull_from_sheets(url, google_forms_path)
    pulled = 1
    if pulled:
        run_demo(google_forms_path)
    

