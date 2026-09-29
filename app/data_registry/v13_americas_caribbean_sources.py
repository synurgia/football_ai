V13_AMERICAS_CARIBBEAN_SOURCE_CANDIDATES = [

    {
        "source_id": "cfu_official",
        "name": "Caribbean Football Union",
        "base_url": "https://www.cfufootball.org/",
        "layer": "OFFICIAL",
        "data_classes": [
            "competition", "fixture", "schedule", "results",
            "match_status", "team", "player", "lineup", "venue"
        ],
        "access_type": "PUBLIC_WEB",
        "free": True,
        "coverage_scope": "CARIBBEAN",
        "status": "CANDIDATE",
    },

    {
        "source_id": "concacaf_caribbean",
        "name": "Concacaf Caribbean",
        "base_url": "https://www.concacaf.com/",
        "layer": "OFFICIAL",
        "data_classes": [
            "competition", "fixture", "schedule", "results",
            "match_status", "team", "player", "lineup", "venue"
        ],
        "access_type": "PUBLIC_WEB",
        "free": True,
        "coverage_scope": "CARIBBEAN",
        "status": "CANDIDATE",
    },

    {
        "source_id": "concacaf_member_associations",
        "name": "Concacaf Member Association Profiles",
        "base_url": "https://www.concacaf.com/inside-concacaf/member-associations",
        "layer": "OFFICIAL",
        "data_classes": [
            "competition", "team", "player", "venue"
        ],
        "access_type": "PUBLIC_WEB",
        "free": True,
        "coverage_scope": "CARIBBEAN",
        "status": "CANDIDATE",
    },
]
