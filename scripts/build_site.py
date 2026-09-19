#!/usr/bin/env python3
"""Stage the lightweight GitHub Pages bundle without uploading source PDFs."""
from __future__ import annotations

import argparse
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def copy_file(root: Path, out: Path, relative: str) -> None:
    source = root / relative
    target = out / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)


def build(root: Path, out: Path) -> None:
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    copy_file(root, out, "index.html")
    shutil.copytree(root / "site", out / "site")
    for relative in [
        "README.md",
        "station_master.md",
        "evidence-ledger.md",
        "summary_2026-09-17.md",
        "review_2026-09-17.md",
        "price_reasonableness_2026-09-17.md",
        "thaith_radar_dossier_review_2026-09-17.md",
        "tmd_budget_explanation_additional_review_2026-09-17.md",
        "data/political_context_2026-09-19.json",
    ]:
        copy_file(root, out, relative)
    # research-staging file with known-refuted claims and a do-not-publish
    # review status must not ship in the public bundle
    deny = {"radar_procurement_sweep_2026-09-15.json"}
    for source in (root / "data").glob("*"):
        if source.is_file() and source.name not in deny:
            copy_file(root, out, str(source.relative_to(root)))
    print(f"staged site at {out} ({sum(1 for _ in out.rglob('*') if _.is_file())} files)")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--out", type=Path, default=ROOT / "_site")
    args = parser.parse_args()
    build(args.root.resolve(), args.out.resolve())


if __name__ == "__main__":
    main()
