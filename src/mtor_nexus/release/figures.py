# pyright: reportUnknownArgumentType=false, reportUnknownMemberType=false
"""Generate byte-stable manuscript SVGs and figure provenance records."""

import argparse
import html
import json
import subprocess
from collections import Counter
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any, cast

from mtor_nexus.graph.web_exports import MANUSCRIPT_MODULES
from mtor_nexus.utils.reproducibility import sha256_file

WEB_ROOT = "webapp/public/data"
FIGURE_ROOT = "figures"
LAYOUT_SEED = "mtor-nexus-deterministic-svg-v1"
SAXTON_DOI = "10.1016/j.cell.2017.02.004"
TFEB_STRUCTURE_DOI = "10.1038/s41586-022-05652-7"


def _read_json(path: Path) -> dict[str, Any]:
    """Read a JSON object from a committed deterministic browser artifact."""

    return cast(dict[str, Any], json.loads(path.read_text(encoding="utf-8")))


def _source_revision() -> str:
    """Record the source-data commit used for a local figure generation run."""

    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def _number(value: Any) -> float:
    """Convert a JSON number into a stable float."""

    if not isinstance(value, int | float):
        raise ValueError(f"expected numeric figure coordinate, got {value!r}")
    return float(value)


def _text(value: Any) -> str:
    """Convert a JSON string into escaped SVG text."""

    if not isinstance(value, str):
        raise ValueError(f"expected figure text, got {value!r}")
    return html.escape(value)


def _module_svg(document: dict[str, Any]) -> str:
    """Render one publication-oriented module diagram from preset positions."""

    elements = cast(dict[str, Any], document["elements"])
    raw_nodes = cast(list[dict[str, Any]], elements["nodes"])
    raw_edges = cast(list[dict[str, Any]], elements["edges"])
    nodes: dict[str, tuple[float, float]] = {}
    for node in raw_nodes:
        data = cast(dict[str, Any], node["data"])
        position = cast(dict[str, Any], node["position"])
        nodes[_text(data["node_id"])] = (_number(position["x"]), _number(position["y"]))
    min_x = min(position[0] for position in nodes.values()) - 70
    min_y = min(position[1] for position in nodes.values()) - 60
    max_x = max(position[0] for position in nodes.values()) + 70
    max_y = max(position[1] for position in nodes.values()) + 60
    width = max_x - min_x
    height = max_y - min_y
    paths: list[str] = []
    for edge in sorted(raw_edges, key=lambda item: cast(dict[str, Any], item["data"])["id"]):
        data = cast(dict[str, Any], edge["data"])
        source = nodes[_text(data["source"])]
        target = nodes[_text(data["target"])]
        mechanism = _text(data["mechanism"])
        dash = ' stroke-dasharray="8 7"' if mechanism == "binds" else ""
        marker = (
            ""
            if mechanism == "binds"
            else ' marker-end="url(#tee)"'
            if mechanism == "inhibits"
            else ' marker-end="url(#arrow)"'
        )
        paths.append(
            f'<path d="M {source[0]:.3f} {source[1]:.3f} L {target[0]:.3f} {target[1]:.3f}" '
            f'fill="none" stroke="#547e70" stroke-width="2"{dash}{marker}/>'
        )
    boxes = [
        (
            f'<g transform="translate({x:.3f} {y:.3f})"><rect x="-28" y="-17" width="56" '
            'height="34" rx="9" fill="#14382b" stroke="#8be7aa" stroke-width="2"/>'
            f'<text y="35" fill="#dff9e8" font-family="Arial, sans-serif" font-size="11" '
            f'text-anchor="middle">{node_id}</text></g>'
        )
        for node_id, (x, y) in sorted(nodes.items())
    ]
    module = cast(dict[str, Any], document["module"])
    title = _text(module["title"])
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="{min_x:.3f} {min_y:.3f} {width:.3f} {height:.3f}" role="img">'
        f"<title>{title}</title><defs>"
        '<marker id="arrow" markerHeight="7" markerWidth="7" orient="auto" refX="6" refY="3.5">'
        '<path d="M0,0 L7,3.5 L0,7 z" fill="#547e70"/></marker>'
        '<marker id="tee" markerHeight="9" markerWidth="7" orient="auto" refX="6" refY="4.5">'
        '<path d="M6,0 L6,9" fill="none" stroke="#ff6b6b" stroke-width="2"/></marker>'
        '</defs><rect x="-10000" y="-10000" width="20000" height="20000" fill="#08130f"/>'
        + "".join(paths)
        + "".join(boxes)
        + "</svg>\n"
    )


def _bar_chart(
    title: str,
    items: list[tuple[str, int]],
    *,
    origin_x: int,
    origin_y: int,
    width: int,
    color: str,
) -> str:
    """Render one stable horizontal-bar group."""

    max_value = max(value for _, value in items)
    bars = [
        (
            f'<text x="{origin_x}" y="{origin_y + index * 38}" fill="#dff9e8" '
            f'font-family="Arial, sans-serif" font-size="16">{_text(label)}</text>'
            f'<rect x="{origin_x + 135}" y="{origin_y + index * 38 - 17}" '
            f'width="{value / max_value * width:.3f}" height="20" rx="4" fill="{color}"/>'
            f'<text x="{origin_x + 150 + value / max_value * width:.3f}" '
            f'y="{origin_y + index * 38}" fill="#dff9e8" '
            f'font-family="Arial, sans-serif" font-size="16">{value}</text>'
        )
        for index, (label, value) in enumerate(items)
    ]
    return (
        f'<text x="{origin_x}" y="{origin_y - 42}" fill="#8be7aa" '
        f'font-family="Arial, sans-serif" font-size="22" font-weight="bold">{_text(title)}</text>'
        + "".join(bars)
    )


def _summary_chart_svg(document: dict[str, Any]) -> str:
    """Render a deterministic README chart from the committed graph export."""

    raw_nodes = cast(list[dict[str, Any]], document["nodes"])
    raw_edges = cast(list[dict[str, Any]], document["edges"])
    tiers = Counter(_text(edge["tier"]) for edge in raw_edges)
    mechanisms = Counter(_text(edge["mechanism"]) for edge in raw_edges)
    tier_items = [(tier, tiers[tier]) for tier in ["robust", "plausible", "speculative"]]
    mechanism_items = sorted(mechanisms.items(), key=lambda item: (-item[1], item[0]))
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 650" role="img">'
        "<title>mTOR-NEXUS atlas summary chart</title>"
        '<rect width="1280" height="650" fill="#08130f"/>'
        '<text x="70" y="65" fill="#dff9e8" font-family="Arial, sans-serif" '
        'font-size="34" font-weight="bold">mTOR-NEXUS atlas summary</text>'
        f'<text x="70" y="103" fill="#a9c9bc" font-family="Arial, sans-serif" font-size="18">'
        f"{len(raw_nodes)} nodes | {len(raw_edges)} evidence-tagged interactions</text>"
        + _bar_chart(
            "Evidence tiers",
            tier_items,
            origin_x=70,
            origin_y=195,
            width=330,
            color="#8be7aa",
        )
        + _bar_chart(
            "Interaction mechanisms",
            mechanism_items,
            origin_x=650,
            origin_y=195,
            width=300,
            color="#60a5fa",
        )
        + '<text x="70" y="610" fill="#a9c9bc" font-family="Arial, sans-serif" '
        'font-size="15">Generated deterministically by Python from the committed atlas '
        "export.</text>"
        "</svg>\n"
    )


def _provenance(
    figure: str,
    source_revision: str,
    inputs: list[str],
    *,
    include_tfeb_structure: bool = False,
) -> str:
    """Build a compact provenance record for one generated SVG."""

    dois = [SAXTON_DOI]
    if include_tfeb_structure:
        dois.append(TFEB_STRUCTURE_DOI)
    return (
        f"# {figure} Provenance\n\n"
        f"- Source-data commit SHA: `{source_revision}`\n"
        f"- Layout seed: `{LAYOUT_SEED}`\n"
        f"- Input artifact(s): {', '.join(f'`{item}`' for item in inputs)}\n"
        f"- Primary source DOI(s): {', '.join(f'`{doi}`' for doi in dois)}\n"
        "- Generator: `python -m mtor_nexus.release.figures`\n"
        "- Note: SVG bytes are deterministic for the recorded input artifacts "
        "and generator version.\n"
    )


def write_figures(
    root: str = FIGURE_ROOT,
    web_root: str = WEB_ROOT,
    *,
    source_revision: str | None = None,
) -> list[Path]:
    """Write seven module SVGs, one README chart, provenance, and checksums."""

    output_root = Path(root)
    source_root = Path(web_root)
    revision = source_revision or _source_revision()
    written: list[Path] = []
    for module in MANUSCRIPT_MODULES:
        source = source_root / "modules" / f"{module.module_id}.json"
        directory = output_root / module.module_id
        directory.mkdir(parents=True, exist_ok=True)
        svg = directory / "module.svg"
        provenance = directory / "provenance.md"
        svg.write_text(_module_svg(_read_json(source)), encoding="utf-8")
        provenance.write_text(
            _provenance(
                module.figure,
                revision,
                [str(source)],
                include_tfeb_structure=module.module_id == "5",
            ),
            encoding="utf-8",
        )
        written.extend([svg, provenance])
    chart_source = source_root / "mtor-graph.json"
    chart_directory = output_root / "readme"
    chart_directory.mkdir(parents=True, exist_ok=True)
    chart_svg = chart_directory / "atlas-summary.svg"
    chart_provenance = chart_directory / "provenance.md"
    chart_svg.write_text(_summary_chart_svg(_read_json(chart_source)), encoding="utf-8")
    chart_provenance.write_text(
        _provenance("README atlas-summary chart", revision, [str(chart_source)]),
        encoding="utf-8",
    )
    written.extend([chart_svg, chart_provenance])
    checksums = output_root / "checksums.sha256"
    checksums.write_text(
        "".join(
            f"{sha256_file(str(path))}  {path.relative_to(output_root)}\n"
            for path in sorted(written)
        ),
        encoding="utf-8",
    )
    written.append(checksums)
    return written


def figure_checksums_match(root: str = FIGURE_ROOT) -> bool:
    """Verify every committed figure artifact against its checksum manifest."""

    output_root = Path(root)
    checksum_path = output_root / "checksums.sha256"
    if not checksum_path.exists():
        return False
    for line in checksum_path.read_text(encoding="utf-8").splitlines():
        expected, relative = line.split("  ", maxsplit=1)
        artifact = output_root / relative
        if not artifact.is_file() or sha256_file(str(artifact)) != expected:
            return False
    return True


def figure_exports_reproduce(root: str = FIGURE_ROOT, web_root: str = WEB_ROOT) -> bool:
    """Regenerate every figure artifact and compare the resulting bytes."""

    output_root = Path(root)
    provenance = output_root / "1" / "provenance.md"
    if not figure_checksums_match(root) or not provenance.is_file():
        return False
    revision_line = next(
        (
            line
            for line in provenance.read_text(encoding="utf-8").splitlines()
            if line.startswith("- Source-data commit SHA: `")
        ),
        "",
    )
    if not revision_line.endswith("`"):
        return False
    revision = revision_line.removeprefix("- Source-data commit SHA: `").removesuffix("`")
    with TemporaryDirectory() as temporary_directory:
        regenerated_root = Path(temporary_directory) / "figures"
        write_figures(
            str(regenerated_root),
            web_root,
            source_revision=revision,
        )
        committed = sorted(
            path.relative_to(output_root)
            for path in output_root.rglob("*")
            if path.is_file() and not path.name.startswith(".")
        )
        regenerated = sorted(
            path.relative_to(regenerated_root)
            for path in regenerated_root.rglob("*")
            if path.is_file()
        )
        return committed == regenerated and all(
            (output_root / relative).read_bytes() == (regenerated_root / relative).read_bytes()
            for relative in committed
        )


def main() -> int:
    """Generate or verify deterministic publication SVG artifacts."""

    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=FIGURE_ROOT)
    parser.add_argument("--web-root", default=WEB_ROOT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.check:
        if not figure_exports_reproduce(args.root, args.web_root):
            print("figure checksum or deterministic regeneration verification failed")
            return 1
        print("verified deterministic publication figure checksums and regeneration")
        return 0
    written = write_figures(args.root, args.web_root)
    print(f"exported {len(written) - 1} figure artifact(s) and checksum manifest")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
