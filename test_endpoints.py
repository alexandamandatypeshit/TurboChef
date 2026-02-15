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


def is_french_expected(endpoint):
    # Paths under /fr/ or with .fr/ suffix are expected to be French
    if endpoint.startswith('/fr/'):
        return True
    if endpoint.endswith('.fr/') or endpoint.endswith('.fr'):
        return True
    return False


def detect_language_from_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    # 1) prefer <html lang="...">
    html_tag = soup.find('html')
    if html_tag and html_tag.get('lang'):
        lang = html_tag.get('lang').lower()
        if lang.startswith('fr'):
            return 'fr'
        if lang.startswith('en'):
            return 'en'
    # 2) fallback: look for common French/English recipe keywords
    text = soup.get_text(" ").lower()
    fr_markers = ['ingrédients', 'étapes', 'préparation', 'cuisson', 'servings', 'minutes']
    en_markers = ['ingredients', 'steps', 'prep', 'cook', 'servings', 'minutes']
    fr_score = sum(1 for m in fr_markers if m in text)
    en_score = sum(1 for m in en_markers if m in text)
    if fr_score > en_score:
        return 'fr'
    if en_score > fr_score:
        return 'en'
    return None


def check_internal_links(html, base_url, max_links=30):
    soup = BeautifulSoup(html, 'html.parser')
    main = soup.find('main') or soup
    anchors = main.find_all('a', href=True)
    checked = 0
    broken = []
    for a in anchors:
        href = a['href']
        # skip external links
        if href.startswith('http://') or href.startswith('https://'):
            continue
        # normalize
        if href.startswith('/'):
            url = base_url + href
        else:
            # relative link: join with base
            url = base_url + '/' + href.lstrip('./')
        try:
            r = requests.head(url, allow_redirects=True, timeout=5)
            status = r.status_code
        except Exception:
            try:
                r = requests.get(url, timeout=10)
                status = r.status_code
            except Exception:
                status = None
        if status != 200:
            broken.append((href, status))
        checked += 1
        if checked >= max_links:
            break
    return broken

def test_endpoints():
    for endpoint in ENDPOINTS:
        url = BASE_URL + endpoint
        try:
            resp = requests.get(url)
            print(f'[{resp.status_code}] {endpoint}')
            if resp.status_code == 200:
                # layout/css
                if check_css_and_layout(resp.text):
                    print('  ✓ Layout and CSS found')
                else:
                    print('  ✗ Layout/CSS missing or broken')
                # language check
                expected_fr = is_french_expected(endpoint)
                detected = detect_language_from_html(resp.text)
                if expected_fr and detected == 'fr':
                    print('  ✓ Language: fr')
                elif not expected_fr and detected == 'en':
                    print('  ✓ Language: en')
                else:
                    print(f'  ⚠ Language mismatch (expected_fr={expected_fr}, detected={detected})')
                # internal links check (first up to 30 links)
                broken = check_internal_links(resp.text, BASE_URL)
                if not broken:
                    print('  ✓ Internal links OK')
                else:
                    print(f'  ✗ Broken internal links (sample): {broken[:5]}')
            else:
                print('  ✗ Not OK (status code)')
        except Exception as e:
            print(f'  ✗ Error: {e}')

if __name__ == '__main__':
    test_endpoints()
