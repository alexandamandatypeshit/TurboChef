#!/usr/bin/env python3
"""
fetch_calories.py

- Extracts ingredients from recipe markdown files
- Optionally fetches a top-N food list from USDA FoodData Central
- Queries USDA for calorie values (kcal per gram) for missing ingredients
- Updates src/assets/calorie-db.json adding new entries

Usage:
  1) Set USDA API key in env var: USDA_API_KEY or edit API_KEY default below.
  2) Run: python fetch_calories.py

Note: This is a pragmatic script; results depend on USDA search matches.
"""

import requests
import json
import time
import glob
import re
import os
import sys

API_KEY = os.environ.get('USDA_API_KEY', 'FVTpPv9SE9Xasnn8EORNcQ8TYnBCbaqQJpaD2ix8')
API_URL = "https://api.nal.usda.gov/fdc/v1/foods/search"
DB_PATH = 'src/assets/calorie-db.json'


def extract_ingredients_from_recipes():
    ingredients = set()
    for file in glob.glob('src/recipes/**/*.md', recursive=True):
        try:
            with open(file, encoding='utf-8') as f:
                content = f.read()
        except Exception:
            continue
        match = re.search(r'ingredients:\s*((?:- .+\n)+)', content)
        if match:
            lines = match.group(1).splitlines()
            for line in lines:
                ing = line.strip().lstrip('-').strip()
                # Remove leading quantities and parentheticals
                ing_name = re.sub(r'^[\d\s/.,()-]+', '', ing)
                ing_name = re.sub(r'\(.*?\)', '', ing_name)
                ing_name = ing_name.split(',')[0].split(' to ')[0].strip().lower()
                if ing_name:
                    ingredients.add(ing_name)
    return sorted(ingredients)


def fetch_calories_for_name(api_key, name):
    params = {
        'api_key': api_key,
        'query': name,
        'pageSize': 1
    }
    try:
        resp = requests.get(API_URL, params=params, timeout=15)
        if resp.status_code != 200:
            return 0
        data = resp.json()
        foods = data.get('foods', [])
        if not foods:
            return 0
        food = foods[0]
        nutrients = {n.get('nutrientName', '').lower(): n.get('value', 0) for n in food.get('foodNutrients', [])}
        cal_per_100g = nutrients.get('energy', 0)
        return round(cal_per_100g / 100, 2) if cal_per_100g else 0
    except Exception:
        return 0


def main():
    print('Scanning recipes for ingredients...')
    recipe_ings = extract_ingredients_from_recipes()
    print(f'Found {len(recipe_ings)} unique ingredients in recipes.')

    # Curated ingredient lists by category (generic names, no brands)
    cooking_common = [
    # Oils & Fats
    'olive oil', 'extra virgin olive oil', 'vegetable oil', 'canola oil',
    'sesame oil', 'avocado oil', 'coconut oil',
    'butter', 'clarified butter', 'ghee',

    # Aromatics
    'garlic', 'garlic powder', 'onion', 'red onion', 'shallot',
    'green onion', 'leek', 'ginger', 'fresh ginger', 'ginger powder',

    # Acids
    'lemon', 'lime', 'lemon juice', 'lime juice',
    'white vinegar', 'apple cider vinegar', 'red wine vinegar',
    'balsamic vinegar', 'rice vinegar',

    # Proteins
    'chicken', 'chicken breast', 'chicken thighs',
    'ground beef', 'beef', 'steak',
    'ground pork', 'pork', 'bacon',
    'shrimp', 'salmon', 'tuna',
    'eggs', 'tofu', 'beans', 'chickpeas',

    # Vegetables
    'tomato', 'cherry tomatoes', 'canned tomatoes',
    'potato', 'sweet potato',
    'carrot', 'celery', 'bell pepper',
    'zucchini', 'broccoli', 'cauliflower',
    'spinach', 'kale', 'mushroom',
    'corn', 'peas',

    # Grains & Carbs
    'rice', 'jasmine rice', 'basmati rice',
    'pasta', 'spaghetti', 'penne',
    'breadcrumbs', 'flour tortilla', 'bread',

    # Dairy
    'milk', 'whole milk', 'cream', 'heavy cream',
    'half and half', 'parmesan', 'cheddar',
    'mozzarella', 'feta', 'sour cream', 'yogurt',

    # Herbs (fresh & dried)
    'parsley', 'cilantro', 'oregano', 'thyme',
    'rosemary', 'basil', 'dill',
    'bay leaf', 'chives',

    # Spices
    'salt', 'kosher salt', 'sea salt',
    'black pepper', 'white pepper',
    'paprika', 'smoked paprika',
    'cumin', 'coriander',
    'turmeric', 'cayenne',
    'chili powder', 'red pepper flakes',
    'italian seasoning',

    # Liquids & Umami
    'chicken broth', 'beef broth', 'vegetable broth',
    'soy sauce', 'tamari', 'fish sauce',
    'oyster sauce', 'worcestershire sauce',
    'hot sauce', 'mustard', 'dijon mustard',
    'ketchup', 'mayonnaise', 'honey',
    'maple syrup',

    # Thickeners & Binding
    'cornstarch',  # Super common thickener for sauces, stir-fries
    'all-purpose flour',  # Dredging, breading, thickening

    # More Aromatics/Peppers  
    'white onion',  # You have onion/red onion, but white is most common
    'jalapeño',  # Very common fresh pepper

    # Sugars (used in savory too)
    'sugar',  # Balancing flavors, caramelizing, marinades

    # Cooking Liquids
    'white wine',  # Deglazing, sauces, risotto
    'tomato paste',  # Concentrated flavor (different from canned)

    # Asian Pantry
    'mirin',  # Common in Japanese cooking
    'rice wine',  # Chinese cooking

    # Specific Beans (you have generic "beans")
    'black beans', 'kidney beans',

    # More Proteins
    'ground turkey',  # Common lean alternative

    ]


    baking_common = [
    # Flours
    'all-purpose flour', 'bread flour', 'whole wheat flour',
    'cake flour', 'pastry flour', 'almond flour',
    'cocoa powder',

    # Leavening
    'baking powder', 'baking soda',
    'active dry yeast', 'instant yeast',

    # Sugars & Sweeteners
    'white sugar', 'granulated sugar',
    'brown sugar', 'light brown sugar', 'dark brown sugar',
    'powdered sugar',
    'honey', 'maple syrup',

    # Fats
    'butter', 'unsalted butter', 'salted butter',
    'vegetable oil', 'coconut oil',

    # Dairy
    'milk', 'whole milk', 'buttermilk',
    'heavy cream', 'cream cheese',
    'sour cream', 'yogurt',

    # Eggs
    'egg', 'eggs', 'egg yolk', 'egg white',

    # Flavorings
    'vanilla extract', 'vanilla',
    'almond extract',
    'cinnamon', 'nutmeg', 'cloves',

    # Add-ins
    'chocolate chips', 'dark chocolate',
    'white chocolate', 'nuts',
    'walnuts', 'pecans', 'almonds',
    'raisins', 'dried cranberries',
    'oats', 'rolled oats',
    # Critical omission:
    'salt',  # Used in almost ALL baking!

    # Sweeteners
    'molasses',  # Gingerbread, some cookies
    'corn syrup',  # Pecan pie, candy, frosting

    # Add-ins
    'shredded coconut',
    'peanut butter',  # Cookies, brownies
    ]

    vegetables_common = [
    # Alliums
    'onion', 'red onion', 'yellow onion', 'shallot',
    'green onion', 'leek', 'garlic',

    # Root Vegetables
    'carrot', 'parsnip', 'turnip', 'rutabaga',
    'beet', 'radish', 'sweet potato', 'potato',

    # Leafy Greens
    'spinach', 'kale', 'arugula', 'lettuce',
    'romaine', 'swiss chard', 'cabbage',

    # Cruciferous
    'broccoli', 'cauliflower', 'brussels sprouts',

    # Nightshades
    'tomato', 'cherry tomato',
    'bell pepper', 'red bell pepper', 'green bell pepper',
    'jalapeno', 'chili pepper', 'eggplant',

    # Squash & Gourds
    'zucchini', 'yellow squash',
    'butternut squash', 'acorn squash',
    'pumpkin', 'cucumber',

    # Legumes
    'green beans', 'snap peas', 'snow peas',
    'corn', 'peas',

    # Mushrooms
    'mushroom', 'cremini mushroom', 'portobello mushroom',

    # Other
    'celery', 'asparagus', 'artichoke'
    ]

    fruits_common = [
    # Citrus
    'lemon', 'lime', 'orange', 'blood orange', 'grapefruit',
    'mandarin', 'clementine',

    # Apples & Pears
    'apple', 'green apple', 'red apple', 'pear',

    # Berries
    'strawberry', 'blueberry', 'raspberry', 'blackberry',
    'cranberry',

    # Stone Fruits
    'peach', 'nectarine', 'plum', 'apricot', 'cherry',

    # Tropical
    'banana', 'pineapple', 'mango', 'papaya',
    'kiwi', 'passion fruit', 'coconut',

    # Melons
    'watermelon', 'cantaloupe', 'honeydew',

    # Other Common
    'grape', 'pomegranate', 'fig', 'date', 'avocado'
    ]

    meats_common = [
    # Chicken
    'whole chicken', 'chicken breast', 'chicken thigh',
    'chicken wings', 'ground chicken',

    # Beef
    'ground beef', 'beef chuck', 'beef steak',
    'ribeye', 'sirloin', 'beef short ribs',
    'beef brisket',

    # Pork
    'pork chop', 'pork tenderloin',
    'ground pork', 'pork shoulder',
    'bacon', 'ham',

    # Turkey
    'ground turkey', 'turkey breast',

    # Lamb
    'lamb chop', 'ground lamb',

    # Seafood
    'salmon', 'tuna', 'cod',
    'tilapia', 'shrimp', 'scallops',
    'mussels', 'clams', 'crab',

    # Other Proteins
    'duck', 'sausage', 'chorizo',
    'tofu', 'tempeh'
    ]


    sauces_common = [
    # Tomato-Based
    'tomato sauce', 'tomato paste',
    'crushed tomatoes', 'marinara sauce',

    # Oils & Fats
    'olive oil', 'butter', 'cream',

    # Acids
    'vinegar', 'balsamic vinegar',
    'rice vinegar', 'lemon juice',
    'lime juice',

    # Asian Staples
    'soy sauce', 'tamari',
    'fish sauce', 'oyster sauce',
    'sesame oil', 'hoisin sauce',

    # Condiments
    'mustard', 'dijon mustard',
    'mayonnaise', 'ketchup',
    'hot sauce', 'sriracha',
    'worcestershire sauce',

    # Dairy & Emulsifiers
    'parmesan', 'cheddar',
    'sour cream', 'yogurt',

    # Aromatics
    'garlic', 'onion', 'shallot',
    'ginger',

    # Sweeteners
    'honey', 'brown sugar',
    'maple syrup',
    # Thickeners
    'cornstarch',  # Slurries, Asian sauces
    'flour',  # Roux, gravy

    # Liquids
    'white wine', 'red wine',  # Pan sauces, reductions
    'chicken broth',  # Sauce base
    'coconut milk',  # Curry, Thai sauces

    # Flavor Bases
    'tahini',  # Middle Eastern sauces
    'miso paste',  # Japanese sauces, umami depth
    ]


    curated = sorted(set(cooking_common) | set(baking_common) | set(sauces_common) | set(fruits_common))

    # Merge curated with recipe-extracted
    all_ingredients = sorted(set(curated) | set(recipe_ings))
    print(f'Total ingredients to check (curated + recipes): {len(all_ingredients)}')

    # Load existing DB
    calorie_db = {}
    if os.path.exists(DB_PATH):
        try:
            with open(DB_PATH, 'r', encoding='utf-8') as f:
                calorie_db = json.load(f)
        except Exception:
            calorie_db = {}

    # Fetch missing entries from USDA (approximate per-gram kcal)
    for ing in all_ingredients:
        key = ing
        # normalize some pluralization
        if key.endswith('s') and key[:-1] in calorie_db:
            print(f'{ing}: plural alias exists')
            continue
        if key in calorie_db:
            print(f'{ing}: already present')
            continue
        cal = fetch_calories_for_name(API_KEY, ing)
        # If USDA returned 0 (not found), apply heuristic fallback
        if not cal:
            # retry once more with a shortened name (first word)
            first_word = ing.split()[0]
            if first_word != ing:
                cal = fetch_calories_for_name(API_KEY, first_word)
            # if still zero, use simple heuristic
        if not cal:
            def heuristic_estimate(name):
                n = name.lower()
                # oils and fats
                if any(x in n for x in ['oil', 'butter', 'ghee', 'lard']):
                    return 8.8
                # sugar and sweeteners
                if any(x in n for x in ['sugar', 'honey', 'syrup', 'molasses']):
                    return 3.8
                # flours, grains, pasta, rice, oats
                if any(x in n for x in ['flour', 'rice', 'pasta', 'bread', 'oat', 'cereal']):
                    return 3.6
                # nuts and seeds
                if any(x in n for x in ['nut', 'almond', 'walnut', 'pecan', 'peanut', 'tahini']):
                    return 6.5
                # dairy (cheese, cream, milk)
                if any(x in n for x in ['cheese', 'cream', 'milk', 'yogurt']):
                    return 3.5
                # proteins/meats
                if any(x in n for x in ['chicken', 'beef', 'pork', 'salmon', 'tuna', 'shrimp', 'steak']):
                    return 2.5
                # legumes, beans, chickpeas
                if any(x in n for x in ['bean', 'chickpea', 'lentil', 'peas']):
                    return 1.3
                # vegetables (low cal)
                if any(x in n for x in ['tomato', 'lettuce', 'spinach', 'zucchini', 'broccoli', 'carrot', 'celery', 'onion', 'pepper']):
                    return 0.4
                # fruits
                if any(x in n for x in ['apple', 'banana', 'orange', 'berry', 'mango', 'pear', 'peach']):
                    return 0.6
                # spices/herbs: negligible per-gram but sometimes dense (nutmeg)
                if any(x in n for x in ['salt', 'pepper', 'cinnamon', 'paprika', 'nutmeg', 'clove']):
                    return 2.0
                # fallback average
                return 1.5

            cal = heuristic_estimate(ing)
            print(f'{ing}: heuristic estimate used -> {cal} kcal/g')
        else:
            print(f'{ing}: {cal} kcal/g (USDA)')
        calorie_db[key] = cal
        time.sleep(0.12)

    # Write back DB
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with open(DB_PATH, 'w', encoding='utf-8') as f:
        json.dump(calorie_db, f, indent=2, ensure_ascii=False)

    print('Done. Updated', DB_PATH)


if __name__ == '__main__':
    main()
