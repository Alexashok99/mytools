"""Abstract base class for tools."""
from abc import ABC, abstractmethod

class BaseTool(ABC):
    """All tools must inherit from this class."""

    name: str = "Unnamed Tool"
    description: str = "No description"

    @abstractmethod
    def run(self) -> None:
        """Execute the tool's main functionality."""
        pass