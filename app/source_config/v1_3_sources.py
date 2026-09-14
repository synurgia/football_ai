from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class V13SourceConfig:
    source_id: str
    name: str
    base_url: str
    scope: str
    capabilities: Tuple[str, ...]
    authority_level: str
    enabled: bool = True


# V1.3 source configuration baseline.
#
# IMPORTANT:
# These are configuration declarations only.
# They do NOT claim that live data has been verified.
# Official source URLs will be added only after they are
# confirmed against the V1.3 source/PDF specification.

V13_SOURCES: Tuple[V13SourceConfig, ...] = ()


def list_configured_sources() -> Tuple[V13SourceConfig, ...]:
    return V13_SOURCES
