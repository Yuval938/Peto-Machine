import time

from ILamp import ILamp
from IPETO import IPETO
from IScale import IScale
from Motor import IMotor
from Meal import Meal
import threading


class PETO(IPETO):
    def __init__(self, machine_id: int, plateScale: IScale, containerScale: IScale, motor: IMotor, lamp: ILamp):
        super().__init__(machine_id, plateScale, containerScale, motor, lamp)
        self.id = None  # should be determine by app\DB
        # self.machine_id = 54321  # each machine gets its own id when manufactured
        self.petName = None  # will be detemine by app
        self.plateScale = plateScale
        self.containerScale = containerScale
        self.motor = motor
        self.lamp = lamp
        self.foodOnPlate = 0
        self.latest = 0
        self.lamp.On()
        self.scheduleHash = 0
        self.currentMeal = None  # SHOULD BE ONLY ONE IN ANY GIVEN TIME

    def GetCurrentPlateStatus(self):
        scale = self.plateScale.weight()
        return scale

    def GetCurrentContainer(self):
        scale = self.containerScale.weight()
        return scale

    def motorOn(self):
        self.motor.motorOn()
        print("motor is on")

    def motorOff(self):
        self.motor.motorOff()
        print("motor is off")

    def FeedPet(self, grams):
        # self.lamp.On()
        self.lamp.blink = True
        amountBeforeFeeding = self.GetCurrentPlateStatus()
        # we should feed as long as the weight in plate is less than the amount given(grams).
        while (self.GetCurrentPlateStatus() < grams):
            self.motorOn()
            # self.GetCurrentPlateStatus()
        self.lamp.blink = False
        num = self.GetCurrentPlateStatus()
        self.foodOnPlate = num
        self.latest = num
        print(f"finished feeding! weight on plate is {num}")
        self.lamp.On()
        return num - amountBeforeFeeding  # this is the amount the was actually added to plate

    # make peto lamp blink
    def Blink(self):
        if (self.lamp.blink):
            self.lamp.blink = False
        else:
            self.lamp.blink = True

    # make peto lamp turn on
    def lightON(self):
        self.lamp.On()

    # make peto lamp turn off
    def lightOFF(self):
        self.lamp.Off()
