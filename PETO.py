from ILamp import ILamp
from IPETO import IPETO
from IScale import IScale
from Motor import IMotor


class PETO(IPETO):
    def __init__(self, plateScale: IScale, containerScale: IScale, motor: IMotor,lamp:ILamp):
        super().__init__(plateScale, containerScale, motor,lamp)
        self.plateScale = plateScale
        self.containerScale = containerScale
        self.motor = motor
        self.lamp = lamp
        self.foodOnPlate=0
        self.latest=0

    def GetCurrentPlateStatus(self):
        scale = self.plateScale.weight()
        print(f"scale on plate is {scale} ")
        return scale#self.plateScale.weight()

    def GetCurrentContainer(self):
        scale = self.containerScale.weight()
        print(f"scale on Container is {scale} ")
        return scale#self.containerScale.weight()

    def motorOn(self):
        self.motor.motorOn()
        print("motor is on")

    def motorOff(self):
        print("motor is off")
        self.motor.motorOff()

    def FeedPet(self, grams):  # I'm assuming the plate is empty.
        self.lamp.On()
        while (self.GetCurrentPlateStatus() < grams):
            self.motorOn()
            # self.GetCurrentPlateStatus()
        num = self.GetCurrentPlateStatus()
        self.foodOnPlate = num
        self.latest = num
        print(f"finished feeding! weight on plate is {num}")
        self.lamp.Off()
