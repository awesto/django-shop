class ProductNotAvailable(Exception):
    """
    The product being purchased isn't available anymore.
    """
    def __init__(self, product):
        self.product = product
        msg = "Product {} isn't available anymore."
        super().__init__(msg.format(product.product_code))
