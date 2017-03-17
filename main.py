#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# About  : Setup and run HAEC demo.
# Contact: xianglinks@gmail.com
"""

import logging
import sys
import time

from MaxiNet.Frontend import maxinet
from topo import MultilayerGrid

logger = logging.getLogger(__name__)


###################
#  Main Function  #
###################

def main():

    # Dict for static mapping
    for i in range(3):
        for j in range(3):
            for k in range(3):
                pass

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

    # Create cluster and topology
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

    # Start Iperf script on all hosts.
    else:
        time.sleep(1)
        # Loop over all hosts
        for i in range(3):
            for j in range(3):
                for k in range(3):
                    hname = 'h%d%d%d' % (i + 1, j + 1, k + 1)
                    # Run go script at background
                    exp.get_node(hname).cmd("~/bin/iperf-server-client-demo-pc -min 30 -max 40 &")

    # Enter infinite loop
    try:
        while 1:
            time.sleep(10)
    except KeyboardInterrupt:
        print('KeyboardInterrupt detected!')
        exp.stop()

if __name__ == "__main__":
    main()
