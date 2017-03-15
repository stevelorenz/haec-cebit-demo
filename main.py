#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# About  : Run demon
"""

from MaxiNet.Frontend import maxinet
from topo import MultilayerGrid


def main():
    """Main function

    For each test function, two important objects:
        1. MaxiNet.Cluster: cluster of workers
        2. Mininet.Topo: to be tested topology
    """

    # Setup MaxiNet cluster
    # Without arguments, returns all the registered Workers
    cluster = maxinet.Cluster()
    topo = MultilayerGrid()

    # Setup MaxiNet experiment
    exp = maxinet.Experiment(cluster, topo)
    exp.setup()

    # Into CLI mode, for debugging
    exp.CLI(locals(), globals())
    exp.stop()


def run_demon():
    """Run demon operations."""
    pass


def ping_all(exp, host_lt, ping_num=3):
    """Simple ping all host."""
    for sender in host_lt:
        for recv in host_lt:
            recv_ip = exp.get_node(recv).IP()
            exp.get_node(sender).cmd("ping -c %d %s" % (ping_num, recv_ip))

if __name__ == "__main__":
    main()
