"""
This module represents the Marketplace.

Computer Systems Architecture Course
Assignment 1
March 2021
"""

from threading import currentThread

class Marketplace:
    """
    Class that represents the Marketplace. It's the central part of the implementation.
    The producers and consumers use its methods concurrently.
    """
    def __init__(self, queue_size_per_producer):
        """
        Constructor

        :type queue_size_per_producer: Int
        :param queue_size_per_producer: the maximum size of a queue associated with each producer
        """

        self.queue_size_per_producer = queue_size_per_producer

        self.producers = {} # dictionar in care pentru fiecare producator retine produsele sale
        self.num_producers = 0

        self.carts = {} # dictionar care pentru fiecare cos retine produsele achitionate producatorul respectiv
        self.num_carts = 0


    def register_producer(self):
        """
        Returns an id for the producer that calls this.
        """

        self.producers[self.num_producers] = []
        self.num_producers += 1

        return self.num_producers - 1

    def publish(self, producer_id, product):
        """
        Adds the product provided by the producer to the marketplace

        :type producer_id: String
        :param producer_id: producer id

        :type product: Product
        :param product: the Product that will be published in the Marketplace

        :returns True or False. If the caller receives False, it should wait and then try again.
        """

        if len(self.producers[producer_id]) == self.queue_size_per_producer:
            return False

        self.producers[producer_id].append(product)

        return True


    def new_cart(self):
        """
        Creates a new cart for the consumer

        :returns an int representing the cart_id
        """
        self.carts[self.num_carts] = []
        self.num_carts += 1
        return self.num_carts - 1

    def add_to_cart(self, cart_id, product):
        """
        Adds a product to the given cart. The method returns

        :type cart_id: Int
        :param cart_id: id cart

        :type product: Product
        :param product: the product to add to cart

        :returns True or False. If the caller receives False, it should wait and then try again
        """

        for p_id in range(self.num_producers):
            if product in self.producers[p_id]:
                tmp = (product, p_id)
                self.carts[cart_id].append(tmp)
                self.producers[p_id].remove(product)

                return True

        return False

    def remove_from_cart(self, cart_id, product):
        """
        Removes a product from cart.

        :type cart_id: Int
        :param cart_id: id cart

        :type product: Product
        :param product: the product to remove from cart
        """
        p_id = -1
        for elem in self.carts[cart_id]:
            if product == elem[0]:
                self.producers[elem[1]].append(product)
                p_id = elem[1]
                break
        self.carts[cart_id].remove((product, p_id))

    def place_order(self, cart_id):
        """
        Return a list with all the products in the cart.

        :type cart_id: Int
        :param cart_id: id cart
        """

        bought_products = []

        for (product, p_id) in self.carts[cart_id]:
            print("{} bought {}".format(currentThread().getName(), product))
            bought_products.append(product)

        return bought_products
