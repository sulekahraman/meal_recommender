# Ideal Meals: A Personalized Recipe Recommender System
We often find ourselves staring at the fridge thinking to ourselves “What should I cook for dinner tonight?”. Today, recipe recommendation engines exist, however many take neither the flavor profile of the user nor ingredients into consideration. Our project aims to simplify the meal selection and preparation process in a personalized way. We believe that we can exploit the robustness of neighborhood- based recommendation systems while using information about user preferences to yield better, more personalized meal recommendations. 

## Installation
```
git clone https://github.com/sulekahraman/meal_recommender.git
pip install -r requirements.txt 
```

## Running Code
All of the code for our system can be found in (either directly or linked within) the [model/sar_deep_dive.ipynb](/model/sar_deep_dive.ipynb). To run, just navegate to the git repo directory and run:
```
jupyter notebook
```
There, you can open the jupyter notebook [sar_deep_dive.ipynb](/model/sar_deep_dive.ipynb) and go through the cells which have infomation about what each cell does/computes. You will find links to other notebooks, specifically ones that explain how we generate our synthetic users, how we create small/usable recipes databases, and how we calculate the similarity and affinity matrices. Here is also where you will find our evaluation of our system


## System Architecture 
### Augmented Simple Algorithm for Recommendation (SAR) Diagram
diagrams/sar_diag.png

### End-to-end System Diagram
diagrams/sys_diag.png


## Data
### Recipes Datasets
* Schema: Provides recipe features (title, unique ID, cuisine, and ingredients)
* Generation: Implemented a Python web scraper to extract over 140 recipes from allrecipes.com’s ’Main Dish’ category. Code can found in the **data_collection** folder.
* Standardization: Cleaned recipes using a custom regex script to remove common ingredients (e.g. salt) and distinguish measurement amounts from ingredients. Code can be found in the **data_processing** folder.
* Use: To generate recipe-recipe similarity matrix for our recommendation engine.

### Reviews Datasets
* Schema: Holds user rating information (username, rating, recipe ID).
* Generation: 
  * Method 1: Scraped up to 150 reviews per recipe from allrecipes.com
  * Method 2: Created ”artificial” users to model simple human behavior by assigning random cuisines as favorite/ least favorite and ratings based on recipe similarity to these two cuisines.
* Use: To generate user-recipe affinity and recipe-recipe similarity matrices for our recommendation engine.

