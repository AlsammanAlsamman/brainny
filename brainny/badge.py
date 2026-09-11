"""A small, optional, embeddable activity badge -- meant for a GitHub
profile README, not the dashboard. Deliberately shows counts and shape
only (kind breakdown, skills, domains, projects, recent activity) and
NEVER idea content (no titles/summaries/detail) -- a profile README is
public, the graph itself usually isn't.

Not "novelty" -- that's stats.py's unbuilt v0.1 decay/novelty model (see
SEED.md §7); showing a fake novelty number here would be dishonest. What
IS real and shown instead: a recent-activity count using the same 3-day
"recent" window viz.py's own Stats tab already uses for its growing/quiet
trend badges (see viz.py's RECENT_MS), so the two stay consistent.
"""

from __future__ import annotations

import html as htmllib
from collections import Counter
from datetime import datetime, timezone

from brainny.schema import Graph
from brainny.viz import KIND_COLOR, _ICON_PNG_B64

RECENT_DAYS = 3


def _esc(s: str) -> str:
    return htmllib.escape(str(s), quote=True)


def _parse_ts(ts: str | None) -> datetime | None:
    if not ts:
        return None
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except ValueError:
        return None


def compute_badge_stats(graph: Graph) -> dict:
    now = datetime.now(timezone.utc)
    by_kind: Counter = Counter(n.kind for n in graph.nodes)
    domains = {n.domain for n in graph.nodes}
    projects = {p.project for n in graph.nodes for p in n.provenance}
    recent = 0
    for n in graph.nodes:
        ts = _parse_ts(n.last_touched)
        if ts and (now - ts).days <= RECENT_DAYS:
            recent += 1
    return {
        "total": len(graph.nodes),
        "by_kind": by_kind,
        "domains": len(domains),
        "projects": len(projects),
        "recent": recent,
    }


def render_badge_svg(graph: Graph, title: str = "brAInny") -> str:
    stats = compute_badge_stats(graph)
    by_kind = stats["by_kind"]

    leaves = [
        ("skills", by_kind.get("skill", 0), KIND_COLOR["skill"]),
        ("techniques", by_kind.get("technique", 0), KIND_COLOR["technique"]),
        ("precautions", by_kind.get("precaution", 0), KIND_COLOR["precaution"]),
        ("projects", stats["projects"], "#7c8c6e"),
        (f"active ({RECENT_DAYS}d)", stats["recent"], "#4f8f52"),
    ]

    width, height = 720, 260
    hub_x, hub_y, hub_r = 150, 130, 48
    leaf_x = 590
    leaf_ys = [34, 82, 130, 178, 226]

    branches = []
    leaf_svgs = []
    for (label, value, color), ly in zip(leaves, leaf_ys):
        c1x, c1y = hub_x + 150, hub_y
        c2x, c2y = leaf_x - 150, ly
        branches.append(
            f'<path d="M{hub_x + hub_r},{hub_y} C{c1x},{c1y} {c2x},{c2y} {leaf_x},{ly}" '
            f'fill="none" stroke="{color}" stroke-opacity="0.55" stroke-width="2"/>'
        )
        r = 13 + min(value, 18) * 0.7
        leaf_svgs.append(
            f'<g>'
            f'<circle cx="{leaf_x}" cy="{ly}" r="{r:.1f}" fill="{color}" fill-opacity="0.22" '
            f'stroke="{color}" stroke-width="1.5"/>'
            f'<text x="{leaf_x}" y="{ly + 5}" text-anchor="middle" font-size="15" font-weight="700" '
            f'fill="#eef3ea" font-family="ui-monospace,Menlo,Consolas,monospace">{value}</text>'
            f'<text x="{leaf_x + r + 12:.1f}" y="{ly + 5}" font-size="13" fill="#9aab97" '
            f'font-family="-apple-system,Segoe UI,Helvetica,Arial,sans-serif">{_esc(label)}</text>'
            f'</g>'
        )

    subtitle = f"{stats['total']} idea(s) captured across {stats['domains']} domain(s)"
    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    return f"""<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{_esc(title)} activity badge">
<rect x="1" y="1" width="{width - 2}" height="{height - 2}" rx="14" fill="#0b1310" stroke="rgba(255,255,255,0.12)"/>
{''.join(branches)}
<circle cx="{hub_x}" cy="{hub_y}" r="{hub_r}" fill="#111a14" stroke="rgba(232,178,61,0.5)" stroke-width="2"/>
<image href="data:image/png;base64,{_ICON_PNG_B64}" x="{hub_x - 30}" y="{hub_y - 30}" width="60" height="60"/>
<text x="40" y="34" font-size="20" font-weight="700" fill="#eef3ea" font-family="-apple-system,Segoe UI,Helvetica,Arial,sans-serif">{_esc(title)}</text>
<text x="40" y="215" font-size="13" fill="#9aab97" font-family="-apple-system,Segoe UI,Helvetica,Arial,sans-serif">{_esc(subtitle)}</text>
<text x="40" y="234" font-size="11" fill="#5c6b63" font-family="-apple-system,Segoe UI,Helvetica,Arial,sans-serif">updated {generated} - github.com/AlsammanAlsamman/brainny</text>
{''.join(leaf_svgs)}
</svg>
"""
