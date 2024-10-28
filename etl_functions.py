from re import search
import requests
from bs4 import BeautifulSoup
        
def extract_page(url):
    page = requests.get(url)
    if page.status_code == 200:     
        soup = BeautifulSoup(page.text, 'html.parser')
        
        book_data = []
        
        book_data.append(url)
        extract_upc(soup, book_data)
        extract_title(soup, book_data) 
        extract_price_incl_tax(soup, book_data)
        extract_price_excl_tax(soup, book_data)
        extract_stock(soup, book_data)
        extract_description(soup, book_data)
        extract_category(soup, book_data)
        extract_rating(soup, book_data)
        extract_url_img(soup, book_data)
    
        #return (book_data)
        for data in book_data:
            print(data)
        
    else: 
        print(f"Erreur {page.status_code} lors de la requête de : {url}")

def extract_upc(soup, book_data):
    td = soup.find_all("td")
    book_data.append(td[0].text)

def extract_title(soup, book_data):
    h1 = soup.find("h1")
    book_data.append(h1.text)

def extract_price_incl_tax(soup, book_data):
    td = soup.find_all("td")
    price_incl_tax = td[3].text
    price_incl_tax = price_incl_tax[2:]
    book_data.append(price_incl_tax)

def extract_price_excl_tax(soup, book_data):
    td = soup.find_all("td")
    price_excl_tax = td[2].text
    price_excl_tax = price_excl_tax[2:]
    book_data.append(price_excl_tax)

def extract_stock(soup, book_data):
    td = soup.find_all("td")
    stock = (td[5].text)
    stock = stock_to_int(stock)
    book_data.append(stock)

def extract_description(soup, book_data):
    product_description_div = soup.find("div", class_="sub-header")
    product_description = product_description_div.find_next("p")
    book_data.append(product_description.text)

def extract_category(soup, book_data):
    anchors = soup.find_all("a")
    book_data.append(anchors[3].text)

def extract_rating(soup, book_data):
    rating_p = soup.find("p", class_="star-rating")
    rating = rating_p["class"][1]
    rating = rating_to_int(rating)
    book_data.append(rating)
    
def extract_url_img(soup, book_data):
    product_img = soup.find("img")   
    book_data.append("http://books.toscrape.com" + product_img["src"][5:])
    
def stock_to_int(stock_str):
    stock = search('(\d+)', stock_str)
    return (int(stock.group(1)))

def rating_to_int(text_rating):
    match text_rating:
        case "One":
            return (1)
        case "Two":
            return (2)
        case "Three":
            return (3)
        case "Four":
            return (4)
        case "Five":
            return (5)
        case _:
            return ("Erreur : Rating invalide")