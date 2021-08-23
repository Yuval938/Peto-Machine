from abc import ABC, abstractmethod

import IPETO


class IScheduler(ABC):
    @abstractmethod
    def __init__(self, peto: IPETO):
        pass
    @abstractmethod
    def add_to_schedule(self,func):
        pass
    @abstractmethod
    def remove_from_schedule(self,func):
        pass
    @abstractmethod
    def normalRoutine(self):
        pass
