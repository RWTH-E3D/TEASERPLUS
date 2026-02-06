from __future__ import annotations

import os
from pathlib import Path

from teaser.data.input.citydpc_input import load_dpc_buildings
from teaser.logic.simulation.export_and_manifest import export_and_manifest
from teaser.logic.utilities import get_default_path, get_full_path
from teaser.project import Project

try:
    from citydpc.dataset import Dataset
    from citydpc.core.input.cityjsonInput import load_buildings_from_json_file
    from citydpc.tools.partywall import get_party_walls
except ImportError as exc:
    raise SystemExit(
        "This example requires the citydpc package. Install it and retry."
    ) from exc


def main() -> None:
    example_root = Path(__file__).resolve().parent / "examplefiles" / "citydpc"
    cityjson_path = example_root / "osm2Cgml_output.json"
    if not cityjson_path.exists():
        raise FileNotFoundError(f"Missing CityJSON example: {cityjson_path}")

    dataset = Dataset()
    load_buildings_from_json_file(dataset, str(cityjson_path))

    for building in dataset.get_building_list():
        if building.measuredHeight is None:
            building.measuredHeight = 6.15

    max_buildings = None
    if max_buildings is not None:
        dataset.buildings = {
            k: v
            for i, (k, v) in enumerate(dataset.buildings.items())
            if i < max_buildings
        }

    use_party_walls = False
    party_walls = get_party_walls(dataset) if use_party_walls else [[None]]

    prj = Project(load_data=True)
    prj.name = "citydpc_bedburg_example"
    load_dpc_buildings(prj, dataset, party_walls, method="tabula_de")
    prj.number_of_elements_calc = 2
    prj.merge_windows_calc = False
    prj.weather_file_path = get_full_path(
        os.path.join(
            "data",
            "input",
            "inputdata",
            "weatherdata",
            "TRY2015_510139065530_Jahr.mos",
        )
    )
    prj.calc_all_buildings(raise_errors=True)

    export_root = Path(get_default_path())
    manifest_file = export_and_manifest(prj, str(export_root))
    package_dir = export_root / prj.name
    print(f"AixLib package written to: {package_dir}")
    print(f"Manifest written to: {manifest_file}")


if __name__ == "__main__":
    main()
