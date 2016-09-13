import requests
from bs4 import BeautifulSoup

ALLOWED_NUTRITION_KEYS = ['energy', 'carbohydrates', 'fat', 'protein']


def get_nutrition_facts(item):
    response = requests.get('https://en.wikipedia.org/wiki/{item}'.format(item=item.capitalize()))
    soup = BeautifulSoup(response.content, 'html.parser')

    nutrition_facts = []

    nutrition_info_box = soup.find_all('table', 'infobox nowrap')
    if nutrition_info_box:
        for row in nutrition_info_box[0].find_all('tr'):
            if row.th is not None and row.td is not None:
                nutrition_key, nutrition_value = row.th.text.strip(), row.td.text.strip()
                if nutrition_key.lower() in ALLOWED_NUTRITION_KEYS:
                    nutrition_facts.append((nutrition_key, nutrition_value))

    return nutrition_facts
