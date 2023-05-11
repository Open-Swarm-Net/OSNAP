from abc import ABC, abstractmethod

class AdapterBase(ABC):
    """This class stores some basic properties that every adapter should implement.
    """

    @property
    @abstractmethod
    def users(self):
        """Returns the information about the users on the server
        """
        raise NotImplementedError