class Book:
    def __init__(
        self,
        url,
        upc,
        title,
        price_incl_tax,
        price_excl_tax,
        stock,
        description,
        category,
        rating,
        image_url,
    ):

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
