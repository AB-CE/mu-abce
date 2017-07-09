# -*- coding: utf-8 -*-

"""
The :py:class:`abce.Agent` class is the basic class for creating your agents.
It automatically handles the possession of goods of an agent. In order to
produce/transforme goods you also need to subclass the :py:class:`abce.Firm` or
to create a consumer the :py:class:`abce.Household`.

For detailed documentation on:

Trading, see :doc:`Trade`

Logging and data creation, see :doc:`Database`.

Messaging between agents, see :doc:`Messaging`.
"""
from collections import OrderedDict, defaultdict
from .trade import Trade
from .messaging import Messaging
import random
from pprint import pprint
import datetime
from .inventory import Inventory


class DummyContracts:
    def step(self, round):
        pass


class Agent(Trade, Messaging):
    def __init__(self, id, group, random_seed):
        """ Do not overwrite __init__ instead use a method called init instead.
        init is called whenever the agent are build.
        """
        self.id = id
        """ self.id returns the agents id READ ONLY"""
        self._name = (group, id)
        """ self.name returns the agents name, which is the group name and the
        id seperated by '_' e.G. "household_12" READ ONLY!
        """
        self.name_without_colon = '%s_%i' % (group, id)
        self.group = group
        """ self.group returns the agents group or type READ ONLY! """

        self._out = [[] for _ in range(1 + 1)]

        self._haves = Inventory(self._name)
        self._haves['money'] = 0
        self._msgs = {}

        self.given_offers = OrderedDict()
        self._open_offers = defaultdict(dict)
        self._polled_offers = {}
        self._offer_count = 0
        self._reject_offers_retrieved_end_subround = []

        self.time = None
        """ self.time, contains the time set with simulation.time(time) """
        self._resources = []

        random.seed(random_seed)

        try:
            self._add_contracts_list()
        except AttributeError:
            self.contracts = DummyContracts()

    def init(self, parameters, agent_parameters):
        """ This method is called when the agents are build.
        It can be overwritten by the user, to initialize the agents.
        parameters and agent_parameters are the parameters given in
        :py:meth:`abce.Simulation.build_agents`
        """
        pass

    def date(self):
        """ If ABCE is run in calendar mode (via
        :py:meth:`abce.Simulation.declare_calendar`), date shows the current
        date.::

        self.date().day
        self.date().month
        self.date().year
        self.date().weekday()  # the weekday as a number Monday being 0
        self.date().toordinal()  #

        The date works like python's
        `date object
        <https://docs.python.org/2/library/datetime.html#date-objects>`_
        """
        try:
            return datetime.date.fromordinal(self.time)
        except ValueError:
            raise ValueError(
                "you need to run ABCE in calendar mode, use "
                "simulation.declare_calendar(2000, 1, 1)")

    def possession(self, good):
        return self._haves.possession(good)

    def possessions(self):
        return self._haves.possessions()

    def _offer_counter(self):
        self._offer_count += 1
        return hash((self.name, self._offer_count))

    def step(self, time):
        for offer in list(self.given_offers.values()):
            if offer.made < self.time:
                print("in agent %s this offers have not been retrieved:" %
                      self.name_without_colon)
                for offer in list(self.given_offers.values()):
                    if offer.made < self.time:
                        print(offer.__repr__())
                raise Exception('%s_%i: There are offers have been made before'
                                'last round and not been retrieved in this'
                                'round get_offer(.)' % (self.group, self.id))

        self._haves.step()
        self.contracts.step(self.time)

        if sum([len(offers) for offers in list(self._open_offers.values())]):
            pprint(dict(self._open_offers))
            raise Exception('%s_%i: There are offers an agent send that have '
                            'not been retrieved in this round get_offer(.)' %
                            (self.group, self.id))

        if sum([len(offers) for offers in list(self._msgs.values())]):
            pprint(dict(self._msgs))
            raise Exception('%s_%i: There are messages an agent send that have '
                            'not been retrieved in this round get_messages(.)' %
                            (self.group, self.id))

        for ingredient, units, product in self._resources:
            self._haves.create(product, self.possession(ingredient) * units)

        self.time = time

    def create(self, good, quantity):
        self._haves.create(good, quantity)

    def destroy(self, good, quantity=None):
        self._haves.destroy(good, quantity)

    def _execute(self, command, incomming_messages):
        self._out = [[] for _ in range(self.num_managers + 2)]
        self._clearing__end_of_subround(incomming_messages)
        self._out[-2] = (getattr(self, command)(), )
        self._reject_polled_but_not_accepted_offers()

        return self._out

    def _register_resource(self, resource, units, product):
        self._resources.append((resource, units, product))

    def _send(self, receiver_group, receiver_id, typ, msg):
        self._out[receiver_id % self.num_managers].append(
            (receiver_group, receiver_id, (typ, msg)))

    def create_agent(self, AgentClass, group_name,
                     parameters=None, agent_parameters=None):
        self._out[-1].append(('add', (AgentClass, group_name,
                                      parameters, agent_parameters)))

    def delete_agent(self, group_name, id, quite=True):
        self._out[-1].append(('delete', (group_name, id, quite)))
