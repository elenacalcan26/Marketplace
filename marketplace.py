"""
This module represents the Marketplace.

Computer Systems Architecture Course
Assignment 1
March 2021
"""

from threading import currentThread, Lock
import unittest

class TestMarketplace(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        print('SetUpClass')

    def setUp(self):
        self.marketplace = Marketplace(15)
        self.prod1 = {  "product_type": "Coffee",
                        "name": "Indonezia",
                        "acidity": 5.05,
                        "roast_level": "MEDIUM",
                        "price": 1
                    }

        self.prod2 = {  "product_type": "Tea",
                        "name": "Linden",
                        "type": "Herbal",
                        "price": 9
                    }

    def test_register_producer(self):
        print('\nTest Register Producer\n')
        num_producers = 3
        res = -1

        for new_id in range(num_producers):
            res = self.marketplace.register_producer()
            self.assertEqual(res, new_id)

    def test_publish(self):
        print('\nTest Publish\n')
        pid = self.marketplace.register_producer()

        for i in range(self.marketplace.queue_size_per_producer):
            res = self.marketplace.publish(0, self.prod1)
            self.assertEqual(res, True)

        res = self.marketplace.publish(0, self.prod2)
        self.assertEqual(res, False)


    def test_new_cart(self):
        print('\nTest New Cart\n')
        num_carts = 3
        tmp = -1

        for i in range(num_carts):
            tmp = self.marketplace.new_cart()
            self.assertEqual(tmp, i)

        self.assertEqual(tmp + 1, num_carts)


    def test_add_to_cart(self):
        print('\nTest Add\n')
        pid = self.marketplace.register_producer()
        cart_id = self.marketplace.new_cart()

        for _ in range(2):
            self.marketplace.publish(pid, self.prod2)

        self.assertTrue(self.marketplace.add_to_cart(cart_id, self.prod2))
        self.assertFalse(self.marketplace.add_to_cart(cart_id, self.prod1))


    def test_remove_from_cart(self):
        print('\nTest Remove\n')
        pid = self.marketplace.register_producer()
        cart_id = self.marketplace.new_cart()
        self.marketplace.producers[pid].extend([self.prod1, self.prod2, self.prod2])
        self.marketplace.carts[cart_id].extend([(self.prod1, pid), (self.prod2, pid)])

        prod1_occurences_prod = self.marketplace.producers[pid].count(self.prod1)
        prod1_occurences_cart = self.marketplace.carts[cart_id].count((self.prod1, pid))

        self.marketplace.remove_from_cart(cart_id, self.prod1)

        new_prod1_occurences_prod = self.marketplace.producers[pid].count(self.prod1)
        new_prod1_occurences_cart = self.marketplace.carts[cart_id].count((self.prod1, pid))

        self.assertGreater(new_prod1_occurences_prod, prod1_occurences_prod)
        self.assertLess(new_prod1_occurences_cart, prod1_occurences_cart)


    def test_place_order(self):
        print('\nTest Place Order\n')
        pid = self.marketplace.register_producer()
        cart_id = self.marketplace.new_cart()
        expected_cart = [self.prod1, self.prod1, self.prod2]

        for _ in range(0, self.marketplace.queue_size_per_producer, 3):
            self.marketplace.publish(pid, self.prod2)
            self.marketplace.publish(pid, self.prod2)
            self.marketplace.publish(pid, self.prod1)

        self.marketplace.add_to_cart(cart_id, self.prod2)

        for _ in  range(3):
            self.marketplace.add_to_cart(cart_id, self.prod1)

        self.marketplace.remove_from_cart(cart_id, self.prod1)

        res = self.marketplace.place_order(cart_id)

        count_expected = expected_cart.count(self.prod1)
        count_res = res.count(self.prod1)

        self.assertEqual(count_expected, count_res)

        count_expected = expected_cart.count(self.prod2)
        count_res = res.count(self.prod2)

        self.assertEqual(count_expected, count_res)


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

        # dictionar care pentru fiecare cos retine produsele achizitionate de la producatorul respectiv
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
