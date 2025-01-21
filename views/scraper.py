class ScraperView:
    def choose_target_to_scrap(self):
        print("Entrez l'url de la cible à extraire.")
        target = input()
        return target

    def show_scraping_progress(self):
        print("Categorie extraite.")

    def end_message(self):
        print("Extraction terminée.")
