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
from brainny.schema import Graph, Node

KIND_ICON = {
    "technique": "T",
    "precaution": "!",
    "solution": "S",
    "insight": "I",
    "seed": ".",
}

KIND_COLOR = {
    "technique": "#3b6fd6",
    "precaution": "#c9432c",
    "solution": "#2f9e5e",
    "insight": "#8b5cd6",
    "seed": "#8a8f98",
}

STATE_ORDER = ["seed", "sprouting", "mature", "harvested"]

# growth axis -> how a fruit/bud reads in the 3D tree (SEED.md's state field)
STATE_META = {
    "seed": {"label": "seed / bud", "size": 0.16, "emissive": 0.12, "gold": False},
    "sprouting": {"label": "sprouting leaf", "size": 0.22, "emissive": 0.22, "gold": False},
    "mature": {"label": "mature fruit", "size": 0.30, "emissive": 0.40, "gold": False},
    "harvested": {"label": "harvested fruit", "size": 0.34, "emissive": 0.65, "gold": True},
}


def _node_line(node: Node) -> str:
    icon = KIND_ICON.get(node.kind, "?")
    tags = f" [{', '.join(node.tags)}]" if node.tags else ""
    recur = f" x{node.recurrence}" if node.recurrence > 1 else ""
    return f"  [{icon}] ({node.state}{recur}) {node.title} - {node.id}{tags}"


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


def _build_payload(graph: Graph, title: str) -> dict:
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
                "domain": n.domain,
                "tags": n.tags,
                "trigger": n.trigger,
                "state": n.state,
                "recurrence": n.recurrence,
                "lastTouched": n.last_touched,
                "session": prov.session if prov else None,
                "sessionTs": prov.ts if prov else "",
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

    return {
        "title": title,
        "nodes": nodes,
        "sessions": sessions,
        "domainCount": len({n.domain for n in graph.nodes}),
        "kindColor": KIND_COLOR,
        "stateMeta": STATE_META,
    }


_CSS = """
  * { box-sizing: border-box; }
  html, body { margin: 0; padding: 0; height: 100%; background: #0b1310; }
  body {
    font: 14px/1.5 -apple-system, Segoe UI, Helvetica, Arial, sans-serif;
    color: #eef3ea; display: flex; flex-direction: column; height: 100%;
  }

  header { padding: 0.9rem 1.25rem; border-bottom: 1px solid rgba(255,255,255,0.08); background: rgba(10,18,12,0.85); flex: none; }
  header .row { display: flex; align-items: center; gap: 0.9rem; flex-wrap: wrap; }
  header h1 { margin: 0; font-size: 1.15rem; }
  header p { margin: 0.35rem 0 0; color: #9aab97; font-size: 0.82rem; }
  #view-select {
    background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.16); color: #eef3ea;
    padding: 0.3rem 0.6rem; border-radius: 8px; font: inherit; font-size: 0.85rem; cursor: pointer;
  }
  #view-select:hover { background: rgba(255,255,255,0.1); }
  /* the dropdown's open popup is native-rendered with a white background
     regardless of the select's own styling, so its options need their
     own dark text or they're invisible against it */
  #view-select option { color: #111; background: #fff; }
  .note {
    margin: 0.6rem 0 0; padding: 0.6rem 0.8rem; border-radius: 8px;
    background: rgba(232,178,61,0.08); border: 1px solid rgba(232,178,61,0.25);
    font-size: 0.78rem; color: #d7c9a0;
  }

  #tab-bar { display: flex; gap: 0.3rem; margin-left: 0.4rem; }
  .tab-btn {
    background: none; border: 1px solid transparent; color: #9aab97; font: inherit;
    font-size: 0.85rem; padding: 0.3rem 0.8rem; border-radius: 8px; cursor: pointer;
  }
  .tab-btn:hover { background: rgba(255,255,255,0.06); color: #eef3ea; }
  .tab-btn.active { background: rgba(232,178,61,0.14); border-color: rgba(232,178,61,0.4); color: #f0e2bb; }

  main { flex: 1; display: grid; grid-template-columns: 300px 1fr; min-height: 0; }
  main#stats-main { display: block; overflow-y: auto; padding: 1.1rem 1.4rem 2rem; }

  /* ---- stats tab ---- */
  .stat-cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 0.7rem; margin: 0 0 1.4rem; }
  .stat-card {
    background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08);
    border-radius: 10px; padding: 0.7rem 0.9rem;
  }
  .stat-card .stat-num { font-size: 1.6rem; font-weight: 600; color: #eef3ea; line-height: 1.1; }
  .stat-card .stat-label { font-size: 0.74rem; color: #8fa08c; margin-top: 0.2rem; text-transform: uppercase; letter-spacing: 0.03em; }

  .stats-grid { display: grid; grid-template-columns: minmax(280px, 1fr) minmax(320px, 1.2fr); gap: 1.4rem; align-items: start; }
  @media (max-width: 900px) { .stats-grid { grid-template-columns: 1fr; } }

  .stats-block h2 { font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.04em; color: #8fa08c; margin: 0 0 0.6rem; }
  .stats-caption { font-size: 0.74rem; color: #7c8c79; margin: 0.5rem 0 0; }

  #treemap-mount svg { display: block; width: 100%; }
  .tm-cell rect { stroke: rgba(11,19,16,0.7); stroke-width: 1.5; cursor: pointer; }
  .tm-cell text { pointer-events: none; fill: #0b1310; font-size: 11px; font-weight: 600; }
  .tm-cell .tm-count { font-weight: 400; opacity: 0.75; }

  .domain-table { width: 100%; border-collapse: collapse; font-size: 0.82rem; }
  .domain-table th { text-align: left; font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.03em; color: #7c8c79; padding: 0.3rem 0.5rem; border-bottom: 1px solid rgba(255,255,255,0.1); }
  .domain-table td { padding: 0.4rem 0.5rem; border-bottom: 1px solid rgba(255,255,255,0.05); vertical-align: middle; }
  .domain-table tr:hover td { background: rgba(255,255,255,0.03); }
  .spark { display: inline-block; vertical-align: middle; }
  .trend-badge { display: inline-flex; align-items: center; gap: 0.3rem; padding: 0.1rem 0.5rem; border-radius: 999px; font-size: 0.72rem; white-space: nowrap; }
  .trend-growing { background: rgba(111,174,92,0.16); color: #8fd67a; }
  .trend-steady { background: rgba(255,255,255,0.06); color: #9aab97; }
  .trend-quiet { background: rgba(201,67,44,0.12); color: #d68a7a; }

  .kind-bars { display: flex; flex-direction: column; gap: 0.4rem; margin-top: 0.4rem; }
  .kind-bar-row { display: flex; align-items: center; gap: 0.6rem; font-size: 0.78rem; }
  .kind-bar-label { width: 90px; flex: none; color: #c9d3c6; }
  .kind-bar-track { flex: 1; height: 10px; border-radius: 999px; background: rgba(255,255,255,0.06); overflow: hidden; }
  .kind-bar-fill { height: 100%; border-radius: 999px; }
  .kind-bar-count { width: 24px; flex: none; text-align: right; color: #8fa08c; }

  .recent-list { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 0.5rem; }
  .recent-item { display: flex; flex-direction: column; gap: 0.1rem; padding: 0.45rem 0.6rem; border-radius: 8px; background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.06); cursor: pointer; }
  .recent-item:hover { background: rgba(255,255,255,0.05); }
  .recent-item .ri-title { color: #eef3ea; font-size: 0.84rem; }
  .recent-item .ri-meta { color: #7c8c79; font-size: 0.72rem; }
  #panel { border-right: 1px solid rgba(255,255,255,0.08); overflow-y: auto; padding: 0.75rem; }
  #panel h2 { font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.04em; color: #8fa08c; margin: 0.25rem 0.25rem 0.6rem; }
  #viz { position: relative; overflow: hidden; }
  #viz svg { display: block; width: 100%; height: 100%; }
  .empty-note { padding: 0.75rem; color: #8fa08c; font-size: 0.85rem; }

  .legend-row { display: flex; flex-wrap: wrap; gap: 0.6rem; margin: 0 0 0.6rem; padding: 0 0.25rem; font-size: 0.76rem; color: #c9d3c6; }
  .legend-item { display: inline-flex; align-items: center; gap: 0.3rem; }
  .dot { width: 9px; height: 9px; border-radius: 50%; display: inline-block; flex: none; }
  .state-dot.state-seed { width: 6px; height: 6px; background: #6b7a68; }
  .state-dot.state-sprouting { width: 8px; height: 8px; background: #6fae5c; }
  .state-dot.state-mature { width: 10px; height: 10px; background: #4f9e63; }
  .state-dot.state-harvested { width: 11px; height: 11px; background: #e8b23d; }

  /* ---- itemized accordion list ---- */
  .item-list { display: flex; flex-direction: column; gap: 0.9rem; }
  .item-group { border-radius: 8px; padding: 0.15rem; }
  .item-group-heading { font-size: 0.76rem; color: #8fa08c; margin: 0 0 0.35rem; padding: 0 0.25rem; }
  .item { border: 1px solid rgba(255,255,255,0.08); border-radius: 8px; margin-bottom: 0.4rem; overflow: hidden; background: rgba(255,255,255,0.02); }
  .item-promising { border-color: rgba(232,178,61,0.55); box-shadow: 0 0 0 1px rgba(232,178,61,0.15) inset; }
  .item-flash { animation: item-flash-kf 1.4s ease-out; }
  @keyframes item-flash-kf {
    0% { background: rgba(191,227,107,0.28); border-color: rgba(191,227,107,0.8); }
    100% { background: rgba(255,255,255,0.02); }
  }
  .item-title-row {
    width: 100%; display: flex; align-items: center; gap: 0.5rem;
    background: none; border: none; color: #eef3ea; text-align: left;
    padding: 0.5rem 0.6rem; cursor: pointer; font: inherit; font-size: 0.85rem;
  }
  .item-title-row:hover { background: rgba(255,255,255,0.04); }
  .item-dot { width: 8px; height: 8px; border-radius: 50%; flex: none; }
  .item-title { flex: 1; }
  .item-caret { color: #6b7a68; transition: transform 0.15s; font-size: 0.7rem; }
  .item-title-row.open .item-caret { transform: rotate(90deg); }
  .item-body { padding: 0 0.75rem 0.7rem 1.85rem; font-size: 0.82rem; }
  .item-summary { margin: 0 0 0.35rem; color: #d7ddd4; }
  .item-detail { margin: 0 0 0.35rem; color: #a9b7a6; }
  .item-trigger { margin: 0 0 0.35rem; color: #c9d3c6; font-size: 0.8rem; }
  .item-meta { margin: 0 0 0.35rem; color: #7c8c79; font-size: 0.72rem; }
  .item-tags { display: flex; flex-wrap: wrap; gap: 0.3rem; }
  .item-tag { background: rgba(255,255,255,0.08); border-radius: 999px; padding: 0.05rem 0.5rem; font-size: 0.7rem; }

  #tooltip {
    position: fixed; z-index: 10; pointer-events: none; max-width: 280px;
    background: rgba(12,20,14,0.96); border: 1px solid rgba(255,255,255,0.12);
    border-radius: 10px; padding: 0.6rem 0.75rem; font-size: 0.8rem; display: none;
  }
  #tooltip .tt-title { font-weight: 600; margin-bottom: 0.2rem; }
  #tooltip .tt-meta { color: #8fa08c; font-size: 0.72rem; }

  #fallback { padding: 2rem; white-space: pre-wrap; color: #eef3ea; background: #0b1310; height: 100%; margin: 0; overflow: auto; }
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

  function escapeHtml(s) {
    var div = document.createElement('div');
    div.textContent = s == null ? '' : String(s);
    return div.innerHTML;
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
        id: idea.id, name: idea.title, kind: 'idea', idea: idea,
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
  function renderItemList(container, data) {
    if (!data.nodes.length) {
      var empty = document.createElement('p');
      empty.className = 'empty-note';
      empty.textContent = 'No ideas captured yet. Run `brainny capture <entries.json>`.';
      container.appendChild(empty);
      return;
    }

    var byDomain = {};
    data.nodes.forEach(function (n) { (byDomain[n.domain] = byDomain[n.domain] || []).push(n); });

    var wrap = document.createElement('div');
    wrap.className = 'item-list';
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
        item.dataset.itemId = idea.id;

        var titleRow = document.createElement('button');
        titleRow.type = 'button';
        titleRow.className = 'item-title-row';
        titleRow.innerHTML =
          '<span class="item-dot" style="background:' + (data.kindColor[idea.kind] || '#8a8f98') + '"></span>' +
          '<span class="item-title">' + escapeHtml(idea.title) + '</span>' +
          '<span class="item-caret">\\u25b8</span>';

        var body = document.createElement('div');
        body.className = 'item-body';
        body.hidden = true;
        var tags = (idea.tags || []).map(function (t) { return '<span class="item-tag">' + escapeHtml(t) + '</span>'; }).join('');
        body.innerHTML =
          '<p class="item-summary">' + escapeHtml(idea.summary) + '</p>' +
          (idea.detail ? '<p class="item-detail">' + escapeHtml(idea.detail) + '</p>' : '') +
          (idea.trigger ? '<p class="item-trigger"><strong>trigger:</strong> ' + escapeHtml(idea.trigger) + '</p>' : '') +
          '<p class="item-meta">' + escapeHtml(idea.kind) + ' \\u00b7 ' + escapeHtml(idea.state) +
          ' \\u00b7 ' + escapeHtml(idea.id) + '</p>' +
          '<div class="item-tags">' + tags + '</div>';

        titleRow.addEventListener('click', function () {
          body.hidden = !body.hidden;
          titleRow.classList.toggle('open', !body.hidden);
        });

        item.appendChild(titleRow);
        item.appendChild(body);
        group.appendChild(item);
      });

      wrap.appendChild(group);
    });

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

  renderItemList(document.getElementById('item-list-mount'), DATA);

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
    var hierarchyData = buildHierarchy(DATA);
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
      .attr('stroke', 'rgba(190,205,180,0.28)')
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
      .attr('stroke', function (d) { return d.data.kind === 'idea' && isPromising(d.data.idea) ? '#e8b23d' : 'none'; })
      .attr('stroke-width', 2)
      .style('cursor', 'pointer')
      .on('mouseenter', function (event, d) { showTooltip(event, tooltipHtml(d.data)); })
      .on('mousemove', function (event, d) { showTooltip(event, tooltipHtml(d.data)); })
      .on('mouseleave', hideTooltip)
      .on('click', function (event, d) { if (d.data.kind === 'idea') focusItem(d.data.id); });

    node.append('text')
      .attr('dy', '0.31em')
      .attr('x', function (d) { return radialPoint(d.x, d.y)[0] < 0 ? -8 : 8; })
      .attr('text-anchor', function (d) { return radialPoint(d.x, d.y)[0] < 0 ? 'end' : 'start'; })
      .attr('fill', '#c9d3c6')
      .style('font-size', '10px')
      .style('pointer-events', 'none')
      .text(function (d) { return d.data.kind === 'root' ? d.data.name : (d.data.name.length > 28 ? d.data.name.slice(0, 27) + '\\u2026' : d.data.name); });

    return function cleanup() {};
  }

  // ---- view 2: force network with cluster halos ----
  function renderForceClusters() {
    var hierarchyData = buildHierarchy(DATA);
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

    var link = linkLayer.selectAll('line').data(links).join('line').attr('stroke', 'rgba(190,205,180,0.25)');

    var node = nodeLayer.selectAll('circle')
      .data(nodes)
      .join('circle')
      .attr('r', radiusOf)
      .attr('fill', function (d) {
        if (d.kind === 'root') return '#e8b23d';
        if (d.kind === 'branch') return '#7c8c6e';
        return DATA.kindColor[d.idea.kind] || '#8a8f98';
      })
      .attr('stroke', function (d) { return d.kind === 'idea' && isPromising(d.idea) ? '#e8b23d' : 'rgba(255,255,255,0.15)'; })
      .attr('stroke-width', function (d) { return d.kind === 'idea' && isPromising(d.idea) ? 2.5 : 1; })
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

    simulation.on('tick', function () {
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
    });

    simulation.on('end', function () {
      var xs = nodes.map(function (d) { return d.x; }), ys = nodes.map(function (d) { return d.y; });
      var pad = 60;
      var x0 = Math.min.apply(null, xs) - pad, x1 = Math.max.apply(null, xs) + pad;
      var y0 = Math.min.apply(null, ys) - pad, y1 = Math.max.apply(null, ys) + pad;
      var scale = Math.min(4, 0.9 / Math.max((x1 - x0) / width, (y1 - y0) / height));
      var tx = width / 2 - scale * (x0 + x1) / 2;
      var ty = height / 2 - scale * (y0 + y1) / 2;
      svg.transition().duration(500).call(zoom.transform, d3.zoomIdentity.translate(tx, ty).scale(scale));
    });

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
  function renderStatsView() {
    var mount = document.getElementById('stats-main');
    mount.innerHTML = '';
    if (!DATA.nodes.length) {
      mount.innerHTML = '<p class="empty-note" style="padding:2rem">No ideas captured yet \\u2014 nothing to show stats on.</p>';
      return;
    }

    var domains = buildDomainStats(DATA);
    var recentTotal = DATA.nodes.filter(function (n) {
      return n.lastTouched && Date.now() - new Date(n.lastTouched).getTime() <= RECENT_MS;
    }).length;

    var cards = document.createElement('div');
    cards.className = 'stat-cards';
    [
      [DATA.nodes.length, 'ideas'],
      [domains.length, 'domains'],
      [DATA.sessions.length, 'sessions'],
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
    renderKindBars(kindBlock, DATA);
    bottom.appendChild(kindBlock);

    var recentBlock = document.createElement('div');
    recentBlock.className = 'stats-block';
    recentBlock.innerHTML = '<h2>newest ideas</h2>';
    renderRecentList(recentBlock, DATA);
    bottom.appendChild(recentBlock);
    mount.appendChild(bottom);

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

  // ---- dropdown + tab wiring ----
  var VIEWS = { radial: renderRadialTree, force: renderForceClusters };
  var currentCleanup = null;

  function switchView(name) {
    if (currentCleanup) currentCleanup();
    vizEl.innerHTML = '';
    hideTooltip();
    descEl.textContent = DESCRIPTIONS[name];
    if (DATA.nodes.length) {
      currentCleanup = VIEWS[name]();
    } else {
      currentCleanup = null;
      var empty = document.createElement('p');
      empty.className = 'empty-note';
      empty.style.padding = '2rem';
      empty.textContent = 'No ideas captured yet \\u2014 just the mother tree. Run `brainny capture <entries.json>`.';
      vizEl.appendChild(empty);
    }
  }

  var select = document.getElementById('view-select');
  select.addEventListener('change', function () { switchView(select.value); });

  var activeTab = 'graph';
  function switchTab(name) {
    if (name === activeTab) return;
    activeTab = name;
    document.querySelectorAll('.tab-btn').forEach(function (b) { b.classList.toggle('active', b.dataset.tab === name); });
    document.getElementById('graph-main').hidden = name !== 'graph';
    document.getElementById('stats-main').hidden = name !== 'stats';
    select.style.display = name === 'graph' ? '' : 'none';
    descEl.hidden = name !== 'graph';
    if (name === 'stats') {
      renderStatsView();
    } else if (!currentCleanup && DATA.nodes.length) {
      switchView(select.value);
    }
  }
  document.querySelectorAll('.tab-btn').forEach(function (b) {
    b.addEventListener('click', function () { switchTab(b.dataset.tab); });
  });

  switchView(select.value);

  window.addEventListener('resize', function () {
    if (activeTab === 'graph') switchView(select.value);
    else if (activeTab === 'stats') renderStatsView();
  });
})();
"""


def render_html(graph: Graph, title: str = "brainny") -> str:
    """Render graph.json as a navigable dashboard (D3, CDN-loaded) with two
    tabs. Graph tab: a dropdown switches between a radial tree (domains
    branching from a center, ideas as rim leaves) and a force-directed
    network with a colored halo per domain group, alongside an itemized
    accordion list (click a title to unfold summary/detail/trigger/tags).
    Clicking an idea in either graph opens + scrolls to its entry in the
    list. Ideas are sized/highlighted by growth state and kind — real
    fields, but inert until v0.1 (dedup.py/stats.py) makes recurrence/
    state actually vary. Stats tab: a domain treemap (size = idea count,
    color = activity) plus a per-cluster table, kind breakdown, and a
    newest-ideas feed — all derived from real timestamps/domains/kinds
    (no fabricated data), with "growing"/"quiet" as an honest recency
    proxy rather than the real decay/novelty model v0.1 will bring.
    Clicking a cluster jumps to it in the Graph tab's idea list. Falls
    back to the plain terminal tree if D3 can't load. No server involved
    — a static, self-contained, git-shareable file."""

    payload = _build_payload(graph, title)
    data_json = json.dumps(payload, ensure_ascii=False).replace("</", "<\\/")

    kind_legend = "".join(
        f'<span class="legend-item"><span class="dot" style="background:{color}"></span>{_esc(kind)}</span>'
        for kind, color in KIND_COLOR.items()
    )
    state_legend = "".join(
        f'<span class="legend-item"><span class="dot state-dot state-{_esc(state)}"></span>{_esc(meta["label"])}</span>'
        for state, meta in STATE_META.items()
    )

    subtitle = (
        f"{len(graph.nodes)} idea(s) · {payload['domainCount']} branch(es), "
        f"grown over {len(payload['sessions'])} session(s)"
        if graph.nodes
        else "No ideas captured yet — just the mother tree."
    )

    head = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{_esc(title)}</title>
<style>{_CSS}</style>
</head>
"""

    body_open = f"""<body>
<header>
  <div class="row">
    <h1>{_esc(title)}</h1>
    <nav id="tab-bar">
      <button type="button" class="tab-btn active" data-tab="graph">Graph</button>
      <button type="button" class="tab-btn" data-tab="stats">Stats</button>
    </nav>
    <select id="view-select">
      <option value="radial">Radial tree</option>
      <option value="force">Force network with cluster halos</option>
    </select>
  </div>
  <p id="view-desc"></p>
  <p class="note">{_esc(subtitle)} · sizing/highlighting uses the real <code>recurrence</code>/<code>state</code> fields, but v0.1 (dedup/stats) doesn't exist yet — every idea is currently <code>recurrence: 1</code>, <code>state: "seed"</code>, so nothing visibly stands out yet. Click any idea to jump to it in the list.</p>
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
<div id="tooltip"></div>
<pre id="fallback" hidden>{_esc(render_tree(graph))}</pre>
<script id="brainny-data" type="application/json">"""

    scripts = f"""</script>
<script src="https://cdn.jsdelivr.net/npm/d3@7.9.0/dist/d3.min.js" crossorigin="anonymous"></script>
<script>{_JS}</script>
</body>
</html>
"""

    return head + body_open + data_json + scripts


def save_html(graph: Graph, out_dir: Path = DEFAULT_OUT_DIR, title: str = "brainny") -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    path = html_path(out_dir)
    path.write_text(render_html(graph, title=title), encoding="utf-8")
    return path
