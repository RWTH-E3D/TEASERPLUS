# Beispiel für einen Test der Simulation mit OpenModelica und Dymola

from teaser.project import Project
from teaser.logic.simulation import simulate as s
import os

def test_simulate_with_different_simulators():
    # Projekt anlegen und Gebäude hinzufügen
    prj = Project(load_data=True)
    prj.name = "TestSimulate"
    prj.add_non_residential(
        method="bmvbs",
        usage="office",
        name="TestBuilding",
        year_of_construction=2015,
        number_of_floors=1,
        height_of_floors=3.0,
        net_leased_area=100.0
    )
    prj.number_of_elements_calc = 2
    prj.merge_windows_calc = False
    prj.calc_all_buildings(raise_errors=True)
    prj.export_aixlib(path="C:/Users/shamovich/TEASEROutput/omctest_1")

    # Exportpfad definieren
    export_path = os.path.join(os.path.dirname(__file__), "SimulationTest")
    os.makedirs(export_path, exist_ok=True)

    # AixLib Modell exportieren
    prj.export_aixlib(path=export_path)

    try:
        # Simulation mit OpenModelica
        result_om = s.simulate(
            prj,
            simulator="OpenModelica",
            result_path=os.path.join(export_path, "results_om"),
            package_path=os.path.join(export_path, "TestBuilding"),
            start_time=0,
            stop_time=3600 * 24 * 7  # Eine Woche simulieren
        )
        print("OpenModelica Simulation erfolgreich:")
        print(f"Ergebnisse gespeichert in: {result_om['result_path']}")

        # Simulation mit Dymola
        result_dy = s.simulate(
            prj,
            simulator="Dymola",
            result_path=os.path.join(export_path, "results_dy"),
            package_path=os.path.join(export_path, "TestBuilding"),
            start_time=0,
            stop_time=3600 * 24 * 7
        )
        print("Dymola Simulation erfolgreich:")
        print(f"Ergebnisse gespeichert in: {result_dy['result_path']}")

    except Exception as e:
        print(f"Fehler bei der Simulation: {str(e)}")
        raise


if __name__ == "__main__":
    test_simulate_with_different_simulators()