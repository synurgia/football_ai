V13_AFRICA_WAFU_A_SOURCE_CANDIDATES = [

    {
        "source_id": "wafu_a_official",
        "name": "WAFU Zone A",
        "base_url": "https://wafua.org/",
        "layer": "REGIONAL_OFFICIAL",
        "data_classes": [
            "competition", "fixture", "schedule", "results",
            "match_status", "team", "player", "lineup", "venue"
        ],
        "access_type": "PUBLIC_WEB",
        "free": True,
        "coverage_scope": "WAFU_A",
        "status": "CANDIDATE",
    },

    {
        "source_id": "caf_wafu_a",
        "name": "CAF WAFU-A",
        "base_url": "https://www.cafonline.com/",
        "layer": "REGIONAL_OFFICIAL",
        "data_classes": [
            "competition", "fixture", "schedule", "results",
            "match_status", "team", "player", "lineup"
        ],
        "access_type": "PUBLIC_WEB",
        "free": True,
        "coverage_scope": "WAFU_A",
        "status": "CANDIDATE",
    },

    {
        "source_id": "senegal_fsf_official",
        "name": "Fédération Sénégalaise de Football",
        "base_url": "https://fsfoot.sn/",
        "layer": "OFFICIAL",
        "data_classes": [
            "competition", "fixture", "schedule", "results",
            "match_status", "team", "player", "lineup"
        ],
        "access_type": "PUBLIC_WEB",
        "free": True,
        "coverage_scope": "SENEGAL",
        "status": "CANDIDATE",
    },

    {
        "source_id": "gambia_gff_official",
        "name": "Gambia Football Federation",
        "base_url": "https://gambiaff.org/",
        "layer": "OFFICIAL",
        "data_classes": [
            "competition", "fixture", "schedule", "results",
            "match_status", "team", "player", "lineup"
        ],
        "access_type": "PUBLIC_WEB",
        "free": True,
        "coverage_scope": "GAMBIA",
        "status": "CANDIDATE",
    },
]
