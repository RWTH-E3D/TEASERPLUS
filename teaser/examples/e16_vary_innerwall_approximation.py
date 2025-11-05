"""
This test case can be used to simulate different building types with varying interior wall approximation
approaches, specifically teaser_default, teco_graph_based, and teco_analytical.
As documented elsewhere, both teco_graph_based and teco_analytical ONLY apply to:
- single-family (tabula_de,kfw)  and terraced houses (tabula_de,kfw) with 2 to 4 floors,
- multi-family houses (tabula_de,kfw),
- office buildings (bmvbs) with at least 200m^2 net leased area per storey (graph-based only).
Using said approaches outside of these boundaries will raise a value error, and terminate the run.

Relevance: Varying interior wall areas/masses lead to changes in heat loads (and building material use).
"""

from teaser.project import Project
from teaser.logic.utilities import get_default_path
from pathlib import Path
from teaser.logic.simulation.export_and_manifest import export_and_manifest
from teaser.logic.simulation.simulate import simulate

def main():
    # Projekt anlegen und Gebäude hinzufügen
    prj = Project(load_data=True)
    prj.name = "inner_wall_approximation"
    # prj.add_residential(
    #     method="tabula_de",
    #     usage="single_family_house",
    #     name="sfh_teaser_default",
    #     year_of_construction=2015,
    #     number_of_floors=2,
    #     height_of_floors=3.0,
    #     net_leased_area=145.0,
    #     inner_wall_approximation_approach="teaser_default"
    # )
    # prj.add_residential(
    #     method="tabula_de",
    #     usage="single_family_house",
    #     name="sfh_teco_graph_based",
    #     year_of_construction=2015,
    #     number_of_floors=2,
    #     height_of_floors=3.0,
    #     net_leased_area=145.0,
    #     inner_wall_approximation_approach="teco_graph_based"
    # )
    # prj.add_residential(
    #     method="tabula_de",
    #     usage="single_family_house",
    #     name="sfh_teco_analytical",
    #     year_of_construction=2015,
    #     number_of_floors=2,
    #     height_of_floors=3.0,
    #     net_leased_area=145.0,
    #     inner_wall_approximation_approach="teco_analytical"
    # )
    # prj.add_residential(
    #     method="tabula_de",
    #     usage="terraced_house",
    #     name="th_teaser_default",
    #     year_of_construction=2015,
    #     number_of_floors=2,
    #     height_of_floors=3.0,
    #     net_leased_area=145.0,
    #     inner_wall_approximation_approach="teaser_default"
    # )
    # prj.add_residential(
    #     method="tabula_de",
    #     usage="terraced_house",
    #     name="th_teco_graph_based",
    #     year_of_construction=2015,
    #     number_of_floors=2,
    #     height_of_floors=3.0,
    #     net_leased_area=145.0,
    #     inner_wall_approximation_approach="teco_graph_based"
    # )
    # prj.add_residential(
    #     method="tabula_de",
    #     usage="terraced_house",
    #     name="th_teco_analytical",
    #     year_of_construction=2015,
    #     number_of_floors=2,
    #     height_of_floors=3.0,
    #     net_leased_area=145.0,
    #     inner_wall_approximation_approach="teco_analytical"
    # )
    # prj.add_residential(
    #     method="kfw",
    #     usage="multi_family_house",
    #     name="mfh_default",
    #     year_of_construction=1995,
    #     number_of_floors=1,
    #     height_of_floors=3.0,
    #     net_leased_area=500.0,
    #     inner_wall_approximation_approach="teaser_default",
    # )
    # prj.add_residential(
    #     method="tabula_de",
    #     usage="multi_family_house",
    #     name="mfh_graph_based",
    #     year_of_construction=1995,
    #     number_of_floors=1,
    #     height_of_floors=3.0,
    #     net_leased_area=500.0,
    #     inner_wall_approximation_approach="teco_graph_based",
    # )
    # prj.add_residential(
    #     method="kfw",
    #     usage="multi_family_house",
    #     name="mfh_analytical",
    #     year_of_construction=1995,
    #     number_of_floors=1,
    #     height_of_floors=3.0,
    #     net_leased_area=500.0,
    #     inner_wall_approximation_approach="teco_analytical",
    # )
    # prj.add_non_residential(
    #     method="bmvbs",
    #     usage="office",
    #     name="Office",
    #     year_of_construction=2005,
    #     number_of_floors=2,
    #     height_of_floors=3.0,
    #     net_leased_area=500.0,
    #     with_ahu=False,
    #     inner_wall_approximation_approach="teaser_default",
    # )
    # prj.add_non_residential(
    #     method="bmvbs",
    #     usage="office",
    #     name="Office",
    #     year_of_construction=2005,
    #     number_of_floors=2,
    #     height_of_floors=3.0,
    #     net_leased_area=500.0,
    #     with_ahu=False,
    #     inner_wall_approximation_approach="teco_graph_based",
    # )
    prj.number_of_elements_calc = 2
    prj.merge_windows_calc = False
    prj.calc_all_buildings(raise_errors=True)


    # Print inner wall areas per zone/wall
    print("\n--- Inner wall areas per zone/wall ---")
    for b in prj.buildings:
        print(f"Building: {b.name} ({type(b).__name__})")
        for tz in b.thermal_zones:
            # Ensure areas are (re)computed for this zone
            try:
                tz.set_inner_wall_area()
            except Exception as e:
                print(f"  Zone {getattr(tz, 'name', '?')}: could not compute inner wall area: {e}")
                continue

            if not tz.inner_walls:
                print(f"  Zone {getattr(tz, 'name', '?')}: no inner_walls")
                continue

            total = 0.0
            for i, w in enumerate(tz.inner_walls, 1):
                print(f"  Zone {tz.name} | inner_wall #{i}: area = {getattr(w, 'area', None)}")
                total += getattr(w, "area", 0.0)
            print(f"  Zone {tz.name} total inner wall area: {total}")


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


    # # Simulation mit OpenModelica
    # simulate(
    #     path=str(export_root),
    #     manifest_path=str(manifest_file),
    #     loading_time=0.0,
    #     result_path=str(result_csv_om),
    #     simulator="OpenModelica",
    #     start_time=start_time,
    #     stop_time=stop_time,
    #     intervals=intervals,
    #     processes=3
    # )
    # print("OpenModelica Simulation erfolgreich:")
    # print(f"Ergebnisse gespeichert in: {result_csv_om}")



if __name__ == "__main__":
    main()
