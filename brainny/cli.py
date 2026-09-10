"""brainny CLI — entry: capture | attach | query | status | config |
search | recall | recent | open | grow | neglected | install | serve | hook.

v0 (see SEED.md §7) implements capture + query for real. status/config/
search/recent/open are OPERATIONS.md §6 step 2 — pure CLI surface on data
that already exists, no new architecture. The rest are named here per the
target shape (§5) and stubbed with a clear pointer to the roadmap stage
that lands them, rather than being silently absent.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import webbrowser
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

from brainny import config
from brainny._version import get_version
from brainny.banner import render_banner
from brainny.capture import capture as do_capture
from brainny.graph import DEFAULT_OUT_DIR, graph_path, html_path, load_graph, save_graph
from brainny.schema import Attachment, Graph, GrowthLogEntry, now_iso
from brainny.viz import render_tree, save_html

ATTACHMENTS_DIRNAME = "attachments"
# "small enough to guide, not to duplicate the dataset" -- a hard cap
# keeps this a pointer/excerpt mechanism, not a file-storage feature.
MAX_ATTACHMENT_BYTES = 2 * 1024 * 1024

# Resolved defensively so `python -m brainny.cli` works from any directory,
# even one that shadows the package as a namespace package.
__version__ = get_version()

NOT_YET = {
    "grow": "v0.1 (needs stats.py + dedup.py)",
    "neglected": "v0.1 (needs stats.py decay math)",
    "install": "v1 (cross-platform installer)",
    "serve": "v0.3 (MCP server)",
    "hook": "v0.2 (git hook integration)",
}


def _sync_to_central(out_dir: Path, graph: Graph, project: str | None) -> Path | None:
    """Project -> central, always, on-disk only -- SEED.md §1.7's "Project
    -> central: always" half, made literal: every capture/attach mirrors
    into the configured central folder immediately, not just when someone
    remembers to run `brainny sync`. Silent no-op if no central folder is
    configured, or `project` can't be determined -- a brand-new install
    with nothing set up yet must behave exactly like today. Never touches
    git: pushing to GitHub stays a separate, fully explicit step
    (`brainny sync --push`), same as always -- this only ever writes local
    files, matching "never auto-committed" for the OTHER direction too."""
    central = config.get_value("central-folder")
    if not central or not project:
        return None
    central_out = Path(central) / project
    save_graph(graph, central_out)
    save_html(graph, central_out)
    local_attachments = out_dir / ATTACHMENTS_DIRNAME
    if local_attachments.is_dir():
        shutil.copytree(local_attachments, central_out / ATTACHMENTS_DIRNAME, dirs_exist_ok=True)
    return central_out


def cmd_capture(args: argparse.Namespace) -> int:
    out_dir = Path(args.out_dir)
    entries_path = Path(args.entries)
    if not entries_path.exists():
        print(f"brainny: no such file: {entries_path}", file=sys.stderr)
        return 1
    nodes, path = do_capture(entries_path, args.project, args.session, out_dir)
    graph = load_graph(out_dir)
    html_path = save_html(graph, out_dir)
    if not nodes:
        print("brainny: 0 entries captured (empty array - correct, common outcome).")
    else:
        print(f"brainny: captured {len(nodes)} idea(s) -> {path}")
        for node in nodes:
            print(f"  + [{node.kind}] {node.title} ({node.id})")
    print(f"brainny: visualization -> {html_path}")
    central_out = _sync_to_central(out_dir, graph, args.project)
    if central_out is not None:
        print(f"brainny: mirrored to central -> {central_out}")
    return 0


def cmd_attach(args: argparse.Namespace) -> int:
    """Attach a small piece of physical evidence -- a script, a tiny
    illustrative table excerpt, a small plot -- to an existing idea, so a
    future session can literally follow it instead of re-deriving it from
    a text description alone. The file itself lives under
    brainny-out/attachments/<idea-id>/; the graph only ever stores its
    filename/type/description, matching the two-contracts rule (SEED.md
    §1.6) -- the JSON entry never carries binary content."""
    out_dir = Path(args.out_dir)
    graph = load_graph(out_dir)
    node = next((n for n in graph.nodes if n.id == args.idea_id), None)
    if node is None:
        print(f"brainny: no idea with id '{args.idea_id}' in {graph_path(out_dir)}", file=sys.stderr)
        return 1

    src = Path(args.file)
    if not src.exists() or not src.is_file():
        print(f"brainny: no such file: {src}", file=sys.stderr)
        return 1
    size = src.stat().st_size
    if size > MAX_ATTACHMENT_BYTES:
        print(
            f"brainny: {src} is {size / 1024:.0f} KB, over the "
            f"{MAX_ATTACHMENT_BYTES // 1024} KB attachment cap. Attachments are meant to "
            "guide, not duplicate a full dataset/output -- trim it to a small excerpt first.",
            file=sys.stderr,
        )
        return 1

    filename = args.rename or src.name
    dest_dir = out_dir / ATTACHMENTS_DIRNAME / node.id
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / filename
    shutil.copyfile(src, dest)

    node.attachments.append(Attachment(type=args.type, filename=filename, description=args.description))
    ts = now_iso()
    node.last_touched = ts
    node.growth_log.append(
        GrowthLogEntry(session=args.session or "unknown", ts=ts, event="attached", note=f"{args.type}: {filename}")
    )
    save_graph(graph, out_dir)
    viz_path = save_html(graph, out_dir)

    print(f"brainny: attached {filename} ({args.type}) to {node.id} -> {dest}")
    print(f"brainny: visualization -> {viz_path}")
    central_out = _sync_to_central(out_dir, graph, _infer_project_name(graph))
    if central_out is not None:
        print(f"brainny: mirrored to central -> {central_out}")
    return 0


def cmd_query(args: argparse.Namespace) -> int:
    out_dir = Path(args.out_dir)
    graph = load_graph(out_dir)
    if args.html:
        path = save_html(graph, out_dir)
        print(f"brainny: wrote {path} - open it in a browser.")
    else:
        print(render_tree(graph), end="")
    return 0


def _infer_project_name(graph: Graph) -> str | None:
    names = [p.project for n in graph.nodes for p in n.provenance]
    if not names:
        return None
    return Counter(names).most_common(1)[0][0]


def cmd_status(args: argparse.Namespace) -> int:
    out_dir = Path(args.out_dir)
    graph = load_graph(out_dir)
    print("brainny status")
    if not graph.nodes:
        print(f"  ideas: 0 ({graph_path(out_dir)} not created yet)")
    else:
        by_kind: dict[str, int] = defaultdict(int)
        for n in graph.nodes:
            by_kind[n.kind] += 1
        summary = ", ".join(f"{v} {k}" for k, v in sorted(by_kind.items()))
        domains = len({n.domain for n in graph.nodes})
        last = max(n.last_touched for n in graph.nodes)
        print(f"  ideas: {len(graph.nodes)} ({summary})")
        print(f"  domains: {domains}")
        print(f"  last capture: {last}")
        print(f"  graph: {graph_path(out_dir)}")

    central = config.get_value("central-folder")
    if not central:
        print("  central folder: not configured - see `brainny config set-central <path>`")
        return 0
    print(f"  central folder: {central}")
    project = _infer_project_name(graph)
    if not project:
        print("  central copy: n/a (no captures yet to infer a project name from)")
        return 0
    central_out = Path(central) / project
    if not graph_path(central_out).exists():
        print("  central copy: not synced yet - run `brainny sync`")
        return 0
    central_graph = load_graph(central_out)
    in_sync = len(central_graph.nodes) == len(graph.nodes)
    state = "in sync" if in_sync else f"{len(graph.nodes) - len(central_graph.nodes):+d} idea(s) since last sync"
    print(f"  central copy: {len(central_graph.nodes)} idea(s) at {graph_path(central_out)} ({state})")

    days_since = _days_since_last_central_commit(Path(central))
    if days_since is not None:
        interval = _sync_interval_days()
        due = " - due for a GitHub push (`brainny sync --push`)" if days_since >= interval else ""
        print(f"  central github: last pushed {days_since:.1f} day(s) ago (push every {interval:g} day(s)){due}")
    return 0


def _sync_interval_days() -> float:
    raw = config.get_value("sync-interval-days")
    if not raw:
        return 1.0
    try:
        return float(raw)
    except ValueError:
        return 1.0


def _days_since_last_central_commit(central_root: Path) -> float | None:
    if not (central_root / ".git").is_dir():
        return None
    result = _run_git(["log", "-1", "--format=%cI"], central_root)
    if result.returncode != 0 or not result.stdout.strip():
        return None
    try:
        last = datetime.fromisoformat(result.stdout.strip())
    except ValueError:
        return None
    if last.tzinfo is None:
        last = last.replace(tzinfo=timezone.utc)
    return (datetime.now(timezone.utc) - last).total_seconds() / 86400


def cmd_config(args: argparse.Namespace) -> int:
    if args.action == "set-central":
        path = Path(args.path).expanduser().resolve()
        clone_url = getattr(args, "clone", None)
        if clone_url:
            if path.exists() and any(path.iterdir()):
                print(f"brainny: {path} already exists and isn't empty - won't clone into it.", file=sys.stderr)
                return 1
            path.parent.mkdir(parents=True, exist_ok=True)
            result = subprocess.run(
                ["git", "clone", clone_url, str(path)], capture_output=True, text=True
            )
            if result.returncode != 0:
                print(f"brainny: git clone failed:\n{result.stderr}", file=sys.stderr)
                return 1
            config.set_value("central-folder", str(path))
            print(f"brainny: cloned {clone_url} -> {path}")
            print(f"brainny: central folder set to {path}")
            return 0
        if path.exists() and not path.is_dir():
            print(f"brainny: {path} exists and is not a directory", file=sys.stderr)
            return 1
        path.mkdir(parents=True, exist_ok=True)
        config.set_value("central-folder", str(path))
        print(f"brainny: central folder set to {path}")
        print("  run `brainny sync` to push this project's ideas there.")
        return 0
    if args.action == "set":
        config.set_value(args.key, args.value)
        print(f"brainny: set {args.key} = {args.value}")
        return 0
    # action == "get"
    if args.key:
        value = config.get_value(args.key)
        if value is None:
            print(f"brainny: {args.key} is not set", file=sys.stderr)
            return 1
        print(value)
        return 0
    cfg = config.load_config()
    if not cfg:
        print("brainny: no settings configured yet.")
        print("  known keys: " + ", ".join(config.KNOWN_KEYS))
        return 0
    for key, value in sorted(cfg.items()):
        print(f"{key} = {value}")
    return 0


def cmd_search(args: argparse.Namespace) -> int:
    out_dir = Path(args.out_dir)
    graph = load_graph(out_dir)
    term = args.term.lower()

    def matches(n) -> bool:
        haystacks = [n.title, n.summary, n.detail or "", n.snippet or "", n.domain, n.kind, n.state, *n.tags]
        return any(term in h.lower() for h in haystacks)

    hits = [n for n in graph.nodes if matches(n)]
    if not hits:
        print(f"brainny: no matches for '{args.term}'")
        return 0
    print(f"brainny: {len(hits)} match(es) for '{args.term}'")
    for n in hits:
        print(f"  [{n.kind}] {n.title} ({n.id}) - {n.domain}")
    return 0


def cmd_recall(args: argparse.Namespace) -> int:
    """Cross-project recall (OPERATIONS.md step 11): search this project's
    ideas AND every other project synced into the configured central
    folder, so a precaution learned in project A can actually surface
    when starting similar work in project B — the "recall" half of
    SEED.md's design that pure capture (search/catch/catch-this) doesn't
    provide on its own. Local-only if no central folder is set up.
    """
    out_dir = Path(args.out_dir)
    terms = [t.lower() for t in args.terms]

    def matches(n) -> bool:
        haystacks = [n.title, n.summary, n.detail or "", n.snippet or "", n.domain, n.kind, n.state, *n.tags]
        return any(term in h.lower() for term in terms for h in haystacks)

    results: list[tuple[str, object]] = []
    local_graph = load_graph(out_dir)
    for n in local_graph.nodes:
        if matches(n):
            results.append(("this project", n))

    central = config.get_value("central-folder")
    searched_central = False
    if central:
        central_path = Path(central)
        if central_path.is_dir():
            searched_central = True
            local_project = _infer_project_name(local_graph)
            for sub in sorted(p for p in central_path.iterdir() if p.is_dir()):
                if local_project and sub.name == local_project:
                    continue  # already covered by the local graph above
                for n in load_graph(sub).nodes:
                    if matches(n):
                        results.append((sub.name, n))

    query = " ".join(args.terms)
    if not results:
        print(f"brainny: no matches for '{query}'")
        if not central:
            print("  (no central folder configured - only this project was searched; see `brainny config set-central <path>`)")
        elif not searched_central:
            print(f"  (central folder {central} doesn't exist yet - only this project was searched)")
        return 0

    scope = "this project + central" if searched_central else "this project only"
    print(f"brainny: {len(results)} match(es) for '{query}' ({scope})")
    for source, n in results:
        print(f"  [{n.kind}] {n.title} ({source}) - {n.domain}")
        if n.trigger:
            print(f"      trigger: {n.trigger}")
    return 0


def cmd_recent(args: argparse.Namespace) -> int:
    out_dir = Path(args.out_dir)
    graph = load_graph(out_dir)
    cutoff = datetime.now(timezone.utc) - timedelta(days=args.days)
    hits = [n for n in graph.nodes if datetime.fromisoformat(n.last_touched) >= cutoff]
    hits.sort(key=lambda n: n.last_touched, reverse=True)
    if not hits:
        print(f"brainny: nothing captured in the last {args.days} day(s)")
        return 0
    print(f"brainny: {len(hits)} idea(s) from the last {args.days} day(s)")
    for n in hits:
        print(f"  [{n.kind}] {n.title} ({n.id}) - {n.last_touched}")
    return 0


def cmd_open(args: argparse.Namespace) -> int:
    out_dir = Path(args.out_dir)

    if args.central:
        central = config.get_value("central-folder")
        if not central:
            print("brainny: no central folder configured - run `brainny config set-central <path>` first.", file=sys.stderr)
            return 1
        project = args.project or _infer_project_name(load_graph(out_dir))
        if not project:
            print(
                "brainny: couldn't infer a project name from the local graph - pass one explicitly: "
                "`brainny open --central --project <name>`.",
                file=sys.stderr,
            )
            return 1
        path = html_path(Path(central) / project)
        if not path.exists():
            print(
                f"brainny: {path} doesn't exist yet - run `brainny sync` from the '{project}' project first.",
                file=sys.stderr,
            )
            return 1
        webbrowser.open(path.resolve().as_uri())
        print(f"brainny: opened {path} (central copy of '{project}')")
        return 0

    path = html_path(out_dir)
    if not path.exists():
        print(f"brainny: {path} doesn't exist yet - run `brainny query --html` first.", file=sys.stderr)
        return 1
    webbrowser.open(path.resolve().as_uri())
    print(f"brainny: opened {path}")
    return 0


def _run_git(args: list[str], cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)


def cmd_sync(args: argparse.Namespace) -> int:
    out_dir = Path(args.out_dir)
    graph = load_graph(out_dir)
    if not graph.nodes:
        print("brainny: nothing to sync - no ideas captured yet.", file=sys.stderr)
        return 1

    central = config.get_value("central-folder")
    if not central:
        print("brainny: no central folder configured - run `brainny config set-central <path>` first.", file=sys.stderr)
        return 1

    project = args.project or _infer_project_name(graph)
    if not project:
        print("brainny: could not infer a project name from captures - pass --project explicitly.", file=sys.stderr)
        return 1

    # local -> central only, always (never the reverse without an explicit
    # pull command) — see SEED.md §1.7 and OPERATIONS.md §3. Capture/attach
    # already do this same mirror automatically on every call (OPERATIONS.md
    # step 17) -- this command exists for backfilling ideas captured before
    # a central folder was configured, and for `--push`, its only GitHub-
    # touching job.
    central_root = Path(central)
    central_out = _sync_to_central(out_dir, graph, project)

    print(f"brainny: synced {len(graph.nodes)} idea(s) to {graph_path(central_out)}")

    return _maybe_push(central_root, project, len(graph.nodes), args.push)


def _maybe_push(central_root: Path, project: str, idea_count: int, push_requested: bool) -> int:
    """GitHub sync (OPERATIONS.md §6 step 5): brainny never runs `git init`
    or `git remote add` on the user's behalf — it only ever pushes to a git
    repo + remote the user already set up themselves in the central folder.
    Pushing is never silent: it only happens when explicitly requested via
    --push for this run, or via the durable `git-auto-push` setting the
    user opted into. (Claude-level rule, not enforced by this code: when
    an AI session invokes --push on the user's behalf, it should still ask
    first — see OPERATIONS.md §6 step 5.)"""
    if not (central_root / ".git").is_dir():
        if push_requested:
            print(f"brainny: {central_root} is not a git repo - run `git init` there first if you want GitHub sync.", file=sys.stderr)
            return 1
        return 0

    try:
        remote = _run_git(["remote"], central_root)
    except FileNotFoundError:
        print("brainny: git is not installed / not on PATH.", file=sys.stderr)
        return 1
    if remote.returncode != 0 or not remote.stdout.strip():
        if push_requested:
            print(f"brainny: {central_root} has no git remote - run `git remote add origin <url>` there first.", file=sys.stderr)
            return 1
        print("brainny: central folder is a git repo without a remote - local sync only.")
        return 0

    want_push = push_requested or config.get_value("git-auto-push") == "true"
    if not want_push:
        print("brainny: central folder has a git remote - rerun with `brainny sync --push` to push, or set `git-auto-push` to skip the flag.")
        return 0

    _run_git(["add", project], central_root)
    if _run_git(["diff", "--cached", "--quiet"], central_root).returncode == 0:
        print("brainny: nothing new to push - central copy already committed.")
        return 0

    commit = _run_git(["commit", "-m", f"brainny sync: {project} ({idea_count} idea(s))"], central_root)
    if commit.returncode != 0:
        print(f"brainny: git commit failed:\n{commit.stderr}", file=sys.stderr)
        return 1

    push = _run_git(["push"], central_root)
    if push.returncode != 0:
        print(f"brainny: git push failed:\n{push.stderr}", file=sys.stderr)
        return 1

    print(f"brainny: pushed to {central_root}'s git remote.")
    return 0


def cmd_not_yet(name: str):
    def _run(args: argparse.Namespace) -> int:
        print(f"brainny {name}: not implemented yet - lands in {NOT_YET[name]}.")
        print("See SEED.md section 7 for the roadmap.")
        return 1

    return _run


class BannerArgumentParser(argparse.ArgumentParser):
    """Same as ArgumentParser, but -h/--help shows the banner first."""

    def format_help(self) -> str:
        return render_banner() + "\n" + super().format_help()


def build_parser() -> argparse.ArgumentParser:
    parser = BannerArgumentParser(prog="brainny", description="brAInny - catches your ideas before the wind.")
    parser.add_argument("--version", action="version", version=f"brainny {__version__}")
    parser.add_argument(
        "--out-dir", default=str(DEFAULT_OUT_DIR), help="output directory (default: brainny-out)"
    )
    sub = parser.add_subparsers(dest="command", required=False)

    p_capture = sub.add_parser("capture", help="ingest entries.json into graph.json")
    p_capture.add_argument("entries", help="path to entries.json")
    p_capture.add_argument("--project", default="default", help="project name for provenance")
    p_capture.add_argument("--session", default="s1", help="session id for provenance")
    p_capture.set_defaults(func=cmd_capture)

    p_attach = sub.add_parser(
        "attach", help="attach a small code/plot/table file to an existing idea as evidence"
    )
    p_attach.add_argument("idea_id", help="the idea's id, e.g. idea_0007")
    p_attach.add_argument("file", help="path to the file to attach (small excerpt, not a full dataset)")
    p_attach.add_argument("--type", choices=["code", "plot", "table"], required=True)
    p_attach.add_argument("--description", help="one line describing what this shows")
    p_attach.add_argument("--rename", help="store under this filename instead of the source file's own name")
    p_attach.add_argument("--session", help="session id for the growth-log entry (default: unknown)")
    p_attach.set_defaults(func=cmd_attach)

    p_query = sub.add_parser("query", help="print the graph as a terminal tree")
    p_query.add_argument(
        "--html", action="store_true", help="(re)write graph.html instead of printing the terminal tree"
    )
    p_query.set_defaults(func=cmd_query)

    p_status = sub.add_parser("status", help="idea count, last capture time, central-sync state")
    p_status.set_defaults(func=cmd_status)

    p_config = sub.add_parser("config", help="get/set local settings (~/.brainny/config.json)")
    config_sub = p_config.add_subparsers(dest="action", required=True)
    p_config_get = config_sub.add_parser("get", help="print a setting (or all settings if omitted)")
    p_config_get.add_argument("key", nargs="?")
    p_config_get.set_defaults(func=cmd_config)
    p_config_set = config_sub.add_parser("set", help="set a setting")
    p_config_set.add_argument("key")
    p_config_set.add_argument("value")
    p_config_set.set_defaults(func=cmd_config)
    p_config_set_central = config_sub.add_parser(
        "set-central", help="set + validate the central folder path (creates it if missing)"
    )
    p_config_set_central.add_argument("path")
    p_config_set_central.add_argument(
        "--clone", metavar="URL",
        help="clone an existing central folder from this git URL instead of creating an empty one (path must not already exist / must be empty)",
    )
    p_config_set_central.set_defaults(func=cmd_config)

    p_sync = sub.add_parser("sync", help="push this project's ideas to the configured central folder")
    p_sync.add_argument("--project", help="project name (default: inferred from provenance)")
    p_sync.add_argument(
        "--push", action="store_true",
        help="also git commit+push if the central folder is a git repo with a remote (never runs without this flag or the git-auto-push setting)",
    )
    p_sync.set_defaults(func=cmd_sync)

    p_search = sub.add_parser("search", help="find ideas by keyword/tag/kind/domain")
    p_search.add_argument("term")
    p_search.set_defaults(func=cmd_search)

    p_recall = sub.add_parser(
        "recall", help="search this project AND every other project in the central folder"
    )
    p_recall.add_argument("terms", nargs="+", help="one or more keywords (matched OR-wise)")
    p_recall.set_defaults(func=cmd_recall)

    p_recent = sub.add_parser("recent", help="ideas captured in the last N days")
    p_recent.add_argument("--days", type=int, default=7)
    p_recent.set_defaults(func=cmd_recent)

    p_open = sub.add_parser("open", help="open graph.html in the default browser")
    p_open.add_argument(
        "--central", action="store_true",
        help="open the configured central folder's copy instead of the local one",
    )
    p_open.add_argument(
        "--project", help="which project's central copy to open with --central (default: inferred from the local graph)"
    )
    p_open.set_defaults(func=cmd_open)

    for name in NOT_YET:
        p = sub.add_parser(name, help=f"(not yet implemented - {NOT_YET[name]})")
        p.set_defaults(func=cmd_not_yet(name))

    return parser


def main(argv: list[str] | None = None) -> int:
    # The banner uses Unicode (braille art); Windows consoles default to a
    # legacy codepage (cp1252 etc.) for non-UTF8-locale processes, which
    # can't encode it and crashes with UnicodeEncodeError. Reconfigure
    # defensively (errors="replace" so worst case is "?", never a crash);
    # guarded because pytest's capsys stdout stand-in has no .reconfigure().
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass

    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command is None:
        print(render_banner())
        print("Run `brainny --help` to see commands.")
        return 0
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
