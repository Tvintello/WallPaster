from abc import ABC, abstractmethod


class Parser(ABC):
    """Base class for all parsers"""
    @abstractmethod
    def get_available_resolutions(self, link: str) -> list:
        pass

    @abstractmethod
    def get_image_bytes(self, link: str, resolution: list) -> bytes:
        pass

    @abstractmethod
    def get_image_links(self, query: dict) -> list:
        pass

    @abstractmethod
    def get_pages(self, query: dict) -> int:
        pass

    @abstractmethod
    def get_quantity(self, query: dict) -> int:
        pass


