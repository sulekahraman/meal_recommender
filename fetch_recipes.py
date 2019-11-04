import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import re
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException, InvalidSelectorException, ElementNotVisibleException, WebDriverException
import pickle
import csv
import tqdm
import time


def search_entire_category(category_url, save_filename):
    '''writes all recipe links for a given category to pickle list file'''
    MAX_NUM_PAGES = 500  # TODO: find a way to set that automatically
    recipe_urls = []

    # browse over all the search pages for a given category and get their recipes
    for page in range(1, MAX_NUM_PAGES):
        recipe_urls.extend(get_recipe_urls(category_url + str(page)))

    # TODO: either pickle and load or do all at once
    with open(save_filename, 'wb') as handle:
        pickle.dump(recipe_urls, handle)


    return recipe_urls


def get_recipe_urls(cat_page_url):
    '''returns all recipe links for a given search page within a category'''
    response = requests.get(cat_page_url)
    soup = BeautifulSoup(response.text, "html.parser")
    recipe_urls = []

    # find all recipe links embedded in search page
    for elt in set(soup.find_all('a', href=re.compile('^(https://www.allrecipes\.com\/recipe\/)[0-9]*(\/)'))):
        recipe_urls.append(elt['href'])

    return list(set(recipe_urls))


def get_recipe_with_reviews_soup(driver, recipe_url):
    '''returns soup for a recipe after loading many reviews'''
    print(recipe_url)
    driver.get(recipe_url)
    driver.implicitly_wait(10)

    N_REVIEW_PAGES = 15

    for _ in range(N_REVIEW_PAGES):
        try:
            clicker = driver.find_element_by_link_text('More Reviews')
            clicker.location_once_scrolled_into_view
            clicker.click()
            time.sleep(1)
        except (TimeoutException, NoSuchElementException, InvalidSelectorException, ElementNotVisibleException,
                WebDriverException):
            break

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    return soup


def get_recipe_reviews(recipe_soup):
    ''' returns reviews consisting of author, rating and date for a recipe '''
    authors = [" ".join(author.text.split()) for author in recipe_soup.find_all('h4', attrs={'itemprop': 'author'})]
    ratings = [content['content'] for content in recipe_soup.find_all('meta', attrs={'itemprop': 'ratingValue'})][
              1:]  # the first one is the average rating
    dates = [date.text for date in recipe_soup.find_all('div', attrs={'itemprop': 'dateCreated'})]

    reviews = list(set(zip(authors, ratings, dates)))
    return reviews


def get_recipe_features(recipe_soup):
    ''' returns features consisting of title, breadcrumbs and ingredients for a recipe '''
    title = recipe_soup.find('h1', attrs={'id': 'recipe-main-content'}).text
    breadcrumbs = [" ".join(breadcrumb.text.split()) for breadcrumb in
                   recipe_soup.find_all('span', attrs={'itemprop': 'name'})]
    #   TODO: do we want categories? there's also cuisines but both might be empty depending on the recipe
    #     categories = [" ".join(category.text.split()) for category in soup.find_all('span', attrs={'itemprop': 'recipeCategory'})]
    ingredients = [ingredient.text for ingredient in
                   recipe_soup.find_all('span', attrs={'itemprop': 'recipeIngredient'})]
    cuisine = [cuisine.text for cuisine in recipe_soup.find_all('span', attrs={'itemprop': 'recipeCuisine'})]

    return title, breadcrumbs, cuisine, ingredients


def generate_db_from_recipe_urls(recipe_urls, db_path):
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome('./chromedriver', options=options)

    with open('recipe_reviews.csv', 'w') as r, open('recipe_features.csv', 'w') as f:
        review_writer = csv.writer(r, delimiter='|', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        feature_writer = csv.writer(f, delimiter='|', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        review_writer.writerow(['recipe_id', 'author', 'rating', 'date'])
        feature_writer.writerow(['recipe_id', 'title', 'breadcrumbs', 'cuisine', 'ingredients'])

        for recipe_url in tqdm.tqdm(recipe_urls):
            soup = get_recipe_with_reviews_soup(driver, recipe_url)
            recipe_id = re.search('^(https://www.allrecipes\.com\/recipe\/)([0-9]*)(\/)', recipe_url,
                                  re.IGNORECASE).group(2)
            reviews = get_recipe_reviews(soup)
            title, breadcrumbs, cuisine, ingredients = get_recipe_features(soup)

            breadcrumbs = '+'.join(breadcrumbs)
            cuisine = '+'.join(cuisine)
            ingredients = '+'.join(ingredients)

            feature_writer.writerow([recipe_id, title, breadcrumbs, cuisine, ingredients])
            for author, rating, date in reviews:
                review_writer.writerow([recipe_id, author, rating, date])

    return


def main():
    #
    # import logging
    # from selenium.webdriver.remote.remote_connection import LOGGER
    # LOGGER.setLevel(logging.ERROR)
    #
    # logger=logging.getLogger()
    # logger.setLevel(logging.ERROR)


    category_url = 'https://www.allrecipes.com/recipes/80/main-dish/?page='
    pickle_filename = 'allrecipe_urls.pkl'
    db_path = 'TODO'

   # recipe_urls = search_entire_category(category_url, pickle_filename)
    file = open('allrecipe_urls.pkl', 'rb')
    recipe_urls = pickle.load(file)
    print('RECIPE URLS DONE')
    generate_db_from_recipe_urls(recipe_urls, db_path)


main()
