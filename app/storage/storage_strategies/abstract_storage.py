from abc import ABC
from abc import abstractmethod

class AbstractStorage(ABC):

    @abstractmethod
    def get_ids(self):
        pass
