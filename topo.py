#!/usr/bin/python2
# -*- coding: utf-8 -*-
"""
# About  : Multi-layer grid network with square topo of hosts in each layer.
"""

import random
import re
from math import log

from mininet.topo import Topo


####################
#  Util Functions  #
####################

def rand_byte():
    """Generater a random byte"""
    return hex(random.randint(0, 255))[2:]


def make_mac(host_index):
    """Make MAC address for a host

    Args:
        host_index (int): index number of host
    """
    return rand_byte() + ":" + rand_byte() + ":" +\
        rand_byte() + ":00:00:" + hex(host_index)[2:]


def make_dpid(switch_index):
    """Make DPID for SDN switch

    Args:
        switch_index (int): index number of switch
    """
    mac_addr = make_mac(switch_index)
    dp_id = "".join(re.findall(r'[a-f0-9]+', mac_addr))
    return "0" * (12 - len(dp_id)) + dp_id


def make_ip(host_index, ip_class='B'):
    """Make IP address for a host

    Args:
        host_index (int): index number of host
        ip_class (str): class of ip addr, 'B' or 'C'
    """
    # B class ip, net-addr 172.16.0.0
    if ip_class == 'B':
        if host_index <= 0:
            raise ValueError('host number should greater than 0')
        elif host_index <= 255:
            host_ip = '172.16.0.' + str(host_index)
        elif host_index <= 65534:
            host_ip = '172.16.' + str(int(host_index / 256)) + '.'\
                + str(host_index - 256 * int(host_index / 256))
        else:
            raise ValueError('B class IP support maximal 65534 hosts')

    # C class ip, net-addr 192.168.36.0
    if ip_class == 'C':
        if host_index <= 0:
            raise ValueError('host number should greater than 0')
        elif host_index <= 254:
            host_ip = '192.168.36.' + str(host_index)
        else:
            raise ValueError('C class IP support maximal 254 hosts')

    return host_ip


##############
#  Topology  #
##############

class MultilayerGrid(Topo):
    """Multi-layer grid network with square topo of hosts in each layer."""

    def __init__(self, width=3, layer_num=3, **args):
        """Init function for FatTreeBinary class."""

        Topo.__init__(self, **args)

        self.h_index = 1
        self.s_index = 1

        # Only switches should be accessed
        # Each value is a list of switches in one layer.
        self.s_dict = {}

        # Create topology
        self._create_layer(1, 3, 3)

    def _create_layer(self, layer_num, row_num, col_num):
        """Create a single layer of nodes

        MARK: Link parameters are hard coded.
        """
        ip_tpl = '10.%d.%d.%d'
        host_tpl = 'h%d%d%d'
        switch_tpl = 's%d%d%d'
        switch_lt = []  # a list of all switches
        # Create all hosts and switches, also connections between them
        for row in range(1, row_num + 1):
            for col in range(1, col_num + 1):
                new_host = self.addHost(
                    host_tpl % (layer_num, row, col),
                    ip=ip_tpl % (layer_num, row, col),
                    mac=make_mac(self.h_index + 1))
                self.h_index += 1
                new_switch = self.addSwitch(
                    switch_tpl % (layer_num, row, col),
                    **dict(listenPort=(13000 + self.s_index - 1))
                )
                self.addLink(new_host, new_switch, bw=1, delay='1ms')
                self.s_index += 1
                switch_lt.append(new_switch)
        self.s_dict[layer_num] = switch_lt

        # Add links between switches, with circles
        # for i in range(0, 9, 3):
            # self.addLink(switch_lt[i], switch_lt[i + 1], bw=1, delay='1ms')
            # self.addLink(switch_lt[i + 1], switch_lt[i + 2], bw=1, delay='1ms')
            # self.addLink(switch_lt[i], switch_lt[i + 2], bw=1, delay='1ms')
        # for i in range(3):
            # self.addLink(switch_lt[i], switch_lt[i + 3], bw=1, delay='1ms')
            # self.addLink(switch_lt[i + 3], switch_lt[i + 6], bw=1, delay='1ms')
            # self.addLink(switch_lt[i], switch_lt[i + 6], bw=1, delay='1ms')

        self.addLink(switch_lt[0], switch_lt[1], bw=1, delay='1ms')

    def _create_layer_connection(self, s_layer, d_layer, conn_num):
        """Create conn_num of connections between s_layer and d_layer
        """
        pass

    def switch_names(self):
        """Get a list of names for all switches"""
        return ['s' + str(i + 1)
                for i in range(len(self.switches()))]

    def node_names(self):
        """Get a list of names for all nodes"""
        return self.hosts() + self.switch_names()
