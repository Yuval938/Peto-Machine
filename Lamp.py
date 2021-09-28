#!/usr/bin/env python3
########################################################################
# Filename    : Blink.py
# Description : Basic usage of GPIO. Let led blink.
# auther      : www.freenove.com
# modification: 2019/12/28
########################################################################
import threading

import RPi.GPIO as GPIO
import time

from ILamp import ILamp


class Lamp(ILamp):
    def __init__(self, ledPin):
        super().__init__()
        self.blink = False
        self.on = True
        self.MachineOn = True
        self.ledPin = ledPin
        GPIO.setmode(GPIO.BCM)  # use PHYSICAL GPIO Numbering
        GPIO.setup(self.ledPin, GPIO.OUT)  # set the ledPin to OUTPUT mode
        GPIO.output(self.ledPin, GPIO.LOW)  # make ledPin output LOW level
        print('using pin%d' % self.ledPin)
        threading.Thread(target=self.Blink).start()
    def On(self):
        GPIO.output(self.ledPin, GPIO.HIGH)
        self.on=True
    def Off(self):
        GPIO.output(self.ledPin, GPIO.LOW)
        self.on=False
    def Blink(self):
        while self.MachineOn:
            time.sleep(0.5)
            while(self.blink):
                self.On()  # make ledPin output HIGH level to turn on led
                # print('led turned on >>>')  # print information on terminal
                time.sleep(0.4)  # Wait for 1 second
                self.Off()  # make ledPin output LOW level to turn off led
                # print('led turned off <<<')
                time.sleep(0.4)  # Wait for 1 second




