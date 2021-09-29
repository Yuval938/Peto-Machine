from abc import ABC, abstractmethod

import IPETO


class IScheduler(ABC):
    @abstractmethod
    def __init__(self, peto: IPETO):
        pass
    @abstractmethod
    def normalRoutine(self):
        pass
