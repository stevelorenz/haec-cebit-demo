#!/usr/bin/python2
# -*- coding: utf-8 -*-
"""
# About  : Topology for HAEC demo in Cebit
           Multi-layer grid network with square topology of hosts in each layer.

# Contact: xianglinks@gmail.com
"""

import logging
import random
from random import randint

from mininet.topo import Topo

logger = logging.getLogger(__name__)


####################
#  Topology Class  #
####################

class MultilayerGrid(Topo):
    """Multi-layer grid network with square topology of hosts in each layer.

    MARK: Currently hard coded with 3 x 3 grid.
    """

    def __init__(self, **args):
        Topo.__init__(self, **args)
        # Dict of switches, each value is a list of switches in the key-layer
        self.switch_dict = {}
        self._build_topo()
        logger.info('*** HAEC topology created successfully.\n')

    def _build_topo(self):
        """Build the HAEC topology."""
        # --------------------------------------------------
        logger.info('*** Create 3 layers...\n')
        for layer in range(1, 4):
            ip_tpl = '10.%d.%d.%d'
            host_tpl = 'h%d%d%d'
            switch_tpl = 's%d%d%d'
            switch_lt = []
            logger.debug('*** Adding hosts and switches.\n')
            # Create all hosts and switches, also connections between them
            # Index start from 1
            for row in range(1, 4):
                for col in range(1, 4):
                    host_name = host_tpl % (layer, row, col)
                    new_host = self.addHost(
                        host_name,
                        ip=ip_tpl % (layer, row, col)
                    )
                    switch_name = switch_tpl % (layer, row, col)
                    new_switch = self.addSwitch(
                        switch_name,
                        # MARK: The supported length of DPID for MaxiNet is 12
                        dpid="000000000%d%d%d" % (layer, row, col)
                    )
                    # Add link between host and switches
                    # MARK: The link between hosts and switches MUST be added before links between switches.
                    # MARK: The interface name is used for routing. It MUST be given.
                    self.addLink(new_switch, new_host, bw=1,
                                 intfName1=switch_name + "-" + host_name,
                                 intfName2=host_name + "-" + switch_name)
                    switch_lt.append(new_switch)

            self.switch_dict[layer] = switch_lt

            # Add links between switches, with circles
            for i in range(0, 9, 3):
                self.addLink(switch_lt[i], switch_lt[i + 1], bw=1,
                             intfName1=switch_lt[i] + '-' + switch_lt[i + 1],
                             intfName2=switch_lt[i + 1] + '-' + switch_lt[i])

                self.addLink(switch_lt[i + 1], switch_lt[i + 2], bw=1,
                             intfName1=switch_lt[i + 1] + '-' + switch_lt[i + 2],
                             intfName2=switch_lt[i + 2] + '-' + switch_lt[i + 1])

                self.addLink(switch_lt[i], switch_lt[i + 2], bw=1,
                             intfName1=switch_lt[i] + '-' + switch_lt[i + 2],
                             intfName2=switch_lt[i + 2] + '-' + switch_lt[i])

            for i in range(3):
                self.addLink(switch_lt[i], switch_lt[i + 3], bw=1,
                             intfName1=switch_lt[i] + '-' + switch_lt[i + 3],
                             intfName2=switch_lt[i + 3] + '-' + switch_lt[i])

                self.addLink(switch_lt[i + 3], switch_lt[i + 6], bw=1,
                             intfName1=switch_lt[i + 3] + '-' + switch_lt[i + 6],
                             intfName2=switch_lt[i + 6] + '-' + switch_lt[i + 3])

                self.addLink(switch_lt[i], switch_lt[i + 6], bw=1,
                             intfName1=switch_lt[i] + '-' + switch_lt[i + 6],
                             intfName2=switch_lt[i + 6] + '-' + switch_lt[i])
        # --------------------------------------------------

        # --------------------------------------------------
        logger.info('Connect 3 layers...\n')
        # TODO: Connect them properly
        # MARK: All node in each layer MUST have at least one direct connection to all other layers.

        # switch_lt = []
        # for layer in range(1, 4):
            # switch_lt.extend(self.switch_dict[layer])

        links = {}
        for i in range(3):
            for j in range(3):
                for k in range(3):
                    # select current node
                    sname = 's%d%d%d' % (i + 1, j + 1, k + 1)
                    # randomly select other nodes
                    for n in ['s%d%d%d' % (1 + (i + 1) % 3, randint(1, 3), randint(1, 3)), 's%d%d%d' % (1 + (i + 4) % 3, randint(1, 3), randint(1, 3))]:
                        if not n + "-" + sname in links:
                            links[sname + "-" + n] = True
                            links[n + "-" + sname] = True
                            self.addLink(sname, n, intfName1=sname + "-" + n, intfName2=n + "-" + sname, bw=1)
        # --------------------------------------------------
