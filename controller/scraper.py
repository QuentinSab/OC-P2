from views.scraper import ScraperView
from model.scraper import ScraperModel


class ScraperController:
    def __init__(self):
        self.view = ScraperView()
        self.model = ScraperModel()

    def execution(self):
        target = self.view.choose_target_to_scrap()
        self.model.get_base_url(target)
        directory_name = self.model.create_scrap_directory()

        match self.model.find_target_size(target):
            case "site":
                self.scrape_site(directory_name)
            case "category":
                self.scrape_category(target, directory_name)
            case "book":
                self.scrape_book(target, directory_name)

        self.view.end_message()

    def scrape_site(self, directory_name):
        categories_url = self.model.get_categories_url()
        for category_url in categories_url:
            self.scrape_category(category_url, directory_name)
            self.view.show_scraping_progress()

    def scrape_category(self, category_url, directory_name):
        books_url = self.model.get_books_url(category_url)
        category_name = self.model.get_category_name(category_url)

        category_image_path = self.model.create_category_directory(
            category_name, directory_name
        )
        books = []

        for book_url in books_url:
            book = self.model.extract_book_data(book_url)
            books.append(book)
            self.model.extract_image(book.image_url, book.title, category_image_path)

        self.model.write_csv(books, directory_name, category_name)

    def scrape_book(self, book_url, directory_name):
        book = self.model.extract_book_data(book_url)
        self.model.write_csv([book], directory_name, book.title)
        self.model.extract_image(book.image_url, book.title, directory_name)
