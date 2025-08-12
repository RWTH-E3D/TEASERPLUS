from __future__ import annotations
from pathlib import Path
from typing import Dict, List, Optional
from collections import defaultdict
import csv
import numpy as np
import pandas as pd

from buildingspy.io.outputfile import Reader


class ResultStreamReader:
    """Stream per-building heat-load results from Dymola/OpenModelica MAT files
    to disk with minimal memory.

    Supports two output layouts:
      - layout="wide": one CSV row per building; columns are timesteps 0..N-1.
      - layout="long": rows = (building, timestep, heatload). (Not default.)

    Manifest item schema (dict):
    {"model": "Proj.Bldg.Bldg", "type": Optional[str], "building": Optional[str]}
    If "building" is missing, the building name is derived from the model string.
    """

    def __init__(
        self,
        manifest: List[Dict[str, Optional[str]]],
        results_dir: Path,
        target_csv: Path,
        keep_type_sum: bool = True,
        expected_len: int = 8760,
        layout: str = "wide",
    ) -> None:
        self.manifest = manifest
        self.results_dir = Path(results_dir)
        self.target_csv = Path(target_csv)
        self.keep_type_sum = keep_type_sum
        self.expected_len = expected_len
        assert layout in {"wide", "long"}
        self.layout = layout
        self._type_sums: Dict[str, np.ndarray] = defaultdict(
            lambda: np.zeros(self.expected_len, dtype=np.float32)
        )

    # ----------------------- public API -----------------------
    def run(self) -> Dict[str, np.ndarray]:
        header_written = self.target_csv.exists() and self.target_csv.stat().st_size > 0

        for item in self.manifest:
            model = item["model"]
            btype = item.get("type")
            bname = item.get("building") or self._building_from_model(model)

            mat = self._locate_results_mat(model)

            try:
                reader = Reader(str(mat), "dymola")
                _, series = reader.values("multizone.PHeater[1]")
                heat = np.asarray(series, dtype=np.float32)

                # Align to expected_len for consistent columns/aggregates
                heat = self._align_len(heat)

                if self.layout == "wide":
                    self._append_wide_csv(bname, heat, header=not header_written)
                else:
                    timesteps = np.arange(len(heat), dtype=np.uint32)
                    self._append_long_csv(bname, timesteps, heat, header=not header_written)

                header_written = True

                if self.keep_type_sum and btype:
                    self._update_type_sum(btype, heat)

            except Exception as e:  # report and continue
                print(f"Failed to process {mat}: {e}")

        return dict(self._type_sums)

    def write_type_sums(self, path: Path) -> None:
        if not self._type_sums:
            return
        df = pd.DataFrame({k: v for k, v in self._type_sums.items()})
        df.index.name = "timestep"  # 0..N-1
        df.to_csv(path)

    # ---------------------- internals ------------------------
    def _building_from_model(self, model: str) -> str:
        parts = str(model).split('.')
        return parts[1] if len(parts) >= 2 else str(model)

    def _locate_results_mat(self, model: str) -> Path:
        # Preferred: per-model subdirectory created by simulate(): <results_dir>/<model>/<model>_res.MAT
        candidate = self.results_dir / model / f"{model}_res.MAT"
        if candidate.exists():
            return candidate
        # Fallback: directly under results_dir (for legacy runs)
        legacy = self.results_dir / f"{model}_res.MAT"
        if legacy.exists():
            return legacy
        # As a last resort, try Modelica-style MAT name without suffix
        alt = self.results_dir / model / f"{model}.mat"
        return alt

    def _align_len(self, heat: np.ndarray) -> np.ndarray:
        n = len(heat)
        if n == self.expected_len:
            return heat
        if n == self.expected_len + 1:
            return heat[1:]
        if n < self.expected_len:
            # pad with last value to keep width stable
            pad = np.full(self.expected_len - n, heat[-1] if n else 0.0, dtype=np.float32)
            return np.concatenate([heat.astype(np.float32, copy=False), pad])
        return heat[: self.expected_len]

    def _append_wide_csv(self, building: str, heatload: np.ndarray, *, header: bool) -> None:
        mode = 'a'
        with open(self.target_csv, mode, newline='') as f:
            writer = csv.writer(f)
            if header:
                header_row = ["building"] + [str(i) for i in range(self.expected_len)]
                writer.writerow(header_row)
            row = [building] + [float(x) for x in heatload.tolist()]
            writer.writerow(row)

    def _append_long_csv(self, building: str, timesteps: np.ndarray, heatload: np.ndarray, *, header: bool) -> None:
        frame = pd.DataFrame({"building": building, "timestep": timesteps, "heatload": heatload})
        frame.to_csv(self.target_csv, mode="a", index=False, header=header)
        del frame  # hint GC

    def _update_type_sum(self, btype: str, heat: np.ndarray) -> None:
        arr = self._type_sums[btype]
        arr += heat.astype(np.float32, copy=False)