from abc import ABC, abstractmethod
from typing import Any, Dict, List


class FootballDataProvider(ABC):
    """
    Common interface for all football data providers.

    Free/public providers and future premium APIs must implement
    this same interface so the analytical pipeline remains unchanged.
    """

    @abstractmethod
    def get_matches(self, **kwargs: Any) -> List[Dict[str, Any]]:
        """
        Return football match data in the provider's raw format.
        """
        raise NotImplementedError
