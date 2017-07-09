from __future__ import division
import abce
from abce import Simulation

simulation_parameters = {'name': 'name',
                         'rounds': 50,
                         'firms': 5,
                         'households': 5}


class Firm(abce.Agent):
    def init(self, param, agent_params):
        pass

    def one(self):
        pass

    def three(self):
        pass


class Household(abce.Agent):
    def init(self, param, agent_params):
        pass

    def two(self):
        pass

    def three(self):
        pass


def main(simulation_parameters, rounds=20):
    simulation = Simulation('sim')

    firms = simulation.build_agents(Firm, 5)
    households = simulation.build_agents(Household, 5)

    allagents = firms + households
    for r in range(rounds):
        # round endowment
        # TODO wrap this
        for h in households:
            h.create('labor', 1)

        for f in firms:
            f.one()
        for h in households:
            h.two()
        for a in allagents:
            a.three()

        # perishable
        for h in households:
            if h.possession('labor') > 0:
                h.destroy('labor', 1)


if __name__ == '__main__':
    main(simulation_parameters)
