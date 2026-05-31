"""Optional Neo4j integration test for the Phase 2 loader."""

import os

import pytest
from neo4j import GraphDatabase

from mtor_nexus.graph.build import MTORGraphBuilder


@pytest.mark.skipif(
    "MTOR_NEXUS_NEO4J_URI" not in os.environ,
    reason="set MTOR_NEXUS_NEO4J_URI to run the Neo4j integration test",
)
def test_neo4j_load_and_phosphorylation_query() -> None:
    """Load the graph and exercise the required phosphorylation query."""

    uri = os.environ["MTOR_NEXUS_NEO4J_URI"]
    auth = (os.getenv("MTOR_NEXUS_NEO4J_USER", "neo4j"), os.environ["MTOR_NEXUS_NEO4J_PASSWORD"])
    MTORGraphBuilder().to_neo4j(uri, auth, clear=True)
    with GraphDatabase.driver(uri, auth=auth) as driver:
        records, _, _ = driver.execute_query(
            "MATCH (n)-[r:PHOSPHORYLATES]->(m) RETURN count(r) AS phospho_count",
        )
    assert records[0]["phospho_count"] >= 70
