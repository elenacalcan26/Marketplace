"""
This module represents the Marketplace.

Computer Systems Architecture Course
Assignment 1
March 2021
"""

from threading import currentThread, Lock
import time
import unittest
import logging
from logging.handlers import RotatingFileHandler

logging.basicConfig(
        handlers=[RotatingFileHandler('./marketplace.log', maxBytes=100000, backupCount=10,
                mode='a')],
        level=logging.INFO,
        format="[%(asctime)s] %(levelname)s %(message)s")
logging.Formatter.converter = time.gmtime
logger = logging.getLogger()

class TestMarketplace(unittest.TestCase):

    """
    Clasa folosita pentru unittesting. Sunt testate functille din clasa Marketplace
    """

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
        """
        Test register_producer()
        """
        print('\nTest Register Producer\n')
        num_producers = 3
        res = -1

        for new_id in range(num_producers):
            res = self.marketplace.register_producer()
            self.assertEqual(res, new_id)

    def test_publish(self):
        """
        Test publish()
        """

        print('\nTest Publish\n')
        pid = self.marketplace.register_producer()

        for _ in range(self.marketplace.queue_size_per_producer):
            res = self.marketplace.publish(pid, self.prod1)
            self.assertEqual(res, True)

        res = self.marketplace.publish(pid, self.prod2)
        self.assertEqual(res, False)


    def test_new_cart(self):
        """
        Test new_cart()
        """
        print('\nTest New Cart\n')
        num_carts = 3
        tmp = -1

        for i in range(num_carts):
            tmp = self.marketplace.new_cart()
            self.assertEqual(tmp, i)

        self.assertEqual(tmp + 1, num_carts)


    def test_add_to_cart(self):
        """
        Test add_to_cart()
        """
        print('\nTest Add\n')
        pid = self.marketplace.register_producer()
        cart_id = self.marketplace.new_cart()

        for _ in range(2):
            self.marketplace.publish(pid, self.prod2)

        self.assertTrue(self.marketplace.add_to_cart(cart_id, self.prod2))
        self.assertFalse(self.marketplace.add_to_cart(cart_id, self.prod1))


    def test_remove_from_cart(self):
        """
        Test remove_from_cart()
        """
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
        """
        Test place_order()
        """
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
        self.num_producers = 0 # numarul tottal de producatori inregistrati

        # dictionar ce retine pentru fiecare cos produsele achizitionate de la producatorul aferent
        self.carts = {}
        self.num_carts = 0 # numarul de cosuri inregistrate

        # lock-uri folosite pentru delimitarea zonelor critice
        self.producer_reg = Lock()
        self.cart_reg = Lock()
        self.print_res = Lock()
        self.add_prod = Lock()
        self.remove_prod = Lock()

        logging.info("Set up Marketplace with queue_size_per_producer = %s",
                    queue_size_per_producer)


    def register_producer(self):
        """
        Returns an id for the producer that calls this.
        """

        # ID-urile producatorilor se asigneaza in ordine consecutiva.
        # Cand un producator este inregistrat, se face o mapare intre id-ul lui
        # si o lista goala, urmand ca aceasta sa fie populate cu produsele sale.

        curr_producer_id = -1

        with self.producer_reg:
            curr_producer_id = self.num_producers
            self.producers[self.num_producers] = []
            self.num_producers += 1

            logging.info('Producer registered with id = %s', curr_producer_id)

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

        # Produsul publicat este adaugat in lista producatorului. Produsul este adaugat doar
        # atunci cand lista de produse a producatorului nu este plina.

        logging.info("Producer with id = %s wants to publish product = %s", producer_id, product)

        if len(self.producers[producer_id]) == self.queue_size_per_producer:
            logging.info("Producer with id = %s can't publish %s", producer_id, product)
            return False

        self.producers[producer_id].append(product)
        logging.info("Producer with id = %s published product = %s", producer_id, product)

        return True


    def new_cart(self):
        """
        Creates a new cart for the consumer

        :returns an int representing the cart_id
        """

        # ID-urile cosurilor sunt asignate in mod consecutiv.
        # Cand se inregistreaza un nou cos, se face o mapare intre id-ul cosului
        # si o lista de tupluri ce retine tupluri formate din produsul adaugat in cos
        # si id-ul producatorului de unde l-a luat.

        curr_cart_id = -1

        with self.cart_reg:
            curr_cart_id = self.num_carts
            self.carts[self.num_carts] = []
            self.num_carts += 1

        logging.info("Consumer has cart registered cart with id = %s ", curr_cart_id)

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

        # La adaugarea unui produs intr-un cos, se cauta primul producator ce are produsul
        # dorit. Produsul este sters din lista de produse a producatorului, devenind astfel
        # indisponibil, iar in cos se adauga un tuplu format din produs si id-ul producatorului.

        with self.add_prod:
            logging.info("Consumer with cart_id = %s wants to add product = %s",
                        cart_id, product)

            for p_id in range(self.num_producers):

                if product in self.producers[p_id]:
                    logging.info('''Consumer with cart_id = %s bought product = %s from producer
                                with id = %s''', cart_id, product, p_id)

                    self.producers[p_id].remove(product)
                    self.carts[cart_id].append((product, p_id))

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

        # Se cauta tuplul ce contine produsul in lista corespunzatoare cosului.
        # Produsul este adaugat inapoi in lista producatorului cu id-ul cu care
        # s-a format tuplul, astfel produsul devine din nou disponibil.
        # Tuplul ce a fost format este sters din lista cosului respectiv.

        with self.remove_prod:

            logging.info("Consumer  with cart_id = %s wants to remove product = %s",
                        cart_id, product)

            p_id = -1
            for elem in self.carts[cart_id]:
                if product == elem[0]:
                    self.producers[elem[1]].append(product)
                    p_id = elem[1]
                    logging.info('''Consumer with cart_id = %s removed product = %s
                                from producer id = %s''', cart_id, product, p_id)
                    break
            self.carts[cart_id].remove((product, p_id))


    def place_order(self, cart_id):
        """
        Return a list with all the products in the cart.

        :type cart_id: Int
        :param cart_id: id cart
        """

        # Se parcurg produsele consumatorului ce se afla in cos si se
        # afiseaza mesajul de output.

        bought_products = []

        with self.print_res:
            logging.info("Consumer with cart_id = %s place order", cart_id)

            for elem in self.carts[cart_id]:
                thread_name = currentThread().getName()
                product = elem[0]
                print(f"{thread_name} bought {product}")
                bought_products.append(elem[0])
            logging.info("Consumer with cart_id = %s has products %s",
                        cart_id, str(bought_products))

        return bought_products
