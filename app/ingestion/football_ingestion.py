from typing import Any, Dict, List

from app.data_normalizers.openfootball_normalizer import OpenFootballNormalizer
from app.data_providers.public_provider import PublicFootballProvider
from app.data_registry.competition_registry import CompetitionRegistry
from app.data_validation.data_sufficiency import DataSufficiencyChecker


class FootballIngestionPipeline:
    """
    Competition-aware football data ingestion.

    The registry identifies the legitimate source for the requested
    competition. The provider performs the external data fetch.
    The normalizer converts provider-specific data into the internal
    structure, and the validation layer checks data sufficiency.

    This layer does not perform prediction and does not modify Pieces 1-9.
    """

    def __init__(self, registry: CompetitionRegistry):
        self.registry = registry

    def fetch_and_validate(
        self,
        competition_id: str,
        **kwargs: Any,
    ) -> List[Dict[str, Any]]:
        source = self.registry.get(competition_id)

        if source is None:
            raise ValueError(
                f"Competition '{competition_id}' is not registered."
            )

        if source.coverage_status != "available":
            raise ValueError(
                f"Competition '{competition_id}' is not currently available."
            )

        provider = PublicFootballProvider(source.source_url)

        source_data = provider.get_dataset(
            timeout=kwargs.get("timeout", 30.0)
        )

        normalized_matches = OpenFootballNormalizer.normalize_dataset(
            source_data
        )

        validated_matches = []

        for match in normalized_matches:
            sufficiency = DataSufficiencyChecker.check_match(match)

            validated_matches.append(
                {
                    "match": match,
                    "sufficiency": sufficiency,
                }
            )

        return validated_matches
