"""graph.json → terminal tree + graph.html. The v0/v0.2 visualizations
(SEED.md §7). No server involved — graph.html is a static, self-contained,
git-shareable file, per SEED.md §0's "nothing runs on a server."
"""

from __future__ import annotations

import html as htmllib
import json
from collections import defaultdict
from pathlib import Path

from brainny.graph import DEFAULT_OUT_DIR, html_path
from brainny.opportunities import load_opportunities
from brainny.schema import Graph, Node, Opportunities

OPPORTUNITY_KIND_COLOR = {
    "tool": "#3b6fd6",
    "website": "#2f9e5e",
    "statistical-module": "#8b5cd6",
    "business-idea": "#e8b23d",
    "other": "#8a8f98",
}
OPPORTUNITY_KIND_LABEL = {
    "tool": "tool",
    "website": "website",
    "statistical-module": "statistical module",
    "business-idea": "business idea",
    "other": "other",
}

# Vendored, not CDN-loaded: graph.html used to pull D3 from
# cdn.jsdelivr.net at view time, which silently produced a blank graph
# (data present, nothing drawn) for anyone opening it offline or behind a
# firewall that blocks that CDN -- a real user hit exactly this. Baking
# the library's own source into the generated HTML instead makes the
# "static, self-contained, git-shareable file" claim above literally true
# -- no network needed to view it, ever. Pinned at v7.9.0 to match the
# `<option>`s/behavior this file's JS was written against; bump
# brainny/vendor/d3.v7.9.0.min.js (and this filename/path) together if
# that version ever changes. License: brainny/vendor/D3_LICENSE.txt.
_D3_JS = (Path(__file__).parent / "vendor" / "d3.v7.9.0.min.js").read_text(encoding="utf-8")

KIND_ICON = {
    "technique": "T",
    "precaution": "!",
    "solution": "S",
    "insight": "I",
    "seed": ".",
    "skill": "K",
}

KIND_COLOR = {
    "technique": "#3b6fd6",
    "precaution": "#c9432c",
    "solution": "#2f9e5e",
    "insight": "#8b5cd6",
    "seed": "#8a8f98",
    "skill": "#e8b23d",
}

# attachment "signs" -- a short badge glyph shown per idea in the itemized
# list so a skill's physical evidence (code/plot/table) is visible without
# opening the entry; small deliberately, per SEED.md's "small enough to
# guide, not duplicate the dataset" attachment discipline.
ATTACHMENT_ICON = {"code": "‹/›", "plot": "△", "table": "☷"}
ATTACHMENT_LABEL = {"code": "code", "plot": "plot", "table": "table"}

# The dashboard header icon — a small (96px) PNG baked in as base64 so
# graph.html stays a single self-contained file (no external asset
# dependency to break when the file moves). Derived from assets/icon.png;
# regenerate by hand (resize to ~96px, base64-encode) if that source
# image changes — not read from disk at runtime, same pattern as
# banner.py's _GLYPH.
_ICON_PNG_B64 = (
    "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Z6iwcMVlF1GQ35E33nqX4uJi5nw/j+U/rKRL587069ubrp0LyWibTqw3FoGgORCgurqGg4eK2bBpMzt37sIT46Fb1y7hDDlUo43E1J996W8sXGRX0/r168vECePp2b2bQ4qilXNuqZBpmqTR52P294v5fuEydu87QE1tPcGggaUslGkxoF8vunYqsLGZcKQjw7tH03RSkpNISU4K76Zf162n7MhR4uK8PHj/3fTt3TMc7Zx04kCm3nojM956j+ZlzdTSgPLYDJF9+/bTo1uXsBmUUrJw0VIOHy4lPS2NYScNjiRFb9KBrUANkKxUaJIPUQ1sI4afRN/ePZn51TcsWryU0rIjrP55DT+v+YWYGA9erzdcALf5m034/X6UUqSkJON2ue3EI4LlHAmezV+0lIULlxAbG8v5Eydw7VVTWo2qsaIY1qFeMSHg+0XLmPHeJ+zac4Bg0CAmxk27jHQy0lPRXS4K8nLI7tC+VRsTUaxp0zSi2BdCwMofV+Pz++xBH47wdV0LL6Lzzz2bwQNP4Nf166mqriY5IYke3btSWNDR6Zmz5VdTU8tXs77FsixOGnIi7dtlKqckWSOl3KoLIcpM09whpRwspbRaNxGEermSkhK56vJL+NO5Z/PTz2v45df17N23n4qqKvw+H/UNDeBw9N0eD7k52cQnJFBUXITb7YqYVCKiss1gMMiXX32DaRoMGTyMa6+aEoHra47ZkOGW05Bzr29o5JmXX2f294sJBE2SEuIYNuQEThs5nF7du5KelhJlmkzLgojyYctCONaMHimvYMPGTXhjvYw4eZjDmlNRtWnLssjOak92VPEqOoQWQvDy9Dc4XFpKmzYpTL7gTyGEUgN2CCHKdEfIPwInWpalIolOoaSkpS5skZycxBljx3DG2DH4m5o4cuQolVXVzooHj8dNUmIi7dplUnK4lFtuuzOqjNeaILt3/wEOFRURFxfPheefFyFkGW60thxyQMhPrVm7kWf/9ibbd+5FCslJg/py0zWX0bdX91Ywhi04XXehRfQEG4ZBXV09dfUNNDY20tzcjGEYeL1eevboxtJlP1BWdoROnQvp36+3g/bSihHdwsQOLyzRQk4DePXvM1j+w0ospbjkogvJyeqAYZhK1zXlyDxMT18ETHMaNI4zFClkkmSYDScExMbEkJebQ15uznEdcXVsDG63m6amZmrr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"
)

STATE_ORDER = ["seed", "sprouting", "mature", "harvested"]

# growth axis -> how a fruit/bud reads in the 3D tree (SEED.md's state field)
STATE_META = {
    "seed": {"label": "seed / bud", "size": 0.16, "emissive": 0.12, "gold": False},
    "sprouting": {"label": "sprouting leaf", "size": 0.22, "emissive": 0.22, "gold": False},
    "mature": {"label": "mature fruit", "size": 0.30, "emissive": 0.40, "gold": False},
    "harvested": {"label": "harvested fruit", "size": 0.34, "emissive": 0.65, "gold": True},
}

# who originated the idea's content (schema.py's Origin) -- an axis
# independent of kind/state: humans supply the innovation and direction,
# the AI supplies collective/pattern knowledge, and a lot of real work is
# neither alone. None (pre-this-field entries) reads as "unclassified",
# a real fourth bucket, not a guessed default.
ORIGIN_COLOR = {
    "human": "#e05a9a",
    "ai": "#e8b23d",
    "collaborative": "#3bb0a8",
}
ORIGIN_LABEL = {
    "human": "human",
    "ai": "AI",
    "collaborative": "collaborative",
    None: "unclassified",
}
UNCLASSIFIED_COLOR = "#5c6b63"


def _node_line(node: Node) -> str:
    icon = KIND_ICON.get(node.kind, "?")
    tags = f" [{', '.join(node.tags)}]" if node.tags else ""
    recur = f" x{node.recurrence}" if node.recurrence > 1 else ""
    origin = f" <{node.origin}>" if node.origin else ""
    return f"  [{icon}] ({node.state}{recur}) {node.title} - {node.id}{tags}{origin}"


def render_tree(graph: Graph) -> str:
    if not graph.nodes:
        return "brainny: no ideas captured yet. Run `brainny capture <entries.json>`."

    by_domain: dict[str, list[Node]] = defaultdict(list)
    for node in graph.nodes:
        by_domain[node.domain].append(node)

    lines: list[str] = []
    total = len(graph.nodes)
    by_kind = defaultdict(int)
    for node in graph.nodes:
        by_kind[node.kind] += 1
    summary = ", ".join(f"{v} {k}" for k, v in sorted(by_kind.items()))
    lines.append(f"brainny - {total} idea(s): {summary}")
    lines.append("")

    for domain in sorted(by_domain):
        lines.append(f"{domain}/")
        nodes = sorted(
            by_domain[domain],
            key=lambda n: (STATE_ORDER.index(n.state) if n.state in STATE_ORDER else 99, n.title),
        )
        for node in nodes:
            lines.append(_node_line(node))
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def _esc(s: str) -> str:
    return htmllib.escape(s, quote=True)


def _build_payload(graph: Graph, opportunities: Opportunities, title: str) -> dict:
    """The data the 3D scene is built from client-side: nodes plus a
    de-duplicated, chronological session list (the trunk's growth rings)."""

    nodes = []
    for n in graph.nodes:
        prov = n.provenance[0] if n.provenance else None
        nodes.append(
            {
                "id": n.id,
                "kind": n.kind,
                "title": n.title,
                "summary": n.summary,
                "detail": n.detail,
                "snippet": n.snippet,
                "domain": n.domain,
                "tags": n.tags,
                "trigger": n.trigger,
                "state": n.state,
                "origin": n.origin,
                "recurrence": n.recurrence,
                "lastTouched": n.last_touched,
                "session": prov.session if prov else None,
                "sessionTs": prov.ts if prov else "",
                "project": prov.project if prov else None,
                "attachments": [
                    {"type": a.type, "filename": a.filename, "description": a.description}
                    for a in n.attachments
                ],
            }
        )

    sessions_by_id: dict[str, dict] = {}
    for n in graph.nodes:
        if not n.provenance:
            continue
        prov = n.provenance[0]
        entry = sessions_by_id.setdefault(
            prov.session, {"session": prov.session, "ts": prov.ts, "count": 0}
        )
        entry["count"] += 1
        if prov.ts < entry["ts"]:
            entry["ts"] = prov.ts
    sessions = sorted(sessions_by_id.values(), key=lambda s: s["ts"])
    projects = sorted({n["project"] for n in nodes if n["project"]})

    return {
        "title": title,
        "nodes": nodes,
        "sessions": sessions,
        "projects": projects,
        "domainCount": len({n.domain for n in graph.nodes}),
        "kindColor": KIND_COLOR,
        "stateMeta": STATE_META,
        "originColor": ORIGIN_COLOR,
        "originLabel": {k: v for k, v in ORIGIN_LABEL.items() if k is not None},
        "unclassifiedColor": UNCLASSIFIED_COLOR,
        "attachmentIcon": ATTACHMENT_ICON,
        "attachmentLabel": ATTACHMENT_LABEL,
        "opportunities": [
            {
                "id": o.id,
                "title": o.title,
                "kind": o.kind,
                "weight": o.weight,
                "summary": o.summary,
                "rationale": o.rationale,
                "ideaIds": o.idea_ids,
                "created": o.created,
            }
            for o in opportunities.items
        ],
        "opportunityKindColor": OPPORTUNITY_KIND_COLOR,
        "opportunityKindLabel": OPPORTUNITY_KIND_LABEL,
    }


_CSS = """
  /* ---- theming: CSS custom properties for every structural/chrome color.
     Dark is the default (:root, no attribute needed); a tiny inline
     script in <head> (see render_html) sets [data-theme] before first
     paint -- from localStorage if the user has toggled before, else from
     prefers-color-scheme -- so there's no flash of the wrong theme. The
     light palette is deliberately NOT stark white (a
     soft warm sage-paper tone instead) per explicit design direction: a
     pure-white dashboard read as harsh next to the dark original. Data-
     semantic colors (kind/origin/opportunity-kind/trend colors, the gold
     brand accent) are intentionally left constant across both themes --
     they encode meaning, not chrome, and should stay recognizable. */
  :root {
    --bg: #0b1310;
    --bg-rgb: 11,19,16;
    --fg: #eef3ea;
    --overlay-rgb: 255,255,255;
    --text: #d7ddd4;
    --text-muted: #c9d3c6;
    --text-dim: #a9b7a6;
    --text-dimmer: #9aab97;
    --text-faint: #8fa08c;
    --text-fainter: #7c8c79;
    --text-faintest: #6b7a68;
    --note-fg: #d7c9a0;
    --code-bg: rgba(0,0,0,0.28);
    --active-tab-fg: #f0e2bb;
    --graph-link: rgba(190,205,180,0.28);
    /* "screen" blend mode brightens toward white -- exactly the "glowing
       lines on near-black" look the Brain tab's bundled mesh wants in
       dark theme, but on a light background it washes every link out to
       nearly nothing (screen(anything, near-white) ~= near-white). Light
       theme swaps to "multiply" instead, which darkens toward the color
       the same way screen brightens -- the equivalent glow, inverted for
       a light backdrop. */
    --brain-link-blend: screen;
  }
  :root[data-theme="light"] {
    --bg: #eef1e4;
    --bg-rgb: 238,241,228;
    --fg: #24302a;
    --overlay-rgb: 20,32,24;
    --text: #3c4a40;
    --text-muted: #47564a;
    --text-dim: #55654f;
    --text-dimmer: #5e6f5a;
    --text-faint: #687a62;
    --text-fainter: #74876c;
    --text-faintest: #869781;
    --note-fg: #7a5f1f;
    --code-bg: rgba(20,32,24,0.06);
    --active-tab-fg: #5a4315;
    --graph-link: rgba(60,80,64,0.35);
    --brain-link-blend: multiply;
  }

  * { box-sizing: border-box; }
  html, body { margin: 0; padding: 0; height: 100%; background: var(--bg); }
  body {
    font: 14px/1.5 -apple-system, Segoe UI, Helvetica, Arial, sans-serif;
    color: var(--fg); display: flex; flex-direction: column; height: 100%;
  }

  header { padding: 0.9rem 1.25rem; border-bottom: 1px solid rgba(var(--overlay-rgb),0.08); background: rgba(var(--bg-rgb),0.85); flex: none; }
  header .row { display: flex; align-items: center; gap: 0.9rem; flex-wrap: wrap; }
  #brand-icon { width: 28px; height: 28px; object-fit: contain; flex: none; }
  header h1 { margin: 0; font-size: 1.15rem; }
  header p { margin: 0.35rem 0 0; color: var(--text-dimmer); font-size: 0.82rem; }
  #view-select {
    background: rgba(var(--overlay-rgb),0.06); border: 1px solid rgba(var(--overlay-rgb),0.16); color: var(--fg);
    padding: 0.3rem 0.6rem; border-radius: 8px; font: inherit; font-size: 0.85rem; cursor: pointer;
  }
  #view-select:hover { background: rgba(var(--overlay-rgb),0.1); }
  /* the dropdown's open popup is native-rendered by the OS, outside CSS
     theme control -- force it light-with-dark-text always, a universal
     fallback that stays readable regardless of the page's own theme */
  #view-select option { color: #111; background: #fff; }
  .note {
    margin: 0.6rem 0 0; padding: 0.6rem 0.8rem; border-radius: 8px;
    background: rgba(232,178,61,0.08); border: 1px solid rgba(232,178,61,0.25);
    font-size: 0.78rem; color: var(--note-fg);
  }

  #theme-toggle {
    margin-left: auto; background: rgba(var(--overlay-rgb),0.06); border: 1px solid rgba(var(--overlay-rgb),0.16);
    color: var(--fg); font: inherit; font-size: 0.9rem; width: 2.1rem; height: 2.1rem; border-radius: 8px;
    cursor: pointer; display: inline-flex; align-items: center; justify-content: center; flex: none;
  }
  #theme-toggle:hover { background: rgba(var(--overlay-rgb),0.1); }

  #tab-bar { display: flex; gap: 0.3rem; margin-left: 0.4rem; }
  .tab-btn {
    background: none; border: 1px solid transparent; color: var(--text-dimmer); font: inherit;
    font-size: 0.85rem; padding: 0.3rem 0.8rem; border-radius: 8px; cursor: pointer;
  }
  .tab-btn:hover { background: rgba(var(--overlay-rgb),0.06); color: var(--fg); }
  .tab-btn.active { background: rgba(232,178,61,0.14); border-color: rgba(232,178,61,0.4); color: var(--active-tab-fg); }

  /* who originated an idea: human / AI / collaborative / all -- an axis
     independent of kind/state, filterable across every view */
  #origin-filter { display: flex; gap: 0.3rem; align-items: center; flex-wrap: wrap; }
  .origin-btn {
    background: rgba(var(--overlay-rgb),0.04); border: 1px solid rgba(var(--overlay-rgb),0.14); color: var(--text-muted);
    font: inherit; font-size: 0.78rem; padding: 0.25rem 0.65rem; border-radius: 999px; cursor: pointer;
    display: inline-flex; align-items: center; gap: 0.35rem;
  }
  .origin-btn:hover { background: rgba(var(--overlay-rgb),0.09); }
  .origin-btn .dot { width: 8px; height: 8px; border-radius: 50%; flex: none; }
  .origin-btn.active { font-weight: 600; }

  /* project filter -- only present on the merged central view (brainny
     central --html) spanning more than one project */
  #project-filter-row { display: flex; align-items: center; gap: 0.4rem; margin-left: 0.6rem; }
  #project-filter {
    background: rgba(var(--overlay-rgb),0.06); border: 1px solid rgba(var(--overlay-rgb),0.16); color: var(--fg);
    padding: 0.25rem 0.55rem; border-radius: 8px; font: inherit; font-size: 0.82rem; cursor: pointer;
  }
  #project-filter option { color: #111; background: #fff; }
  .item-project-group { margin-bottom: 1.1rem; }
  .item-project-group:last-child { margin-bottom: 0; }
  .item-project-heading {
    font-size: 0.82rem; font-weight: 600; color: var(--fg); margin: 0 0 0.5rem; padding: 0.3rem 0.5rem;
    background: rgba(232,178,61,0.1); border: 1px solid rgba(232,178,61,0.25); border-radius: 6px;
  }

  main { flex: 1; display: grid; grid-template-columns: 300px 1fr; min-height: 0; }
  main#stats-main, main#opportunities-main { display: block; overflow-y: auto; padding: 1.1rem 1.4rem 2rem; }
  main#brain-main, main#network-main { display: block; overflow: hidden; padding: 0; position: relative; }
  #graph-main[hidden], #stats-main[hidden], #opportunities-main[hidden], #brain-main[hidden], #network-main[hidden] { display: none !important; }

  /* ---- network tab: the central brain (this central folder, or just
     this one project when there's nothing else synced into it yet) with
     a small brain per connected project -- literally what's feeding it
     ideas. Static, not animated (no probe, no loop) -- a map, not a
     performance. ---- */
  #network-main svg { display: block; width: 100%; height: 100%; }
  .network-link { fill: none; }
  .network-node { cursor: pointer; }
  .network-node.dimmed { opacity: 0.35; }
  .network-label { font-size: 12px; fill: var(--text-muted); pointer-events: none; text-anchor: middle; }
  .network-count { font-size: 10px; fill: var(--text-fainter); pointer-events: none; text-anchor: middle; }
  .network-hub-label { font-size: 13px; font-weight: 700; fill: var(--fg); pointer-events: none; text-anchor: middle; }
  .network-caption {
    position: absolute; top: 0; left: 0; right: 0; z-index: 2; padding: 0.8rem 1.1rem;
    background: linear-gradient(180deg, rgba(var(--bg-rgb),0.85), rgba(var(--bg-rgb),0));
    font-size: 0.78rem; color: var(--text-dimmer); pointer-events: none; max-width: 640px;
  }
  .network-caption strong { color: var(--fg); }

  /* ---- opportunities tab: AI-proposed combinations of ideas ---- */
  .opp-list { display: flex; flex-direction: column; gap: 0.9rem; max-width: 760px; margin: 0 auto; }
  .opp-card {
    background: rgba(var(--overlay-rgb),0.03); border: 1px solid rgba(var(--overlay-rgb),0.08);
    border-radius: 10px; padding: 0.9rem 1.1rem;
  }
  .opp-header { display: flex; align-items: center; gap: 0.6rem; margin-bottom: 0.5rem; flex-wrap: wrap; }
  .opp-kind-badge {
    font-size: 0.7rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.03em;
    padding: 0.15rem 0.55rem; border-radius: 999px; border: 1px solid; flex: none;
  }
  .opp-title { font-size: 0.98rem; font-weight: 600; color: var(--fg); }
  .opp-weight-row { display: flex; align-items: center; gap: 0.6rem; margin-bottom: 0.6rem; }
  .opp-weight-track { flex: 1; height: 8px; border-radius: 999px; background: rgba(var(--overlay-rgb),0.07); overflow: hidden; }
  .opp-weight-fill { height: 100%; border-radius: 999px; }
  .opp-weight-pct { font-size: 0.76rem; color: var(--text-dimmer); width: 2.6rem; text-align: right; flex: none; }
  .opp-summary { margin: 0 0 0.4rem; color: var(--text); font-size: 0.86rem; }
  .opp-rationale { margin: 0 0 0.6rem; color: var(--text-dimmer); font-size: 0.8rem; font-style: italic; }
  .opp-ideas-label { font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.03em; color: var(--text-fainter); margin-bottom: 0.35rem; }
  .opp-ideas { display: flex; flex-wrap: wrap; gap: 0.35rem; }
  .opp-idea-chip {
    background: rgba(var(--overlay-rgb),0.06); border: 1px solid rgba(var(--overlay-rgb),0.14); color: var(--text-muted);
    font: inherit; font-size: 0.76rem; padding: 0.2rem 0.6rem; border-radius: 999px; cursor: pointer;
  }
  .opp-idea-chip:hover { background: rgba(var(--overlay-rgb),0.11); color: var(--fg); }

  /* ---- stats tab ---- */
  .stat-cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 0.7rem; margin: 0 0 1.4rem; }
  .stat-card {
    background: rgba(var(--overlay-rgb),0.03); border: 1px solid rgba(var(--overlay-rgb),0.08);
    border-radius: 10px; padding: 0.7rem 0.9rem;
  }
  .stat-card .stat-num { font-size: 1.6rem; font-weight: 600; color: var(--fg); line-height: 1.1; }
  .stat-card .stat-label { font-size: 0.74rem; color: var(--text-faint); margin-top: 0.2rem; text-transform: uppercase; letter-spacing: 0.03em; }

  .stats-grid { display: grid; grid-template-columns: minmax(280px, 1fr) minmax(320px, 1.2fr); gap: 1.4rem; align-items: start; }
  @media (max-width: 900px) { .stats-grid { grid-template-columns: 1fr; } }

  .stats-block h2 { font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.04em; color: var(--text-faint); margin: 0 0 0.6rem; }
  .stats-caption { font-size: 0.74rem; color: var(--text-fainter); margin: 0.5rem 0 0; }

  #treemap-mount svg { display: block; width: 100%; }
  .tm-cell rect { stroke: rgba(11,19,16,0.7); stroke-width: 1.5; cursor: pointer; }
  .tm-cell text { pointer-events: none; fill: #0b1310; font-size: 11px; font-weight: 600; }
  .tm-cell .tm-count { font-weight: 400; opacity: 0.75; }

  .domain-table { width: 100%; border-collapse: collapse; font-size: 0.82rem; }
  .domain-table th { text-align: left; font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.03em; color: var(--text-fainter); padding: 0.3rem 0.5rem; border-bottom: 1px solid rgba(var(--overlay-rgb),0.1); }
  .domain-table td { padding: 0.4rem 0.5rem; border-bottom: 1px solid rgba(var(--overlay-rgb),0.05); vertical-align: middle; }
  .domain-table tr:hover td { background: rgba(var(--overlay-rgb),0.03); }
  .spark { display: inline-block; vertical-align: middle; }
  .trend-badge { display: inline-flex; align-items: center; gap: 0.3rem; padding: 0.1rem 0.5rem; border-radius: 999px; font-size: 0.72rem; white-space: nowrap; }
  .trend-growing { background: rgba(111,174,92,0.16); color: #8fd67a; }
  .trend-steady { background: rgba(var(--overlay-rgb),0.06); color: var(--text-dimmer); }
  .trend-quiet { background: rgba(201,67,44,0.12); color: #d68a7a; }

  .kind-bars { display: flex; flex-direction: column; gap: 0.4rem; margin-top: 0.4rem; }
  .kind-bar-row { display: flex; align-items: center; gap: 0.6rem; font-size: 0.78rem; }
  .kind-bar-label { width: 110px; flex: none; color: var(--text-muted); }
  .kind-bar-track { flex: 1; height: 10px; border-radius: 999px; background: rgba(var(--overlay-rgb),0.06); overflow: hidden; }
  .kind-bar-fill { height: 100%; border-radius: 999px; }
  .kind-bar-count { width: 24px; flex: none; text-align: right; color: var(--text-faint); }

  .recent-list { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 0.5rem; }
  .recent-item { display: flex; flex-direction: column; gap: 0.1rem; padding: 0.45rem 0.6rem; border-radius: 8px; background: rgba(var(--overlay-rgb),0.02); border: 1px solid rgba(var(--overlay-rgb),0.06); cursor: pointer; }
  .recent-item:hover { background: rgba(var(--overlay-rgb),0.05); }
  .recent-item .ri-title { color: var(--fg); font-size: 0.84rem; }
  .recent-item .ri-meta { color: var(--text-fainter); font-size: 0.72rem; }
  #panel { border-right: 1px solid rgba(var(--overlay-rgb),0.08); overflow-y: auto; padding: 0.75rem; }
  #panel h2 { font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.04em; color: var(--text-faint); margin: 0.25rem 0.25rem 0.6rem; }
  #viz { position: relative; overflow: hidden; }
  #viz svg { display: block; width: 100%; height: 100%; }
  .empty-note { padding: 0.75rem; color: var(--text-faint); font-size: 0.85rem; }

  .legend-row { display: flex; flex-wrap: wrap; gap: 0.6rem; margin: 0 0 0.6rem; padding: 0 0.25rem; font-size: 0.76rem; color: var(--text-muted); }
  .legend-item { display: inline-flex; align-items: center; gap: 0.3rem; }
  .dot { width: 9px; height: 9px; border-radius: 50%; display: inline-block; flex: none; }
  .state-dot.state-seed { width: 6px; height: 6px; background: #6b7a68; }
  .state-dot.state-sprouting { width: 8px; height: 8px; background: #6fae5c; }
  .state-dot.state-mature { width: 10px; height: 10px; background: #4f9e63; }
  .state-dot.state-harvested { width: 11px; height: 11px; background: #e8b23d; }

  /* ---- itemized accordion list ---- */
  .item-list { display: flex; flex-direction: column; gap: 0.9rem; }
  .item-group { border-radius: 8px; padding: 0.15rem; }
  .item-group-heading { font-size: 0.76rem; color: var(--text-faint); margin: 0 0 0.35rem; padding: 0 0.25rem; }
  .item { border: 1px solid rgba(var(--overlay-rgb),0.08); border-radius: 8px; margin-bottom: 0.4rem; overflow: hidden; background: rgba(var(--overlay-rgb),0.02); }
  .item-promising { border-color: rgba(232,178,61,0.55); box-shadow: 0 0 0 1px rgba(232,178,61,0.15) inset; }
  .item-flash { animation: item-flash-kf 1.4s ease-out; }
  @keyframes item-flash-kf {
    0% { background: rgba(191,227,107,0.28); border-color: rgba(191,227,107,0.8); }
    100% { background: rgba(var(--overlay-rgb),0.02); }
  }
  .item-title-row {
    width: 100%; display: flex; align-items: center; gap: 0.5rem;
    background: none; border: none; color: var(--fg); text-align: left;
    padding: 0.5rem 0.6rem; cursor: pointer; font: inherit; font-size: 0.85rem;
  }
  .item-title-row:hover { background: rgba(var(--overlay-rgb),0.04); }
  .item-dot { width: 8px; height: 8px; border-radius: 50%; flex: none; }
  .item-title { flex: 1; }
  .item-caret { color: var(--text-faintest); transition: transform 0.15s; font-size: 0.7rem; }
  .item-title-row.open .item-caret { transform: rotate(90deg); }
  .item-body { padding: 0 0.75rem 0.7rem 1.85rem; font-size: 0.82rem; }
  .item-summary { margin: 0 0 0.35rem; color: var(--text); }
  .item-detail { margin: 0 0 0.35rem; color: var(--text-dim); }
  .item-trigger { margin: 0 0 0.35rem; color: var(--text-muted); font-size: 0.8rem; }
  .item-meta { margin: 0 0 0.35rem; color: var(--text-fainter); font-size: 0.72rem; }
  .item-tags { display: flex; flex-wrap: wrap; gap: 0.3rem; }
  .item-tag { background: rgba(var(--overlay-rgb),0.08); border-radius: 999px; padding: 0.05rem 0.5rem; font-size: 0.7rem; }

  /* attachment "signs" -- code/plot/table evidence badges (SEED.md
     attachments: small physical proof, not the full dataset) */
  .item-signs { display: inline-flex; gap: 0.2rem; flex: none; }
  .item-sign {
    display: inline-flex; align-items: center; justify-content: center;
    min-width: 1.3em; height: 1.3em; padding: 0 0.25em; border-radius: 4px;
    font-size: 0.68rem; font-weight: 600; letter-spacing: -0.02em;
    background: rgba(var(--overlay-rgb),0.08); color: var(--text-muted);
  }
  .item-sign-code { background: rgba(59,111,214,0.18); color: #9db8ef; }
  .item-sign-plot { background: rgba(139,92,214,0.18); color: #c4aef0; }
  .item-sign-table { background: rgba(47,158,94,0.18); color: #8fd6a8; }
  .item-sign-snippet { background: rgba(232,178,61,0.18); color: #e8c877; }
  /* inline snippet -- a code excerpt/equation/table-structure note kept
     directly on the entry, no separate file needed (see schema.py's
     `snippet` field) */
  .item-snippet {
    margin: 0 0 0.5rem; padding: 0.55rem 0.7rem; border-radius: 6px;
    background: var(--code-bg); border: 1px solid rgba(var(--overlay-rgb),0.08);
    font: 0.76rem/1.45 ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
    color: var(--text); white-space: pre-wrap; word-break: break-word; overflow-x: auto;
  }
  .item-evidence { display: flex; flex-direction: column; gap: 0.4rem; margin-top: 0.5rem; }
  .item-evidence-row { display: flex; align-items: center; gap: 0.4rem; flex-wrap: wrap; }
  .item-evidence-row a { color: #6f96e0; font-size: 0.78rem; text-decoration: none; }
  .item-evidence-row a:hover { text-decoration: underline; }
  .item-evidence-thumb { max-width: 160px; max-height: 100px; border-radius: 6px; border: 1px solid rgba(var(--overlay-rgb),0.12); display: block; margin-top: 0.2rem; }

  #tooltip {
    position: fixed; z-index: 10; pointer-events: none; max-width: 280px;
    background: rgba(var(--bg-rgb),0.96); border: 1px solid rgba(var(--overlay-rgb),0.12);
    border-radius: 10px; padding: 0.6rem 0.75rem; font-size: 0.8rem; display: none; color: var(--fg);
  }
  #tooltip .tt-title { font-weight: 600; margin-bottom: 0.2rem; }
  #tooltip .tt-meta { color: var(--text-faint); font-size: 0.72rem; }

  #fallback { padding: 2rem; white-space: pre-wrap; color: var(--fg); background: var(--bg); height: 100%; margin: 0; overflow: auto; }

  /* ---- brain tab: hierarchical edge-bundled connections resolve into a
     brain silhouette (no literal neuron dots), a probe circles it
     continuously gathering ideas into a live report, and clicking opens
     the mesh into real labeled/clickable idea circles. Ported from
     examples/viz-prototypes/12-neural-bundle.html -- see renderBrainView()
     in the JS below for the full port notes. ---- */
  #brain-main svg { display: block; width: 100%; height: 100%; }
  .bundle-link { fill: none; mix-blend-mode: var(--brain-link-blend); }
  .rim-arc { fill: none; stroke-width: 5; opacity: 0.85; }
  .brain-leaf { cursor: pointer; }
  .brain-leaf-label { font-size: 9px; fill: var(--fg); opacity: 0.85; pointer-events: none; }
  .brain-caption {
    position: absolute; top: 0; left: 0; right: 0; z-index: 2; padding: 0.8rem 1.1rem;
    background: linear-gradient(180deg, rgba(var(--bg-rgb),0.85), rgba(var(--bg-rgb),0));
    font-size: 0.78rem; color: var(--text-dimmer); pointer-events: none; max-width: 640px;
  }
  .brain-caption strong { color: var(--fg); }
  /* the report/constellation HUD panels float directly over the mesh
     itself, which passes all sorts of colors behind them regardless of
     page theme -- so unlike the rest of the chrome, these deliberately
     stay a fixed dark glass with light text in BOTH themes (like a
     tooltip or toast does), rather than trying to keep enough contrast
     against an arbitrary, constantly-shifting backdrop. */
  #brain-report {
    position: absolute; left: 1.1rem; bottom: 1.1rem; z-index: 3; width: 300px; max-height: 220px;
    background: rgba(9,15,12,0.88); border: 1px solid rgba(255,255,255,0.1); border-radius: 10px;
    padding: 0.65rem 0.8rem; font-size: 0.72rem; color: #c9d3c6; overflow: hidden;
  }
  #brain-report h3 { margin: 0 0 0.4rem; font-size: 0.68rem; text-transform: uppercase; letter-spacing: 0.04em; color: #e8b23d; }
  #brain-report .line { padding: 0.12rem 0; border-bottom: 1px dashed rgba(255,255,255,0.06); opacity: 0; animation: brain-fade-in 0.4s forwards; }
  @keyframes brain-fade-in { to { opacity: 1; } }
  #brain-constellation {
    position: absolute; top: 46%; left: 50%; transform: translate(-50%, -50%); z-index: 3;
    text-align: center; pointer-events: none; opacity: 0; transition: opacity 0.4s ease;
    background: rgba(9,15,12,0.85); border: 1px solid rgba(255,224,140,0.3); border-radius: 12px;
    padding: 0.65rem 1.2rem; max-width: 400px;
  }
  #brain-constellation .opp-kind { font-size: 0.66rem; text-transform: uppercase; letter-spacing: 0.05em; color: #e8b23d; }
  #brain-constellation .opp-title { font-size: 0.96rem; font-weight: 700; color: #fff3d0; margin: 0.15rem 0; }
  #brain-constellation .opp-conf { font-size: 0.74rem; color: #9aab97; }
  #brain-hint { position: absolute; bottom: 1rem; right: 1.2rem; z-index: 2; font-size: 0.72rem; color: var(--text-faintest); text-align: right; pointer-events: none; }
"""

_JS = """
(function () {
  function showFallback() {
    var main = document.querySelector('main');
    var fb = document.getElementById('fallback');
    if (main) main.hidden = true;
    if (fb) fb.hidden = false;
  }

  var DATA;
  try {
    DATA = JSON.parse(document.getElementById('brainny-data').textContent);
  } catch (e) {
    showFallback();
    return;
  }

  if (typeof d3 === 'undefined') {
    showFallback();
    return;
  }

  var STATE_RANK = { seed: 1, sprouting: 2, mature: 3, harvested: 4 };

  function potentialScore(idea) {
    return idea.recurrence * (STATE_RANK[idea.state] || 1);
  }

  function isPromising(idea) {
    return idea.recurrence > 1 || idea.state !== 'seed';
  }

  // ---- merged central view (brainny central --html): ids like "idea_0001"
  // are only unique WITHIN one project's own graph.json, so a dashboard
  // merging several projects needs a project-qualified key for DOM/d3 node
  // identity -- itemKey() is that key. idea.id itself stays the real,
  // original id everywhere else (attachment folder names, the id shown to
  // the user, growth_log/edges), since that's what's actually on disk. ----
  var MULTI_PROJECT = (DATA.projects || []).length > 1;

  function itemKey(idea) {
    return MULTI_PROJECT && idea.project ? idea.project + '::' + idea.id : idea.id;
  }

  // ---- origin filter: who actually originated each idea (human / AI /
  // collaborative / unclassified) -- independent of kind/state, and
  // applied consistently across every view (list, both graphs, stats) ----
  var activeOrigin = 'all';

  function originColor(idea) {
    if (!idea.origin) return DATA.unclassifiedColor || '#5c6b63';
    return (DATA.originColor && DATA.originColor[idea.origin]) || DATA.unclassifiedColor || '#5c6b63';
  }

  function originLabel(idea) {
    if (!idea.origin) return 'unclassified';
    return (DATA.originLabel && DATA.originLabel[idea.origin]) || idea.origin;
  }

  function matchesOriginFilter(idea) {
    if (activeOrigin === 'all') return true;
    if (activeOrigin === 'unclassified') return !idea.origin;
    return idea.origin === activeOrigin;
  }

  // ---- project filter: only present (and only rendered by the server)
  // when this is a merged central view spanning more than one project ----
  var activeProject = 'all';

  function matchesProjectFilter(idea) {
    return activeProject === 'all' || idea.project === activeProject;
  }

  function filteredData() {
    if (activeOrigin === 'all' && activeProject === 'all') return DATA;
    var filtered = {};
    for (var k in DATA) { if (Object.prototype.hasOwnProperty.call(DATA, k)) filtered[k] = DATA[k]; }
    filtered.nodes = DATA.nodes.filter(function (n) { return matchesOriginFilter(n) && matchesProjectFilter(n); });
    return filtered;
  }

  function escapeHtml(s) {
    var div = document.createElement('div');
    div.textContent = s == null ? '' : String(s);
    return div.innerHTML;
  }

  // resolves a CSS custom property to its actual current value (the
  // literal hex/rgb string, not the token) -- for the handful of places
  // that set a chrome color via D3's .attr() on an SVG element (fill/
  // stroke), which is a genuine SVG attribute, not a CSS declaration, so
  // it can't just reference var(--x) the way ordinary CSS/inline styles
  // can. Re-read on every (re)render, so it always reflects whichever
  // theme is active right now.
  function cssVar(name) {
    return getComputedStyle(document.documentElement).getPropertyValue(name).trim();
  }

  // domain path ("GWAS / sub-analysis") -> nested {name, kind, children}
  // tree, d3.hierarchy()-ready. Leaves carry the idea + its potentialScore
  // as `value` (branch/root nodes leave value undefined so d3's .sum()
  // aggregates bottom-up from real leaves only).
  function buildHierarchy(data) {
    var root = { id: '__root__', name: data.title, kind: 'root', children: [] };
    var byId = { __root__: root };

    function ensureBranch(pathParts) {
      var id = pathParts.join(' / ');
      if (byId[id]) return byId[id];
      var parentParts = pathParts.slice(0, -1);
      var parent = parentParts.length ? ensureBranch(parentParts) : root;
      var node = { id: id, name: pathParts[pathParts.length - 1], kind: 'branch', children: [] };
      byId[id] = node;
      parent.children.push(node);
      return node;
    }

    data.nodes.forEach(function (idea) {
      var parts = idea.domain.split('/').map(function (p) { return p.trim(); }).filter(Boolean);
      var parent = parts.length ? ensureBranch(parts) : root;
      parent.children.push({
        id: itemKey(idea), name: idea.title, kind: 'idea', idea: idea,
        value: potentialScore(idea), children: [],
      });
    });

    (function prune(node) {
      if (!node.children.length) { delete node.children; }
      else { node.children.forEach(prune); }
    })(root);

    return root;
  }

  // ---- itemized accordion list (click a title to unfold) ----
  function renderDomainGroups(container, ideas) {
    var byDomain = {};
    ideas.forEach(function (n) { (byDomain[n.domain] = byDomain[n.domain] || []).push(n); });

    Object.keys(byDomain).sort().forEach(function (domain) {
      var group = document.createElement('div');
      group.className = 'item-group';
      group.dataset.domain = domain;
      var heading = document.createElement('div');
      heading.className = 'item-group-heading';
      heading.textContent = domain + ' (' + byDomain[domain].length + ')';
      group.appendChild(heading);

      byDomain[domain].forEach(function (idea) {
        var item = document.createElement('div');
        item.className = 'item' + (isPromising(idea) ? ' item-promising' : '');
        item.dataset.itemId = itemKey(idea);

        var attachments = idea.attachments || [];
        var signBadges = attachments.map(function (a) {
          return '<span class="item-sign item-sign-' + escapeHtml(a.type) + '" title="' +
            escapeHtml((DATA.attachmentLabel[a.type] || a.type) + ': ' + a.filename) + '">' +
            escapeHtml(DATA.attachmentIcon[a.type] || '?') + '</span>';
        }).join('') + (idea.snippet
          ? '<span class="item-sign item-sign-snippet" title="inline snippet">\\u270e</span>'
          : '');

        var titleRow = document.createElement('button');
        titleRow.type = 'button';
        titleRow.className = 'item-title-row';
        titleRow.innerHTML =
          '<span class="item-dot" style="background:' + (DATA.kindColor[idea.kind] || '#8a8f98') + '"></span>' +
          '<span class="item-dot" style="background:' + originColor(idea) + '" title="' + escapeHtml(originLabel(idea)) + '"></span>' +
          '<span class="item-title">' + escapeHtml(idea.title) + '</span>' +
          (signBadges ? '<span class="item-signs">' + signBadges + '</span>' : '') +
          '<span class="item-caret">\\u25b8</span>';

        var body = document.createElement('div');
        body.className = 'item-body';
        body.hidden = true;
        var tags = (idea.tags || []).map(function (t) { return '<span class="item-tag">' + escapeHtml(t) + '</span>'; }).join('');
        // attachments physically live under <that project's own out_dir>/attachments/<id>/ --
        // in a single-project dashboard that's right alongside this file (attachments/<id>/...),
        // but the merged central view lives one level up from each project's own folder, so the
        // path needs that project segment too.
        var attachmentBase = (MULTI_PROJECT && idea.project ? encodeURIComponent(idea.project) + '/' : '') + 'attachments/';
        var evidence = attachments.map(function (a) {
          var href = attachmentBase + encodeURIComponent(idea.id) + '/' + encodeURIComponent(a.filename);
          var label = (DATA.attachmentLabel[a.type] || a.type) + ': ' + a.filename + (a.description ? ' \\u2014 ' + a.description : '');
          var preview = a.type === 'plot'
            ? '<a href="' + href + '" target="_blank" rel="noopener"><img class="item-evidence-thumb" src="' + href + '" alt="' + escapeHtml(a.filename) + '" loading="lazy"></a>'
            : '';
          return '<div class="item-evidence-row">' +
            '<span class="item-sign item-sign-' + escapeHtml(a.type) + '">' + escapeHtml(DATA.attachmentIcon[a.type] || '?') + '</span>' +
            '<a href="' + href + '" target="_blank" rel="noopener">' + escapeHtml(label) + '</a>' +
            preview +
            '</div>';
        }).join('');
        var metaBits = [idea.kind, idea.state, originLabel(idea)];
        if (MULTI_PROJECT && idea.project) metaBits.push('project: ' + idea.project);
        metaBits.push(idea.id);
        body.innerHTML =
          '<p class="item-summary">' + escapeHtml(idea.summary) + '</p>' +
          (idea.detail ? '<p class="item-detail">' + escapeHtml(idea.detail) + '</p>' : '') +
          (idea.snippet ? '<pre class="item-snippet"><code>' + escapeHtml(idea.snippet) + '</code></pre>' : '') +
          (idea.trigger ? '<p class="item-trigger"><strong>trigger:</strong> ' + escapeHtml(idea.trigger) + '</p>' : '') +
          '<p class="item-meta">' + metaBits.map(escapeHtml).join(' \\u00b7 ') + '</p>' +
          '<div class="item-tags">' + tags + '</div>' +
          (evidence ? '<div class="item-evidence">' + evidence + '</div>' : '');

        titleRow.addEventListener('click', function () {
          body.hidden = !body.hidden;
          titleRow.classList.toggle('open', !body.hidden);
        });

        item.appendChild(titleRow);
        item.appendChild(body);
        group.appendChild(item);
      });

      container.appendChild(group);
    });
  }

  function renderItemList(container, data) {
    if (!data.nodes.length) {
      var empty = document.createElement('p');
      empty.className = 'empty-note';
      empty.textContent = (DATA.nodes.length && (activeOrigin !== 'all' || activeProject !== 'all'))
        ? 'No ideas match this filter \\u2014 try a different one, or "All".'
        : 'No ideas captured yet. Run `brainny capture <entries.json>`.';
      container.appendChild(empty);
      return;
    }

    var wrap = document.createElement('div');
    wrap.className = 'item-list';

    if (MULTI_PROJECT) {
      var byProject = {};
      data.nodes.forEach(function (n) { var p = n.project || 'unknown'; (byProject[p] = byProject[p] || []).push(n); });
      Object.keys(byProject).sort().forEach(function (project) {
        var projGroup = document.createElement('div');
        projGroup.className = 'item-project-group';
        var projHeading = document.createElement('div');
        projHeading.className = 'item-project-heading';
        projHeading.textContent = project + ' (' + byProject[project].length + ')';
        projGroup.appendChild(projHeading);
        renderDomainGroups(projGroup, byProject[project]);
        wrap.appendChild(projGroup);
      });
    } else {
      renderDomainGroups(wrap, data.nodes);
    }

    container.appendChild(wrap);
  }

  // clicking an idea in a visualization calls this to open + scroll to its
  // entry in the itemized list, so the list is where its info actually shows
  var focusFlashTimer = null;
  function focusItem(id) {
    var el = document.querySelector('[data-item-id="' + CSS.escape(id) + '"]');
    if (!el) return;
    var row = el.querySelector('.item-title-row');
    var body = el.querySelector('.item-body');
    body.hidden = false;
    row.classList.add('open');
    el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    el.classList.remove('item-flash');
    void el.offsetWidth;
    el.classList.add('item-flash');
    clearTimeout(focusFlashTimer);
    focusFlashTimer = setTimeout(function () { el.classList.remove('item-flash'); }, 1400);
  }

  function refreshItemList() {
    var mount = document.getElementById('item-list-mount');
    mount.innerHTML = '';
    renderItemList(mount, filteredData());
  }
  refreshItemList();

  var vizEl = document.getElementById('viz');
  var tooltip = document.getElementById('tooltip');
  var descEl = document.getElementById('view-desc');

  var DESCRIPTIONS = {
    radial: 'Domains as branches radiating from the center; ideas as leaves at the rim. Simplest to scan for hierarchy.',
    force: 'Physics-based layout with an explicit colored halo per domain group, instead of relying on link topology alone to imply grouping.',
  };

  function showTooltip(event, html) {
    tooltip.innerHTML = html;
    tooltip.style.display = 'block';
    tooltip.style.left = (event.clientX + 14) + 'px';
    tooltip.style.top = (event.clientY + 14) + 'px';
  }
  function hideTooltip() { tooltip.style.display = 'none'; }

  function tooltipHtml(n) {
    var html = '<div class="tt-title">' + escapeHtml(n.name) + '</div>';
    if (n.kind === 'idea') {
      html += '<div class="tt-meta">' + escapeHtml(n.idea.kind) + ' \\u00b7 ' + escapeHtml(n.idea.state) + ' \\u00b7 click to view</div>';
    } else if (n.kind === 'branch') {
      html += '<div class="tt-meta">branch</div>';
    } else {
      html += '<div class="tt-meta">mother tree</div>';
    }
    return html;
  }

  // ---- view 1: radial tree ----
  function renderRadialTree() {
    var hierarchyData = buildHierarchy(filteredData());
    var root = d3.hierarchy(hierarchyData);

    var width = vizEl.clientWidth;
    var height = vizEl.clientHeight;
    var radius = Math.min(width, height) / 2 - 90;

    var tree = d3.tree().size([2 * Math.PI, radius])
      .separation(function (a, b) { return (a.parent === b.parent ? 1 : 2) / a.depth; });
    tree(root);

    var svg = d3.select(vizEl).append('svg').attr('viewBox', [-width / 2, -height / 2, width, height]);
    var g = svg.append('g');
    svg.call(d3.zoom().scaleExtent([0.4, 4]).on('zoom', function (event) { g.attr('transform', event.transform); }));

    function radialPoint(x, y) {
      return [y * Math.cos(x - Math.PI / 2), y * Math.sin(x - Math.PI / 2)];
    }

    g.append('g')
      .attr('fill', 'none')
      .attr('stroke', cssVar('--graph-link'))
      .selectAll('path')
      .data(root.links())
      .join('path')
      .attr('d', d3.linkRadial().angle(function (d) { return d.x; }).radius(function (d) { return d.y; }));

    var node = g.append('g')
      .selectAll('g')
      .data(root.descendants())
      .join('g')
      .attr('transform', function (d) {
        var p = radialPoint(d.x, d.y);
        return 'translate(' + p[0] + ',' + p[1] + ')';
      });

    node.append('circle')
      .attr('r', function (d) { return d.data.kind === 'idea' ? 4 + (d.data.value || 1) * 2 : d.data.kind === 'root' ? 7 : 5; })
      .attr('fill', function (d) {
        if (d.data.kind === 'root') return '#e8b23d';
        if (d.data.kind === 'branch') return '#7c8c6e';
        return DATA.kindColor[d.data.idea.kind] || '#8a8f98';
      })
      .attr('stroke', function (d) { return d.data.kind === 'idea' ? originColor(d.data.idea) : 'none'; })
      .attr('stroke-width', function (d) { return d.data.kind === 'idea' && isPromising(d.data.idea) ? 3 : 1.5; })
      .style('cursor', 'pointer')
      .on('mouseenter', function (event, d) { showTooltip(event, tooltipHtml(d.data)); })
      .on('mousemove', function (event, d) { showTooltip(event, tooltipHtml(d.data)); })
      .on('mouseleave', hideTooltip)
      .on('click', function (event, d) { if (d.data.kind === 'idea') focusItem(d.data.id); });

    node.append('text')
      .attr('dy', '0.31em')
      .attr('x', function (d) { return radialPoint(d.x, d.y)[0] < 0 ? -8 : 8; })
      .attr('text-anchor', function (d) { return radialPoint(d.x, d.y)[0] < 0 ? 'end' : 'start'; })
      .attr('fill', cssVar('--text-muted'))
      .style('font-size', '10px')
      .style('pointer-events', 'none')
      .text(function (d) { return d.data.kind === 'root' ? d.data.name : (d.data.name.length > 28 ? d.data.name.slice(0, 27) + '\\u2026' : d.data.name); });

    return function cleanup() {};
  }

  // ---- view 2: force network with cluster halos ----
  function renderForceClusters() {
    var hierarchyData = buildHierarchy(filteredData());
    var nodes = [];
    var links = [];
    var groupPalette = ['#3b6fd6', '#c9432c', '#2f9e5e', '#8b5cd6', '#d68a3b', '#3bb0d6', '#d63b8a'];
    var groupColor = {};
    var groupIdx = 0;

    (function walk(node, parent, group) {
      var thisGroup = group || (node.kind === 'branch' ? node.id : null);
      if (thisGroup && !(thisGroup in groupColor)) groupColor[thisGroup] = groupPalette[groupIdx++ % groupPalette.length];
      nodes.push({
        id: node.id, name: node.name, kind: node.kind,
        idea: node.idea || null, value: node.value || 0,
        group: node.kind === 'root' ? null : thisGroup,
      });
      if (parent) links.push({ source: parent.id, target: node.id });
      (node.children || []).forEach(function (c) { walk(c, node, thisGroup); });
    })(hierarchyData, null, null);

    var width = vizEl.clientWidth;
    var height = vizEl.clientHeight;

    var svg = d3.select(vizEl).append('svg').attr('viewBox', [0, 0, width, height]);
    var g = svg.append('g');
    var zoom = d3.zoom().scaleExtent([0.4, 4]).on('zoom', function (event) { g.attr('transform', event.transform); });
    svg.call(zoom);

    var hullLayer = g.append('g');
    var linkLayer = g.append('g');
    var nodeLayer = g.append('g');

    function radiusOf(d) {
      if (d.kind === 'root') return 12;
      if (d.kind === 'branch') return 7;
      return 5 + (d.value || 1) * 2.5;
    }

    function forceCluster(strength) {
      var n;
      function force(alpha) {
        var centroids = {};
        n.forEach(function (d) {
          if (!d.group) return;
          var c = centroids[d.group] || (centroids[d.group] = { x: 0, y: 0, count: 0 });
          c.x += d.x; c.y += d.y; c.count += 1;
        });
        Object.keys(centroids).forEach(function (k) { centroids[k].x /= centroids[k].count; centroids[k].y /= centroids[k].count; });
        n.forEach(function (d) {
          if (!d.group) return;
          var c = centroids[d.group];
          d.vx -= (d.x - c.x) * strength * alpha;
          d.vy -= (d.y - c.y) * strength * alpha;
        });
      }
      force.initialize = function (_) { n = _; };
      return force;
    }

    var simulation = d3.forceSimulation(nodes)
      .force('link', d3.forceLink(links).id(function (d) { return d.id; }).distance(38).strength(0.6))
      .force('charge', d3.forceManyBody().strength(-90))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('collide', d3.forceCollide().radius(function (d) { return radiusOf(d) + 4; }))
      .force('cluster', forceCluster(0.12));

    var link = linkLayer.selectAll('line').data(links).join('line').attr('stroke', cssVar('--graph-link'));

    var node = nodeLayer.selectAll('circle')
      .data(nodes)
      .join('circle')
      .attr('r', radiusOf)
      .attr('fill', function (d) {
        if (d.kind === 'root') return '#e8b23d';
        if (d.kind === 'branch') return '#7c8c6e';
        return DATA.kindColor[d.idea.kind] || '#8a8f98';
      })
      .attr('stroke', function (d) { return d.kind === 'idea' ? originColor(d.idea) : 'rgba(' + cssVar('--overlay-rgb') + ',0.15)'; })
      .attr('stroke-width', function (d) { return d.kind === 'idea' && isPromising(d.idea) ? 3 : 1.5; })
      .style('cursor', 'pointer')
      .on('mouseenter', function (event, d) { showTooltip(event, tooltipHtml(d)); })
      .on('mousemove', function (event, d) { showTooltip(event, tooltipHtml(d)); })
      .on('mouseleave', hideTooltip)
      .on('click', function (event, d) { if (d.kind === 'idea') focusItem(d.id); })
      .call(d3.drag()
        .on('start', function (event, d) { if (!event.active) simulation.alphaTarget(0.25).restart(); d.fx = d.x; d.fy = d.y; })
        .on('drag', function (event, d) { d.fx = event.x; d.fy = event.y; })
        .on('end', function (event, d) { if (!event.active) simulation.alphaTarget(0); d.fx = null; d.fy = null; }));

    function paddedHull(points, pad) {
      if (points.length === 0) return null;
      if (points.length < 3) {
        var cx = d3.mean(points, function (p) { return p[0]; });
        var cy = d3.mean(points, function (p) { return p[1]; });
        var steps = 12;
        return d3.range(steps).map(function (i) {
          var a = (i / steps) * Math.PI * 2;
          return [cx + Math.cos(a) * pad, cy + Math.sin(a) * pad];
        });
      }
      var hull = d3.polygonHull(points);
      if (!hull) return null;
      var centroid = d3.polygonCentroid(hull);
      return hull.map(function (p) {
        var dx = p[0] - centroid[0], dy = p[1] - centroid[1];
        var len = Math.sqrt(dx * dx + dy * dy) || 1;
        return [p[0] + (dx / len) * pad, p[1] + (dy / len) * pad];
      });
    }

    var lineGen = d3.line().curve(d3.curveCatmullRomClosed.alpha(0.7));

    function renderPositions() {
      link.attr('x1', function (d) { return d.source.x; }).attr('y1', function (d) { return d.source.y; })
        .attr('x2', function (d) { return d.target.x; }).attr('y2', function (d) { return d.target.y; });
      node.attr('cx', function (d) { return d.x; }).attr('cy', function (d) { return d.y; });

      var byGroup = {};
      nodes.forEach(function (d) {
        if (!d.group) return;
        (byGroup[d.group] = byGroup[d.group] || []).push([d.x, d.y]);
      });
      hullLayer.selectAll('path')
        .data(Object.keys(byGroup).map(function (k) { return [k, byGroup[k]]; }), function (d) { return d[0]; })
        .join('path')
        .attr('fill', function (d) { return groupColor[d[0]]; })
        .attr('fill-opacity', 0.08)
        .attr('stroke', function (d) { return groupColor[d[0]]; })
        .attr('stroke-opacity', 0.35)
        .attr('d', function (d) { return lineGen(paddedHull(d[1], 26)); });
    }

    function fitToViewport(animate) {
      var xs = nodes.map(function (d) { return d.x; }), ys = nodes.map(function (d) { return d.y; });
      var pad = 60;
      var x0 = Math.min.apply(null, xs) - pad, x1 = Math.max.apply(null, xs) + pad;
      var y0 = Math.min.apply(null, ys) - pad, y1 = Math.max.apply(null, ys) + pad;
      var scale = Math.min(4, 0.9 / Math.max((x1 - x0) / width, (y1 - y0) / height));
      var tx = width / 2 - scale * (x0 + x1) / 2;
      var ty = height / 2 - scale * (y0 + y1) / 2;
      var t = d3.zoomIdentity.translate(tx, ty).scale(scale);
      if (animate) svg.transition().duration(500).call(zoom.transform, t);
      else svg.call(zoom.transform, t);
    }

    // Pre-converge synchronously (a static force layout, computed with plain
    // .tick() calls instead of waiting on the simulation's own animation
    // timer) so the graph renders already-settled on the very first paint —
    // no animate-in delay for users, and no dependency on requestAnimationFrame
    // actually advancing (which headless browsers don't reliably do, unlike
    // real ones — screenshots of the live rAF-driven version came out with
    // the cluster barely spread apart because the simulation hadn't run yet).
    simulation.stop();
    for (var i = 0; i < 300; i++) simulation.tick();
    renderPositions();
    fitToViewport(false);

    // Resume live physics (softly) so drag interactions still feel right;
    // renderPositions/fitToViewport re-run per ongoing tick same as before.
    simulation.on('tick', renderPositions);
    simulation.on('end', function () { fitToViewport(true); });
    simulation.alpha(0.05).restart();

    return function cleanup() { simulation.stop(); };
  }

  // ---- stats tab: real, derived-from-timestamps cluster health ----
  // "growing" / "quiet" are honest proxies from real last_touched timestamps,
  // not a decay model — that's v0.1 (stats.py), not built yet (see SEED.md §7).
  var RECENT_MS = 3 * 24 * 3600 * 1000;
  var QUIET_MS = 14 * 24 * 3600 * 1000;

  function formatRelative(ts) {
    if (!ts) return 'never';
    var diff = Date.now() - ts;
    var mins = diff / 60000;
    if (mins < 1) return 'just now';
    if (mins < 60) return Math.round(mins) + 'm ago';
    var hours = mins / 60;
    if (hours < 24) return Math.round(hours) + 'h ago';
    var days = hours / 24;
    if (days < 30) return Math.round(days) + 'd ago';
    return Math.round(days / 30) + 'mo ago';
  }

  function buildDomainStats(data) {
    var now = Date.now();
    var byDomain = {};
    data.nodes.forEach(function (n) {
      var d = byDomain[n.domain] || (byDomain[n.domain] = {
        domain: n.domain, count: 0, recentCount: 0, kinds: {}, lastTouched: null, timestamps: [],
      });
      d.count += 1;
      d.kinds[n.kind] = (d.kinds[n.kind] || 0) + 1;
      var ts = n.lastTouched ? new Date(n.lastTouched).getTime() : null;
      if (ts) {
        d.timestamps.push(ts);
        if (!d.lastTouched || ts > d.lastTouched) d.lastTouched = ts;
        if (now - ts <= RECENT_MS) d.recentCount += 1;
      }
    });
    var domains = Object.keys(byDomain).map(function (k) { return byDomain[k]; });
    domains.forEach(function (d) {
      d.timestamps.sort(function (a, b) { return a - b; });
      var daysSince = d.lastTouched ? (now - d.lastTouched) / 86400000 : Infinity;
      if (d.recentCount > 0) d.trend = 'growing';
      else if (now - (d.lastTouched || 0) > QUIET_MS) d.trend = 'quiet';
      else d.trend = 'steady';
      d.daysSince = daysSince;
    });
    domains.sort(function (a, b) { return b.count - a.count; });
    return domains;
  }

  var TREND_LABEL = { growing: '\\u25b2 active', steady: '\\u2013 steady', quiet: '\\u25bc quiet' };
  var TREND_FILL = { growing: '#4f8f52', steady: '#5b6b63', quiet: '#8a4a3d' };

  function renderSparkline(mount, domainStat) {
    var w = 92, h = 22;
    var svg = d3.select(mount).append('svg').attr('width', w).attr('height', h).attr('class', 'spark');
    var pts = domainStat.timestamps;
    if (pts.length < 2) {
      svg.append('circle').attr('cx', w / 2).attr('cy', h / 2).attr('r', 2.5).attr('fill', TREND_FILL[domainStat.trend]);
      return;
    }
    var x = d3.scaleLinear().domain([pts[0], pts[pts.length - 1]]).range([2, w - 2]);
    var cumulative = pts.map(function (t, i) { return { t: t, y: i + 1 }; });
    var y = d3.scaleLinear().domain([0, cumulative[cumulative.length - 1].y]).range([h - 3, 3]);
    var line = d3.line().curve(d3.curveStepAfter).x(function (d) { return x(d.t); }).y(function (d) { return y(d.y); });
    svg.append('path').attr('d', line(cumulative)).attr('fill', 'none')
      .attr('stroke', TREND_FILL[domainStat.trend]).attr('stroke-width', 1.6);
  }

  function scrollToDomainGroup(domain) {
    switchTab('graph');
    setTimeout(function () {
      var group = document.querySelector('.item-group[data-domain="' + CSS.escape(domain) + '"]');
      if (!group) return;
      group.scrollIntoView({ behavior: 'smooth', block: 'start' });
      group.classList.remove('item-flash');
      void group.offsetWidth;
      group.classList.add('item-flash');
      setTimeout(function () { group.classList.remove('item-flash'); }, 1400);
    }, 0);
  }

  function goToIdea(id) {
    switchTab('graph');
    setTimeout(function () { focusItem(id); }, 0);
  }

  function renderTreemap(mount, domains) {
    var w = mount.clientWidth || 480;
    var h = 260;
    var svg = d3.select(mount).append('svg').attr('viewBox', [0, 0, w, h]).attr('width', '100%').attr('height', h);

    var root = d3.hierarchy({ children: domains })
      .sum(function (d) { return d.count || 0; })
      .sort(function (a, b) { return b.value - a.value; });
    d3.treemap().size([w, h]).paddingInner(3)(root);

    var cell = svg.selectAll('g').data(root.leaves()).join('g')
      .attr('class', 'tm-cell')
      .attr('transform', function (d) { return 'translate(' + d.x0 + ',' + d.y0 + ')'; })
      .style('cursor', 'pointer')
      .on('click', function (event, d) { scrollToDomainGroup(d.data.domain); })
      .on('mouseenter', function (event, d) {
        showTooltip(event, '<div class="tt-title">' + escapeHtml(d.data.domain) + '</div>' +
          '<div class="tt-meta">' + d.data.count + ' idea(s) \\u00b7 ' + TREND_LABEL[d.data.trend] +
          ' \\u00b7 last touched ' + escapeHtml(formatRelative(d.data.lastTouched)) + '</div>');
      })
      .on('mousemove', function (event) { showTooltip(event, tooltip.innerHTML); })
      .on('mouseleave', hideTooltip);

    cell.append('rect')
      .attr('width', function (d) { return Math.max(0, d.x1 - d.x0); })
      .attr('height', function (d) { return Math.max(0, d.y1 - d.y0); })
      .attr('fill', function (d) { return TREND_FILL[d.data.trend]; })
      .attr('fill-opacity', 0.85);

    cell.append('text').attr('x', 6).attr('y', 16)
      .text(function (d) {
        var w0 = d.x1 - d.x0;
        if (w0 < 40) return '';
        var name = d.data.domain;
        return name.length > 20 ? name.slice(0, 19) + '\\u2026' : name;
      });
    cell.append('text').attr('class', 'tm-count').attr('x', 6).attr('y', 30)
      .text(function (d) { return (d.x1 - d.x0) < 40 || (d.y1 - d.y0) < 34 ? '' : d.data.count + ' idea(s)'; });
  }

  function renderKindBars(mount, data) {
    var counts = {};
    data.nodes.forEach(function (n) { counts[n.kind] = (counts[n.kind] || 0) + 1; });
    var max = Math.max.apply(null, Object.keys(counts).map(function (k) { return counts[k]; }).concat([1]));
    var wrap = document.createElement('div');
    wrap.className = 'kind-bars';
    Object.keys(data.kindColor).forEach(function (kind) {
      var n = counts[kind] || 0;
      var row = document.createElement('div');
      row.className = 'kind-bar-row';
      row.innerHTML =
        '<span class="kind-bar-label">' + escapeHtml(kind) + '</span>' +
        '<span class="kind-bar-track"><span class="kind-bar-fill" style="width:' + (n / max * 100) +
        '%;background:' + data.kindColor[kind] + '"></span></span>' +
        '<span class="kind-bar-count">' + n + '</span>';
      wrap.appendChild(row);
    });
    mount.appendChild(wrap);
  }

  function renderOriginBars(mount, data) {
    var counts = { human: 0, ai: 0, collaborative: 0, unclassified: 0 };
    data.nodes.forEach(function (n) { counts[n.origin || 'unclassified'] += 1; });
    var max = Math.max.apply(null, Object.keys(counts).map(function (k) { return counts[k]; }).concat([1]));
    var wrap = document.createElement('div');
    wrap.className = 'kind-bars';
    ['human', 'ai', 'collaborative', 'unclassified'].forEach(function (key) {
      var n = counts[key];
      var color = key === 'unclassified' ? (data.unclassifiedColor || '#5c6b63') : (data.originColor[key] || '#5c6b63');
      var label = key === 'unclassified' ? 'unclassified' : (data.originLabel[key] || key);
      var row = document.createElement('div');
      row.className = 'kind-bar-row';
      row.innerHTML =
        '<span class="kind-bar-label">' + escapeHtml(label) + '</span>' +
        '<span class="kind-bar-track"><span class="kind-bar-fill" style="width:' + (n / max * 100) +
        '%;background:' + color + '"></span></span>' +
        '<span class="kind-bar-count">' + n + '</span>';
      wrap.appendChild(row);
    });
    mount.appendChild(wrap);
  }

  function renderRecentList(mount, data) {
    var withTs = data.nodes.filter(function (n) { return n.lastTouched; })
      .slice().sort(function (a, b) { return new Date(b.lastTouched) - new Date(a.lastTouched); })
      .slice(0, 8);
    var ul = document.createElement('ul');
    ul.className = 'recent-list';
    if (!withTs.length) {
      mount.innerHTML = '<p class="empty-note">Nothing captured yet.</p>';
      return;
    }
    withTs.forEach(function (n) {
      var li = document.createElement('li');
      li.className = 'recent-item';
      li.innerHTML =
        '<span class="ri-title">' + escapeHtml(n.title) + '</span>' +
        '<span class="ri-meta">' + escapeHtml(n.domain) + ' \\u00b7 ' + escapeHtml(formatRelative(new Date(n.lastTouched).getTime())) + '</span>';
      li.addEventListener('click', function () { goToIdea(n.id); });
      ul.appendChild(li);
    });
    mount.appendChild(ul);
  }

  var statsRendered = false;
  // ---- opportunities tab: AI-proposed combinations of ideas that could
  // support each other toward something bigger (SEED.md principle #1 --
  // "statistics propose, the AI adjudicates" at its purest: nothing here
  // is computed, every opportunity was a deliberate semantic judgment
  // call made by an assistant running the synthesis skill). ----
  function opportunityMatchesProjectFilter(opp) {
    if (activeProject === 'all') return true;
    var first = (opp.ideaIds || [])[0] || '';
    var project = first.indexOf('::') !== -1 ? first.split('::')[0] : null;
    return project === activeProject;
  }

  function renderOpportunitiesView() {
    var mount = document.getElementById('opportunities-main');
    mount.innerHTML = '';

    var byKey = {};
    DATA.nodes.forEach(function (n) { byKey[itemKey(n)] = n; });

    var opps = (DATA.opportunities || []).filter(opportunityMatchesProjectFilter);
    if (!opps.length) {
      mount.innerHTML = '<p class="empty-note" style="padding:2rem">' +
        ((DATA.opportunities || []).length
          ? 'No opportunities for this project filter \\u2014 try "All".'
          : 'No opportunities proposed yet. An assistant running the synthesis skill ' +
            '(<code>brainny propose</code>) looks over captured ideas for ones that genuinely ' +
            'support each other toward a tool, website, statistical module, or business idea ' +
            '\\u2014 most passes propose nothing, and that\\u2019s the common, correct outcome.') +
        '</p>';
      return;
    }

    opps = opps.slice().sort(function (a, b) { return b.weight - a.weight; });

    var wrap = document.createElement('div');
    wrap.className = 'opp-list';
    opps.forEach(function (opp) {
      var card = document.createElement('div');
      card.className = 'opp-card';
      var color = DATA.opportunityKindColor[opp.kind] || '#8a8f98';
      var kindLabel = DATA.opportunityKindLabel[opp.kind] || opp.kind;
      var pct = Math.round(opp.weight * 100);

      var chips = (opp.ideaIds || []).map(function (key) {
        var idea = byKey[key];
        var label = idea ? idea.title : key;
        return '<button type="button" class="opp-idea-chip" data-key="' + escapeHtml(key) + '">' +
          escapeHtml(label) + '</button>';
      }).join('');

      card.innerHTML =
        '<div class="opp-header">' +
        '<span class="opp-kind-badge" style="background:' + color + '22;color:' + color + ';border-color:' + color + '66">' + escapeHtml(kindLabel) + '</span>' +
        '<span class="opp-title">' + escapeHtml(opp.title) + '</span>' +
        '</div>' +
        '<div class="opp-weight-row">' +
        '<div class="opp-weight-track"><div class="opp-weight-fill" style="width:' + pct + '%;background:' + color + '"></div></div>' +
        '<span class="opp-weight-pct">' + pct + '%</span>' +
        '</div>' +
        '<p class="opp-summary">' + escapeHtml(opp.summary) + '</p>' +
        (opp.rationale ? '<p class="opp-rationale">' + escapeHtml(opp.rationale) + '</p>' : '') +
        '<div class="opp-ideas-label">built from</div>' +
        '<div class="opp-ideas">' + chips + '</div>';

      card.querySelectorAll('.opp-idea-chip').forEach(function (chip) {
        chip.addEventListener('click', function () {
          switchTab('graph');
          setTimeout(function () { focusItem(chip.dataset.key); }, 0);
        });
      });

      wrap.appendChild(card);
    });
    mount.appendChild(wrap);
  }

  function renderStatsView() {
    var mount = document.getElementById('stats-main');
    mount.innerHTML = '';
    var data = filteredData();
    if (!data.nodes.length) {
      mount.innerHTML = '<p class="empty-note" style="padding:2rem">' +
        ((DATA.nodes.length && activeOrigin !== 'all')
          ? 'No ' + escapeHtml(activeOrigin) + ' ideas yet \\u2014 try a different filter, or "All".'
          : 'No ideas captured yet \\u2014 nothing to show stats on.') +
        '</p>';
      return;
    }

    var domains = buildDomainStats(data);
    var recentTotal = data.nodes.filter(function (n) {
      return n.lastTouched && Date.now() - new Date(n.lastTouched).getTime() <= RECENT_MS;
    }).length;

    var cards = document.createElement('div');
    cards.className = 'stat-cards';
    [
      [data.nodes.length, 'ideas'],
      [domains.length, 'domains'],
      [data.sessions.length, 'sessions'],
      [recentTotal, 'new (3d)'],
      [domains.filter(function (d) { return d.trend === 'growing'; }).length, 'growing clusters'],
      [domains.filter(function (d) { return d.trend === 'quiet'; }).length, 'quiet clusters'],
    ].forEach(function (pair) {
      var card = document.createElement('div');
      card.className = 'stat-card';
      card.innerHTML = '<div class="stat-num">' + pair[0] + '</div><div class="stat-label">' + pair[1] + '</div>';
      cards.appendChild(card);
    });
    mount.appendChild(cards);

    var grid = document.createElement('div');
    grid.className = 'stats-grid';

    var left = document.createElement('div');
    left.className = 'stats-block';
    left.innerHTML = '<h2>domain treemap \\u2014 size = idea count, color = activity</h2><div id="treemap-mount"></div>' +
      '<p class="stats-caption">Click a cluster to jump to it in the Graph tab\\u2019s idea list.</p>';
    grid.appendChild(left);

    var right = document.createElement('div');
    right.className = 'stats-block';
    var tableRows = domains.map(function (d) {
      return '<tr data-domain="' + escapeHtml(d.domain) + '">' +
        '<td>' + escapeHtml(d.domain) + '</td>' +
        '<td>' + d.count + '</td>' +
        '<td><span class="trend-badge trend-' + d.trend + '">' + TREND_LABEL[d.trend] + '</span></td>' +
        '<td>' + escapeHtml(formatRelative(d.lastTouched)) + '</td>' +
        '<td><span id="spark-' + tableRows_i(d.domain) + '"></span></td>' +
        '</tr>';
    });
    right.innerHTML = '<h2>clusters, by activity</h2>' +
      '<table class="domain-table"><thead><tr><th>domain</th><th>ideas</th><th>trend</th><th>last touched</th><th>growth</th></tr></thead>' +
      '<tbody>' + tableRows.join('') + '</tbody></table>';
    grid.appendChild(right);

    mount.appendChild(grid);

    var bottom = document.createElement('div');
    bottom.className = 'stats-grid';
    bottom.style.marginTop = '1.4rem';
    var kindBlock = document.createElement('div');
    kindBlock.className = 'stats-block';
    kindBlock.innerHTML = '<h2>by kind</h2>';
    renderKindBars(kindBlock, data);
    bottom.appendChild(kindBlock);

    var originBlock = document.createElement('div');
    originBlock.className = 'stats-block';
    originBlock.innerHTML = '<h2>by origin \\u2014 who came up with it</h2>';
    renderOriginBars(originBlock, data);
    bottom.appendChild(originBlock);
    mount.appendChild(bottom);

    var bottom2 = document.createElement('div');
    bottom2.className = 'stats-grid';
    bottom2.style.marginTop = '1.4rem';
    var recentBlock = document.createElement('div');
    recentBlock.className = 'stats-block';
    recentBlock.innerHTML = '<h2>newest ideas</h2>';
    renderRecentList(recentBlock, data);
    bottom2.appendChild(recentBlock);
    mount.appendChild(bottom2);

    renderTreemap(document.getElementById('treemap-mount'), domains);
    domains.forEach(function (d) {
      var el = document.getElementById('spark-' + tableRows_i(d.domain));
      if (el) renderSparkline(el, d);
    });

    document.querySelectorAll('.domain-table tbody tr').forEach(function (tr) {
      tr.style.cursor = 'pointer';
      tr.addEventListener('click', function () { scrollToDomainGroup(tr.dataset.domain); });
    });
  }

  // stable per-domain DOM-safe id for sparkline mounts
  var _sparkIds = {};
  var _sparkIdSeq = 0;
  function tableRows_i(domain) {
    if (!(domain in _sparkIds)) _sparkIds[domain] = 'd' + (_sparkIdSeq++);
    return _sparkIds[domain];
  }

  // ---- brain tab: hierarchical edge-bundled connections, a probe that
  // circles gathering ideas into a live report, click-to-open into real
  // labeled circles. Ported from examples/viz-prototypes/12-neural-
  // bundle.html, which was built and refined standalone against a
  // fabricated demo dataset with its own DATA.nodes[].hasAttachment/
  // hasSnippet/opportunityCount fields and a own detail side-panel. This
  // port differs from that prototype in three deliberate ways:
  //   1. reads filteredData() (origin + project filters) like every other
  //      tab, instead of a fixed standalone DATA;
  //   2. derives evidence from the REAL payload fields (attachments[],
  //      snippet, and actual opportunity co-membership) instead of the
  //      prototype's precomputed convenience fields, which don't exist
  //      on the real dashboard payload;
  //   3. uses itemKey() for all idea identity (so it namespaces correctly
  //      on a merged multi-project central view, like every other view
  //      here) instead of the prototype's raw idea.id, and routes a leaf
  //      click to the existing Graph-tab item list (switchTab + focusItem)
  //      instead of duplicating a separate detail panel.
  // Because this view runs a requestAnimationFrame loop plus a couple of
  // setInterval/setTimeout timers and recursive D3 transitions, it needs
  // explicit teardown when the tab is left or re-rendered (filter change,
  // resize) -- see the `alive` flag below and brainCleanup().
  var brainCleanup = null;

  function renderBrainView() {
    if (brainCleanup) { brainCleanup(); brainCleanup = null; }
    var mount = document.getElementById('brain-main');
    mount.innerHTML = '';

    var data = filteredData();
    if (!data.nodes.length) {
      mount.innerHTML = '<p class="empty-note" style="padding:2rem">' +
        ((DATA.nodes.length && (activeOrigin !== 'all' || activeProject !== 'all'))
          ? 'No ideas match this filter \\u2014 try a different one, or "All".'
          : 'No ideas captured yet \\u2014 nothing to bundle into a brain yet.') +
        '</p>';
      return;
    }

    var alive = true;

    mount.innerHTML =
      '<svg id="brain-viz"></svg>' +
      '<div class="brain-caption"><strong>Brain view</strong> \\u2014 every connection (same kind, same domain, ' +
      'proven to combine in an Opportunity) bundled into one living mesh; a probe circles it gathering ideas into ' +
      'the report below, pausing to show readiness on ones with real evidence behind them. Click anywhere to open it.</div>' +
      '<div id="brain-report"><h3>Scanning\\u2026</h3><div id="brain-report-lines"></div></div>' +
      '<div id="brain-constellation"><div class="opp-kind"></div><div class="opp-title"></div><div class="opp-conf"></div></div>' +
      '<div id="brain-hint">Click the brain to open it \\u00b7 click a circle once open to jump to it</div>';

    function evidence(n) {
      var k = itemKey(n);
      return (n.attachments && n.attachments.length ? 1 : 0) + (n.snippet ? 1 : 0) + (oppCountByKey[k] || 0) * 1.6;
    }

    var byKey = {};
    data.nodes.forEach(function (n) { byKey[itemKey(n)] = n; });

    // project-filtered (not origin-filtered, matching renderOpportunitiesView's
    // convention) so a signal link only needs BOTH its endpoints to still be
    // present among the current (origin-filtered) leaves -- checked per-pair
    // below via byIdeaId, not by discarding the whole opportunity.
    var opps = (DATA.opportunities || []).filter(opportunityMatchesProjectFilter);
    var oppCountByKey = {};
    opps.forEach(function (opp) {
      (opp.ideaIds || []).forEach(function (k) { if (byKey[k]) oppCountByKey[k] = (oppCountByKey[k] || 0) + 1; });
    });

    var domains = Array.from(new Set(data.nodes.map(function (n) { return n.domain; }))).sort();
    var domainColor = d3.scaleOrdinal().domain(domains).range([
      '#e05a9a', '#e8b23d', '#3bb0a8', '#3b6fd6', '#c9432c', '#2f9e5e', '#8b5cd6',
      '#e07a3b', '#4fa8e0', '#c94fa0', '#7abf5e', '#d6c53b', '#5e7ac9', '#c96f5e',
    ]);

    var hierarchyData = {
      name: 'root',
      children: domains.map(function (dom) {
        return {
          name: dom,
          children: data.nodes.filter(function (n) { return n.domain === dom; }).map(function (n) {
            return { name: itemKey(n), idea: n };
          }),
        };
      }),
    };

    var mountEl = document.getElementById('brain-viz');
    var width = mount.clientWidth || 800;
    var height = mount.clientHeight || 600;
    var cx = width / 2, cy = height / 2;
    var outerR = Math.max(60, Math.min(width, height) / 2 - 60);

    var root = d3.hierarchy(hierarchyData);
    var cluster = d3.cluster().size([2 * Math.PI, outerR]);
    cluster(root);

    var leaves = root.leaves();
    var byIdeaId = {};
    leaves.forEach(function (l) { byIdeaId[itemKey(l.data.idea)] = l; });

    var linkSet = {}, localPairs = [], signalPairs = [];
    domains.forEach(function (dom) {
      var domLeaves = leaves.filter(function (l) { return l.data.idea.domain === dom; });
      for (var i = 0; i < domLeaves.length; i++) {
        for (var j = i + 1; j < domLeaves.length; j++) localPairs.push([domLeaves[i], domLeaves[j], 'local']);
      }
    });
    opps.forEach(function (opp) {
      var ids = (opp.ideaIds || []).filter(function (k) { return byIdeaId[k]; });
      for (var i = 0; i < ids.length; i++) {
        for (var j = i + 1; j < ids.length; j++) {
          var a = ids[i], b = ids[j];
          var key = [a, b].sort().join('|');
          if (linkSet[key]) continue;
          linkSet[key] = true;
          signalPairs.push([byIdeaId[a], byIdeaId[b], 'signal', opp.id]);
        }
      }
    });
    var byKind = {};
    leaves.forEach(function (l) { (byKind[l.data.idea.kind] = byKind[l.data.idea.kind] || []).push(l); });
    var kinshipPairs = [];
    Object.keys(byKind).forEach(function (k) {
      var group = byKind[k];
      for (var i = 0; i < group.length; i++) {
        kinshipPairs.push([group[i], group[(i + 1) % group.length], 'kinship']);
        if (group.length > 3) kinshipPairs.push([group[i], group[(i + 2) % group.length], 'kinship']);
      }
    });
    var pairs = kinshipPairs.concat(localPairs);

    var tagSetOf = {};
    data.nodes.forEach(function (n) { tagSetOf[itemKey(n)] = n.tags || []; });
    function sharedTagCount(aId, bId) {
      var a = tagSetOf[aId] || [], b = tagSetOf[bId] || [], c = 0;
      for (var i = 0; i < a.length; i++) if (b.indexOf(a[i]) !== -1) c++;
      return c;
    }
    var oppCoCount = {};
    opps.forEach(function (opp) {
      var ids = (opp.ideaIds || []).filter(function (k) { return byIdeaId[k]; });
      for (var i = 0; i < ids.length; i++) {
        for (var j = i + 1; j < ids.length; j++) {
          var k2 = [ids[i], ids[j]].sort().join('|');
          oppCoCount[k2] = (oppCoCount[k2] || 0) + 1;
        }
      }
    });
    var signalMeta = signalPairs.map(function (pr) {
      var aId = itemKey(pr[0].data.idea), bId = itemKey(pr[1].data.idea);
      var weight = (oppCoCount[[aId, bId].sort().join('|')] || 1) + sharedTagCount(aId, bId);
      return { weight: weight, pulses: Math.max(1, Math.min(4, weight)) };
    });

    var svg = d3.select(mountEl).attr('viewBox', [0, 0, width, height]).attr('width', '100%').attr('height', '100%');
    var g = svg.append('g').attr('transform', 'translate(' + cx + ',' + cy + ')');

    var rimG = g.append('g');
    domains.forEach(function (dom) {
      var domLeaves = leaves.filter(function (l) { return l.data.idea.domain === dom; });
      if (!domLeaves.length) return;
      var a0 = d3.min(domLeaves, function (l) { return l.x; }) - 0.01;
      var a1 = d3.max(domLeaves, function (l) { return l.x; }) + 0.01;
      var arc = d3.arc().innerRadius(outerR + 14).outerRadius(outerR + 14).startAngle(a0).endAngle(a1);
      var avgEvidence = d3.mean(domLeaves, function (l) { return evidence(l.data.idea); });
      var brightness = Math.min(1, avgEvidence / 2.2);
      var color = domainColor(dom);
      var arcEl = rimG.append('path').attr('class', 'rim-arc').attr('d', arc())
        .attr('stroke', color)
        .attr('stroke-width', 2 + brightness * 7)
        .attr('opacity', 0.16 + brightness * 0.84)
        .style('filter', brightness > 0.25 ? 'drop-shadow(0 0 ' + (2 + brightness * 9) + 'px ' + color + ')' : 'none');
      if (brightness > 0.25) {
        (function loopBreath() {
          if (!alive) return;
          arcEl.transition().duration(1400 + Math.random() * 600).attr('opacity', 0.16 + brightness * 0.5)
            .transition().duration(1400 + Math.random() * 600).attr('opacity', 0.16 + brightness * 0.84)
            .on('end', loopBreath);
        })();
      }
    });

    var linkG = g.append('g');
    var line = d3.lineRadial().angle(function (d) { return d.x; }).radius(function (d) { return d.y; }).curve(d3.curveBundle.beta(0.82));

    function linkType(d) { return d[2]; }
    var LINK_STYLE = {
      kinship: { color: function (d) { return DATA.kindColor[d[0].data.idea.kind] || '#8a8f98'; }, width: 0.8, opacity: 0.32 },
      local: { color: function (d) { return domainColor(d[0].data.idea.domain); }, width: 1.1, opacity: 0.4 },
      signal: { color: function () { return '#ffe08c'; }, width: 2, opacity: 0.7 },
    };
    var linkPaths = linkG.selectAll('path').data(pairs).join('path')
      .attr('class', 'bundle-link')
      .attr('stroke', function (d) { return LINK_STYLE[linkType(d)].color(d); })
      .attr('stroke-width', function (d) { return LINK_STYLE[linkType(d)].width; })
      .attr('opacity', function (d) { return LINK_STYLE[linkType(d)].opacity; });

    var signalPathSel = linkG.selectAll('path.signal').data(signalPairs).join('path')
      .attr('class', 'bundle-link signal')
      .attr('stroke', LINK_STYLE.signal.color())
      .attr('stroke-width', LINK_STYLE.signal.width)
      .attr('opacity', LINK_STYLE.signal.opacity);
    var signalPathNodes = signalPathSel.nodes();

    var pulseLayer = g.append('g');
    var pulses = [];
    signalMeta.forEach(function (meta, idx) {
      for (var k = 0; k < meta.pulses; k++) {
        ['fwd', 'back'].forEach(function (dir) {
          pulses.push({
            pathIndex: idx, dir: dir, phase: Math.random(), speed: 0.00028 + Math.random() * 0.00018,
            el: pulseLayer.append('circle').attr('r', 2.6).attr('fill', '#fff3d0')
              .style('filter', 'drop-shadow(0 0 5px #ffe08c) drop-shadow(0 0 2px #fff3d0)'),
          });
        });
      }
    });

    function leafXY(l, r) {
      var rad = r !== undefined ? r : l.y;
      var ang = l.x - Math.PI / 2;
      return [Math.cos(ang) * rad, Math.sin(ang) * rad];
    }

    var nodeG = g.append('g');
    var nodeSel = nodeG.selectAll('circle').data(leaves).join('circle')
      .attr('class', 'brain-leaf')
      .attr('r', function (l) { return 2 + Math.min(evidence(l.data.idea), 6); })
      .attr('fill', function (l) { return DATA.kindColor[l.data.idea.kind] || '#8a8f98'; })
      .attr('fill-opacity', 0.55)
      .attr('stroke', function (l) { return originColor(l.data.idea); })
      .attr('stroke-width', 1);

    var labelSel = nodeG.selectAll('text').data(leaves).join('text')
      .attr('class', 'brain-leaf-label').attr('opacity', 0)
      .text(function (l) { return l.data.idea.title.length > 30 ? l.data.idea.title.slice(0, 28) + '\\u2026' : l.data.idea.title; });

    function positionNodes() {
      nodeSel.attr('transform', function (l) { var p = leafXY(l); return 'translate(' + p[0] + ',' + p[1] + ')'; });
      labelSel.attr('transform', function (l) {
        var p = leafXY(l, l.y + 8);
        var deg = (l.x * 180 / Math.PI) - 90;
        var flip = l.x > Math.PI;
        return 'translate(' + p[0] + ',' + p[1] + ') rotate(' + (flip ? deg + 180 : deg) + ')';
      }).attr('text-anchor', function (l) { return l.x > Math.PI ? 'end' : 'start'; });
    }

    var opened = false, beta = 0.82;

    function bundlePath(d, t) {
      var path = d[0].path(d[1]).map(function (node, i) {
        var wob = opened ? 0 : Math.sin(t * 0.0009 + i) * 0.012;
        return { x: node.x + wob, y: node.y };
      });
      return line(path);
    }

    function render(t) {
      line.curve(d3.curveBundle.beta(beta));
      linkPaths.attr('d', function (d) { return bundlePath(d, t); });
      signalPathSel.attr('d', function (d) { return bundlePath(d, t); });
      positionNodes();
      updatePulses(t);
    }

    function updatePulses(t) {
      pulses.forEach(function (p) {
        var pathEl = signalPathNodes[p.pathIndex];
        if (!pathEl) return;
        var len = pathEl.getTotalLength();
        if (!len) return;
        var phase = (p.phase + t * p.speed) % 1;
        var frac = p.dir === 'fwd' ? phase : 1 - phase;
        var pt = pathEl.getPointAtLength(frac * len);
        p.el.attr('cx', pt.x).attr('cy', pt.y)
          .attr('opacity', opened ? 0.15 : (0.55 + 0.45 * Math.sin(phase * Math.PI)));
      });
    }

    // ---- scanning probe (old-tin-robot) + report ----
    var reportLines = document.getElementById('brain-report-lines');
    var reportedThisLap = {};
    var lapCount = 0;
    var MAX_LINES = 10;

    function addReportLine(html) {
      var div = document.createElement('div');
      div.className = 'line';
      div.innerHTML = html;
      reportLines.insertBefore(div, reportLines.firstChild);
      while (reportLines.children.length > MAX_LINES) reportLines.removeChild(reportLines.lastChild);
    }

    var templates = [
      function (n) { return 'Passing <b>' + escapeHtml(n.domain) + '</b> \\u2014 "' + escapeHtml(n.title) + '" (' + escapeHtml(n.kind) + ')'; },
      function (n) { return escapeHtml(n.kind) + ' from ' + escapeHtml(originLabel(n)) + ': "' + escapeHtml(n.title) + '"'; },
      function (n) { return 'Signal in <b>' + escapeHtml(n.domain) + '</b>: ' + escapeHtml(n.title.toLowerCase()); },
    ];

    var probeAngle = 0;
    var probeR = outerR + 30;
    var METAL = '#9aab97', METAL_DARK = '#5c6b63', LIGHT = '#ffe08c', LIGHT_BRIGHT = '#fff3d0';

    var TRAIL_LEN = 16;
    var trailG = g.append('g');
    var trailPts = [];
    var trailEls = [];
    for (var ti = 0; ti < TRAIL_LEN; ti++) trailEls.push(trailG.append('circle').attr('r', 0).attr('fill', LIGHT).attr('opacity', 0));

    var robot = g.append('g').attr('class', 'robot');
    robot.append('circle').attr('r', 15).attr('cy', -13).attr('fill', 'rgba(255,224,140,0.16)');
    robot.append('line').attr('x1', 0).attr('y1', -23).attr('x2', 0).attr('y2', -27).attr('stroke', METAL_DARK).attr('stroke-width', 1.3);
    robot.append('circle').attr('r', 1.6).attr('cy', -27.5).attr('fill', LIGHT).style('filter', 'drop-shadow(0 0 4px #ffe08c)');
    robot.append('rect').attr('x', -5).attr('y', -23).attr('width', 10).attr('height', 8).attr('rx', 1).attr('fill', METAL).attr('stroke', METAL_DARK).attr('stroke-width', 1);
    var eyeL = robot.append('rect').attr('x', -3.2).attr('y', -20.5).attr('width', 2.4).attr('height', 2.4).attr('fill', LIGHT).style('filter', 'drop-shadow(0 0 3px #ffe08c)');
    var eyeR = robot.append('rect').attr('x', 0.8).attr('y', -20.5).attr('width', 2.4).attr('height', 2.4).attr('fill', LIGHT).style('filter', 'drop-shadow(0 0 3px #ffe08c)');
    robot.append('rect').attr('x', -1.3).attr('y', -15).attr('width', 2.6).attr('height', 2).attr('fill', METAL_DARK);
    robot.append('rect').attr('x', -5.5).attr('y', -13).attr('width', 11).attr('height', 13).attr('rx', 1.5).attr('fill', METAL).attr('stroke', METAL_DARK).attr('stroke-width', 1);
    robot.append('circle').attr('r', 1.8).attr('cy', -7).attr('fill', LIGHT).attr('opacity', 0.85);
    robot.append('circle').attr('r', 0.8).attr('cx', -3.5).attr('cy', -3).attr('fill', METAL_DARK);
    robot.append('circle').attr('r', 0.8).attr('cx', 3.5).attr('cy', -3).attr('fill', METAL_DARK);

    var armL = robot.append('line').attr('stroke', METAL).attr('stroke-width', 2.6).attr('stroke-linecap', 'square');
    var armR = robot.append('line').attr('stroke', METAL).attr('stroke-width', 2.6).attr('stroke-linecap', 'square');
    var elbowL = robot.append('circle').attr('r', 1.3).attr('fill', METAL_DARK);
    var elbowR = robot.append('circle').attr('r', 1.3).attr('fill', METAL_DARK);
    var handL = robot.append('circle').attr('r', 2.4).attr('fill', LIGHT_BRIGHT).style('filter', 'drop-shadow(0 0 4px #ffe08c)');
    var handR = robot.append('circle').attr('r', 2.4).attr('fill', LIGHT_BRIGHT).style('filter', 'drop-shadow(0 0 4px #ffe08c)');
    var legL = robot.append('line').attr('stroke', METAL).attr('stroke-width', 2.8).attr('stroke-linecap', 'square');
    var legR = robot.append('line').attr('stroke', METAL).attr('stroke-width', 2.8).attr('stroke-linecap', 'square');
    var kneeL = robot.append('circle').attr('r', 1.3).attr('fill', METAL_DARK);
    var kneeR = robot.append('circle').attr('r', 1.3).attr('fill', METAL_DARK);
    var footL = robot.append('rect').attr('width', 5).attr('height', 2.4).attr('fill', METAL_DARK).attr('rx', 0.6);
    var footR = robot.append('rect').attr('width', 5).attr('height', 2.4).attr('fill', METAL_DARK).attr('rx', 0.6);

    var pctLabel = robot.append('text').attr('class', 'pct-label')
      .attr('text-anchor', 'middle').attr('font-size', 10).attr('font-weight', 700)
      .attr('fill', LIGHT_BRIGHT).style('paint-order', 'stroke').style('stroke', '#070c0a').style('stroke-width', '3px')
      .attr('opacity', 0);

    // Minimal angular distance, 0..PI -- NOT `Math.abs(a - b)` alone, which
    // breaks across the 0/2*PI wrap point.
    function angleDist(a, b) {
      var raw = Math.abs(a - b) % (Math.PI * 2);
      return raw > Math.PI ? Math.PI * 2 - raw : raw;
    }

    function limbEnd(pivotY, angRad, len) { return [Math.sin(angRad) * len, pivotY + Math.cos(angRad) * len]; }
    function placeFoot(rectSel, end, angRad) {
      rectSel.attr('transform', 'translate(' + end[0] + ',' + end[1] + ') rotate(' + (angRad * 180 / Math.PI) + ') translate(-2.5,-1.2)');
    }

    var shoulderY = -12, hipY = -1, armLen = 9, legLen = 10;
    function poseRobot(runPhase) {
      var swing = Math.sin(runPhase);
      var armSwing = swing * 0.9, legSwing = swing * 0.65;
      var aL = limbEnd(shoulderY, armSwing, armLen), aR = limbEnd(shoulderY, -armSwing, armLen);
      var lL = limbEnd(hipY, -legSwing, legLen), lR = limbEnd(hipY, legSwing, legLen);
      armL.attr('x1', 0).attr('y1', shoulderY).attr('x2', aL[0]).attr('y2', aL[1]);
      armR.attr('x1', 0).attr('y1', shoulderY).attr('x2', aR[0]).attr('y2', aR[1]);
      elbowL.attr('cx', aL[0] * 0.55).attr('cy', shoulderY + (aL[1] - shoulderY) * 0.55);
      elbowR.attr('cx', aR[0] * 0.55).attr('cy', shoulderY + (aR[1] - shoulderY) * 0.55);
      handL.attr('cx', aL[0]).attr('cy', aL[1]);
      handR.attr('cx', aR[0]).attr('cy', aR[1]);
      legL.attr('x1', 0).attr('y1', hipY).attr('x2', lL[0]).attr('y2', lL[1]);
      legR.attr('x1', 0).attr('y1', hipY).attr('x2', lR[0]).attr('y2', lR[1]);
      kneeL.attr('cx', lL[0] * 0.55).attr('cy', hipY + (lL[1] - hipY) * 0.55);
      kneeR.attr('cx', lR[0] * 0.55).attr('cy', hipY + (lR[1] - hipY) * 0.55);
      placeFoot(footL, lL, -legSwing);
      placeFoot(footR, lR, legSwing);
      return Math.abs(swing) * 2.2;
    }
    function poseIdle(t) {
      poseRobot(0);
      var shimmer = 0.75 + 0.25 * Math.sin(t * 0.006);
      eyeL.attr('opacity', shimmer); eyeR.attr('opacity', shimmer);
      return 0;
    }

    var readiness = {};
    data.nodes.forEach(function (n) { readiness[itemKey(n)] = Math.round(Math.min(1, evidence(n) / 4) * 100); });

    var stopUntilTs = -1;
    var showingPct = false;
    var rafId = null;

    function tick(t) {
      if (!alive) return;
      if (!opened) {
        var stopped = t < stopUntilTs;
        if (!stopped) {
          probeAngle += 0.004;
          if (probeAngle > Math.PI * 2) { probeAngle -= Math.PI * 2; lapCount++; reportedThisLap = {}; summarizeLap(); }
          if (showingPct) { showingPct = false; pctLabel.transition().duration(250).attr('opacity', 0); }
        }
        var pp = leafXY({ x: probeAngle, y: 1 }, probeR);
        var facingDeg = probeAngle * 180 / Math.PI;
        var bounce = stopped ? poseIdle(t) : poseRobot(t * 0.014);
        robot.attr('transform', 'translate(' + pp[0] + ',' + (pp[1] + bounce) + ') rotate(' + facingDeg + ')').attr('opacity', 1);
        pctLabel.attr('transform', 'translate(0,-32) rotate(' + (-facingDeg) + ')');

        if (!stopped) {
          trailPts.unshift([pp[0], pp[1] + bounce]);
          if (trailPts.length > TRAIL_LEN) trailPts.length = TRAIL_LEN;
        }
        trailEls.forEach(function (el, i) {
          var pt = trailPts[i];
          if (!pt) { el.attr('opacity', 0); return; }
          var frac = 1 - i / TRAIL_LEN;
          el.attr('cx', pt[0]).attr('cy', pt[1]).attr('r', 3.2 * frac).attr('opacity', 0.5 * frac * frac);
        });

        if (!stopped) {
          leaves.forEach(function (l) {
            var near = angleDist(l.x, probeAngle) < 0.035;
            var key = itemKey(l.data.idea);
            if (!near || reportedThisLap[key]) return;
            reportedThisLap[key] = true;
            var tmpl = templates[Math.floor(Math.random() * templates.length)];
            addReportLine(tmpl(l.data.idea));
            d3.select(nodeSel.nodes()[leaves.indexOf(l)]).attr('fill-opacity', 1).transition().duration(1200).attr('fill-opacity', 0.55);

            var pct = readiness[key];
            if (pct > 0) {
              stopUntilTs = t + 1100;
              showingPct = true;
              pctLabel.text(pct + '% ready').transition().duration(150).attr('opacity', 1);
            }
          });
        }
      } else {
        robot.attr('opacity', 0);
        if (trailPts.length) { trailPts.length = 0; trailEls.forEach(function (el) { el.attr('opacity', 0); }); }
      }
      render(t);
      rafId = requestAnimationFrame(tick);
    }

    function summarizeLap() {
      var byKindCount = {};
      data.nodes.forEach(function (n) { byKindCount[n.kind] = (byKindCount[n.kind] || 0) + 1; });
      var top = Object.keys(byKindCount).sort(function (a, b) { return byKindCount[b] - byKindCount[a]; })[0];
      document.querySelector('#brain-report h3').textContent = 'Lap ' + lapCount + ' complete \\u2014 ' + data.nodes.length + ' ideas \\u00b7 ' + domains.length + ' domains \\u00b7 mostly ' + top;
    }

    var oppCycleIndex = 0;
    var constellationHideTimer = null;
    function revealConstellation() {
      if (!alive || !opps.length) return;
      var opp = opps[oppCycleIndex % opps.length];
      oppCycleIndex++;
      var memberIds = {};
      (opp.ideaIds || []).forEach(function (id) { memberIds[id] = true; });

      nodeSel.filter(function (l) { return memberIds[itemKey(l.data.idea)]; })
        .transition().duration(350).attr('r', function (l) { return (5 + Math.min(evidence(l.data.idea), 6)) * 1.7; }).attr('fill-opacity', 1)
        .transition().delay(1700).duration(600)
        .attr('r', function (l) { return 2 + Math.min(evidence(l.data.idea), 6); }).attr('fill-opacity', 0.55);

      signalPathSel.filter(function (d) { return d[3] === opp.id; })
        .transition().duration(350).attr('stroke-width', 4.5).attr('opacity', 1)
        .transition().delay(1700).duration(600).attr('stroke-width', LINK_STYLE.signal.width).attr('opacity', LINK_STYLE.signal.opacity);

      var box = d3.select('#brain-constellation');
      box.select('.opp-kind').text((DATA.opportunityKindLabel && DATA.opportunityKindLabel[opp.kind]) || opp.kind.replace('-', ' '));
      box.select('.opp-title').text(opp.title);
      box.select('.opp-conf').text(Math.round(opp.weight * 100) + '% confidence \\u00b7 built from ' + (opp.ideaIds || []).length + ' ideas');
      box.style('opacity', 1);
      clearTimeout(constellationHideTimer);
      constellationHideTimer = setTimeout(function () { if (alive) box.style('opacity', 0); }, 2600);
    }

    var revealIntervalId = null;
    var revealStartTimer = setTimeout(function () {
      if (!alive) return;
      revealIntervalId = setInterval(function () { if (!opened) revealConstellation(); }, 6000);
    }, 2500);
    if (!opened) revealConstellation();

    rafId = requestAnimationFrame(tick);

    function animateBeta(to, ms) {
      var from = beta, start = null;
      function step(ts) {
        if (!alive) return;
        if (start === null) start = ts;
        var p = Math.min(1, (ts - start) / ms);
        beta = from + (to - from) * (1 - Math.pow(1 - p, 3));
        if (p < 1) requestAnimationFrame(step);
      }
      requestAnimationFrame(step);
    }

    svg.on('click', function (event) {
      if (event.target.tagName === 'circle' && event.target.__data__ && event.target.__data__.data) return;
      opened = !opened;
      animateBeta(opened ? 0.15 : 0.82, 900);
      labelSel.transition().duration(opened ? 700 : 200).delay(opened ? 300 : 0).attr('opacity', opened ? 1 : 0);
      nodeSel.transition().duration(500).attr('r', function (l) { return opened ? 5 + Math.min(evidence(l.data.idea), 6) * 1.3 : 2 + Math.min(evidence(l.data.idea), 6); });
      linkPaths.transition().duration(700).attr('opacity', function (d) {
        var base = LINK_STYLE[linkType(d)].opacity;
        return opened ? base * 0.35 : base;
      });
      signalPathSel.transition().duration(700).attr('opacity', opened ? LINK_STYLE.signal.opacity * 0.5 : LINK_STYLE.signal.opacity);
      var reportEl = document.getElementById('brain-report');
      if (reportEl) reportEl.style.display = opened ? 'none' : 'block';
    });

    nodeSel.on('click', function (event, l) {
      if (!opened) return;
      event.stopPropagation();
      switchTab('graph');
      var key = itemKey(l.data.idea);
      setTimeout(function () { focusItem(key); }, 0);
    });

    brainCleanup = function cleanup() {
      alive = false;
      if (rafId !== null) cancelAnimationFrame(rafId);
      clearTimeout(revealStartTimer);
      if (revealIntervalId !== null) clearInterval(revealIntervalId);
      clearTimeout(constellationHideTimer);
    };
  }

  // ---- network tab: the central brain (this central folder's merged
  // view, or just this one project when nothing else is synced into it
  // yet) with a small brain per connected project -- literally what's
  // feeding it ideas, per the user's own framing. Deliberately static
  // (no probe, no requestAnimationFrame loop) -- a map to click around
  // in, not another performance; nothing here needs the teardown
  // machinery the Brain tab needs. Clicking a project sets the same
  // `activeProject` filter the dropdown does (and vice versa -- the
  // dropdown and this view always agree on the current filter);
  // clicking the hub clears it.
  function renderNetworkView() {
    var mount = document.getElementById('network-main');
    mount.innerHTML = '';

    if (!DATA.nodes.length) {
      mount.innerHTML = '<p class="empty-note" style="padding:2rem">No ideas captured yet \\u2014 nothing connected to the central brain yet.</p>';
      return;
    }

    var data = filteredData();
    var byProject = {};
    data.nodes.forEach(function (n) { var p = n.project || 'unknown'; byProject[p] = (byProject[p] || 0) + 1; });
    var projects = (DATA.projects && DATA.projects.length) ? DATA.projects.slice() : Object.keys(byProject).sort();

    var soloNote = projects.length <= 1
      ? ' Only one project is synced here so far \\u2014 run <code>brainny sync</code> from another project (pointed at the same central folder) to see it join.'
      : '';
    mount.innerHTML =
      '<div class="network-caption"><strong>Network</strong> \\u2014 the central brain, and every project connected to it. ' +
      'Click a project to filter the whole dashboard to it; click the center to clear the filter.' + soloNote + '</div>' +
      '<svg id="network-viz"></svg>';

    var width = mount.clientWidth || 800;
    var height = mount.clientHeight || 600;
    var cx = width / 2, cy = height / 2;
    var ringR = Math.max(90, Math.min(width, height) / 2 - 100);
    var hubR = 34;
    var iconHref = document.getElementById('brand-icon').getAttribute('src');
    var maxCount = Math.max(1, projects.reduce(function (m, p) { return Math.max(m, byProject[p] || 0); }, 0));

    var nodesData = projects.map(function (p, i) {
      var angle = projects.length === 1 ? -Math.PI / 2 : (i / projects.length) * Math.PI * 2 - Math.PI / 2;
      var count = byProject[p] || 0;
      return {
        project: p, count: count, r: 14 + (count / maxCount) * 22,
        x: Math.cos(angle) * ringR, y: Math.sin(angle) * ringR,
      };
    });

    var svg = d3.select('#network-viz').attr('viewBox', [0, 0, width, height]).attr('width', '100%').attr('height', '100%');
    var g = svg.append('g').attr('transform', 'translate(' + cx + ',' + cy + ')');

    g.append('g').selectAll('path').data(nodesData).join('path')
      .attr('class', 'network-link')
      .attr('d', function (d) { return 'M0,0 Q' + (d.x * 0.5) + ',' + (d.y * 0.5) + ' ' + d.x + ',' + d.y; })
      .attr('stroke', function (d) { return d.count > 0 ? '#e8b23d' : 'rgba(var(--overlay-rgb),0.3)'; })
      .attr('stroke-width', function (d) { return d.count > 0 ? 1.2 + (d.count / maxCount) * 2.6 : 1; })
      .attr('opacity', function (d) {
        if (activeProject !== 'all' && activeProject !== d.project) return 0.12;
        return d.count > 0 ? 0.65 : 0.3;
      });

    var hub = g.append('g').attr('class', 'network-node')
      .on('click', function () { setActiveProject('all'); })
      .on('mouseenter', function (event) { showTooltip(event, '<div class="tt-title">central brain</div><div class="tt-meta">' + DATA.nodes.length + ' idea(s) \\u00b7 ' + projects.length + ' project(s) \\u00b7 click to clear the project filter</div>'); })
      .on('mousemove', function (event) { showTooltip(event, '<div class="tt-title">central brain</div><div class="tt-meta">' + DATA.nodes.length + ' idea(s) \\u00b7 ' + projects.length + ' project(s) \\u00b7 click to clear the project filter</div>'); })
      .on('mouseleave', hideTooltip);
    hub.append('circle').attr('r', hubR + 6).attr('fill', 'rgba(232,178,61,0.12)');
    hub.append('circle').attr('r', hubR).attr('fill', '#111a14')
      .attr('stroke', activeProject === 'all' ? '#e8b23d' : 'rgba(232,178,61,0.5)')
      .attr('stroke-width', activeProject === 'all' ? 2.6 : 1.6);
    hub.append('image').attr('href', iconHref)
      .attr('x', -hubR * 0.62).attr('y', -hubR * 0.62).attr('width', hubR * 1.24).attr('height', hubR * 1.24);
    hub.append('text').attr('class', 'network-hub-label').attr('y', hubR + 20).text('central brain');
    hub.append('text').attr('class', 'network-count').attr('y', hubR + 34)
      .text(DATA.nodes.length + ' idea(s) \\u00b7 ' + projects.length + ' project(s)');

    g.append('g').selectAll('g').data(nodesData).join('g')
      .attr('class', function (d) { return 'network-node' + (activeProject !== 'all' && activeProject !== d.project ? ' dimmed' : ''); })
      .attr('transform', function (d) { return 'translate(' + d.x + ',' + d.y + ')'; })
      .on('click', function (event, d) { setActiveProject(activeProject === d.project ? 'all' : d.project); })
      .on('mouseenter', function (event, d) { showTooltip(event, '<div class="tt-title">' + escapeHtml(d.project) + '</div><div class="tt-meta">' + d.count + ' idea(s) currently shown \\u00b7 click to filter</div>'); })
      .on('mousemove', function (event, d) { showTooltip(event, '<div class="tt-title">' + escapeHtml(d.project) + '</div><div class="tt-meta">' + d.count + ' idea(s) currently shown \\u00b7 click to filter</div>'); })
      .on('mouseleave', hideTooltip)
      .call(function (sel) {
        sel.append('circle').attr('r', function (d) { return d.r + 5; }).attr('fill', 'rgba(59,111,214,0.1)');
        sel.append('circle').attr('r', function (d) { return d.r; }).attr('fill', '#111a14')
          .attr('stroke', function (d) { return activeProject === d.project ? '#e8b23d' : 'rgba(59,111,214,0.55)'; })
          .attr('stroke-width', function (d) { return activeProject === d.project ? 2.4 : 1.4; });
        sel.append('image').attr('href', iconHref)
          .attr('x', function (d) { return -d.r * 0.62; }).attr('y', function (d) { return -d.r * 0.62; })
          .attr('width', function (d) { return d.r * 1.24; }).attr('height', function (d) { return d.r * 1.24; });
        sel.append('text').attr('class', 'network-label').attr('y', function (d) { return d.r + 16; })
          .text(function (d) { return d.project.length > 22 ? d.project.slice(0, 20) + '\\u2026' : d.project; });
        sel.append('text').attr('class', 'network-count').attr('y', function (d) { return d.r + 30; })
          .text(function (d) { return d.count + ' idea(s)'; });
      });
  }

  // ---- dropdown + tab wiring ----
  var VIEWS = { radial: renderRadialTree, force: renderForceClusters };
  var currentCleanup = null;

  function switchView(name) {
    if (currentCleanup) currentCleanup();
    vizEl.innerHTML = '';
    hideTooltip();
    descEl.textContent = DESCRIPTIONS[name];
    if (filteredData().nodes.length) {
      currentCleanup = VIEWS[name]();
    } else {
      currentCleanup = null;
      var empty = document.createElement('p');
      empty.className = 'empty-note';
      empty.style.padding = '2rem';
      empty.textContent = (DATA.nodes.length && activeOrigin !== 'all')
        ? 'No ' + activeOrigin + ' ideas yet \\u2014 try a different filter, or "All".'
        : 'No ideas captured yet \\u2014 just the mother tree. Run `brainny capture <entries.json>`.';
      vizEl.appendChild(empty);
    }
  }

  var select = document.getElementById('view-select');
  select.addEventListener('change', function () { switchView(select.value); });

  var activeTab = 'graph';
  function switchTab(name) {
    if (name === activeTab) return;
    if (activeTab === 'brain' && brainCleanup) { brainCleanup(); brainCleanup = null; }
    activeTab = name;
    document.querySelectorAll('.tab-btn').forEach(function (b) { b.classList.toggle('active', b.dataset.tab === name); });
    document.getElementById('graph-main').hidden = name !== 'graph';
    document.getElementById('stats-main').hidden = name !== 'stats';
    document.getElementById('opportunities-main').hidden = name !== 'opportunities';
    document.getElementById('brain-main').hidden = name !== 'brain';
    document.getElementById('network-main').hidden = name !== 'network';
    select.style.display = name === 'graph' ? '' : 'none';
    descEl.hidden = name !== 'graph';
    if (name === 'stats') {
      renderStatsView();
    } else if (name === 'opportunities') {
      renderOpportunitiesView();
    } else if (name === 'brain') {
      renderBrainView();
    } else if (name === 'network') {
      renderNetworkView();
    } else if (!currentCleanup && filteredData().nodes.length) {
      switchView(select.value);
    }
  }
  document.querySelectorAll('.tab-btn').forEach(function (b) {
    b.addEventListener('click', function () { switchTab(b.dataset.tab); });
  });

  function applyOriginFilterUI() {
    document.querySelectorAll('.origin-btn').forEach(function (b) {
      var on = b.dataset.origin === activeOrigin;
      b.classList.toggle('active', on);
      var color = b.dataset.color;
      if (on && color) {
        b.style.background = color + '29'; // ~16% alpha, hex shorthand
        b.style.borderColor = color;
        b.style.color = 'var(--fg)';
      } else if (on) {
        b.style.background = 'rgba(var(--overlay-rgb),0.14)';
        b.style.borderColor = 'rgba(var(--overlay-rgb),0.3)';
        b.style.color = 'var(--fg)';
      } else {
        b.style.background = '';
        b.style.borderColor = '';
        b.style.color = '';
      }
    });
  }

  function refreshActiveTab() {
    if (activeTab === 'stats') renderStatsView();
    else if (activeTab === 'opportunities') renderOpportunitiesView();
    else if (activeTab === 'brain') renderBrainView();
    else if (activeTab === 'network') renderNetworkView();
    else switchView(select.value);
  }

  document.querySelectorAll('.origin-btn').forEach(function (b) {
    b.addEventListener('click', function () {
      activeOrigin = b.dataset.origin;
      applyOriginFilterUI();
      refreshItemList();
      refreshActiveTab();
    });
  });
  applyOriginFilterUI();

  // shared by the project <select> (when this is a merged multi-project
  // view) and the Network tab's clickable nodes -- both just need to
  // agree on `activeProject` and stay in sync with each other.
  var projectSelect = document.getElementById('project-filter');
  function setActiveProject(project) {
    activeProject = project;
    if (projectSelect) projectSelect.value = project;
    refreshItemList();
    refreshActiveTab();
  }
  if (projectSelect) {
    projectSelect.addEventListener('change', function () { setActiveProject(projectSelect.value); });
  }

  switchView(select.value);

  window.addEventListener('resize', function () {
    if (activeTab === 'graph') switchView(select.value);
    else if (activeTab === 'stats') renderStatsView();
    else if (activeTab === 'brain') renderBrainView();
    else if (activeTab === 'network') renderNetworkView();
  });

  // ---- day/night theme toggle: localStorage persists an explicit choice;
  // absent that, prefers-color-scheme decides. The actual [data-theme]
  // attribute is already set by a tiny inline script in <head> (before
  // this script runs, before first paint) -- this just wires the button
  // and keeps localStorage in sync with further clicks. ----
  var themeToggle = document.getElementById('theme-toggle');
  if (themeToggle) {
    function currentTheme() { return document.documentElement.getAttribute('data-theme') === 'light' ? 'light' : 'dark'; }
    function setThemeIcon() { themeToggle.textContent = currentTheme() === 'light' ? '\\u2600' : '\\u263e'; }
    setThemeIcon();
    themeToggle.addEventListener('click', function () {
      var next = currentTheme() === 'light' ? 'dark' : 'light';
      document.documentElement.setAttribute('data-theme', next);
      try { localStorage.setItem('brainny-theme', next); } catch (e) { /* private browsing etc -- theme just won't persist */ }
      setThemeIcon();
      // most chrome colors are CSS vars and update instantly via the
      // cascade, but a few (graph link strokes/labels) are baked into an
      // SVG attribute at render time via cssVar() -- re-render the
      // current tab so those pick up the new theme's resolved colors too.
      refreshActiveTab();
    });
  }
})();
"""


def render_html(graph: Graph, opportunities: Opportunities | None = None, title: str = "brainny") -> str:
    """Render graph.json (+ opportunities.json) as a navigable dashboard
    (D3, vendored inline — see `_D3_JS` above, no CDN/network dependency)
    with four tabs, and a day/night theme toggle (top-right of the header)
    that applies to all of them — an explicit choice persists via
    localStorage, defaulting to the OS's prefers-color-scheme; the light
    palette is a soft warm tone deliberately, not stark white. Graph tab: a dropdown switches between a radial tree
    (domains branching from a center, ideas as rim leaves) and a
    force-directed network with a colored halo per domain group, alongside
    an itemized accordion list (click a title to unfold
    summary/detail/trigger/tags). Clicking an idea in either graph opens +
    scrolls to its entry in the list. Ideas are sized/highlighted by
    growth state and kind — real fields, but inert until v0.1
    (dedup.py/stats.py) makes recurrence/state actually vary. Stats tab: a
    domain treemap (size = idea count, color = activity) plus a
    per-cluster table, kind breakdown, and a newest-ideas feed — all
    derived from real timestamps/domains/kinds (no fabricated data), with
    "growing"/"quiet" as an honest recency proxy rather than the real
    decay/novelty model v0.1 will bring. Clicking a cluster jumps to it in
    the Graph tab's idea list. Opportunities tab: AI-proposed combinations
    of ideas that could support each other toward something bigger (a
    tool, website, statistical module, business idea) — see
    opportunities.py/SEED.md principle #1; empty and hidden when there are
    none, since most projects won't have any. Brain tab: every idea as a
    hierarchical edge-bundled mesh that resolves into a living brain
    silhouette (no literal neuron dots) — kinship (same kind), local
    (same domain), and signal (proven to combine in an Opportunity, the
    brightest layer, with animated bidirectional synapse pulses) links
    layered together; an old-robot probe circles it continuously,
    stopping to show a percent-ready readout on ideas with real evidence
    behind them, and gathering a live scrolling report as it passes.
    Click anywhere to open the mesh into real, labeled, clickable idea
    circles — clicking one jumps to it in the Graph tab's list, same as
    every other view. See renderBrainView() in the JS below for exactly
    how this differs from the standalone prototype it was ported from
    (examples/viz-prototypes/12-neural-bundle.html). Network tab: the
    central brain (this central folder's merged view, or just this one
    project when nothing else is synced into it yet) with a small brain
    per connected project, sized by how many of its ideas are currently
    shown — literally what's feeding the central brain, and how much.
    Static, not animated. Clicking a project sets the same project filter
    the dropdown does (and vice versa); clicking the center clears it.
    Falls back to the plain terminal tree in the (now near-impossible)
    case the embedded D3 fails to execute. No server involved — a
    static, self-contained, git-shareable file that renders identically
    with zero network access."""
    if opportunities is None:
        opportunities = Opportunities()

    payload = _build_payload(graph, opportunities, title)
    data_json = json.dumps(payload, ensure_ascii=False).replace("</", "<\\/")

    kind_legend = "".join(
        f'<span class="legend-item"><span class="dot" style="background:{color}"></span>{_esc(kind)}</span>'
        for kind, color in KIND_COLOR.items()
    )
    state_legend = "".join(
        f'<span class="legend-item"><span class="dot state-dot state-{_esc(state)}"></span>{_esc(meta["label"])}</span>'
        for state, meta in STATE_META.items()
    )

    origin_buttons = ['<button type="button" class="origin-btn active" data-origin="all">All</button>']
    for origin, color in ORIGIN_COLOR.items():
        label = _esc(ORIGIN_LABEL[origin])
        origin_buttons.append(
            f'<button type="button" class="origin-btn" data-origin="{origin}" data-color="{color}">'
            f'<span class="dot" style="background:{color}"></span>{label}</button>'
        )
    origin_buttons.append(
        f'<button type="button" class="origin-btn" data-origin="unclassified" data-color="{UNCLASSIFIED_COLOR}">'
        f'<span class="dot" style="background:{UNCLASSIFIED_COLOR}"></span>unclassified</button>'
    )
    origin_filter_html = "".join(origin_buttons)

    projects = payload["projects"]
    multi_project = len(projects) > 1
    project_filter_html = ""
    if multi_project:
        project_options = "".join(f'<option value="{_esc(p)}">{_esc(p)}</option>' for p in projects)
        project_filter_html = (
            '<label for="project-filter" style="color:var(--text-dimmer);font-size:0.82rem">project</label>'
            f'<select id="project-filter"><option value="all">All ({len(projects)})</option>{project_options}</select>'
        )

    subtitle = (
        f"{len(graph.nodes)} idea(s) · {payload['domainCount']} branch(es), "
        f"grown over {len(payload['sessions'])} session(s)"
        + (f" across {len(projects)} project(s)" if multi_project else "")
        if graph.nodes
        else "No ideas captured yet — just the mother tree."
    )
    project_note = (
        " This is the merged central view — every project synced into the central folder, "
        "shown together (concatenated, not deduplicated yet; that's still v0.4 work per SEED.md). "
        "Use the <strong>project</strong> dropdown above to narrow to one."
        if multi_project
        else ""
    )

    head = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{_esc(title)}</title>
<link rel="icon" type="image/png" href="data:image/png;base64,{_ICON_PNG_B64}">
<style>{_CSS}</style>
<script>
// Sets [data-theme] before first paint -- an explicit prior choice
// (localStorage) wins, otherwise prefers-color-scheme decides. Runs
// synchronously in <head> specifically to avoid a flash of the wrong
// theme; see #theme-toggle's wiring at the end of the main script for
// what happens on further clicks.
(function () {{
  var saved = null;
  try {{ saved = localStorage.getItem('brainny-theme'); }} catch (e) {{ /* private browsing etc */ }}
  var theme = saved === 'light' || saved === 'dark'
    ? saved
    : (window.matchMedia && window.matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark');
  document.documentElement.setAttribute('data-theme', theme);
}})();
</script>
</head>
"""

    body_open = f"""<body>
<header>
  <div class="row">
    <img id="brand-icon" src="data:image/png;base64,{_ICON_PNG_B64}" alt="">
    <h1>{_esc(title)}</h1>
    <nav id="tab-bar">
      <button type="button" class="tab-btn active" data-tab="graph">Graph</button>
      <button type="button" class="tab-btn" data-tab="stats">Stats</button>
      <button type="button" class="tab-btn" data-tab="opportunities">Opportunities{f' ({len(opportunities.items)})' if opportunities.items else ''}</button>
      <button type="button" class="tab-btn" data-tab="brain">Brain</button>
      <button type="button" class="tab-btn" data-tab="network">Network</button>
    </nav>
    <select id="view-select">
      <option value="radial">Radial tree</option>
      <option value="force">Force network with cluster halos</option>
    </select>
    <button type="button" id="theme-toggle" title="Toggle day/night theme" aria-label="Toggle day/night theme">&#9789;</button>
  </div>
  <div class="row" style="margin-top:0.5rem">
    <nav id="origin-filter">{origin_filter_html}</nav>
    {f'<div id="project-filter-row">{project_filter_html}</div>' if project_filter_html else ""}
  </div>
  <p id="view-desc"></p>
  <p class="note">{_esc(subtitle)} · sizing/highlighting uses the real <code>recurrence</code>/<code>state</code> fields, but v0.1 (dedup/stats) doesn't exist yet — every idea is currently <code>recurrence: 1</code>, <code>state: "seed"</code>, so nothing visibly stands out yet. Click any idea to jump to it in the list. The <strong>human / AI / collaborative</strong> filter above shows who actually originated each idea — the human supplies direction and innovation, the AI supplies collective/pattern knowledge, and a lot of real work is both.{project_note}</p>
</header>
<main id="graph-main">
  <div id="panel">
    <h2>legend</h2>
    <div class="legend-row">{kind_legend}</div>
    <div class="legend-row">{state_legend}</div>
    <h2>ideas</h2>
    <div id="item-list-mount"></div>
  </div>
  <div id="viz"></div>
</main>
<main id="stats-main" hidden></main>
<main id="opportunities-main" hidden></main>
<main id="brain-main" hidden></main>
<main id="network-main" hidden></main>
<div id="tooltip"></div>
<pre id="fallback" hidden>{_esc(render_tree(graph))}</pre>
<script id="brainny-data" type="application/json">"""

    d3_js = _D3_JS.replace("</", "<\\/")
    scripts = f"""</script>
<script>{d3_js}</script>
<script>{_JS}</script>
</body>
</html>
"""

    return head + body_open + data_json + scripts


def save_html(graph: Graph, out_dir: Path = DEFAULT_OUT_DIR, title: str = "brainny") -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    path = html_path(out_dir)
    # opportunities.json lives alongside graph.json in the same out_dir --
    # loaded transparently here so every existing save_html() call site
    # (capture/attach/sync/reassign/central/query) picks up the
    # Opportunities tab automatically, with no changes needed at any of
    # them.
    opportunities = load_opportunities(out_dir)
    path.write_text(render_html(graph, opportunities, title=title), encoding="utf-8")
    return path
