#!/usr/bin/env python3
from pathlib import Path
from typing import Optional

# Reuse your own helpers
from teaser.logic.simulation.simulate import load_manifest  # manifest loader
from teaser.logic.simulation.results_reader import ResultStreamReader  # streaming reader

def read_results_only(
    manifest_path: str,
    out_csv: str,
    *,
    intervals: int = 8760,
    layout: str = "wide",
    keep_type_sum: bool = True,
    write_building_sums: bool = True,
    write_type_sums: bool = True,
) -> None:
    # Use the same manifest semantics as simulate.simulate()
    _, output_dir, items, _ = load_manifest(manifest_path)  # :contentReference[oaicite:0]{index=0}
    results_dir = Path(output_dir)

    reader = ResultStreamReader(
        manifest=[
            {"model": it["model"], "type": it.get("type"), "building": it.get("building")}
            for it in items
        ],
        results_dir=results_dir,
        target_csv=Path(out_csv),
        expected_len=int(intervals),
        keep_type_sum=keep_type_sum,
        layout=layout,
    )  # same ctor you use in simulate.py step 5 :contentReference[oaicite:1]{index=1}

    type_sums = reader.run()  # streams MAT → CSV (and keeps in-memory sums) :contentReference[oaicite:2]{index=2}

    if write_building_sums:
        # writes building_sums.csv next to out_csv (your existing method) :contentReference[oaicite:3]{index=3}
        reader.write_building_sums()

    if keep_type_sum and write_type_sums and type_sums:
        reader.write_type_sums(Path(out_csv).with_name("type_sums.csv"))  # :contentReference[oaicite:4]{index=4}


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="Aggregate simulation results only (no simulation).")
    ap.add_argument("--manifest", required=True, help="Path to manifest JSON")
    ap.add_argument("--out", required=True, help="Path to output CSV (wide or long)")
    ap.add_argument("--layout", choices=["wide", "long"], default="wide")
    ap.add_argument("--intervals", type=int, default=8760)
    ap.add_argument("--no-type-sums", action="store_true")
    ap.add_argument("--no-building-sums", action="store_true")
    args = ap.parse_args()

    read_results_only(
        manifest_path=args.manifest,
        out_csv=args.out,
        intervals=args.intervals,
        layout=args.layout,
        keep_type_sum=not args.no_type_sums,
        write_building_sums=not args.no_building_sums,
        write_type_sums=not args.no_type_sums,
    )
