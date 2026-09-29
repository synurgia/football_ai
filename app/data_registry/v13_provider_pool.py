from __future__ import annotations

from typing import Dict

from app.data_registry.v13_global_match_discovery import (
    V13GlobalMatchDiscovery,
)
from app.data_registry.v13_espn_match_discovery import (
    V13ESPNMatchDiscovery,
)
from app.data_registry.v13_gsa_match_discovery import (
    V13GSAMatchDiscovery,
)


def build_v13_match_discovery() -> V13GlobalMatchDiscovery:
    return V13GlobalMatchDiscovery(
        providers=[
            V13ESPNMatchDiscovery(),
            V13GSAMatchDiscovery(),
        ]
    )


def get_v13_provider_ids() -> Dict[str, str]:
    return {
        "espn_football": "ACTIVE",
        "gsa_global_football": "REGISTERED_NOT_YET_WIRED",
    }
