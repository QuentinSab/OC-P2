import csv
import os
from datetime import date
from re import search

import requests
from bs4 import BeautifulSoup

from model.book import Book


class ScraperModel:
    def __init__(self):
        self.base_url = []

    def find_target_size(self, target):
        if target == self.base_url:
            return "site"
        elif (target.rsplit("/", 3)[0]) == (self.base_url + "/catalogue/category"):
            return "category"
        else:
            return "book"

    def get_page(self, page_url):
        page = requests.get(page_url, timeout=10)

        if page.status_code == 200:
            return BeautifulSoup(page.content, "html.parser")
        else:
            raise Exception(
                f"Erreur {page.status_code} lors de la requête de : {page_url}"
            )

    def get_base_url(self, target):
        segments = target.split("/", 3)
        base_url = "/".join(segments[:3])
        self.base_url = base_url

    def get_books_url(self, category_url):
        """Fetches all books URL from a category and adds them to a list"""

        soup = self.get_page(category_url)

        books_url = []
        category_page_n = 1

        self.get_local_books_url(soup, books_url, self.base_url)

        # Fetch books URL from the subsequent pages
        while soup.find("li", class_="next"):  # Check if there is a next page
            category_page_n += 1

            # Generate the next page URL
            category_url = (
                category_url.rpartition("/")[0]
                + "/page-"
                + str(category_page_n)
                + ".html"
            )

            soup = self.get_page(category_url)  # Load the next page

            self.get_local_books_url(soup, books_url, self.base_url)

        return books_url

    def get_local_books_url(self, soup, books_url, base_url):
        """Fetches books URL from a category page and adds them to a list"""

        for h3 in soup.find_all("h3"):
            book_url = base_url + "/catalogue/" + (h3.find("a")["href"][9:])
            books_url.append(book_url)

    def get_categories_url(self):
        """Fetches the list of categories from a page content"""
        soup = self.get_page(self.base_url)
        ul_category = soup.find_all("ul")[2]
        li_category = ul_category.find_all("li")
        categories_url = []

        for a_category in li_category:
            category_url = self.base_url + "/" + a_category.find("a")["href"]
            categories_url.append(category_url)

        return categories_url

    def get_category_name(self, category_url):
        """Fetches the category name from its URL"""

        # Extract the part before the last "/"
        category_name_part = category_url.rsplit("/", 2)[1]
        # Extract the part before the first "_"
        category_name = category_name_part.split("_", 1)[0]
        return category_name

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
        image_url = self.base_url + path_img["src"][5:]

        return Book(
            book_url,
            upc,
            title,
            price_incl_tax,
            price_excl_tax,
            stock,
            description,
            category,
            rating,
            image_url,
        )

    def create_scrap_directory(self):
        """Creates a timestamped directory for storing scraped data and image."""

        current_date = date.today()
        # Converts date in a string
        str_current_date = current_date.strftime("%d-%m-%Y")
        directory_name = "books_to_scrape_" + str_current_date

        if not os.path.exists(directory_name):
            os.mkdir(directory_name)
            print('Création du dossier "' + directory_name + '"')

        return directory_name

    def create_category_directory(self, category_name, parent_directory):
        """Creates a folder named after the category and returns its path."""

        category_image_path = parent_directory + "/" + category_name + "_image"

        if not os.path.exists(category_image_path):
            os.mkdir(category_image_path)

        return category_image_path

    def write_csv(self, books, directory_name, csv_name):

        file_path = directory_name + "/" + csv_name[:16] + ".csv"

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
                writer.writerow(
                    [
                        book.url,
                        book.upc,
                        book.title,
                        book.price_incl_tax,
                        book.price_excl_tax,
                        book.stock,
                        book.description,
                        book.category,
                        book.rating,
                        book.image_url,
                    ]
                )

    def extract_image(self, image_url, book_title, image_path):
        image_data = requests.get(image_url, timeout=10).content
        file_image_name = image_path + "/" + book_title[:16] + ".jpg"

        with open(file_image_name, "wb") as img_file:
            img_file.write(image_data)
