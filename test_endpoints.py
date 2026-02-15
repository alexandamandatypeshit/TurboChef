import requests
from bs4 import BeautifulSoup

# List of endpoints to test
ENDPOINTS = [
    '/',
    '/fr/',
    '/recipes/baking/',
    '/recipes/cooking/',
    '/recipes/sauces/',
    '/recipes/baking/brioche-cinnamon-buns/',
    '/recipes/baking/rustic-boule/',
    '/recipes/baking/raisin-bread/',
    '/recipes/baking/gooey-fudgey-brownie/',
    '/recipes/cooking/roast-chicken/',
    '/recipes/sauces/garlic-aioli/',
    '/recipes/sauces/simple-syrup-glaze/',
    '/fr/recipes/baking/',
    '/fr/recipes/cooking/',
    '/fr/recipes/sauces/',
    '/recipes/baking/brioche-cinnamon-buns.fr/',
    '/recipes/baking/rustic-boule.fr/',
    '/recipes/baking/raisin-bread.fr/',
    '/recipes/baking/gooey-fudgey-brownie.fr/',
    '/recipes/cooking/roast-chicken.fr/',
    '/recipes/sauces/garlic-aioli.fr/',
    '/recipes/sauces/simple-syrup-glaze.fr/',
]

BASE_URL = 'http://127.0.0.1:8080'

def check_css_and_layout(html):
    soup = BeautifulSoup(html, 'html.parser')
    # Check for stylesheet link
    css = soup.find('link', rel='stylesheet')
    # Check for main header
    header = soup.find('header')
    # Check for main content
    main = soup.find('main')
    # Check for footer
    footer = soup.find('footer')
    return all([css, header, main, footer])

def test_endpoints():
    for endpoint in ENDPOINTS:
        url = BASE_URL + endpoint
        try:
            resp = requests.get(url)
            print(f'[{resp.status_code}] {endpoint}')
            if resp.status_code == 200:
                if check_css_and_layout(resp.text):
                    print('  ✓ Layout and CSS found')
                else:
                    print('  ✗ Layout/CSS missing or broken')
            else:
                print('  ✗ Not OK (status code)')
        except Exception as e:
            print(f'  ✗ Error: {e}')

if __name__ == '__main__':
    test_endpoints()
