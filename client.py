#!/usr/bin/env python

import os
import time
import zerorpc
import balena
import multiprocessing

import gi
gi.require_version('NM', '1.0')

from gi.repository import NM, GLib

SERVER_PORT = 54863
SERVER_IP = os.environ['SERVER_IP']


def get_ip_address(nm_client):
    device = nm_client.get_device_by_iface('eth0')
    config = device.get_ip4_config()

    address =  config.get_addresses()[0].get_address()

    print('IP address:', address)
    return address

def has_wifi_inteface(nm_client):
    device = nm_client.get_device_by_iface('wlan0')
    success =  device is not None
    print('WiFi present:', success)
    return success

def probe():
    nm_client = NM.Client.new(None)

    success = has_wifi_inteface(nm_client)
    address = get_ip_address(nm_client)

    return {
        'address': address,
        'success': success,
    }

def connect():
    server = 'tcp://{}:{}'.format(SERVER_IP, SERVER_PORT)

    rpc = zerorpc.Client()
    rpc.connect(server)

    print('Connected to:', server)

    return rpc

def reboot():
    Supervisor = balena.models.supervisor.Supervisor
    print('On device: ', Supervisor._on_device)
    Supervisor.SUPERVISOR_API_KEY = os.environ.get('RESIN_SUPERVISOR_API_KEY')
    supervisor = Supervisor()
    supervisor.reboot()

def calculate(x):
    while True:
        x*x

def stress():
    processes = multiprocessing.cpu_count()
    print('Stressing {} cores'.format(processes))

    pool = multiprocessing.Pool(processes)
    pool.map(calculate, range(processes))

def main():
    data = probe()

    rpc = connect()

    rpc.report(data)

    stress()

main()
