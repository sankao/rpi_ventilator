#!/usr/bin/env python
import sys
import piplates.RELAYplate as rel
relay_id = int(sys.argv[1])
is_on = int(sys.argv[2])
on_off = 'on' if is_on else 'off'
print ('relay : ',relay_id,' ',on_off)
if is_on:
    rel.relayON(0, relay_id)
else:
    rel.relayOFF(0, relay_id)


