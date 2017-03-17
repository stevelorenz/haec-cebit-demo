#!/usr/bin/python

"""
This example shows how to create an empty Mininet object
(without a topology object) and add nodes to it manually.
"""

from random import randint

from mininet.net import Mininet
from mininet.node import RemoteController, Controller, UserSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info

def haecnet():
    net = Mininet( controller=RemoteController )

    info( '*** Adding controller\n' )
    net.addController( 'c0' )

    info( '*** Adding hosts\n' )
    for i in range(3):
        for j in range(3):
            for k in range(3):
                name = 'h%d%d%d'%(i+1,j+1,k+1)
                host = net.addHost(name)
                #net[name].setIP("10.%d.%d.%d"%(i+1,j+1,k+1))

    info( '*** Adding switch\n' )
    for i in range(3):
        for j in range(3):
            for k in range(3):
                # dpid should match the id of the switch
                # the id of the switch should match the ip of the host
                net.addSwitch( 's%d%d%d'%(i+1,j+1,k+1), dpid="00000000%d%d%d"%(i+1, j+1, k+1))

    info( '*** Creating host links\n' )
    # important! first link the hosts to the switches
    # this way the port on the switch is always 1!
    for i in range(3):
        for j in range(3):
            for k in range(3):
                sname = 's%d%d%d'%(i+1,j+1,k+1)
                s = net[sname]
                n = 'h%d%d%d'%(i+1,j+1,k+1)
                net.addLink(s, net[n], intfName1=sname+"-"+n, intfName2=n+"-"+sname)

    info( '*** Connect within layers\n' )
    for i in range(3):
        for j in range(3):
            for k in range(3):
                sname = 's%d%d%d'%(i+1,j+1,k+1)
                s = net[sname]
                for n in ['s%d%d%d'%(i+1,j+1,1+(k+1)%3), 's%d%d%d'%(i+1,1+(j+1)%3,k+1)]:
                    net.addLink(s, net[n], intfName1=sname+"-"+n, intfName2=n+"-"+sname)

    links = {}

    info( '*** Connect cross layers\n' )
    for i in range(3):
        for j in range(3):
            for k in range(3):
                # select current node
                sname = 's%d%d%d'%(i+1,j+1,k+1)
                s = net[sname]

                # randomly select other nodes
                for n in ['s%d%d%d'%(1+(i+1)%3, randint(1,3),randint(1,3)), 's%d%d%d'%(1+(i+4)%3,randint(1,3),randint(1,3))]:
                    if not n+"-"+sname in links:
                        links[sname+"-"+n] = True
                        links[n+"-"+sname] = True
                        net.addLink(s, net[n], intfName1=sname+"-"+n, intfName2=n+"-"+sname)

    info( '*** Starting network\n')
    net.start()

    for i in range(3):
        for j in range(3):
            for k in range(3):
                name = 'h%d%d%d'%(i+1,j+1,k+1)
                net[name].setIP("10.%d.%d.%d/8"%(i+1,j+1,k+1))

    info( '*** Running CLI\n' )
    CLI( net )

    info( '*** Stopping network' )
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    haecnet()

