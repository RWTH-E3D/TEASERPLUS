# created November 2023
# by Clara Schmitz (master thesis)

"""This module includes a class for the final energy calculation of the heating system
"""
import math
from teaser.teaser.logic.buildingobjects.buildingsystems.fedemandwater import FEDemandWater


class FEDemandHeating(object):
    """FEDemandHeating class

    This class holds information for the heating system of the Building.
    The heat losses for the heating system are being set. This class does
    not affect the calculation in Dymola. It uses the calculated heat
    load and adds heat losses for water to calculate the final energy demand.

    Parameters
    ----------

    parent: HeatSupplySystem()
        The parent class of this object, the HeatSupplySystem the final
        energy demand belongs to. Allows for better control of hierarchical
        structures.
        Default is None

    Attributes
    ----------

    temp_ambient_water : float [degC]
        Holds the surrounding temperature of the warm water system.
    temp_ambient_heating : float [degC]
        Holds the surrounding temperature of the heating system.
    """

    def __init__(self, parent=None):
        """Constructor of FEDemandHeating class
        """
        self.parent = parent
        
        self._temp_ambient_water = self.parent.temp_ambient
        self._temp_ambient_heating = None
        if self.parent.pipe_routing_heating == "centralised outside":
            self._temp_ambient_heating = 13  # iwu formula 4-1
        else:
            self._temp_ambient_heating = self.parent.temp_ambient

    def _calc_gains_distribution_water_for_heating(self):
        """
        Calculation of heat gains through distribution of warm water
        that benefits the heating system. Dependent of the pipe routing and
        geometrical building values.

        Returns
        ----------
        result : float [kWh/a]
            gains distribution water for heating
        """

        length_horizontal_water = 0
        length_strand_water = 0
        length_stubs_water = 0

        # calculation of pipe length for hot water
        # iwu table 9
        if self.parent.pipe_routing_water == "centralised with circulation":

            length_horizontal_water = 2 * self.parent.length_char - 10
            length_strand_water = self.parent.length_char * self.parent.parent.number_of_floors / 2
            length_stubs_water = self.parent.length_char * self.parent.parent.number_of_floors / 2

        elif self.parent.pipe_routing_water == "centralised without circulation":

            length_horizontal_water = self.parent.length_char - 5
            length_strand_water = self.parent.length_char * self.parent.parent.number_of_floors / 4
            length_stubs_water = self.parent.length_char * self.parent.parent.number_of_floors / 2

        elif self.parent.pipe_routing_water == "decentralised":

            length_stubs_water = self.parent.length_char * self.parent.parent.number_of_floors / 2

        # calculation of heat loss coefficient and factor for hot water
        # iwu table 10
        heat_loss_coefficient_horizontal_water = 0.2
        heat_loss_factor_horizontal_water = 1.0

        heat_loss_coefficient_strand_water = 0.2
        heat_loss_factor_strand_water = 0.15

        if self.parent.parent.year_of_construction >= 2000 or self.parent.year_of_retrofit >= 2000:
            heat_loss_coefficient_stubs_water = 0.2
        else:
            heat_loss_coefficient_stubs_water = 1.4

        heat_loss_factor_stubs_water = 0.15

        # DIN V4701-10 formula 5.1.2-2 with iwu formula 4-2 and 4-3
        if self.parent.pipe_routing_water == "centralised with circulation":

            during_circulation = (self.parent.avg_temp_distribution_water - self._temp_ambient_water) * \
                                 self.parent.daily_operating_time_pump

            during_interruption = 0.5 * (32 - self._temp_ambient_water) * (24 - self.parent.daily_operating_time_pump)
            # 32 = avg_temp_distribution_water without circulation

            result = 1 / 1000 * (length_horizontal_water * heat_loss_coefficient_horizontal_water *
                               (1 - heat_loss_factor_horizontal_water) +
                               length_strand_water * heat_loss_coefficient_strand_water *
                               (1 - heat_loss_factor_strand_water) +
                               length_stubs_water * heat_loss_coefficient_stubs_water *
                               (1 - heat_loss_factor_stubs_water)) * \
                   (during_circulation + during_interruption) * self.parent.annual_operating_time_water * \
                   self.parent.annual_operating_time_heating / self.parent.annual_operating_time_water  # [kWh/a]

        else:

            result = 1 / 1000 * \
                   (length_horizontal_water * heat_loss_coefficient_horizontal_water *
                    (1 - heat_loss_factor_horizontal_water) +
                    length_strand_water * heat_loss_coefficient_strand_water *
                    (1 - heat_loss_factor_strand_water) +
                    length_stubs_water * heat_loss_coefficient_stubs_water *
                    (1 - heat_loss_factor_stubs_water)) * \
                   (self.parent.avg_temp_distribution_water - self._temp_ambient_water) * 24 \
                   * self.parent.annual_operating_time_water * \
                   self.parent.annual_operating_time_heating / self.parent.annual_operating_time_water  # [kWh/a]

        # print("_calc_gains_distribution_water_for_heating: " + str(result))
        if result is None or result == 0:
            return 0
        else:
            return result

    def _calc_gains_storage_water_for_heating(self):
        """
        Calculation of heat gains through storage of warm water
        that benefits the heating system. Dependent of the pipe routing and
        the storage loss that is calculated in FEDemandWater class.

        Returns
        ----------
        result : float [kWh/a]
            gains storage water for heating
        """

        fedemandwater = FEDemandWater(parent=self.parent)
        dissipation_storage_water = fedemandwater.calc_dissipation_storage_water()

        # DIN V 4701-10 table C.1-3a
        if self.parent.pipe_routing_heating != "centralised outside" and self.parent.pipe_routing_heating is not None:

            # DIN V 4701-10 formula 5.1.3-10
            result = self.parent.annual_operating_time_heating / self.parent.annual_operating_time_water * \
                   (1 - 0.15) * dissipation_storage_water  # [kWh/a]
            # 0.15 = Heat loss factor for components within the thermal envelope, DIN V 4701-10 table 5-2
        else:
            result = 0

        # print("_calc_gains_storage_water_for_heating: " + str(result))

        return result

    def _calc_dissipation_controll_emission_heating(self):
        """
        Calculation of heat dissipation through controll and
        emission of heating system.

        Returns
        ----------
        result : float [kWh/a]
            dissipation controll and emission heating
        """

        # iwu chapter 5.5
        if self.parent.pipe_routing_heating != "decentralised":
            if self.parent.building_type == "sfh":
                result = 10 * 8760 / 1000
            else:
                result = 20 * 8760 / 1000

        else:
            result = 0

        if self.parent.storage == "solar":
            result += (5 * 8760 / 1000)

        # print("_calc_dissipation_controll_emission_heating: " + str(result))
        return result

    def _calc_dissipation_distribution_heating(self):
        """
        Calculation of heat dissipation through distribution of heating energy.
        Dependent of the pipe routing and geometrical building values.

        Returns
        ----------
        result : float [kWh/a]
            dissipation distribution heating
        """

        length_horizontal_heating = 0
        length_strand_heating = 0
        length_tethers_heating = 0
        heat_loss_coefficient_horizontal_heating = 0
        heat_loss_factor_horizontal_heating = 0
        heat_loss_coefficient_strand_heating = 0
        heat_loss_factor_strand_heating = 0
        heat_loss_coefficient_tethers_heating = 0
        heat_loss_factor_tethers_heating = 0

        # calculation of pipe length and heat loss coefficient and factor for heating
        # iwu table 9 and table 10
        if self.parent.pipe_routing_heating == "centralised outside":

            length_horizontal_heating = 4 * self.parent.length_char - 10
            length_strand_heating = self.parent.length_char * self.parent.parent.number_of_floors
            length_tethers_heating = self.parent.length_char * self.parent.parent.number_of_floors * 2 / 3

            heat_loss_coefficient_horizontal_heating = 0.2
            heat_loss_factor_horizontal_heating = 1.0

            if self.parent.parent.year_of_construction >= 2000 or self.parent.year_of_retrofit >= 2000:
                heat_loss_coefficient_strand_heating = 0.26
            else:
                heat_loss_coefficient_strand_heating = 0.8
            heat_loss_factor_strand_heating = 0.35

            if self.parent.parent.year_of_construction >= 2000 or self.parent.year_of_retrofit >= 2000:
                heat_loss_coefficient_tethers_heating = 0.26
            else:
                heat_loss_coefficient_tethers_heating = 0.8
            heat_loss_factor_tethers_heating = 0.32

        elif self.parent.pipe_routing_heating == "centralised inside":

            length_horizontal_heating = 2 * self.parent.length_char - 10
            length_strand_heating = self.parent.length_char * self.parent.parent.number_of_floors / 2
            length_tethers_heating = self.parent.length_char * self.parent.parent.number_of_floors * 4
            
            heat_loss_coefficient_horizontal_heating = 0.2
            heat_loss_factor_horizontal_heating = 1.0

            if self.parent.parent.year_of_construction >= 2000 or self.parent.year_of_retrofit >= 2000:
                heat_loss_coefficient_strand_heating = 0.26
            else:
                heat_loss_coefficient_strand_heating = 0.2
            heat_loss_factor_strand_heating = 0.15

            if self.parent.parent.year_of_construction >= 2000 or self.parent.year_of_retrofit >= 2000:
                heat_loss_coefficient_tethers_heating = 0.3
            else:
                heat_loss_coefficient_tethers_heating = 0.26
            heat_loss_factor_tethers_heating = 0.1

        else:

            length_strand_heating = self.parent.length_char * self.parent.parent.number_of_floors * 6
            length_tethers_heating = self.parent.length_char * self.parent.parent.number_of_floors

            if self.parent.parent.year_of_construction >= 2000 or self.parent.year_of_retrofit >= 2000:
                heat_loss_coefficient_strand_heating = 0.26
            else:
                heat_loss_coefficient_strand_heating = 0.8
            heat_loss_factor_strand_heating = 0.35

            if self.parent.parent.year_of_construction >= 2000 or self.parent.year_of_retrofit >= 2000:
                heat_loss_coefficient_tethers_heating = 0.26
            else:
                heat_loss_coefficient_tethers_heating = 0.8
            heat_loss_factor_tethers_heating = 0.32

        # TABULA values
        if self.parent.heat_generation != "night storage":
            # iwu formula 4-1
            result = 1 / 1000 * (length_horizontal_heating * heat_loss_coefficient_horizontal_heating *
                               heat_loss_factor_horizontal_heating +
                               length_strand_heating * heat_loss_coefficient_strand_heating *
                               heat_loss_factor_strand_heating +
                               length_tethers_heating * heat_loss_coefficient_tethers_heating *
                               heat_loss_factor_tethers_heating * 0.8) * \
                   (self.parent.avg_temp_distribution_heating - self._temp_ambient_heating) * \
                   24 * self.parent.annual_operating_time_heating  # [kWh/a]
            # print("self.parent.avg_temp_distribution_heating: ", self.parent.avg_temp_distribution_heating)
            # print("self._temp_ambient_heating: ", self._temp_ambient_heating)
            # print("self.parent.annual_operating_time_heating: ", self.parent.annual_operating_time_heating)
            # print("self.parent.pipe_routing_heating: ", self.parent.pipe_routing_heating)
            # 24 = standard value of daily running time of circulation pump
            # 0.8 = partial heating factor acc. DIN V 4701-10 table 5.3-2 (= 1.0 for horizontal and strand pipes)

        else:
            result = 0

        # print("calc_dissipation_distribution_heating", result)

        return result

    def _calc_dissipation_storage_heating(self):
        """
        Calculation of heat dissipation through storage of heating energy.
        Dependent of the kind of the storage.

        Returns
        ----------
        result : float [kWh/a]
            dissipation storage heating
        """

        # Condition from TABULA for buffer storage
        if (self.parent.heat_generation in ["heatpump air", "condensing - chp", "chp"] or \
                (self.parent.heat_generation == "heatpump ground" and self.parent.building_type == "sfh")) and \
                    self.parent.avg_temp_distribution_water != 32:

            # DIN V 4701-10 formula 5.3.3-2
            vol_storage = 4 * self.parent.usable_area ** 0.7
            standby_heat_loss_heating = (0.5 + 0.25 * 1000 ** 0.4) * math.floor(vol_storage / 1000) + \
                               0.5 + 0.25 * (vol_storage % 1000) ** 0.4  # including calculation of n_storage

            if self.parent.pipe_routing_heating == "centralised outside":
                result = 1.2 * (self.parent.avg_temp_distribution_heating - self._temp_ambient_heating) / 45 * \
                         self.parent.annual_operating_time_heating * 1 * standby_heat_loss_heating  # [kWh/a]
            else:
                # DIN V 4701-10 formula 5.3.3-1
                result = 1.2 * (self.parent.avg_temp_distribution_heating - self._temp_ambient_heating) / 45 * \
                       self.parent.annual_operating_time_heating * 0.15 * standby_heat_loss_heating  # [kWh/a]
                # 0.15 = Heat loss factor for components within the thermal envelope, table 5-2 DIN V 4701-10

        else:
            result = 0

        # print("_calc_dissipation_storage_heating: " + str(result))

        return result

    def _calc_dissipation_generation_heating(self):
        """
        Calculation of heat dissipation through generation of heating energy.
        Dependent of the heat system and generation of the  building.

        Returns
        ----------
        expenditure_figure : float [-]
            for dissipation generation heating
        """

        if self.parent.heat_system == "electricity" and self.parent.heat_generation != "night storage":

            # iwu chapter 2.2
            if self.parent.heat_generation == "heatpump air":
                annual_performance_factor_heat_pump_55 = 2.6
            else:
                annual_performance_factor_heat_pump_55 = 3.1
            annual_performance_factor_heat_pump = annual_performance_factor_heat_pump_55 * \
                                                  (1 - 0.0075 * (self.parent.avg_temp_distribution_heating - 55))

            # DIN V 4701-10 formula 5.3.4.2-19
            expenditure_figure = 1 / annual_performance_factor_heat_pump

        else:
            load_factor_boiler = 1
            # iwu table 5
            if self.parent.heat_generation == "night storage":
                boiler_efficiency = 0.97
            elif self.parent.heat_system == "district":
                boiler_efficiency = 0.98
            elif self.parent.heat_system == "biomass":
                boiler_efficiency = 0.7

            else:
                # iwu formula B.1

                # no boiler before 1995, therefore circulating water heater like condensing (iwu table 5)
                # iwu table 2
                standby_heat_loss_heating_70_20kw = 0.015
                boiler_efficiency_70_20kw = 0.92

                if self.parent.nominal_heat_output_boiler_heating == 20:
                    standby_heat_loss_heating_70 = standby_heat_loss_heating_70_20kw
                    boiler_efficiency_70 = boiler_efficiency_70_20kw
                else:
                    # iwu formula 2-1 and 2-2
                    standby_heat_loss_heating_70 = standby_heat_loss_heating_70_20kw * 2.456 * \
                                                   self.parent.nominal_heat_output_boiler_heating ** (-0.3)
                    boiler_efficiency_70 = boiler_efficiency_70_20kw - 0.0195 + 0.015 * \
                                           math.log10(self.parent.nominal_heat_output_boiler_heating)

                # avg_temp_boiler_heat_period = self.parent.avg_temp_distribution_heating, no standard boiler in archetypes
                if self.parent.avg_temp_distribution_heating < 70:
                    if "low temperature" in self.parent.heat_generation:
                        efficiency_correction = 0.0004 * (70 - self.parent.avg_temp_distribution_heating)
                    else:
                        if self.parent.heat_system == "oil":
                            efficiency_correction = 0.0016 * (70 - self.parent.avg_temp_distribution_heating)
                        else:
                            efficiency_correction = 0.0024 * (70 - self.parent.avg_temp_distribution_heating)
                else:
                    efficiency_correction = 0
                # print("efficiency_correction:", efficiency_correction)

                if self.parent.pipe_routing_heating == "centralised outside":
                    utilisation_factor_heat_use = 0
                else:
                    utilisation_factor_heat_use = 0.85

                if self.parent.pipe_routing_heating == "centralised outside":
                    avg_standby_heat_loss_heating = standby_heat_loss_heating_70 / 50 * \
                                                    (self.parent.avg_temp_distribution_heating - 15)
                else:
                    avg_standby_heat_loss_heating = standby_heat_loss_heating_70 / 50 * \
                                       (self.parent.avg_temp_distribution_heating - 20)  # [-]
                # print("avg_standby_heat_loss_heating:", avg_standby_heat_loss_heating)

                load_level_boiler = 0.3 * self.parent.heat_load / self.parent.nominal_heat_output_boiler_heating  # [-]
                # print("load_level_boiler:", load_level_boiler)

                boiler_efficiency = (boiler_efficiency_70 + efficiency_correction) * \
                                     (1 + utilisation_factor_heat_use * avg_standby_heat_loss_heating /
                                      load_level_boiler) / (1 + avg_standby_heat_loss_heating *
                                                            (1 / load_level_boiler - 1))  # [-]
                # print("boiler_efficiency:", boiler_efficiency)

                # DIN V 4701-10 formula 5.3.4.2-6
                load_factor_boiler = (1 + (1 / 0.3 - 1) * avg_standby_heat_loss_heating) / \
                                     (1 + (1 / load_level_boiler - 1) * avg_standby_heat_loss_heating)  # [-]
                # print("load_factor_boiler:", load_factor_boiler)

            if self.parent.heat_system in ["gas", "oil"] and "low temperature" not in self.parent.heat_generation:

                expenditure_figure = 1 / (load_factor_boiler * (boiler_efficiency + 0.003 *
                                                                (30 - self.parent.avg_temp_distribution_heating)))  # [-]
                # 30°C = boiler temperature for condensing boilers at 30 % partial load efficiency - iwu table 3
            else:
                expenditure_figure = 1 / (load_factor_boiler * boiler_efficiency)

        # print("expenditure_figure: " + str(expenditure_figure))

        if expenditure_figure is None or expenditure_figure == 0:

            return 0

        else:

            return expenditure_figure

    def _dissipation_heating(self):
        """
        Sums up the heat demand without auxiliary energy.

        Returns
        ----------
        result : float [kWh/a]
            dissipation heating without auxiliary
        """

        try:
            annual_heat_energy = self.parent.parent.calc_simulated_annual_heat_energy()
            if annual_heat_energy is not None:
                pass
            else:
                annual_heat_energy = self.parent.heat_load * self.parent.annual_operating_time_heating * 24
        except:
            annual_heat_energy = self.parent.heat_load * self.parent.annual_operating_time_heating * 24
            print("Mistake while function calc_simulated_annual_heat_energy() in Building class.")

        result = (annual_heat_energy -
                self._calc_gains_distribution_water_for_heating() -
                self._calc_gains_storage_water_for_heating() +
                self._calc_dissipation_controll_emission_heating() +
                self._calc_dissipation_distribution_heating() +
                self._calc_dissipation_storage_heating()) * \
               self._calc_dissipation_generation_heating()

        # print("_dissipation_heating: " + str(result))

        if result is None or result == 0:

            return 0

        else:

            return result

    def _calc_dissipation_distribution_auxiliary_heating(self):
        """
        Calculation of heat dissipation through auxiliary energy for
        distribution of heating energy.

        Returns
        ----------
        result : float [kWh/a]
            dissipation distribution auxiliary heating
        """

        # DIN V 4701-10 table C.3-2d "night storage"
        # iwu chapter 5.3 "circulating water heater" already in calc_dissipation_generation_auxiliary_heating
        if self.parent.heat_generation not in ["night storage", "circulating water heater"]:

            # iwu formula 5-16, 5-17 and 5-19
            if self.parent.heat_loss_distribution_heating == "minimised":
                nominal_power_consumption_of_circulator = 7.1 + 0.53 * self.parent.heat_load  # [W]
            elif self.parent.heat_loss_distribution_heating == "small":
                nominal_power_consumption_of_circulator = 25 + 0.77 * self.parent.heat_load
            else:
                nominal_power_consumption_of_circulator = 163 + 3.7 * self.parent.heat_load - \
                                                          0.001 * self.parent.heat_load ** 2
            if nominal_power_consumption_of_circulator < 0:
                nominal_power_consumption_of_circulator = 0

            # print("nominal_power_consumption_of_circulator:", nominal_power_consumption_of_circulator)

            # iwu formula 5-8
            if self.parent.parent.year_of_construction >= 2016 or self.parent.year_of_retrofit >= 2016:
                # DIN V 4701-10 formula 5.3.2-4
                result = nominal_power_consumption_of_circulator * self.parent.annual_operating_time_heating * \
                       self.parent.daily_operating_time_pump / ((1.4 - 20 / self.parent.usable_area) * 1000)

            else:
                # correction factor for controllable pumps in stock = 1
                result = nominal_power_consumption_of_circulator * self.parent.annual_operating_time_heating * \
                       self.parent.daily_operating_time_pump / 1000  # [kWh/a]

        else:
            result = 0

        # print("_calc_dissipation_distribution_auxiliary_heating: " + str(result))

        return result

    def _calc_dissipation_storage_auxiliary_heating(self):
        """
        Calculation of heat dissipation through auxiliary energy for
        storage of hot water.

        Returns
        ----------
        result : float [kWh/a]
            dissipation storage auxiliary heating
        """

        # Condition from TABULA
        if self.parent.heat_generation in ["heatpump air", "condensing - chp", "chp"] or \
                (self.parent.heat_generation == "heatpump ground" and
                 self.parent.building_type == "sfh"):

            # DIN V 4701-10 formula 5.3.3-3 and 5.3.3-4
            result = (40 + 0.03 * self.parent.usable_area) * 24 * \
                     self.parent.annual_operating_time_heating / 1000
            # 0.3324 = simultaneous operation with heat generator (if not simultaneous, tP = 24)
        else:
            result = 0

        # print("_calc_dissipation_storage_auxiliary_heating: " + str(result))

        return result

    def _calc_dissipation_generation_auxiliary_heating(self):
        """
        Calculation of heat dissipation through auxiliary energy for
        generation of heating energy.

        Returns
        ----------
        result : float [kWh/a]
            dissipation generation auxiliary heating
        """

        auxiliary_energy_demand_boiler = None
        nominal_power_consumption_boiler = None

        if self.parent.heat_system in ["oil", "biomass"]:
            # iwu formula 5-6
            nominal_power_consumption_boiler = 170 + 1.95 * self.parent.heat_load  # [kW]

        elif self.parent.heat_system == "gas":

            if self.parent.heat_generation == "circulating water heater":
                # iwu chapter 5-3
                auxiliary_energy_demand_boiler = (100 * self.parent.annual_operating_time_heating * 24 +
                                                  20 * (self.parent.annual_operating_time_water -
                                                        self.parent.annual_operating_time_heating) * 24) / 1000
                # [kWh/a]

            else:
                # iwu formula 5-7
                nominal_power_consumption_boiler = 20 + 0.85 * self.parent.heat_load

        elif "heatpump ground" in self.parent.heat_generation:
            # DIN V 4701-10 table C3-4c
            auxiliary_energy_demand_boiler = 1.9 * self.parent.usable_area ** (-0.1) * self.parent.usable_area

        if auxiliary_energy_demand_boiler is None and nominal_power_consumption_boiler is not None:
            # DIN V 4701-10 formula 5.3.4.2-9 and 5.3.4.2-7
            auxiliary_energy_demand_boiler = (0.3 * self.parent.heat_load / self.parent.nominal_heat_output_boiler_heating) * \
                                             self.parent.annual_operating_time_heating * 24 * \
                                             nominal_power_consumption_boiler  # [kWh/a]

        # print("_calc_dissipation_generation_auxiliary_heating: " + str(auxiliary_energy_demand_boiler))

        if auxiliary_energy_demand_boiler is None or auxiliary_energy_demand_boiler == 0:

            return 0

        else:

            return auxiliary_energy_demand_boiler

    def calc_final_energy_demand_heating(self):
        """
        Sums up the final heat demand for heating.
        It uses all the equations above and includes weighting for
        any additional heat generators.

        Returns
        ----------
        final energy demand heating : float [kWh/a]
        """

        # PE for heating
        if self.parent.heat_generation == "heatpump air":
            # coverage of heat generator from TABULA archetypes
            generator_one = 0.8 * (self._dissipation_heating() + self._calc_dissipation_generation_auxiliary_heating())\
                            + self._calc_dissipation_distribution_auxiliary_heating() + \
                            self._calc_dissipation_storage_auxiliary_heating()

            # DIN V 4701-10 table C.3-4a
            self.parent.heat_system = "gas"
            self.parent.heat_generation = "condensing"
            self.parent.setting_derived_values()

            generator_two = 0.2 * (self._dissipation_heating() + self._calc_dissipation_generation_auxiliary_heating())

            final_energy_demand_heating = generator_one + generator_two

        elif self.parent.heat_generation == "condensing - chp":
            # 0.53  natural gas, condensing, 0.47 chp
            generator_two = 0.47 * (self._dissipation_heating() +
                                    self._calc_dissipation_generation_auxiliary_heating())

            # DIN V 4701-10 table C.3-4a
            self.parent.heat_system = "gas"
            self.parent.heat_generation = "condensing"
            self.parent.setting_derived_values()

            generator_one = 0.53 * (self._dissipation_heating() +
                                    self._calc_dissipation_generation_auxiliary_heating()) + \
                            self._calc_dissipation_distribution_auxiliary_heating() + \
                            self._calc_dissipation_storage_auxiliary_heating()

            final_energy_demand_heating = generator_two + generator_one

        else:
            final_energy_demand_heating = self._dissipation_heating() + \
                                          self._calc_dissipation_generation_auxiliary_heating() + \
                                          self._calc_dissipation_distribution_auxiliary_heating() + \
                                          self._calc_dissipation_storage_auxiliary_heating()

        print("final_energy_demand_heating:", final_energy_demand_heating)
        return final_energy_demand_heating

    @property
    def parent(self):
        return self.__parent

    @parent.setter
    def parent(self, value):
        from teaser.teaser.logic.buildingobjects.buildingsystems.heatsupplysystem import HeatSupplySystem
        import inspect
        if value is not None:
            if inspect.isclass(HeatSupplySystem):
                self.__parent = value

    @property
    def temp_ambient_water(self):
        return self._temp_ambient_water

    @temp_ambient_water.setter
    def temp_ambient_water(self, value):

        if isinstance(value, float):
            self._temp_ambient_water = value
        elif value is None:
            self._temp_ambient_water = value
        else:
            try:
                value = float(value)
                self._temp_ambient_water = value
            except:
                raise ValueError("Can't convert temp_ambient_water to float")

    @property
    def temp_ambient_heating(self):
        return self._temp_ambient_heating

    @temp_ambient_heating.setter
    def temp_ambient_heating(self, value):

        if isinstance(value, float):
            self._temp_ambient_heating = value
        elif value is None:
            self._temp_ambient_heating = value
        else:
            try:
                value = float(value)
                self._temp_ambient_heating = value
            except:
                raise ValueError("Can't convert temp_ambient_heating to float")