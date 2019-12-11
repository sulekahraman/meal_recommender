# Ideal Meals: A Personalized Recipe Recommender System
We often find ourselves staring at the fridge thinking to ourselves “What should I cook for dinner tonight?”. Today, recipe recommendation engines exist, however many take neither the flavor profile of the user nor ingredients into consideration. Our project aims to simplify the meal selection and preparation process in a personalized way. We believe that we can exploit the robustness of neighborhood- based recommendation systems while using information about user preferences to yield better, more personalized meal recommendations. 

## Installation
```
git clone https://github.com/sulekahraman/meal_recommender.git
pip install -r requirements.txt 
```

## System Architecture
### Augment Simple Algorithm for Recommendation (SAR)
diagrams/sar_diag.png

### End-to-end system
diagrams/sys_diag.png


## Data
### Recipes Dataset
* Schema: Provides recipe features (title, unique ID, cuisine, and ingredients)
* Generation: Implemented a Python web scraper to extract over 140 recipes from allrecipes.com’s ’Main Dish’ category. Code can found in the **data_collection** folder.
* Standardization: Cleaned recipes using a custom regex script to remove common ingredients (e.g. salt) and distinguish measurement amounts from ingredients. Code can be found in the **data_processing** folder.
* Use: To generate recipe-recipe similarity matrix for our recommendation engine.

### Reviews Dataset
* Schema: Holds user rating information (username, rating, recipe ID).
* Generation: 
  * Method 1: Scraped up to 150 reviews per recipe from allrecipes.com
  * Method 2: Created ”artificial” users to model simple human behavior by assigning random cuisines as favorite/ least favorite and ratings based on recipe similarity to these two cuisines.
* Use: To generate user-recipe affinity and recipe-recipe similarity matrices for our recommendation engine.

