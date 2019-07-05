#!/usr/bin/env python

import zerorpc
import gevent
import pytuya
import copy
import time
import os

SERVER_PORT = 54863

OUTLET_ID = os.environ['OUTLET_ID']
OUTLET_IP = os.environ['OUTLET_IP']
OUTLET_LOCAL_KEY = os.environ['OUTLET_LOCAL_KEY']

OUTLET = pytuya.OutletDevice(OUTLET_ID, OUTLET_IP, OUTLET_LOCAL_KEY)

KNOWN_DEVICES = set()
AWAITING_DEVICES = set()

POWERED = False

class RPC:
    def __init__(self):

        self.stats = {
            'ok': 0,
            'no': 0,
        }

    def report(self, data):
        if data['success']:
            self.stats['ok'] += 1
        else:
            self.stats['no'] += 1

        print(data)
        print(self.stats)

        address = data['address']
        KNOWN_DEVICES.add(address)

        if address in AWAITING_DEVICES:
            AWAITING_DEVICES.remove(address)

        if len(AWAITING_DEVICES) == 0:
            gevent.spawn_later(10, power_off)


def power_outlet(state):
    while True:
        try:
            data = OUTLET.status()
        except:
            continue

        current_state = data['dps']['1']

        if current_state == state:
            break

        try:
            OUTLET.set_status(state)
        except:
            continue

        time.sleep(1)


def power_off():
    global POWERED

    if not POWERED:
        print('Already powered off')
        return

    print('Power off...')
    power_outlet(False)
    gevent.spawn_later(1, power_on)
    POWERED = False

def power_on():
    global POWERED
    global AWAITING_DEVICES

    if POWERED:
        print('Already powered on')
        return

    print('Power on...')
    AWAITING_DEVICES = copy.copy(KNOWN_DEVICES)
    power_outlet(True)
    POWERED = True

def main():
    power_on()
    print('Starting server...')
    server = zerorpc.Server(RPC())
    server.bind("tcp://0.0.0.0:{}".format(SERVER_PORT))
    server.run()

main()
