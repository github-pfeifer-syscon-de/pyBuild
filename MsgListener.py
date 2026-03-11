from abc import ABC, abstractmethod

class MsgListenerInterface(ABC):

    @abstractmethod
    def out(self, msg: str):
        """Stdout message"""
        pass

    @abstractmethod
    def err(self, msg: str):
        """Stderr message"""
        pass

    @abstractmethod
    def closed(self, status):
        """Process in finished"""
        pass