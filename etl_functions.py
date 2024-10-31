import csv
from re import search
import requests
from bs4 import BeautifulSoup

def extract_category_data(category_url, fichier_csv):
    
    with open(fichier_csv, mode='w', newline='', encoding='utf-8') as fichier:
        header = ["product_page_url", "universal_product_code (upc)", "title", "price_including_tax", "price_excluding_tax", "number_available", "product_description", "category", "review_rating", "image_url"]
        writer = csv.writer(fichier)
        
        writer.writerow(header)
        print(f"Écriture de {fichier_csv} en cours ...")
        
        for livre_url in extract_category_livres_url(category_url):
            book_data = extract_livre_data(livre_url)
            writer.writerow(book_data)

    print(f"{fichier_csv} édité avec succès.")

def extract_category_livres_url(category_url):
    soup = extract_page(category_url)
        
    livres_url = []
    category_n_page = 1
    
    extract_page_livres_url(soup, livres_url)
        
    while soup.find("li", class_="next"):
        category_n_page += 1
        category_url = (category_url.rpartition("/")[0] + "/page-" + str(category_n_page) + ".html")
        soup = extract_page(category_url)
        extract_page_livres_url(soup, livres_url)
        
    return(livres_url)
               
def extract_page(page_url):
    page = requests.get(page_url)
    if page.status_code == 200:     
        soup = BeautifulSoup(page.text, 'html.parser')
        return (soup)
    else: 
        print(f"Erreur {page.status_code} lors de la requête de : {page_url}")
      
def extract_page_livres_url(soup, livres_url):
    for h3 in soup.find_all('h3'):
        livre_url = "http://books.toscrape.com/catalogue/" + (h3.find('a')["href"][9:])            
        livres_url.append(livre_url)
        
def extract_livre_data(livre_url):
    soup = extract_page(livre_url)    
    book_data = []
        
    book_data.append(livre_url)
    extract_upc(soup, book_data)
    extract_title(soup, book_data) 
    extract_price_incl_tax(soup, book_data)
    extract_price_excl_tax(soup, book_data)
    extract_stock(soup, book_data)
    extract_description(soup, book_data)
    extract_category(soup, book_data)
    extract_rating(soup, book_data)
    extract_url_img(soup, book_data)
    
    return (book_data)
        
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
    url_img = soup.find("img")   
    book_data.append("http://books.toscrape.com" + url_img["src"][5:])
    
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