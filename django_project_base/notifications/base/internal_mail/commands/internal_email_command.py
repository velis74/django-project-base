from abc import ABC, abstractmethod
from typing import Any


class InternalEmailCommand(ABC):

    def __init__(self, command_payload: Any) -> None:
        super().__init__()
        self.__payload = None
        self.payload = command_payload

    @abstractmethod
    def execute(self) -> None:
        pass

    @property
    def payload(self) -> Any:
        return self.__payload

    @payload.setter
    def payload(self, val):
        if self.payload:
            raise Exception('Command payload already set')
        self.__payload = val
