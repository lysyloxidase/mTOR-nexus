"""Exercise identifier-check behavior without reaching external services."""

from urllib.error import HTTPError

from mtor_nexus.utils import http_check, pdb_check, uniprot_check


class _Response:
    """Tiny context-managed HTTP response stub."""

    status = 200

    def __enter__(self) -> "_Response":
        return self

    def __exit__(self, *_args: object) -> None:
        return None


def test_http_check_retries_transient_failures(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """Transient upstream errors are retried before an ID is rejected."""

    responses = [
        HTTPError("https://example.test", 429, "rate limit", {}, None),
        _Response(),
    ]
    monkeypatch.setattr(http_check, "urlopen", lambda *_args, **_kwargs: responses.pop(0))
    monkeypatch.setattr(http_check.time, "sleep", lambda _seconds: None)

    assert http_check.resolves("https://example.test")
    assert responses == []


def test_http_check_does_not_retry_missing_identifier(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """A permanent missing-ID response fails immediately."""

    responses = [HTTPError("https://example.test", 404, "missing", {}, None), _Response()]
    monkeypatch.setattr(http_check, "urlopen", lambda *_args, **_kwargs: responses.pop(0))

    assert not http_check.resolves("https://example.test")
    assert len(responses) == 1


def test_uniprot_check_reports_malformed_and_unresolved(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """UniProt checks retain malformed IDs and failed endpoint resolutions."""

    monkeypatch.setattr(
        uniprot_check, "_accession_resolves", lambda accession: accession != "Q9UBS0"
    )

    assert uniprot_check.broken_accessions(["bad-id", "Q9UBS0", "P42345"]) == ["Q9UBS0", "bad-id"]


def test_pdb_check_reports_malformed_and_unresolved(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """PDB checks retain malformed IDs and failed endpoint resolutions."""

    monkeypatch.setattr(pdb_check, "_pdb_id_resolves", lambda pdb_id: pdb_id != "5H64")

    assert pdb_check.broken_pdb_ids(["bad-id", "5H64", "4JSV"]) == ["5H64", "bad-id"]
