""" This file defines the :exc:`tools.NotEnoughGoods` """
from __future__ import division
from builtins import str


class NotEnoughGoods(Exception):
    """ Methods raise this exception when the agent has less goods than needed

    These functions (self.produce, self.offer, self.sell, self.buy)
    should be encapsulated by a try except block::

     try:
        self.produce(...)
     except NotEnoughGoods:
        alternative_statements()

    """

    def __init__(self, _agent_name, good, amount_missing):
        self.good = good
        self.amount_missing = amount_missing
        self.name = _agent_name
        Exception.__init__(self)

    def __str__(self):
        return repr(str(self.name) + " " + str(self.amount_missing) + " of good '" + self.good + "' missing")
