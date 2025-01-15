import csv
import os
from re import search
import requests
from bs4 import BeautifulSoup

BASE_URL = "http://books.toscrape.com"

# ********************************* Model *********************************
class Book:
    def __init__(self, url, upc, title, price_incl_tax, price_excl_tax, stock, description, category, rating, image_url):
        self.url = url
        self.upc = upc
        self.title = title
        self.price_incl_tax = price_incl_tax
        self.price_excl_tax = price_excl_tax
        self.stock = stock
        self.description = description
        self.category = category
        self.rating = rating
        self.image_url = image_url

class ScraperModel:
    def __init__(self, base_url):
        self.base_url = base_url

    def get_page(self, page_url):
        page = requests.get(page_url, timeout=10)
        
        if page.status_code == 200:
            return BeautifulSoup(page.content, "html.parser")
        else:
            raise Exception(f"Erreur {page.status_code} lors de la requête de : {page_url}")

    def extract_book_data(self, book_url):
        soup = self.get_page(book_url)

        # upc
        td_data = soup.find_all("td")
        upc = td_data[0].text

        # title
        h1_title = soup.find("h1")
        title = h1_title.text

        # price_incl_tax
        td_data = soup.find_all("td")
        price_incl_tax = td_data[3].text[1:]

        # price_excl_tax
        td_data = soup.find_all("td")
        price_excl_tax = td_data[2].text[1:]

        # stock
        td_data = soup.find_all("td")
        stock = search("(\\d+)", td_data[5].text)
        stock = int(stock.group(1))

        # description
        div_product_description = soup.find("div", class_="sub-header")
        product_description = div_product_description.find_next("p")
        description = product_description.text

        # category
        anchor = soup.find_all("a")
        category = anchor[3].text

        # rating
        p_rating = soup.find("p", class_="star-rating")
        rating = p_rating["class"][1]  
        match rating:
            case "One":
                rating = 1
            case "Two":
                rating = 2
            case "Three":
                rating = 3
            case "Four":
                rating = 4
            case "Five":
                rating = 5

        # image_url
        path_img = soup.find("img")
        image_url = (self.base_url + path_img["src"][5:])

        return Book(book_url, upc, title, price_incl_tax, price_excl_tax, stock, description, category, rating, image_url)

# ********************************* View *********************************
class CsvView:
    def write_category_csv(self, books, file_path):

        header = [
            "product_page_url",
            "universal_product_code (upc)",
            "title",
            "price_including_tax",
            "price_excluding_tax",
            "number_available",
            "product_description",
            "category",
            "review_rating",
            "image_url",
        ]

        with open(file_path, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(header)

            for book in books:
                writer.writerow([
                    book.url,
                    book.upc,
                    book.title,
                    book.price_incl_tax,
                    book.price_excl_tax,
                    book.stock,
                    book.description,
                    book.category,
                    book.rating,
                    book.image_url
                ])

class ImageView:
    def write_book_image(self, book, file_path):
        pass

# ********************************* Controller *********************************
class ScraperController:
    def __init__(self, model, view):
        self.model = model
        self.view = view
