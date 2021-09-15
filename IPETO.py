from abc import ABC, abstractmethod

from ILamp import ILamp
from IScale import IScale


class IPETO(ABC):
    @abstractmethod
    def __init__(self,plateScale:IScale,containerScale:IScale,motor,lamp:ILamp):
        pass

    @abstractmethod
    def GetCurrentPlateStatus(self):
        pass
    @abstractmethod
    def GetCurrentContainer(self):
        pass
    @abstractmethod
    def FeedPet(self,grams):
        pass
    @abstractmethod
    def motorOn(self):
        pass
    @abstractmethod
    def motorOff(self):
        pass


