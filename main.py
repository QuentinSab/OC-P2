# -*- coding: utf-8 -*-

import csv
import sys

from functions import *


BASE_URL = "http://books.toscrape.com"


def etl_site(directory_path):
    """Extracts data and cover images from all categories and store them at the specified path."""

    soup = get_page(BASE_URL + "/index.html")  # Load the main page

    for a_category in get_categories(soup):  # Iterate over each category

        category_url = (
            BASE_URL + "/" + a_category.find("a")["href"]  # Build category URL
        )
        etl_category(category_url, directory_path)  # Extract data for each category


def etl_category(category_url, directory_path):
    """Extracts data and cover images for a category and stores them at the specified path."""

    # Get the category name from URL
    category_name = get_category_name(category_url)
    # Create directory for images in the specified directory
    category_image_path = create_category_directory(category_name, directory_path)
    # Define CSV file path
    file_csv_path = directory_path + "/" + category_name + "_data.csv"

    # Extract and save data
    load_data(category_url, file_csv_path, category_image_path)


def load_data(url_to_extract, file_csv, image_path):
    """
    Loads data from a specified URL into a CSV file
    and downloads cover images to the specified path.
    """

    with open(file_csv, mode="w", newline="", encoding="utf-8") as fichier:

        csv_header = [
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

        writer = csv.writer(fichier)
        writer.writerow(csv_header)  # Write CSV header

        # Process if the URL points to a category page
        if (url_to_extract.rsplit("/", 3)[0]) == (BASE_URL + "/catalogue/category"):

            # Fetch and iterate over each book URL from the category
            for book_url in get_books_url(url_to_extract, BASE_URL):
                book_data = extract_book_data(book_url)
                writer.writerow(book_data)  # Write book data to CSV

                # Download the cover image
                download_image(book_url, book_data[9], image_path)

            print(f'Catégorie "{book_data[7]}" extraite avec succès.')

        # Process if the URL points to a single book page
        else:
            book_data = extract_book_data(url_to_extract)
            writer.writerow(book_data)

            # Download the cover image
            download_image(url_to_extract, book_data[9], image_path)

            print(f'Livre "{book_data[2]}" extrait avec succès.')


def download_image(book_url, image_url, image_path):
    """Downloads a book cover image and saves it to the specified path."""

    # Fetch image data
    img_data = requests.get(image_url, timeout=10).content
    # Generate file name from book title
    file_image_name = image_path + "/" + get_book_title(book_url) + ".jpg"

    # Save image data to a file in write mode
    with open(file_image_name, "wb") as img_file:
        img_file.write(img_data)


def extract_book_data(book_url):
    """Extracts and returns a list containing all data for a given book URL."""

    soup = get_page(book_url)  # Load the page content into a object
    book_data = []

    # Append each piece of book data to the list
    book_data.append(book_url)  # Book URL
    extract_upc(soup, book_data)  # Universal Product Code (UPC)
    extract_title(soup, book_data)  # Book title
    extract_price_incl_tax(soup, book_data)  # Price including tax
    extract_price_excl_tax(soup, book_data)  # Price excluding tax
    extract_stock(soup, book_data)  # Stock availability
    extract_description(soup, book_data)  # Book description
    extract_category_name(soup, book_data)  # Category name
    extract_rating(soup, book_data)  # Review rating
    extract_url_img(soup, book_data, BASE_URL)  # Cover image URL

    return book_data


def main():
    """Extracts data based on given system argument: full site, category, or single book."""

    # Create directory for extracted data
    scrap_directory = create_scrap_directory()

    # Full site extraction if no argument is provided
    if len(sys.argv) < 2:
        print(
            f'Extraction de "{BASE_URL}" dans le dossier "{scrap_directory}" en cours ...'
        )
        etl_site(scrap_directory)
        sys.exit(1)

    # Partial extraction if one argument is provided
    elif len(sys.argv) == 2:

        # Extract a category if the system argument is a category URL
        if (sys.argv[1].rsplit("/", 3)[0]) == (BASE_URL + "/catalogue/category"):
            print(
                f'Extraction de "{sys.argv[1]}" dans '
                f'le dossier "{scrap_directory}" en cours ...'
            )
            etl_category(sys.argv[1], scrap_directory)
            sys.exit(1)

        # Extract a single book if it's not a category URL
        else:
            image_name = get_book_title(sys.argv[1])
            file_csv_name = scrap_directory + "/" + image_name + "_data.csv"
            load_data(sys.argv[1], file_csv_name, scrap_directory)
            sys.exit(1)


if __name__ == "__main__":
    main()
