"""Static renderer entry point (architecture: "a static renderer -- `bitbull
dash render` turns runs/** into self-contained HTML on disk"). Round A scope
only: writes index.html per run directory using render.render_run_page_html.
Stdlib only -- json + pathlib + argparse. No polars import needed here since
this module never touches a Parquet series file.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

from bitbull.ui.render import render_run_page_html


def _load_run_json(run_dir: pathlib.Path) -> dict:
    run_json_path = run_dir / "run.json"
    with run_json_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def render_one(run_dir: pathlib.Path, out_dir: pathlib.Path) -> pathlib.Path:
    run = _load_run_json(run_dir)
    html_text = render_run_page_html(run)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{run_dir.name}.html"
    tmp_path = out_path.with_suffix(".html.tmp")
    tmp_path.write_text(html_text, encoding="utf-8")
    tmp_path.replace(out_path)  # atomic rename, matching run-output-contract-v1 §2's own discipline
    return out_path


def render_all(runs_dir: pathlib.Path, out_dir: pathlib.Path) -> list[pathlib.Path]:
    written = []
    for run_dir in sorted(p for p in runs_dir.iterdir() if p.is_dir()):
        if not (run_dir / "run.json").is_file():
            continue
        written.append(render_one(run_dir, out_dir))
    return written


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="bitbull-dash-render")
    parser.add_argument("runs_dir", type=pathlib.Path)
    parser.add_argument("out_dir", type=pathlib.Path)
    args = parser.parse_args(argv)
    written = render_all(args.runs_dir, args.out_dir)
    for path in written:
        print(path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
