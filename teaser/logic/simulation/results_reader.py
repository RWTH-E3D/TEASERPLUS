from __future__ import annotations
from pathlib import Path
from typing import Dict, Iterable, List, Optional
from collections import defaultdict
import numpy as np
import pandas as pd

from buildingspy.io.outputfile import Reader


class ResultStreamReader:
    """Stream per-building heat-load results from Dymola/OpenModelica MAT files
    into a long-format CSV, keeping memory usage minimal.

    Expected manifest item schema (dict):
    {"model": "Proj.BldgName.BldgName", "type": Optional[str]}

    Output CSV schema (long format):
    building, timestep, heatload
    """

    def __init__(
        self,
        manifest: List[Dict[str, Optional[str]]],
        results_dir: Path,
        target_csv: Path,
        keep_type_sum: bool = True,
        expected_len: int = 8760,
    ) -> None:
        self.manifest = manifest
        self.results_dir = Path(results_dir)
        self.target_csv = Path(target_csv)
        self.keep_type_sum = keep_type_sum
        self.expected_len = expected_len
        self._type_sums: Dict[str, np.ndarray] = defaultdict(
            lambda: np.zeros(self.expected_len, dtype=np.float32)
        )

    # ----------------------- public API -----------------------
    def run(self) -> Dict[str, np.ndarray]:
        header_written = self.target_csv.exists() and self.target_csv.stat().st_size > 0

        for item in self.manifest:
            model = item["model"]
            btype = item.get("type")
            mat = self.results_dir / f"{model}_res.MAT"

            try:
                reader = Reader(str(mat), "dymola")
                time_vec, series = reader.values("multizone.PHeater[1]")
                heat = np.asarray(series, dtype=np.float32)

                # Some solvers give 8761 points (including t=0). Use indices instead of hours.
                timesteps = np.arange(len(heat), dtype=np.uint32)
                self._append_long_csv(model, timesteps, heat, header=not header_written)
                header_written = True

                if self.keep_type_sum and btype:
                    self._update_type_sum(btype, heat)

            except Exception as e:  # noqa: BLE001 – report and continue
                print(f"Failed to process {mat.name}: {e}")

        return dict(self._type_sums)

    def write_type_sums(self, path: Path) -> None:
        if not self._type_sums:
            return
        df = pd.DataFrame({k: v for k, v in self._type_sums.items()})
        # index is timestep (0..N-1)
        df.index.name = "timestep"
        df.to_csv(path)

    # ---------------------- internals ------------------------
    def _append_long_csv(
        self,
        building: str,
        timesteps: np.ndarray,
        heatload: np.ndarray,
        *,
        header: bool,
    ) -> None:
        # Minimal in-RAM object; downcast already done
        frame = pd.DataFrame(
            {
                "building": building,
                "timestep": timesteps,
                "heatload": heatload,
            }
        )
        frame.to_csv(self.target_csv, mode="a", index=False, header=header)
        del frame  # hint GC

    def _update_type_sum(self, btype: str, heat: np.ndarray) -> None:
        arr = self._type_sums[btype]
        # Align lengths if solver produced one extra sample
        if len(heat) != len(arr):
            if len(heat) == len(arr) + 1:
                heat = heat[1:]
            elif len(heat) == len(arr) - 1:
                # pad with last value; rare, but makes sums robust
                heat = np.pad(heat, (0, 1), mode="edge")
            else:
                # fallback: resize to expected_len
                heat = heat[: self.expected_len]
        arr += heat.astype(np.float32, copy=False)