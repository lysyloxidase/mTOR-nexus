"""Runtime settings loaded from environment variables."""

from dataclasses import dataclass
from os import getenv


@dataclass(frozen=True)
class Settings:
    """Small environment-backed settings surface for Phase 1."""

    environment: str = getenv("MTOR_NEXUS_ENV", "development")
    graph_path: str = getenv("MTOR_NEXUS_GRAPH_PATH", "data/processed/mtor-graph.json")
    disease_path: str = getenv("MTOR_NEXUS_DISEASE_PATH", "data/processed/disease-layer.json")
    drug_path: str = getenv("MTOR_NEXUS_DRUG_PATH", "data/processed/drug-layer.json")
    neo4j_uri: str = getenv("NEO4J_URI", "bolt://neo4j:7687")


settings = Settings()
