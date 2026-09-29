"""Verified multi-source registry, chunked by region.

Each entry declares:
  name         — display name
  federation   — official federation URL (always recorded)
  sources      — dict of {source_key: id_or_slug}
                 keys: apif, espn, tsdb, fd, oldb, ofb, zafx
"""
