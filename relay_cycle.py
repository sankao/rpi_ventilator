#!/usr/bin/env python
import sys
import piplates.RELAYplate as rel
import time
cycle = float(sys.argv[1])
while True:
    print ('relay : 1 on  relay 2 off')
    rel.relayON(0, 1)
    rel.relayOFF(0, 2)
    time.sleep(cycle)
    print ('relay : 1 off relay 2 on')
    rel.relayOFF(0, 1)
    rel.relayON(0, 2)
    time.sleep(cycle * 3)


