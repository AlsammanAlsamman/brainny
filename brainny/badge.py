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


# the little tin-robot probe's round trip on each link, and how long it
# lingers at the hub laughing before doing another lap -- SMIL-only (this
# SVG is served raw and embedded via <img>, which never runs <script>), so
# the whole choreography is a chain of <animateMotion>/<animateTransform>
# elements timed off each other's `id.end`, looping via a `begin` value
# that fires both at page-load ("0s") and every time the last segment in
# the chain finishes ("badge-robot-pause.end").
_LEG_DUR = 1.6
_PAUSE_DUR = 2.6
_LINK_SLUGS = ["skills", "techniques", "precautions", "projects", "active"]


def _robot_scale(value: int) -> float:
    # same "more evidence -> visually bigger" idea as the leaf circles'
    # own radius formula just above, just a different (smaller) range so
    # the robot reads as a robot at every size, never a dot or a giant.
    return round(0.55 + min(value, 20) * 0.0325, 3)


def _badge_robot_svg(hub_x: int, hub_y: int, values: list[int]) -> str:
    """The animated probe: a round trip on each link (sized to that
    link's value), then a pause at the hub to laugh, then the next link --
    looping forever. Position and scale are two independent, nested
    transforms (an outer <g> animated by <animateMotion>, an inner <g>
    animated by <animateTransform type="scale">) so they never have to
    fight over which one "owns" the `transform` attribute."""
    scales = [_robot_scale(v) for v in values]
    seg_ids: list[str] = []
    motion_segs = []
    scale_segs = []

    def add_leg(slug: str, direction: str, begin: str, from_scale: float, to_scale: float) -> str:
        seg_id = f"badge-robot-{slug}-{direction}"
        key_points = "0;1" if direction == "out" else "1;0"
        motion_segs.append(
            f'<animateMotion id="{seg_id}" begin="{begin}" dur="{_LEG_DUR}s" fill="freeze" '
            f'keyPoints="{key_points}" keyTimes="0;1" calcMode="linear">'
            f'<mpath href="#badge-link-{slug}"/></animateMotion>'
        )
        scale_segs.append(
            f'<animateTransform attributeName="transform" type="scale" '
            f'begin="{begin}" dur="{_LEG_DUR}s" fill="freeze" '
            f'from="{from_scale}" to="{to_scale}"/>'
        )
        seg_ids.append(seg_id)
        return seg_id

    prev_end = '0s;badge-robot-pause.end'  # fires on load, then every completed lap
    prev_scale = scales[-1]  # the loop starts already at last lap's final size
    for slug, target_scale in zip(_LINK_SLUGS, scales):
        out_id = add_leg(slug, "out", prev_end, prev_scale, target_scale)
        back_id = add_leg(slug, "back", f"{out_id}.end", target_scale, target_scale)
        prev_end = f"{back_id}.end"
        prev_scale = target_scale

    # the pause: holds position at the hub (a zero-length "path") for
    # `_PAUSE_DUR`, its `id` is what the very first leg above loops back
    # off of. The bounce + "ha ha" both key off this same segment's begin.
    motion_segs.append(
        f'<animateMotion id="badge-robot-pause" begin="{prev_end}" dur="{_PAUSE_DUR}s" fill="freeze" '
        f'path="M{hub_x},{hub_y} L{hub_x},{hub_y}"/>'
    )

    bounce = (
        f'<animateTransform attributeName="transform" type="translate" '
        f'begin="badge-robot-pause.begin" dur="{_PAUSE_DUR}s" fill="freeze" '
        f'values="0,0; 0,-3; 0,0; 0,-3; 0,0" keyTimes="0;0.25;0.5;0.75;1"/>'
    )
    laugh = (
        f'<text x="{hub_x}" y="{hub_y - 35}" text-anchor="middle" font-size="12" font-weight="700" '
        f'fill="#e8b23d" font-family="-apple-system,Segoe UI,Helvetica,Arial,sans-serif" opacity="0">'
        f'ha ha!'
        f'<animate attributeName="opacity" begin="badge-robot-pause.begin" dur="{_PAUSE_DUR}s" '
        f'fill="freeze" values="0;0;1;1;0" keyTimes="0;0.12;0.28;0.8;1"/>'
        f'</text>'
    )

    # tin-robot shape, local origin at roughly hip height (head goes
    # negative y, feet positive y) -- the same silhouette/palette as the
    # Brain tab's probe, at a scale this badge can actually show.
    shape = (
        '<g>'
        '<line x1="0" y1="-16" x2="0" y2="-19" stroke="#5c6b63" stroke-width="1"/>'
        '<circle cx="0" cy="-19.5" r="1.1" fill="#ffe08c"/>'
        '<rect x="-3.5" y="-16" width="7" height="5.5" rx="0.8" fill="#9aab97" stroke="#5c6b63" stroke-width="0.7"/>'
        '<rect x="-2.2" y="-14.3" width="1.6" height="1.6" fill="#ffe08c"/>'
        '<rect x="0.6" y="-14.3" width="1.6" height="1.6" fill="#ffe08c"/>'
        '<rect x="-4" y="-9" width="8" height="9" rx="1" fill="#9aab97" stroke="#5c6b63" stroke-width="0.7"/>'
        '<circle cx="0" cy="-5" r="1.2" fill="#ffe08c" opacity="0.85"/>'
        '<line x1="-4" y1="-8" x2="-6" y2="-2" stroke="#9aab97" stroke-width="1.8"/>'
        '<line x1="4" y1="-8" x2="6" y2="-2" stroke="#9aab97" stroke-width="1.8"/>'
        '<line x1="-2" y1="0" x2="-2.5" y2="6" stroke="#9aab97" stroke-width="2"/>'
        '<line x1="2" y1="0" x2="2.5" y2="6" stroke="#9aab97" stroke-width="2"/>'
        '<rect x="-4" y="6" width="3.5" height="1.6" rx="0.4" fill="#5c6b63"/>'
        '<rect x="0.5" y="6" width="3.5" height="1.6" rx="0.4" fill="#5c6b63"/>'
        '</g>'
    )

    return (
        f'<g>{laugh}'
        f'<g>{"".join(motion_segs)}{bounce}'
        f'<g transform="scale({scales[-1]})">{"".join(scale_segs)}{shape}</g>'
        f'</g></g>'
    )


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
    for (label, value, color), ly, slug in zip(leaves, leaf_ys, _LINK_SLUGS):
        c1x, c1y = hub_x + 150, hub_y
        c2x, c2y = leaf_x - 150, ly
        branches.append(
            f'<path id="badge-link-{slug}" d="M{hub_x + hub_r},{hub_y} C{c1x},{c1y} {c2x},{c2y} {leaf_x},{ly}" '
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
    robot = _badge_robot_svg(hub_x, hub_y, [v for _, v, _ in leaves])

    return f"""<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{_esc(title)} activity badge">
<rect x="1" y="1" width="{width - 2}" height="{height - 2}" rx="14" fill="#0b1310" stroke="rgba(255,255,255,0.12)"/>
{''.join(branches)}
<circle cx="{hub_x}" cy="{hub_y}" r="{hub_r}" fill="#111a14" stroke="rgba(232,178,61,0.5)" stroke-width="2"/>
<image href="data:image/png;base64,{_ICON_PNG_B64}" x="{hub_x - 30}" y="{hub_y - 30}" width="60" height="60"/>
<text x="40" y="34" font-size="20" font-weight="700" fill="#eef3ea" font-family="-apple-system,Segoe UI,Helvetica,Arial,sans-serif">{_esc(title)}</text>
<text x="40" y="215" font-size="13" fill="#9aab97" font-family="-apple-system,Segoe UI,Helvetica,Arial,sans-serif">{_esc(subtitle)}</text>
<text x="40" y="234" font-size="11" fill="#5c6b63" font-family="-apple-system,Segoe UI,Helvetica,Arial,sans-serif">updated {generated} - github.com/AlsammanAlsamman/brainny</text>
{''.join(leaf_svgs)}
{robot}
</svg>
"""
