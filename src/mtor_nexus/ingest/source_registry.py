"""Pinned source registry and redistribution policy helpers."""

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class SourceConfig:
    """Configuration for one upstream data source."""

    name: str
    version: str
    url: str
    license: str
    redistribution: str
    options: dict[str, Any]


def load_source_registry(
    path: str = "src/mtor_nexus/config/data_sources.yaml",
) -> dict[str, SourceConfig]:
    """Load pinned source metadata from the committed registry."""

    document = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    sources: dict[str, SourceConfig] = {}
    for name, raw_source in document["sources"].items():
        source = dict(raw_source)
        sources[name] = SourceConfig(
            name=name,
            version=str(source.pop("version")),
            url=str(source.pop("url")),
            license=str(source.pop("license")),
            redistribution=str(source.pop("redistribution")),
            options=source,
        )
    return sources


def restricted_sources(registry: dict[str, SourceConfig]) -> set[str]:
    """Return source names whose raw records must remain segregated."""

    return {
        source.name
        for source in registry.values()
        if source.redistribution == "segregated-non-commercial"
    }
