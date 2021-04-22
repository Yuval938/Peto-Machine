from abc import ABC, abstractmethod
import RPi.GPIO as GPIO  # import GPIO


class IScale(ABC):
    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def weight(self):
        pass

