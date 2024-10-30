from etl_functions import *

category_url = "http://books.toscrape.com/catalogue/category/books/mystery_3/index.html"

fichier_csv = "scrapped_books/mon_fichier.csv"

extract_category_data(category_url, fichier_csv)