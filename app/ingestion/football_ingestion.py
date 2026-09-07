from typing import Any, Dict, List

import httpx

from app.data_providers.public_provider import PublicFootballProvider
from app.data_normalizers.openfootball_normalizer import OpenFootballNormalizer
from app.data_validation.data_sufficiency import DataSufficiencyChecker


class FootballIngestionPipeline:
    """
    Connects the external football data provider to the internal
    normalized and validated data layers.

    Competition identity is preserved from the source.
    This layer does not perform prediction.
    """

    def __init__(self, source_url: str):
        self.source_url = source_url
        self.provider = PublicFootballProvider(source_url)

    def fetch_and_validate(self, **kwargs: Any) -> List[Dict[str, Any]]:
        response = httpx.get(
            self.source_url,
            timeout=kwargs.get("timeout", 30.0),
            follow_redirects=True,
        )
        response.raise_for_status()

        source_data = response.json()

        if not isinstance(source_data, dict):
            raise ValueError("Football data source did not return a JSON object.")

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
