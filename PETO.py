from IPETO import IPETO
from IScale import IScale


class PETO(IPETO):
    def __init__(self, plateScale: IScale, containerScale: IScale, motor):
        super().__init__(plateScale, containerScale, motor)
        self.plateScale = plateScale
        self.containerScale = containerScale
        self.motor = motor

    def GetCurrentPlateStatus(self):
        return self.plateScale.weight()

    def GetCurrentContainer(self):
        return self.containerScale.weight()

    def motorOn(self):
        print("motor is on")

    def motorOff(self):
        print("motor is off")

    def FeedPet(self, grams):  # I'm assuming the plate is empty.
        while(self.GetCurrentPlateStatus() < grams):
            self.motorOn()
            self.GetCurrentPlateStatus()
        num = self.GetCurrentPlateStatus()
        print(f"finished feeding! weight on plate is {num}")
