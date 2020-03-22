#!/usr/bin/python
import RPi.GPIO as GPIO
import time
from timeit import default_timer as timer
import sys

PIN_TRIGGER = 7
PIN_ECHO = 11
PULSE_US = 20.
MAX_WAIT_0 = 0.08
MAX_WAIT_1 = 0.08

def read():
    try:
          GPIO.setmode(GPIO.BOARD)
    
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
              print '{}\r'.format('failed to get echo pin down state'),
          elif failed_up:
              print '{}\r'.format('failed to get echo pin up state'),
          else:
              pulse_duration = pulse_end_time - pulse_start_time
              distance = round(pulse_duration * 17150, 2)
              #print ("pulse:",1000000 * pulse_duration,"us")
              #print ("Distance:",distance,"cm")
              print 'Distance {}cm\r'.format(distance),
              sys.stdout.flush()
    
    finally:
          #print ('cleaning up GPIO')
          GPIO.cleanup()

if __name__ == '__main__':
  while True:
      time.sleep(0.1)
      read()
