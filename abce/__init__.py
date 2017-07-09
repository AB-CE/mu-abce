# pylint: disable=W0212, C0111
""" The best way to start creating a simulation is by copying the start.py
file and other files from 'abce/template'.

To see how to create a simulation read :doc:`Walk_through`. In this module you
will find the explanation for the command.

This is a minimal template for a start.py::

    from agent import Agent
    from abce import *


    simulation = Simulation(name='ABCE')
    agents = simulation.build_agents(Agent, 'agent', 2)
    for round in simulation.next_round():
        agents.do('one')
        agents.do('two')
        agents.do('three')
    simulation.graphs()
"""
import datetime
import time
import random
from .agent import Agent, Trade
from collections import defaultdict, OrderedDict
from abce.exceptions import NotEnoughGoods


class Simulation(object):
    def __init__(self, name='abce', random_seed=None, processes=1):
        """
        """
        self._messages = {}
        self._resource_command_group = {}
        self.num_agents = 0
        self._build_first_run = True
        self.resource_endowment = defaultdict(list)
        self._start_round = 0
        self.round = int(self._start_round)

        self.messagess = [list() for _ in range(self.processes + 2)]

        self.clock = time.time()
        if random_seed is None or random_seed == 0:
            random_seed = self.clock
        random.seed(random_seed)

        self.sim_parameters = OrderedDict(
            {'name': name, 'random_seed': random_seed})

    def advance_round(self, time):
        print("\rRound" + str(time))
        for g in self.groups.values():
            for a in g:
                a.step()

    def __del__(self):
        self.finalize()

    def finalize(self):
        if self._db_started:
            self._db_started = False
            print()
            print(str("time only simulation %6.2f" %
                  (time.time() - self.clock)))

    def build_agents(self, AgentClass, number=1, group_name=None,
                     parameters={}, agent_parameters=None):
        self.number = number
        if group_name is None:
            group_name = AgentClass.__name__

        self.sim_parameters.update(parameters)

        agents = []
        for i in range(self.number):
            a = AgentClass(i, group_name, random.random())
            a.init(parameters, agent_parameters)
            agents.append(a)
        return agents
