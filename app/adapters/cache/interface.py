from abc import ABC, abstractmethod

class CacheAdapterInterface(ABC):
    @abstractmethod
    def set(self, key, value, ex=None):
        pass

    @abstractmethod
    def get(self, key):
        pass 