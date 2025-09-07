from teaser.project import Project
from teaser.logic.utilities import get_default_path, create_path
from pathlib import Path
from teaser.logic.simulation.export_and_manifest import export_and_manifest
from teaser.logic.simulation.simulate import simulate


def main():
    # Projekt anlegen und Gebäude hinzufügen
    prj = Project(load_data=True)
    prj.name = "inner_graph_approx"
    prj.add_non_residential(
        method="bmvbs",
        usage="office",
        name="Office",
        year_of_construction=2015,
        number_of_floors=2,
        height_of_floors=3.0,
        net_leased_area=100.0,
        with_ahu=False,
        inner_wall_approximation_approach="teaser_default",
    )
    prj.add_residential(
        method="tabula_de",
        usage="single_family_house",
        name="sfh",
        year_of_construction=2015,
        number_of_floors=2,
        height_of_floors=3.0,
        net_leased_area=45.0,
        inner_wall_approximation_approach="teco_graph_based"
    )
    prj.add_residential(
        method="tabula_de",
        usage="multi_family_house",
        name="mfh",
        year_of_construction=2005,
        number_of_floors=1,
        height_of_floors=3.0,
        net_leased_area=100.0,
        inner_wall_approximation_approach="teco_graph_based",
    )
    prj.number_of_elements_calc = 2
    prj.merge_windows_calc = False
    prj.calc_all_buildings(raise_errors=True)

    # Standard-Ausgabepfad der TEASER-Utilities verwenden
    export_root = Path(get_default_path())

    # AixLib Modell exportieren und Manifest schreiben (nutzt Utilities)
    manifest_file = export_and_manifest(prj, str(export_root))

    # Eine Woche simulieren (in Sekunden) mit 168 Intervallen
    start_time = 0
    stop_time = 3600 * 24 * 7
    intervals = 24 * 7

    # Pfade für Ergebnis-CSV im Projektordner
    package_dir = export_root / prj.name
    result_csv_om = package_dir / "results_om.csv"
    result_csv_dy = package_dir / "results_dy.csv"

    # Simulation mit Dymola
    simulate(
        path=str(export_root),
        manifest_path=str(manifest_file),
        loading_time=0.0,
        result_path=str(result_csv_dy),
        simulator="Dymola",
        start_time=start_time,
        stop_time=stop_time,
        intervals=intervals,
    )
    print("Dymola Simulation erfolgreich:")
    print(f"Ergebnisse gespeichert in: {result_csv_dy}")

    # Simulation mit OpenModelica
    simulate(
        path=str(export_root),
        manifest_path=str(manifest_file),
        loading_time=0.0,
        result_path=str(result_csv_om),
        simulator="OpenModelica",
        start_time=start_time,
        stop_time=stop_time,
        intervals=intervals,
        processes=3
    )
    print("OpenModelica Simulation erfolgreich:")
    print(f"Ergebnisse gespeichert in: {result_csv_om}")



if __name__ == "__main__":
    main()