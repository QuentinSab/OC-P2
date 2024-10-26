import requests
import csv
from bs4 import BeautifulSoup

import requests

from bs4 import BeautifulSoup

url = "http://books.toscrape.com/catalogue/the-requiem-red_995/index.html"
page = requests.get(url)
soup = BeautifulSoup(page.content, 'html.parser')
titre = soup.find_all("h1")
titre_text = []

for h1 in titre:
    titre_text.append(h1.string)
    
print(titre_text[0])