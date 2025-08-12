from __future__ import annotations
import json
import os
import re
import gc
from pathlib import Path
from contextlib import contextmanager
from timeit import default_timer as timer
from multiprocessing import Pool
from typing import Dict, List, Optional, Tuple, Union

import tqdm
from buildingspy.simulate.OpenModelica import Simulator as OpenModelicaSimulator
from buildingspy.simulate.Dymola import Simulator as DymolaSimulator

# Local
from .results_reader import ResultStreamReader
from teaser.logic.utilities import create_path


# ----------------------------- utils -----------------------------
@contextmanager
def timing(description: str):
    """Context Manager for simulation time measurement.

    Parameters
    ----------
    description : str, name and description of timer
    """
    start = timer()
    yield lambda: timer() - start
    elapsed = timer() - start
    print(f"{description}: {elapsed:.2f} Seconds")

def _to_posix(p: Union[str, Path]) -> str:
    return Path(p).as_posix()

def _simulator_factory(simulator: str):
    if simulator.lower() in {"omc", "openmodelica"}:
        return OpenModelicaSimulator
    if simulator.lower() in {"dymola"}:
        return DymolaSimulator
    raise ValueError("simulator must be 'omc' / 'openmodelica' or 'dymola'")


# ---------------------- manifest loading ------------------------
# We support two shapes produced by your export step:
#  A) Full object:
#     {
#       "project": "MyProj",
#       "engine": "omc",
#       "packagePath": "/path/to/MyProj",
#       "outputDir": "/path/to/BuildingsPyResults/results",
#       "items": [ {"model": "MyProj.B1.B1", "type": "X"}, ... ]
#     }
#  B) Minimal list (legacy):
#     [ {"model": "MyProj.B1.B1", "type": "X"}, ... ]

ManifestItems = List[Dict[str, Optional[str]]]




def _load_manifest(
        manifest_path: Union[str, Path],
        default_base: Optional[Path] = None,
        default_project: Optional[str] = None,
) -> Tuple[str, str, ManifestItems, Optional[str]]:
    """Return (packagePath, outputDir, items, engine_from_manifest).

    Fills in paths when absent using `default_base`/`default_project`.
    """
    mp = Path(manifest_path)
    data = json.loads(mp.read_text())

    if isinstance(data, list):
        items: ManifestItems = data
        project = default_project or _infer_project_from_items(items)
        base = default_base or mp.parent
        package_path = _to_posix(base / project)
        output_dir = _to_posix(base / "BuildingsPyResults" / "results")
        engine = None
    else:
        items = data.get("items", [])
        project = data.get("project") or default_project or _infer_project_from_items(items)
        package_path = data.get("packagePath") or _to_posix((default_base or mp.parent) / (project or ""))
        output_dir = data.get("outputDir") or _to_posix((default_base or mp.parent) / "BuildingsPyResults" / "results")
        engine = data.get("engine")

    if not items:
        raise ValueError("Manifest has no items.")

    return package_path, output_dir, items, engine


def _infer_project_from_items(items: ManifestItems) -> str:
    # Expect models like "Proj.Bldg.Bldg" – take the first token
    for it in items:
        m = re.match(r"([^.]+)\.\w+\.\w+", str(it.get("model", "")))
        if m:
            return m.group(1)
    raise ValueError("Cannot infer project name from manifest items.")

# ------------------------- worker task --------------------------

def _simulate_one(task: Dict[str, Union[str, float, int]]):
    """Run a single model simulation. `task` only contains small strings.
    Expected keys: model, packagePath, outputDir, engine, startTime, stopTime, intervals.
    Each task has its own outputDir to avoid OMC parallel I/O collisions.

    """
    Sim = _simulator_factory(task["engine"])  # type: ignore

    # Ensure the per-model output directory exists (safety in workers too)
    create_path(str(task["outputDir"]))

    s = Sim(
        modelName=task["model"],
        packagePath=task["packagePath"],
        outputDirectory=task["outputDir"],
    )

    # Settings – keep parity with the original code
    s.setSolver("dassl")
    s.setStartTime(float(task.get("startTime", 0)))
    s.setStopTime(float(task.get("stopTime", 31536000)))
    s.setNumberOfIntervals(int(task.get("intervals", 8760)))

    #ToDo: Gui for now for dymola, as BuildingsPy does not yet work properly with new dmc cli

    # Translate + simulate
    if task["engine"] == "dymola":
        s.showGUI()
    else:
        pass
    s.translate()
    s.simulate()

    return task["model"]


def simulate(
    path: str,
    manifest_path: str,
    loading_time: float,
    result_path: str,
    simulator: Optional[str] = None,
    *,
    start_time: Optional[float] = None,
    stop_time: Optional[float] = None,
    intervals: Optional[int] = None,
    keep_type_sum: bool = True,
    processes: Optional[int] = None,
) -> None:
    """Run BuildingsPy simulations based on an *external* manifest and
    stream results to a long CSV.

    Parameters
    ----------
    path : str
        Base directory that contains the exported Modelica package.
        Used as a fallback if the manifest omits absolute paths.
    manifest_path : str
        JSON file written by your export step. Supports the two shapes documented above.
    loading_time : float
        Previously measured TEASER+ loading time (logged to metadata).
    result_path : str
        Target CSV for long-format results: (building, timestep, heatload).
    simulator : Optional[str]
        Engine override ("omc"/"OpenModelica" or "dymola"). If None, use the value
        from the manifest or default to "omc".
    start_time, stop_time, intervals : Optional
        Simulation horizon. If None, use defaults (0, 31536000, 8760).
    keep_type_sum : bool
        Maintain lightweight per-type running sums during streaming.
    processes : Optional[int]
        Max worker processes. Defaults to `os.cpu_count()`.
    """

    base = Path(path)

    # 1) Load manifest created by the export step
    package_path, output_dir, items, engine_in_manifest = _load_manifest(
        manifest_path, default_base=base
    )

    engine = (simulator or engine_in_manifest or "omc").lower()

    # Defaults if not provided
    st = 0 if start_time is None else float(start_time)
    et = 31536000 if stop_time is None else float(stop_time)
    iv = 8760 if intervals is None else int(intervals)

    #Todo: double defaults set, look at sim runner -> get function!

    # 2) Compose worker tasks (small payload only)
    results_dir = Path(output_dir)
    results_dir.mkdir(parents=True, exist_ok=True)

    def _per_model_dir(model: str) -> Path:
        # Use the model string as a distinct subdir; dots are allowed on all OSes
        return results_dir / model

    tasks: List[Dict[str, Union[str, int, float]]] = []
    for it in items:
        model = it["model"]
        out_dir = _per_model_dir(model)
        create_path(str(out_dir))
        tasks.append(
            {
                "model": model,
                "packagePath": package_path,
                "outputDir": _to_posix(out_dir),
                "engine": engine,
                "startTime": st,
                "stopTime": et,
                "intervals": iv,
            }
        )

    # 3) Ensure minimal memory footprint
    gc.collect()

    # 4) Run simulations in parallel
    with timing("BuildingsPy-Simulation") as sim_time:
        with Pool(processes=processes) as pool:
            for _ in tqdm.tqdm(
                pool.imap_unordered(_simulate_one, tasks),
                total=len(tasks),
                desc="Simulated Buildings",
            ):
                pass
        total_sim_seconds = sim_time()

    #ToDo: maybe optional Flag, so not always necessary

    # 5) Stream results (one building at a time)
    with timing("Post-processing") as post_time:
        reader = ResultStreamReader(
            manifest=[
                {
                    "model": it["model"],
                    "type": it.get("type"),
                    "building": it.get("building"),
                }
                for it in items
            ],
            results_dir=results_dir,
            target_csv=Path(result_path),
            expected_len=int(iv),
            keep_type_sum=keep_type_sum,
            layout="wide",  # one row per building, columns = timesteps
        )
        type_sums = reader.run()
        total_post_seconds = post_time()

    # 6) Write metadata sidecar
    meta = {
        "engine": engine,
        "loading_time_s": float(loading_time),
        "simulation_time_s": float(total_sim_seconds),
        "post_processing_time_s": float(total_post_seconds),
        "result_csv": os.fspath(result_path),
        "results_dir": _to_posix(results_dir),
        "manifest": os.fspath(manifest_path),
        "start_time": st,
        "stop_time": et,
        "intervals": iv,
    }
    Path(result_path).with_suffix(".meta.json").write_text(json.dumps(meta, indent=2))

    # 7) Optional wide CSV with per-type sums
    if keep_type_sum and type_sums:
        reader.write_type_sums(Path(result_path).with_name("type_sums.csv"))

# def simulate_old(path, prj, loading_time, result_path, simulator="omc",  save_in_gml=False):
#     """
#     BuildingsPy: simulation, loading and saving results with either OpenModelica or Dymola
#     For that either software must be installed and the executable in the PATH.
#     Furthermore, the correct AixLib version must be also set.
#     By default is using pooling to use all cores for simulation.
#
#     :param save_in_gml: saves the heatload series in EnergyADE
#     :param simulator: omc or dymola currently supported
#     :param result_path: path to the excated heating load Dataframe
#     :param loading_time: Initial TEASER+ loading time
#     :param prj: TEASER+ Instance
#     :param path: Simulation Result path
#
#     """
#
#     with timing("BuildingsPy-Simulation") as sim_time:
#         simulators = []
#         for buildings in prj.buildings:
#             if simulator == "omc":
#                 s = OpenModelicaSimulator(modelName=prj.name + "." + buildings.name + "." + buildings.name,
#                               packagePath=path + "/" + prj.name,
#                               outputDirectory=path + "/" +prj.name + 'BuildingsPyResults'+ "\\results\\")
#             elif simulator == "dymola":
#                 s = DymolaSimulator(modelName=prj.name + "." + buildings.name + "." + buildings.name,
#                               packagePath=path + "/" + prj.name,
#                               outputDirectory=path + "/" + prj.name + 'BuildingsPyResults'+ "\\results\\")
#             else:
#                 raise Exception("Simulation not supported. Only omc or dymola are currently supported")
#             simulators.append(s)
#
#         with Pool() as pool:
#             for _ in tqdm.tqdm(
#                     pool.imap_unordered(simulateCase, simulators),
#                     total=len(simulators),
#                     desc="Simulated Buildings:"
#             ):
#                 pass
#
#
#     """BuildingsPy: Load Results"""
#     df_results = pd.DataFrame()
#     start_post_processing = timer()
#     for buildings in prj.buildings:
#         if re.match(r"(\w+)bt_", buildings.name):
#             try:
#                 matchObj = re.match(r"(\w+)bt_", buildings.name)
#                 results = os.path.join(path + "\\" + 'BuildingsPyResults' + "\\" +
#                                        prj.name + "\\results\\" + buildings.name)
#                 r = Reader(results, "dymola")
#                 (time1, heatload) = r.values('multizone.PHeater[1]')
#                 buildings.simulated_heat_load = heatload
#
#                 if matchObj.group(1) in df_results.columns:
#                     hl = pd.Series(heatload)
#                     df_results[matchObj.group(1)] = df_results[matchObj.group(1)].add(hl)
#                 else:
#                     df_results[matchObj.group(1)] = heatload
#
#             except:
#                 print(f'failed simulation for building {buildings.name}')
#         else:
#             try:
#                 results = os.path.join(path + "\\" + 'BuildingsPyResults' + "\\results\\"
#                                        +prj.name+"." +buildings.name+"."+buildings.name+"_res.MAT")
#                 print(results)
#                 r = Reader(results, "dymola")
#                 print(r)
#                 (time1, heatload) = r.values('multizone.PHeater[1]')
#                 # print(len(heatload))
#
#                 (time2, insidetemperature) = r.values('multizone.TAir[1]')
#                 (time3, outsidetemperature) = r.values('weaDat.weaBus.TDryBul')
#
#                 """Write into the building class instance"""
#                 buildings.simulated_heat_load = heatload
#                 """Write in a DataFrame, Each buiding gets a column for the heatload"""
#                 df_results[f'{buildings.name}'] = heatload
#
#             except:
#                 print(f'failed simulation for building {buildings.name}')
#
#
#
#     '''calculating the simulation time'''
#     end_post_processing = timer()
#     post_processing_time = (end_post_processing-start_post_processing)
#     df_results['loading time'] = loading_time
#     df_results['simulation time'] = sim_time
#     df_results['post processing time'] = post_processing_time
#
#     df_results.to_csv(result_path)


# def simulateCase(s):
#     """
#     sets the general parameters for the simulation
#     :param s: BuildingsPy Simulator object
#     """
#     # s.showGUI()
#     s.translate()
#     s.setSolver("dassl")
#     # print(s.printModelAndTime())
#     s.setStartTime(0)
#     s.setStopTime(31536000)
#     s.setNumberOfIntervals(8760)
#     s.simulate()