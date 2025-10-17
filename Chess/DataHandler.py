from abc import ABC, abstractmethod
from bitstring import BitArray

class DataHandler(ABC):
    def __init__(self, handlerId: int):
        self.handlerId = handlerId
    @abstractmethod
    def detect(self, board) -> bool:
        pass
    @abstractmethod
    def encode(self, board) -> str:
        pass
    @abstractmethod
    def decode(self, bits:BitArray, board):
        pass
