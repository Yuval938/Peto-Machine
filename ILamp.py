from abc import ABC, abstractmethod
import RPi.GPIO as GPIO  # import GPIO


class ILamp(ABC):
    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def On(self):
        pass
    @abstractmethod
    def Off(self):
        pass

    @abstractmethod
    def Blink(self):
        pass

