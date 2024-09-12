from abc import ABC, abstractmethod


class Docs(ABC):

    @abstractmethod
    def docs(self, attachment: str) -> str:
        pass
