#!/usr/bin/python2
# -*- coding: utf-8 -*-
"""
Fabric is used here to manage the cluster of MaxiNet workers.

# Settings
    - Workers are defined as haec_workers_16 roles and setted as default
    - Data operations are running parallel, while others use sequential mode

# Add new task
    - Write a function with @task decorator in this file to define a new task
    - Use @parallel decorator to run task parallel
"""

from __future__ import with_statement

from re import search
from time import sleep, strftime

from fabric.api import (cd, env, get, local, parallel, put, run, settings,
                        sudo, task)
from fabric.context_managers import hide
from fabric.contrib import project

# Fabric Configurations
# -----------------------------------------------
# number of times for connection
env.connection_attempts = 1
# skip the unavailable hosts
env.skip_bad_hosts = True
env.colorize_errrors = True
# -----------------------------------------------

# Init Remote Hosts and Roles
# -----------------------------------------------
# -- haec playground workers --
# Only 16 odroids on Nr.3
WORKER_LIST_16 = ['odroid@192.168.3.%d:22' % h for h in range(51, 67)]

# 16 odroids on Nr.3 and 11 on Nr.4
WORKER_LIST_27 = []
WORKER_LIST_27.extend(['odroid@192.168.3.%d:22' % h for h in range(51, 67)])
WORKER_LIST_27.extend(['odroid@192.168.4.%d:22' % h for h in range(67, 78)])

env.roledefs = {
    'haec_workers_16': WORKER_LIST_16,
    'haec_workers_27': WORKER_LIST_27,
    'frondend': 'odroid@192.168.3.42:22'
}

# set default roles, haec_workers_16
# without -R and -H option, default roles will be used
if not env.roles and not env.hosts:
    env.roles = ['haec_workers_16']

# set password directory
PASSWORD_DICT = {}
for host in WORKER_LIST_16:
    PASSWORD_DICT[host] = "odroid"

env.passwords = PASSWORD_DICT
# -----------------------------------------------


# Operations for the Demo
# -----------------------------------------------
@task
@parallel
def del_mxn_cfg():
    """Delete MaxiNet config file."""
    run('rm -f ~/.MaxiNet.cfg')


@task
@parallel
def put_mxn_cfg():
    """Put MaxiNet config file."""
    remote_path = '~/.MaxiNet.cfg'
    local_path = './haec_cebit_demo.cfg'
    put(local_path, remote_path)


@task
@parallel
def put_iperf_demo():
    """Put Iperf demo executable file."""
    run('mkdir -p ~/bin/')  # make sure ~/bin exist.
    remote_path = '~/bin/iperf-server-client-demo-odroid'
    local_path = './iperf-server-client-demo-odroid'
    put(local_path, remote_path)


# MARK: Do not run it parallel
@task
def run_worker():
    """Run MaxiNet WorkerServer process at background without hang up.

    Run serially and sleep 1s for each worker.
    Try to make the registration in order and successfully.
    """
    with settings(hide('warnings'), warn_only=True):
        # check if MaxiNetWorker is running
        count = int(run('pgrep -c MaxiNetWorker').splitlines()[0])
        while count == 0:
            # run cmd without pty, stdin data won't be echoed
            sudo('nohup MaxiNetWorker > /dev/null 2>&1 &', pty=False)
            sleep(1)  # wait 1 second
            count = int(run('pgrep -c MaxiNetWorker').splitlines()[0])


@task
@parallel
def kill_worker():
    """Kill MaxiNet WorkerServer process at background."""
    with settings(hide('warnings'), warn_only=True):
        count = int(run('pgrep -c MaxiNetWorker').splitlines()[0])
        while count > 0:
            # kill all MaxiNetWorker
            sudo('killall MaxiNetWorker', pty=False)
            sleep(1)
            count = int(run('pgrep -c MaxiNetWorker').splitlines()[0])
