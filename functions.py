import os
from re import search
from datetime import date

import requests
from bs4 import BeautifulSoup


def extract_upc(soup, book_data):
    """
    Extracts the UPC (Universal Product Code) and appends it to book data.
    """

    td_data = soup.find_all("td")
    book_data.append(td_data[0].text)


def extract_title(soup, book_data):
    """Extracts the book title and appends it to book data."""

    h1_title = soup.find("h1")
    book_data.append(h1_title.text)


def extract_price_incl_tax(soup, book_data):
    """Extracts the price including tax and appends it to book data."""

    td_data = soup.find_all("td")
    # Extract price from the fourth cell and remove the currency symbol
    price_incl_tax = td_data[3].text[1:]
    book_data.append(price_incl_tax)


def extract_price_excl_tax(soup, book_data):
    """Extracts the price excluding tax and appends it to book data."""

    td_data = soup.find_all("td")
    # Extract price from the third cell and remove the currency symbol
    price_excl_tax = td_data[2].text[1:]
    book_data.append(price_excl_tax)


def extract_stock(soup, book_data):
    """Extracts the stock quantity and appends it to book data."""

    td_data = soup.find_all("td")
    # Extract and transform stock information from the appropriate cell
    stock = transform_stock(td_data[5].text)
    book_data.append(stock)


def extract_description(soup, book_data):
    """Extracts the product description and appends it to book data."""

    div_product_description = soup.find("div", class_="sub-header")
    product_description = div_product_description.find_next("p")
    book_data.append(product_description.text)


def extract_category_name(soup, book_data):
    """Extracts the category name and appends it to book data."""

    anchor = soup.find_all("a")
    book_data.append(anchor[3].text)


def extract_rating(soup, book_data):
    """Extracts the book's rating and appends it to book data."""

    p_rating = soup.find("p", class_="star-rating")
    rating = p_rating["class"][1]
    rating = transform_rating(rating)  # Convert text rating to integer
    book_data.append(rating)


def extract_url_img(soup, book_data, base_url):
    """Extracts the image URL and appends it to book data."""

    path_img = soup.find("img")
    # Returns full cover image URL
    book_data.append(base_url + path_img["src"][5:])


def transform_stock(text_stock):
    """Extracts the stock quantity as an integer from a given text."""

    # Search for the first sequence of digits in the string
    stock = search("(\\d+)", text_stock)
    # Convert the digits to an integer and returns it
    return int(stock.group(1))


def transform_rating(text_rating):
    """Converts a rating note in words to an integer."""

    match text_rating:
        case "One":
            return 1
        case "Two":
            return 2
        case "Three":
            return 3
        case "Four":
            return 4
        case "Five":
            return 5
        case _:
            return "Erreur : Rating invalide"


def create_scrap_directory():
    """Creates a timestamped directory for storing scraped data and image."""

    current_date = date.today()
    # Converts date in a string
    str_current_date = current_date.strftime("%d-%m-%Y")
    directory_name = "books_to_scrape_" + str_current_date

    if not os.path.exists(directory_name):
        os.mkdir(directory_name)
        print('Création du dossier "' + directory_name + '"')

    return directory_name


def create_category_directory(category_name, parent_directory):
    """Creates a folder named after the category and returns its path."""

    category_image_path = parent_directory + "/" + category_name + "_image"

    if not os.path.exists(category_image_path):
        os.mkdir(category_image_path)

    return category_image_path


def get_page(page_url):
    """Fetches and parses page content from a URL."""

    page = requests.get(page_url, timeout=10)

    if page.status_code == 200:  # If the request is successful
        soup = BeautifulSoup(page.content, "html.parser")
        return soup

    print(f"Erreur {page.status_code} lors de la requête de : {page_url}")


def get_categories(soup):
    """Fetches the list of categories from a page content"""

    ul_category = soup.find_all("ul")[2]
    li_category = ul_category.find_all("li")
    return li_category


def get_category_name(category_url):
    """Fetches the category name from its URL"""

    # Extract the part before the last "/"
    category_name_part = category_url.rsplit("/", 2)[1]
    # Extract the part before the first "_"
    category_name = category_name_part.split("_", 1)[0]
    return category_name


def get_book_title(book_url):
    """Fetches the book title from its URL"""

    # Extract the part before the last "/"
    book_title = book_url.rsplit("/", 2)[1]
    # Extract the part before the last "_"
    book_title = book_title.rsplit("_", 1)[0]
    return book_title


def get_books_url(category_url, base_url):
    """Fetches all books URL from a category and adds them to a list"""

    soup = get_page(category_url)

    books_url = []
    category_page_n = 1

    get_local_books_url(soup, books_url, base_url)

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

        soup = get_page(category_url)  # Load the next page

        get_local_books_url(soup, books_url, base_url)

    return books_url


def get_local_books_url(soup, books_url, base_url):
    """Fetches books URL from a category page and adds them to a list"""

    for h3 in soup.find_all("h3"):
        book_url = base_url + "/catalogue/" + (h3.find("a")["href"][9:])
        books_url.append(book_url)
