"""Static renderer entry point (architecture: "a static renderer -- `bitbull
dash render` turns runs/** into self-contained HTML on disk"). Stdlib only.
It never touches a Parquet series file.

For each run directory holding a `run.json` it writes
  <out>/<run_id>.html            the run page (results / cost-unset / in-progress / failed)
  <out>/<run_id>.explorer.html   only if the directory also holds `sweep.json`
  <out>/<run_id>.report.md       only with --reports (rendered from run.json alone)

Reports are written to <out>, never into the runs directory: this tool does
not modify run directories. (The contract's canonical location for report.md
is `runs/<run_id>/report.md`; use `write_report_md(run_dir)` to put one there.)

Heartbeat freshness is judged against the wall clock at render time, and the
page says so; a static page cannot stay fresh. Pass --now for a reproducible
render.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys
from datetime import datetime, timezone

from bitbull.ui.explorer import render_explorer_html
from bitbull.ui.freshness import parse_rfc3339_utc
from bitbull.ui.render import render_run_page_html
from bitbull.ui.report_md import render_report_md


def _load_json(path: pathlib.Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _atomic_write(path: pathlib.Path, text: str) -> pathlib.Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f"{path.name}.tmp")
    tmp.write_text(text, encoding="utf-8", newline="\n")
    tmp.replace(path)  # atomic rename, matching run-output-contract-v1 SS2's own discipline
    return path


def render_one(
    run_dir: pathlib.Path,
    out_dir: pathlib.Path,
    *,
    now_utc: datetime | None = None,
    stale_after_seconds: int | None = None,
    reports: bool = False,
) -> list[pathlib.Path]:
    run = _load_json(run_dir / "run.json")
    heartbeat_path = run_dir / "heartbeat.json"
    heartbeat = _load_json(heartbeat_path) if heartbeat_path.is_file() else None
    written = [
        _atomic_write(
            out_dir / f"{run_dir.name}.html",
            render_run_page_html(run, heartbeat=heartbeat, now_utc=now_utc, stale_after_seconds=stale_after_seconds),
        )
    ]
    sweep_path = run_dir / "sweep.json"
    if sweep_path.is_file():
        written.append(_atomic_write(out_dir / f"{run_dir.name}.explorer.html", render_explorer_html(_load_json(sweep_path))))
    if reports:
        written.append(_atomic_write(out_dir / f"{run_dir.name}.report.md", render_report_md(run)))
    return written


def render_all(
    runs_dir: pathlib.Path,
    out_dir: pathlib.Path,
    *,
    now_utc: datetime | None = None,
    stale_after_seconds: int | None = None,
    reports: bool = False,
) -> list[pathlib.Path]:
    written: list[pathlib.Path] = []
    for run_dir in sorted(p for p in runs_dir.iterdir() if p.is_dir()):
        if not (run_dir / "run.json").is_file():
            continue
        written.extend(render_one(run_dir, out_dir, now_utc=now_utc, stale_after_seconds=stale_after_seconds, reports=reports))
    return written


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="bitbull-dash-render")
    parser.add_argument("runs_dir", type=pathlib.Path)
    parser.add_argument("out_dir", type=pathlib.Path)
    parser.add_argument("--reports", action="store_true", help="also write report.md per run, into out_dir")
    parser.add_argument("--now", default=None, help="RFC3339 UTC time (with Z) for heartbeat age; default: the wall clock")
    parser.add_argument("--stale-after-seconds", type=int, default=None, help="heartbeat age beyond which a running run is called stale; none is specified by the contracts, so none is assumed")
    args = parser.parse_args(argv)
    if args.now is not None:
        now = parse_rfc3339_utc(args.now)
        if now is None:
            parser.error("--now must be RFC3339 UTC with an explicit Z")
    else:
        now = datetime.now(timezone.utc)
    for path in render_all(args.runs_dir, args.out_dir, now_utc=now, stale_after_seconds=args.stale_after_seconds, reports=args.reports):
        print(path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
