# -*- coding: utf-8 -*-
import csv
import os
from re import search
from datetime import date
import requests
from bs4 import BeautifulSoup

base_url = "http://books.toscrape.com"

def etl_site():
    soup = get_page(base_url + "/index.html")

    main_directory_name = create_scrap_directory()

    print(f"Écriture de {main_directory_name} en cours ...")
    for a_category in get_categories(soup):  
        category_url = get_category_url(a_category)
        category_name = get_category_name(category_url)
        
        category_image_path = create_category_directory(category_name, main_directory_name)
        
        file_csv_name = (main_directory_name + "/" + category_name + "_data.csv")
         
        load_data(category_url, file_csv_name, category_image_path)
    print(f"Écriture de {main_directory_name} terminée")

def load_data(category_url, file_csv, category_image_path):
    
    with open(file_csv, mode='w', newline='', encoding='utf-8') as fichier:
        header = ["product_page_url", "universal_product_code (upc)", "title", "price_including_tax", "price_excluding_tax", "number_available", "product_description", "category", "review_rating", "image_url"]
        writer = csv.writer(fichier)
        
        writer.writerow(header)
        
        for book_url in get_books_url(category_url):
            book_data = extract_book_data(book_url)
            writer.writerow(book_data)
            
            download_image(book_data, category_image_path)
    
    print(f"{file_csv} édité avec succès.")

def download_image(book_data, category_image_path):
    img_data = requests.get(book_data[9]).content
    file_image_name = get_image_name(book_data[0])
    
    with open(category_image_path + "/" + file_image_name + ".jpg", 'wb') as img_file:
        img_file.write(img_data)

def get_categories(soup):
    ul_category = soup.find_all("ul")[2]
    li_category = ul_category.find_all("li")
    return (li_category)

def get_category_url(category):
    category_url = (base_url + "/" + category.find("a")["href"])
    return (category_url)

def get_category_name(category_url):
    category_name_part = category_url.rsplit("/", 2)[1]
    category_name = category_name_part.split("_", 1)[0]
    return (category_name)

def get_image_name(image_url):
    image_name = image_url.rsplit("/", 2)[1]
    image_name = image_name.rsplit("_", 1)[0]
    return (image_name)

def get_books_url(category_url):
    soup = get_page(category_url)
        
    books_url = []
    category_n_page = 1
    
    get_local_books_url(soup, books_url)
        
    while soup.find("li", class_="next"):
        category_n_page += 1
        category_url = (category_url.rpartition("/")[0] + "/page-" + str(category_n_page) + ".html")
        soup = get_page(category_url)
        get_local_books_url(soup, books_url)
        
    return(books_url)
          
def get_local_books_url(soup, books_url):
    for h3 in soup.find_all('h3'):
        book_url = base_url + "/catalogue/" + (h3.find('a')["href"][9:])            
        books_url.append(book_url)
     
def get_page(page_url):
    page = requests.get(page_url)
    if page.status_code == 200:     
        soup = BeautifulSoup(page.content, 'html.parser')
        return (soup)
    else: 
        print(f"Erreur {page.status_code} lors de la requête de : {page_url}")
      
def extract_book_data(book_url):
    soup = get_page(book_url)    
    book_data = []
        
    book_data.append(book_url)
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
    td_data = soup.find_all("td")
    book_data.append(td_data[0].text)

def extract_title(soup, book_data):
    h1_title = soup.find("h1")
    book_data.append(h1_title.text)

def extract_price_incl_tax(soup, book_data):
    td_data = soup.find_all("td")
    price_incl_tax = td_data[3].text
    price_incl_tax = price_incl_tax[1:]
    book_data.append(price_incl_tax)

def extract_price_excl_tax(soup, book_data):
    td_data = soup.find_all("td")
    price_excl_tax = td_data[2].text
    price_excl_tax = price_excl_tax[1:]
    book_data.append(price_excl_tax)

def extract_stock(soup, book_data):
    td_data = soup.find_all("td")
    stock = (td_data[5].text)
    stock = transform_stock(stock)
    book_data.append(stock)

def extract_description(soup, book_data):
    div_product_description = soup.find("div", class_="sub-header")
    product_description = div_product_description.find_next("p")
    book_data.append(product_description.text)

def extract_category(soup, book_data):
    anchor = soup.find_all("a")
    book_data.append(anchor[3].text)

def extract_rating(soup, book_data):
    p_rating = soup.find("p", class_="star-rating")
    rating = p_rating["class"][1]
    rating = transform_rating(rating)
    book_data.append(rating)
    
def extract_url_img(soup, book_data):
    path_img = soup.find("img")   
    book_data.append(base_url + path_img["src"][5:])
    
def transform_stock(text_stock):
    stock = search('(\d+)', text_stock)
    return (int(stock.group(1)))

def transform_rating(text_rating):
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

def create_scrap_directory():
    current_date = date.today()
    str_current_date = current_date.strftime("%d-%m-%Y")
    directory_name = "books_to_scrape_" + str_current_date

    if not os.path.exists(directory_name):
        os.mkdir(directory_name)
        print("Création du dossier " + directory_name)
        
    return (directory_name)

def create_category_directory(category_name, main_directory_name):
    category_image_path = main_directory_name + "/" + category_name + "_image"
    if not os.path.exists(category_image_path):
        os.mkdir(category_image_path)
    
    return(category_image_path)
        
etl_site()