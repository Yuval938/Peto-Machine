from abc import ABC, abstractmethod

from ILamp import ILamp
from IScale import IScale
from main import config


class IPETO(ABC):
    @abstractmethod
    def __init__(self,plateScale: IScale, containerScale: IScale, motor, lamp: ILamp):
        self.machine_id = config['DEFAULT']['machine_id']
        pass

    @abstractmethod
    def GetCurrentPlateStatus(self):
        pass

    @abstractmethod
    def GetCurrentContainer(self):
        pass

    @abstractmethod
    def FeedPet(self, grams):
        pass

    @abstractmethod
    def motorOn(self):
        pass

    @abstractmethod
    def motorOff(self):
        pass

    @abstractmethod
    def Blink(self):
        pass

    @abstractmethod
    def lightON(self):
        pass

    @abstractmethod
    def lightOFF(self):
        pass
