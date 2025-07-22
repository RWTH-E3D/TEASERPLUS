import os
import pandas as pd
from contextlib import contextmanager
from buildingspy.simulate.OpenModelica import Simulator as OpenModelicaSimulator
from buildingspy.simulate.Dymola import Simulator as DymolaSimulator
from buildingspy.io.outputfile import Reader
from multiprocessing import Pool
from timeit import default_timer as timer
import re
import tqdm as tqdm

@contextmanager
def timing(description: str):
    """Context Manager for simulation time measurement.

    Parameters
    ----------
    description : str, name and description of timer
    """
    start = timer()
    yield
    elapsed = timer() - start
    print(f"{description}: {elapsed:.2f} Seconds")

def simulate(path, prj, loading_time, result_path, simulator="omc",  save_in_gml=False):
    """
    BuildingsPy: simulation, loading and saving results with either OpenModelica or Dymola
    For that either software must be installed and the executable in the PATH.
    Furthermore, the correct AixLib version must be also set.
    By default is using pooling to use all cores for simulation.

    :param save_in_gml: saves the heatload series in EnergyADE
    :param simulator: omc or dymola currently supported
    :param result_path: path to the excated heating load Dataframe
    :param loading_time: Initial TEASER+ loading time
    :param prj: TEASER+ Instance
    :param path: Simulation Result path

    """

    with timing("BuildingsPy-Simulation") as sim_time:
        simulators = []
        for buildings in prj.buildings:
            if simulator == "omc":
                s = OpenModelicaSimulator(modelName=prj.name + "." + buildings.name + "." + buildings.name,
                              packagePath=path + "/" + prj.name,
                              outputDirectory=path + "/" +prj.name + 'BuildingsPyResults'+ "\\results\\")
            elif simulator == "dymola":
                s = DymolaSimulator(modelName=prj.name + "." + buildings.name + "." + buildings.name,
                              packagePath=path + "/" + prj.name,
                              outputDirectory=path + "/" + prj.name + 'BuildingsPyResults'+ "\\results\\")
            else:
                raise Exception("Simulation not supported. Only omc or dymola are currently supported")
            simulators.append(s)

        with Pool() as pool:
            for _ in tqdm.tqdm(
                    pool.imap_unordered(simulateCase, simulators),
                    total=len(simulators),
                    desc="Simulated Buildings:"
            ):
                pass


    """BuildingsPy: Load Results"""
    df_results = pd.DataFrame()
    start_post_processing = timer()
    for buildings in prj.buildings:
        if re.match(r"(\w+)bt_", buildings.name):
            try:
                matchObj = re.match(r"(\w+)bt_", buildings.name)
                results = os.path.join(path + "\\" + 'BuildingsPyResults' + "\\" +
                                       prj.name + "\\results\\" + buildings.name)
                r = Reader(results, "dymola")
                (time1, heatload) = r.values('multizone.PHeater[1]')
                buildings.simulated_heat_load = heatload

                if matchObj.group(1) in df_results.columns:
                    hl = pd.Series(heatload)
                    df_results[matchObj.group(1)] = df_results[matchObj.group(1)].add(hl)
                else:
                    df_results[matchObj.group(1)] = heatload

            except:
                print(f'failed simulation for building {buildings.name}')
        else:
            try:
                results = os.path.join(path + "\\" + 'BuildingsPyResults' + "\\results\\"
                                       +prj.name+"." +buildings.name+"."+buildings.name+"_res.MAT")
                print(results)
                r = Reader(results, "dymola")
                print(r)
                (time1, heatload) = r.values('multizone.PHeater[1]')
                # print(len(heatload))

                (time2, insidetemperature) = r.values('multizone.TAir[1]')
                (time3, outsidetemperature) = r.values('weaDat.weaBus.TDryBul')

                """Write into the building class instance"""
                buildings.simulated_heat_load = heatload
                """Write in a DataFrame, Each buiding gets a column for the heatload"""
                df_results[f'{buildings.name}'] = heatload

            except:
                print(f'failed simulation for building {buildings.name}')



    '''calculating the simulation time'''
    end_post_processing = timer()
    post_processing_time = (end_post_processing-start_post_processing)
    df_results['loading time'] = loading_time
    df_results['simulation time'] = sim_time
    df_results['post processing time'] = post_processing_time

    df_results.to_csv(result_path)


def simulateCase(s):
    """
    sets the general parameters for the simulation
    :param s: BuildingsPy Simulator object
    """
    # s.showGUI()
    s.translate()
    s.setSolver("dassl")
    # print(s.printModelAndTime())
    s.setStartTime(0)
    s.setStopTime(31536000)
    s.setNumberOfIntervals(8760)
    s.simulate()