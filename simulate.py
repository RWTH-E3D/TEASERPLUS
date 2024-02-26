import os
import pandas as pd
from buildingspy.simulate.Simulator import Simulator
from buildingspy.io.outputfile import Reader
import matplotlib.pyplot as plt
from multiprocessing import Pool
from timeit import default_timer as timer
import re
import shutil
import tqdm as tqdm
def simulate(path, prj, loading_time, result_path, visualization=False, save_in_gml=False):
    """BuildingsPy: simulation, loading and saving results, visualization
    :param save_in_gml: saves the heatload series in EnergyADE
    :param visualization: Graphs the heatload, inner and outside temperature
    :param result_path: path to the excated heating load Dataframe
    :param loading_time: Initial TEASER+ loasing time
    :param prj: TEASER+ Instance
    :param path: Simulation Result path
    """

    """BuildingsPy: Setup / Simulation"""
    start_simulation = timer()
    li = []
    for buildings in prj.buildings:
        s = Simulator(modelName=prj.name + "." + buildings.name + "." + buildings.name,
                          simulator="dymola", packagePath=path + "\\" + prj.name,
                          outputDirectory=path + "\\" + 'BuildingsPyResults' + "\\" + prj.name + "\\results")
        li.append(s)

    po = Pool()
    # result = po.map(simulateCase, li, chunksize=8)
    result_list_tqdm = []
    for _ in tqdm.tqdm(po.imap(simulateCase, li), total=len(li)):
        result_list_tqdm.append(_)
    end_simulation = timer()
    simulation_time = (end_simulation-start_simulation)

    """Clean up"""
    # for buildings in prj1.buildings:
    #     shutil.rmtree(path + "\\" + prj1.name)

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
                results = os.path.join(path + "\\" + 'BuildingsPyResults' + "\\" +
                                       prj.name + "\\results\\" + buildings.name)
                r = Reader(results, "dymola")
                (time1, heatload) = r.values('multizone.PHeater[1]')
                # print(len(heatload))

                (time2, insidetemperature) = r.values('multizone.TAir[1]')
                (time3, outsidetemperature) = r.values('weaDat.weaBus.TDryBul')

                """Write into the building class instance"""
                buildings.simulated_heat_load = heatload
                """Write in a DataFrame, Each buiding gets a column for the heatload"""
                df_results[f'{buildings.name}'] = heatload

                # df_results.to_csv(f'C:/Users/MaxPaine33/PycharmProjects/teaserplus/gmlfiles/Hamburg/'
                #                   f'Results_pandas_csv/5_Buildings_test/{prj.name}_results.csv')

            except:
                print(f'failed simulation for building {buildings.name}')

    if visualization:
        """BuildingsPy: plot Results"""
        fig = plt.figure(figsize=(12.8, 7.2), frameon=False, dpi=150)
        ax = fig.add_subplot(211)
        ax.plot(time1 / 3600, heatload / 1000, 'b', label=f'{buildings.name}', linewidth=1)
        ax.set_xlabel('Time [h]')
        ax.set_ylabel('Heat load [kW]')
        ax.xaxis.get_major_ticks(1440)
        ax.set_xlim(0, 8760)
        ax.legend()

        ax = fig.add_subplot(212)
        ax.plot(time3 / 3600, outsidetemperature - 273.15, 'b', label='Outside Temperature', linewidth=1)
        ax.plot(time2 / 3600, insidetemperature - 273.15, 'r', label='Inside Temperature', linewidth=1)
        ax.set_xlabel('Time [h]')
        ax.set_ylabel('temperature [$^\circ$C]')
        ax.xaxis.get_major_ticks(1440)
        ax.set_xlim(0, 8760)
        ax.legend()
        plt.show()

    '''calculating the simulation time'''
    end_post_processing = timer()
    post_processing_time = (end_post_processing-start_post_processing)
    df_results['loading time'] = loading_time
    df_results['simulation time'] = simulation_time
    df_results['post processing time'] = post_processing_time

    df_results.to_csv(result_path)


def simulateCase(s):
    """
    sets the general parameters for the simulation
    :param s: BuildingsPy Simulator object
    """
    # s.showGUI()
    # s.translate()
    s.setSolver("Cvode")
    # print(s.printModelAndTime())
    s.setStartTime(0)
    s.setStopTime(31536000)
    s.setNumberOfIntervals(8760)
    s.simulate()