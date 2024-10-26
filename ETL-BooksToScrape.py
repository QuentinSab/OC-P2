import requests
from bs4 import BeautifulSoup

url = "http://books.toscrape.com/catalogue/category/books/mystery_3/index.html"
page = requests.get(url)

if page.status_code == 200:
    
    soup = BeautifulSoup(page.text, 'html.parser')
    
    titles = [a['title'] for a in soup.find_all('a', title=True)]
    for title in titles:
        print(title)
    
    class_price = "price_color"
    prices = soup.find_all("p", class_=class_price)
    for price in prices:
        print(price.text[2:])
        
else:
    
    print(f"Erreur {page.status_code} lors de la requête de : {url}")