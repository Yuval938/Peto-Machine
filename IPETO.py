from abc import ABC, abstractmethod
class IPETO(ABC):
    @abstractmethod
    def __init__(self,plateScale:IScale,containerScale,Motor):
        pass

    @abstractmethod
    def weight(self):
        pass

