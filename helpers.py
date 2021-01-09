import requests
from selectorlib import Extractor
from bs4 import BeautifulSoup

e_product = Extractor.from_yaml_file('selectors.yml')

def scrape_search(url):  
    r = requests.get(url)
    # Simple check to check if page was blocked (Usually 503)
    if r.status_code > 500:
        return []
    # Pass the HTML of the page and create 
    soup = BeautifulSoup(r.text, "html.parser")
    links = []
    for link in soup.select('a.a-link-normal.a-text-normal'):
        link_str = link.get('href')
        if link_str:
            links.append(link_str)
    return links

def scrape_product(url):
    # Create an Extractor by reading from the YAML file
    HEADERS = ({'User-Agent':
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36',
            'Accept-Language': 'en-US, en;q=0.5'})
    r = requests.get(url, headers=HEADERS)
    # Simple check to check if page was blocked (Usually 503)
    if r.status_code > 500:
        return None
    # Pass the HTML of the page and create
    return e_product.extract(r.text)


def data_builder(data, DETAIL_KEYS):
    DETAIL_KEYS = set(DETAIL_KEYS)
    if data and data['details__private__DO_NOT_MODIFY']:
        for detail in data['details__private__DO_NOT_MODIFY']:
            if detail['key'] in DETAIL_KEYS:
                val = str(detail['value'])
                val = val.replace(',', '')
                data[detail['key']] = val
        for key in DETAIL_KEYS:
            if key not in data:
                data[key] = ""
        del data['details__private__DO_NOT_MODIFY']
    return data
