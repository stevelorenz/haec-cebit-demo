#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# About  : Run demon
"""

import argparse
import logging
import sys

from MaxiNet.Frontend import maxinet
from topo import MultilayerGrid

logger = logging.getLogger(__name__)

def main():

    # Dict for static mapping
    # mapping = {"h1111": 0,
               # "h2": 0,
               # "h3": 1,
               # "h4": 1,
               # "s1": 0,
               # "s2": 0,
               # "s3": 1,
               # "s4": 1,
               # "s5": 0,
               # "s6": 1,
               # "s7": 1
               # }

    cluster = maxinet.Cluster()
    topo = MultilayerGrid()

    exp = maxinet.Experiment(cluster, topo)
    # exp = maxinet.Experiment(cluster, topo, nodemapping=mapping)
    exp.setup()

    if len(sys.argv) > 1:
        if sys.argv[1] == '-d':
            # Into the CLI mode, for debugging
            exp.CLI(locals(), globals())
            exp.stop()
    else:
        logger.info('*** Nothing happens!')


def run_demon():
    """Run demon operations.

    Each node should run ./iperf-server-client-demo script
    """
    pass


def ping_all(exp, host_lt, ping_num=3):
    """Simple ping all host."""
    for sender in host_lt:
        for recv in host_lt:
            recv_ip = exp.get_node(recv).IP()
            exp.get_node(sender).cmd("ping -c %d %s" % (ping_num, recv_ip))

if __name__ == "__main__":
    main()
