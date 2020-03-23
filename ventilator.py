#!/usr/bin/python
import RPi.GPIO as GPIO
import time
from timeit import default_timer as timer
import sys
import logging

#PIN_TRIGGER = 7 #BOARD
#PIN_ECHO = 11 #BOARD
PIN_TRIGGER = 4 #BCM
PIN_ECHO = 17 #BCM
PULSE_US = 20.
MAX_WAIT_0 = 0.08
MAX_WAIT_1 = 0.08
MAX_DIST_CM = 12.5
#safety to prevent blowing up the balloon
MAX_INFLATION_TIME = 4
DEFLATION_TIME = 4

def get_raw_distance():
    try:
          #relay uses BCM
          GPIO.setmode(GPIO.BCM)

          GPIO.setup(PIN_TRIGGER, GPIO.OUT)
          GPIO.setup(PIN_ECHO, GPIO.IN)

          GPIO.output(PIN_TRIGGER, GPIO.LOW)

          #print "Waiting for sensor to settle"

          #print "Calculating distance"

          start = timer()
          loop_end = 0.
          pulse_duration = 0.
          GPIO.output(PIN_TRIGGER, GPIO.HIGH)
          while True:
              loop_end = timer()
              pulse_duration = 100000 * (loop_end - start)
              if pulse_duration > PULSE_US:
                  break
          GPIO.output(PIN_TRIGGER, GPIO.LOW)

          #need a give up condition
          failed_down = False
          failed_up = False
          pulse_start_time = -1
          while GPIO.input(PIN_ECHO)==0:
                pulse_start_time = timer()
                if pulse_start_time - loop_end > MAX_WAIT_0:
                    failed_down = True
                    break
          while GPIO.input(PIN_ECHO)==1:
                pulse_end_time = timer()
                if pulse_end_time - loop_end > MAX_WAIT_1:
                    failed_up = True
                    break

          #print ('time waited', pulse_duration)
          if failed_down or pulse_start_time < 0:
              logging.warning('{}\r'.format('failed to get echo pin down state'))
              logging.info('CSV:{:.6f},n/a'.format(timer()))
              return -1
          elif failed_up:
              logging.warning('{}\r'.format('failed to get echo pin up state'))
              logging.info('CSV:{:.6f},n/a'.format(timer(), distance))
              return -1
          else:
              pulse_duration = pulse_end_time - pulse_start_time
              distance = round(pulse_duration * 17150, 2)
              #print ("pulse:",1000000 * pulse_duration,"us")
              #print ("Distance:",distance,"cm")
              logging.info('Distance {}cm\r'.format(distance))
              logging.info('CSV:{:.6f},{:.6f}'.format(pulse_end_time, distance))
              return distance
    finally:
          #print ('cleaning up GPIO')
          #GPIO.cleanup()
          logging.debug('no cleanup')

def get_distance():
    sample_cnt = 5
    samples = []

    for i in range(0, sample_cnt):
        samples.append(get_raw_distance())

    #throw out aberrant values
    min_dist = 15
    max_dist = 30
    samples = [s for s in samples if s > min_dist and s < max_dist]
    if len(samples) == 0:
        return -1
    samples = sorted(samples)
    median = 0.5 * (samples[int(len(samples) / 2)] + samples[1 + int(len(samples) / 2)])
    logging.info('distance : {:.2f} samples {}'.format(median, ','.join(['{:.2f}'.format(s) for s in samples])))
    return median

def log_alarm(reason):
    logging.WARN('Alarm triggered: {}'.format(reason))
    time.sleep(1)

def all_off():
    #GPIO.setmode(GPIO.BCM)
    import piplates.RELAYplate as rel
    rel.relayOFF(0, 1)
    rel.relayOFF(0, 2)
    logging.info('RELAY 1 OFF')
    logging.info('RELAY 2 OFF')

def inflate():
    d = get_distance()
    #no measurement, something wrong, turn off the valves
    if d < 0:
        all_off()
        log_alarm('inflate: failed to get distance')
    if d < MAX_DIST_CM:
        return
    inflate_start = timer()
    import piplates.RELAYplate as rel
    rel.relayON(0, 1)
    rel.relayOFF(0, 2)
    while True:
        time.sleep(0.1)
        if timer() - inflate_start > MAX_INFLATION_TIME:
            all_off()
            log_alarm('inflate: max inflation time reached')
            break
        d = get_distance()
        if d < MAX_DIST_CM:
            break

    #we're done inflating, lock the valves
    all_off()

def deflate():
    import piplates.RELAYplate as rel
    rel.relayOFF(0, 1)
    time.sleep(0.1)
    rel.relayON(0, 2)
    time.sleep(DEFLATION_TIME)
    all_off()

def do_cycle():
    #the sleeps are here to prevent over-triggering the relays in case
    #of sensor/logic error
    all_off()
    time.sleep(0.1)
    logging.info('STATE: INFLATING')
    inflate()
    time.sleep(0.1)
    logging.info('STATE: DEFLATING')
    deflate()
    time.sleep(0.1)

if __name__ == '__main__':
    #GPIO.setmode(GPIO.BCM)
    logging.basicConfig(filename='ventilator.log',format='[%(asctime)s][%(levelname)s]%(message)s',level=logging.DEBUG)
    try:
        while True:
            do_cycle()
    finally:
        all_off()
