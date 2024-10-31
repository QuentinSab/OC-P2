from etl_functions import *

soup = extract_page("http://books.toscrape.com/index.html")

ul_category = soup.find_all("ul")[2]
li_category = ul_category.find_all("li")

for a_category in li_category:
    category_url = ("http://books.toscrape.com/" + a_category.find("a")["href"])
    
    category_nom_morceau = category_url.rsplit("/", 2)
    category_nom = category_nom_morceau[1]
    
    #category_nom = a_category.find("a").text
    
    print(category_nom)
    
    fichier_csv_nom = ("scrapped_books/" + category_nom + ".csv")
    
    extract_category_data(category_url, fichier_csv_nom)