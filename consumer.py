"""
This module represents the Consumer.

Computer Systems Architecture Course
Assignment 1
March 2021
"""

from threading import Thread
import time


class Consumer(Thread):
    """
    Class that represents a consumer.
    """

    def __init__(self, carts, marketplace, retry_wait_time, **kwargs):
        """
        Constructor.

        :type carts: List
        :param carts: a list of add and remove operations

        :type marketplace: Marketplace
        :param marketplace: a reference to the marketplace

        :type retry_wait_time: Time
        :param retry_wait_time: the number of seconds that a producer must wait
        until the Marketplace becomes available

        :type kwargs:
        :param kwargs: other arguments that are passed to the Thread's __init__()
        """
        Thread.__init__(self, **kwargs)
        self.carts = carts
        self.marketplace = marketplace
        self.retry_wait_time = retry_wait_time
        self.cart_id = self.marketplace.new_cart()

    def run(self):
        for cart in self.carts:
            cart_id = self.marketplace.new_cart()

            for operation in cart:
                op_type = operation['type']
                wanted_product = operation['product']
                wanted_quantity = operation['quantity']

                current_quantity = 0

                while current_quantity < wanted_quantity:

                    can_do_op = None

                    if op_type == "add":
                        can_do_op = self.marketplace.add_to_cart(cart_id, wanted_product)
                    elif op_type == "remove":
                        self.marketplace.remove_from_cart(cart_id, wanted_product)

                    if can_do_op == False:
                        time.sleep(self.retry_wait_time)
                    else:
                        current_quantity += 1

            self.marketplace.place_order(cart_id)


