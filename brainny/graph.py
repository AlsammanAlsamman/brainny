"""Read/write graph.json — the per-project brain (Part 3 of SEED.md)."""

from __future__ import annotations

import json
from pathlib import Path

from brainny.schema import Graph

DEFAULT_OUT_DIR = Path("brainny-out")
GRAPH_FILENAME = "graph.json"
HTML_FILENAME = "graph.html"


def graph_path(out_dir: Path = DEFAULT_OUT_DIR) -> Path:
    return out_dir / GRAPH_FILENAME


def html_path(out_dir: Path = DEFAULT_OUT_DIR) -> Path:
    return out_dir / HTML_FILENAME


def load_graph(out_dir: Path = DEFAULT_OUT_DIR) -> Graph:
    path = graph_path(out_dir)
    if not path.exists():
        return Graph()
    data = json.loads(path.read_text(encoding="utf-8"))
    return Graph.model_validate(data)


def save_graph(graph: Graph, out_dir: Path = DEFAULT_OUT_DIR) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    path = graph_path(out_dir)
    path.write_text(
        json.dumps(graph.model_dump(mode="json"), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return path


def next_id(graph: Graph) -> str:
    n = len(graph.nodes) + 1
    while True:
        candidate = f"idea_{n:04d}"
        if not any(node.id == candidate for node in graph.nodes):
            return candidate
        n += 1
