"""
This module represents the Marketplace.

Computer Systems Architecture Course
Assignment 1
March 2021
"""

from threading import currentThread, Lock

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

        # dictionar care pentru fiecare cos retine produsele achitionate producatorul respectiv
        self.carts = {}
        self.num_carts = 0

        self.producer_reg = Lock()
        self.cart_reg = Lock()
        self.print_res = Lock()



    def register_producer(self):
        """
        Returns an id for the producer that calls this.
        """
        curr_producer_id = -1

        with self.producer_reg:
            curr_producer_id = self.num_producers
            self.producers[self.num_producers] = []
            self.num_producers += 1


        return curr_producer_id

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

        curr_cart_id = -1

        with self.cart_reg:
            curr_cart_id = self.num_carts
            self.carts[self.num_carts] = []
            self.num_carts += 1

        return curr_cart_id

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

        with self.print_res:
            for elem in self.carts[cart_id]:
                thread_name = currentThread().getName()
                product = elem[0]
                print(f"{thread_name} bought {product}")
                bought_products.append(elem[0])

        return bought_products
