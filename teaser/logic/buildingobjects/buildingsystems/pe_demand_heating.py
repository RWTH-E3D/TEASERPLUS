# created November 2023
# by Clara Schmitz (master thesis)

"""This module includes a class for the Primary Energy Calculation of the Heating System
"""
import math
from teaser.teaser.logic.buildingobjects.buildingsystems.pe_demand_water import PEDemandWater


class PEDemandHeating(object):
    """PEDemandHeating class

    This class holds information for the Heating System of the Building.
    The heat losses for the heating system are being set. This class does not affect
    the calculation in Dymola. It uses the calculated heat load and adds
    heat losses for heating to calculate the primary energy demand.

    Parameters
        ----------

        parent: HeatSupplySystem()

        Attributes
        ----------

    """

    def __init__(self, parent=None):
        """Constructor of PEDemandHeating class
        """
        self.parent = parent
        
        self._temp_ambient_water = self.parent.temp_ambient
        self._temp_ambient_heating = self.parent.temp_ambient
        if self.parent.pipe_routing_heating == "centralised outside":
            self._temp_ambient_heating = 13  # iwu formula 4-1

    def _calc_dissipation_distribution_water_for_heating(self):
        """calculation of heat dissipation through distribution of hot water for heating"""

        length_horizontal_water = None
        length_strand_water = None
        length_stubs_water = None

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

        if self.parent.parent.year_of_construction >= 2000 or self.parent.parent.year_of_retrofit >= 2000:
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

            return 1 / 1000 * ((length_horizontal_water * heat_loss_coefficient_horizontal_water) *
                               (1 - heat_loss_factor_horizontal_water) +
                               (length_strand_water * heat_loss_coefficient_strand_water) *
                               (1 - heat_loss_factor_strand_water) +
                               (length_stubs_water * heat_loss_coefficient_stubs_water) *
                               (1 - heat_loss_factor_stubs_water)) * \
                   (during_circulation + during_interruption) * self.parent.annual_operating_time_water * \
                   self.parent.annual_operating_time_heating / self.parent.annual_operating_time_water

        elif self.parent.pipe_routing_water in ["centralised without circulation", "decentralised"]:

            return 1 / 1000 * \
                   ((length_horizontal_water * heat_loss_coefficient_horizontal_water) *
                    (1 - heat_loss_factor_horizontal_water) +
                    (length_strand_water * heat_loss_coefficient_strand_water) *
                    (1 - heat_loss_factor_strand_water) +
                    (length_stubs_water * heat_loss_coefficient_stubs_water) *
                    (1 - heat_loss_factor_stubs_water)) * \
                   (self.parent.avg_temp_distribution_water - self._temp_ambient_water) * 24 \
                   * self.parent.annual_operating_time_water * \
                   self.parent.annual_operating_time_heating / self.parent.annual_operating_time_water

    def _calc_dissipation_storage_water_for_heating(self):

        dissipation_storage_water = PEDemandWater.calc_dissipation_storage_water()

        # DIN V 4701-10 table C.1-3a
        if self.parent.pipe_routing_heating == "centralised inside":

            if self.parent.pipe_routing_water == "decentralised":
                return 0.5 * self.parent.parent.net_leased_area

            # DIN V 4701-10 formula 5.1.3-10
            else:
                return self.parent.annual_operating_time_heating / self.parent.annual_operating_time_water * \
                       (1 - 0.15) * dissipation_storage_water
                # 0.15 = Heat loss factor for components within the thermal envelope, DIN V 4701-10 table 5-2

        else:
            return 0

    def _calc_dissipation_controll_emission_heating(self):
        # iwu chapter 5.5
        if self.parent.pipe_routing_heating == "decentralised":
            return 0

        else:
            if type(self.parent).__name__ in ["SingleFamilyHouse", "TerracedHouse"]:
                return 10 * 8760 / 1000
            elif type(self.parent).__name__ in ["MultiFamilyHouse", "ApartmentBlock"]:
                return 20 * 8760 / 1000

    def _calc_dissipation_distribution_heating(self):
        # calculation of heat dissipation through distribution of hot water

        length_horizontal_heating = None
        length_strand_heating = None
        length_tethers_heating = None
        heat_loss_coefficient_horizontal_heating = None
        heat_loss_factor_horizontal_heating = None
        heat_loss_coefficient_strand_heating = None
        heat_loss_factor_strand_heating = None
        heat_loss_coefficient_tethers_heating = None
        heat_loss_factor_tethers_heating = None

        # calculation of pipe length and heat loss coefficient and factor for heating
        # iwu table 9 and table 10
        if self.parent.pipe_routing_heating == "centralised outside":

            length_horizontal_heating = 4 * self.parent.length_char - 10
            length_strand_heating = self.parent.length_char * self.parent.parent.number_of_floors
            length_tethers_heating = self.parent.length_char * self.parent.parent.number_of_floors * 2 / 3

            heat_loss_coefficient_horizontal_heating = 0.2
            heat_loss_factor_horizontal_heating = 1.0

            if self.parent.parent.year_of_construction >= 2000 or self.parent.parent.year_of_retrofit >= 2000:
                heat_loss_coefficient_strand_heating = 0.26
            else:
                heat_loss_coefficient_strand_heating = 0.8
            heat_loss_factor_strand_heating = 0.35

            if self.parent.parent.year_of_construction >= 2000 or self.parent.parent.year_of_retrofit >= 2000:
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

            if self.parent.parent.year_of_construction >= 2000 or self.parent.parent.year_of_retrofit >= 2000:
                heat_loss_coefficient_strand_heating = 0.26
            else:
                heat_loss_coefficient_strand_heating = 0.2
            heat_loss_factor_strand_heating = 0.15

            if self.parent.parent.year_of_construction >= 2000 or self.parent.parent.year_of_retrofit >= 2000:
                heat_loss_coefficient_tethers_heating = 0.3
            else:
                heat_loss_coefficient_tethers_heating = 0.26
            heat_loss_factor_tethers_heating = 0.1

        elif self.parent.pipe_routing_heating == "decentralised":

            length_strand_heating = self.parent.length_char * self.parent.parent.number_of_floors * 6
            length_tethers_heating = self.parent.length_char * self.parent.parent.number_of_floors

            if self.parent.parent.year_of_construction >= 2000 or self.parent.parent.year_of_retrofit >= 2000:
                heat_loss_coefficient_strand_heating = 0.26
            else:
                heat_loss_coefficient_strand_heating = 0.8
            heat_loss_factor_strand_heating = 0.35

            if self.parent.parent.year_of_construction >= 2000 or self.parent.parent.year_of_retrofit >= 2000:
                heat_loss_coefficient_tethers_heating = 0.26
            else:
                heat_loss_coefficient_tethers_heating = 0.8
            heat_loss_factor_tethers_heating = 0.32
        
        # TABULA values
        if self.parent.heat_generation == "night storage":
            return 0

        # iwu formula 4-1
        else:
            return 1 / 1000 * ((length_horizontal_heating * heat_loss_coefficient_horizontal_heating) *
                               heat_loss_factor_horizontal_heating +
                               (length_strand_heating * heat_loss_coefficient_strand_heating) *
                               heat_loss_factor_strand_heating +
                               (length_tethers_heating * heat_loss_coefficient_tethers_heating) *
                               heat_loss_factor_tethers_heating * 0.8) * \
                   (self.parent.avg_temp_distribution_heating - self._temp_ambient_heating) * \
                   24 * self.parent.annual_operating_time_heating
            # 24 = standard value of daily running time of circulation pump
            # 0.8 = partial heating factor acc. DIN V 4701-10 table 5.3-2 (= 1.0 for horizontal and strand pipes)

    def _calc_dissipation_storage_heating(self):

        # Condition from TABULA for buffer storage
        if self.parent.heat_generation in ["heatpump air", "condensing - chp", "chp"] or \
                (self.parent.heat_generation == "heatpump ground" and
                 type(self.parent).__name__ in ["SingleFamilyHouse", "TerracedHouse"]):

            # DIN V 4701-10 formula 5.3.3-2
            vol_storage = 4 * self.parent.parent.net_leased_area ** 0.7
            standby_heat_loss_heating = (0.5 + 0.25 * 1000 ** 0.4) * math.floor(vol_storage / 1000) + \
                               0.5 + 0.25 * (vol_storage % 1000) ** 0.4

            # DIN V 4701-10 formula 5.3.3-1
            return 1.2 * (self.parent.avg_temp_distribution_heating - self._temp_ambient_heating) / 45 * \
                   self.parent.annual_operating_time_heating * 0.15 * standby_heat_loss_heating
            # 0.15 = Heat loss factor for components within the thermal envelope, table 5-2 DIN V 4701-10

        else:
            return 0

    def _calc_dissipation_generation_heating(self):

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

                if self.parent.nominal_heat_output_boiler == 20:
                    standby_heat_loss_heating_70 = standby_heat_loss_heating_70_20kw
                    boiler_efficiency_70 = boiler_efficiency_70_20kw
                else:
                    # iwu formula 2-1 and 2-2
                    standby_heat_loss_heating_70 = standby_heat_loss_heating_70_20kw * 2.456 * \
                                                   self.parent.nominal_heat_output_boiler ** (-0.3)
                    boiler_efficiency_70 = boiler_efficiency_70_20kw - 0.0195 + 0.015 * \
                                           math.log10(self.parent.nominal_heat_output_boiler)

                # avg_temp_boiler_heat_period = self.parent.avg_temp_distribution_heating, no standard boiler in archetypes
                if self.parent.avg_temp_distribution_heating < 70:  # todo gibt es andere Fälle?
                    if self.parent.heat_generation in ["low temperature", "low temperature - not combined"]:
                        efficiency_correction = 0.0004 * (70 - self.parent.avg_temp_distribution_heating)
                    else:
                        if self.parent.heat_system == "oil":
                            efficiency_correction = 0.0016 * (70 - self.parent.avg_temp_distribution_heating)
                        else:
                            efficiency_correction = 0.0024 * (70 - self.parent.avg_temp_distribution_heating)
                else:
                    efficiency_correction = 0

                if self.parent.pipe_routing_heating == "centralised outside":
                    utilisation_factor_heat_use = 0
                else:
                    utilisation_factor_heat_use = 0.85

                avg_standby_heat_loss_heating = standby_heat_loss_heating_70 / 50 * \
                                       (self.parent.avg_temp_distribution_heating - self._temp_ambient_heating)
                load_level_boiler = 0.3 * self.parent.parent.simulated_heat_load / self.parent.nominal_heat_output_boiler

                boiler_efficiency = ((boiler_efficiency_70 + efficiency_correction) *
                                     (1 + utilisation_factor_heat_use * avg_standby_heat_loss_heating /
                                      load_level_boiler)) / (1 + avg_standby_heat_loss_heating * (1 / load_level_boiler - 1))

                # DIN V 4701-10 formula 5.3.4.2-6
                load_factor_boiler = (1 + (1 / 0.3 - 1) * avg_standby_heat_loss_heating) / \
                                     (1 + (1 / load_level_boiler - 1) * avg_standby_heat_loss_heating)

            if self.parent.heat_system in ["gas", "oil"] and \
                    self.parent.heat_generation not in ["low temperature", "low temperature - not combined"]:

                expenditure_figure = 1 / (load_factor_boiler * (boiler_efficiency + 0.003 *
                                                                (30 - self.parent.avg_temp_distribution_heating)))
                # 30°C = boiler temperature for condensing boilers at 30 % partial load efficiency - iwu table 3
            else:
                expenditure_figure = 1 / (load_factor_boiler * boiler_efficiency)

        return expenditure_figure

    def _dissipation_heating(self):
        return (self.parent.parent.calc_simulated_annual_heat_energy() -
                self._calc_dissipation_distribution_water_for_heating() -
                self._calc_dissipation_storage_water_for_heating() +
                self._calc_dissipation_controll_emission_heating() +
                self._calc_dissipation_distribution_heating() +
                self._calc_dissipation_storage_heating()) * \
               self._calc_dissipation_generation_heating()

    def _calc_dissipation_distribution_auxiliary_heating(self):

        # DIN V 4701-10 table C.3-2d "night storage"
        # iwu chapter 5.3 "circulating water heater" already in calc_dissipation_generation_auxiliary_heating
        if self.parent.heat_generation in ["night storage", "circulating water heater"]:
            return 0

        else:

            # iwu formula 5-16, 5-17 and 5-19
            if self.parent.heat_loss_distribution_heating == "minimised":
                nominal_power_consumption_of_circulator = 7.1 + 0.53 * self.parent.parent.simulated_heat_load
            elif self.parent.heat_loss_distribution_heating == "small":
                nominal_power_consumption_of_circulator = 25 + 0.77 * self.parent.parent.simulated_heat_load
            else:
                nominal_power_consumption_of_circulator = 163 + 3.7 * self.parent.parent.simulated_heat_load - \
                                                          0.001 * self.parent.parent.simulated_heat_load ** 2

            # iwu formula 5-8
            if self.parent.parent.year_of_construction >= 2016 or self.parent.parent.year_of_retrofit >= 2016:
                # DIN V 4701-10 formula 5.3.2-4
                # todo wenn hier Unterscheidung in Bestand und Neubau gemacht wird, wo sonst noch notwenig?
                return nominal_power_consumption_of_circulator * self.parent.annual_operating_time_heating * \
                       self.parent.daily_operating_time_pump / ((1.4 - 20 / self.parent.parent.net_leased_area) * 1000)

            else:
                # correction factor for controllable pumps in stock = 1
                return nominal_power_consumption_of_circulator * self.parent.annual_operating_time_heating * \
                       self.parent.daily_operating_time_pump / 1000

    def _calc_dissipation_storage_auxiliary_heating(self):

        # Condition from TABULA
        if self.parent.heat_generation in ["heatpump air", "condensing - chp", "chp"] or \
                (self.parent.heat_generation == "heatpump ground" and
                 type(self.parent).__name__ in ["SingleFamilyHouse", "TerracedHouse"]):

            # DIN V 4701-10 formula 5.3.3-3 and 5.3.3-4
            return (40 + 0.03 * self.parent.parent.net_leased_area) * 0.3324 * self.parent.annual_operating_time_heating / 1000
            # 0.3324 = simultaneous operation with heat generator (if not simultaneous, set tP = 24)

        else:
            return 0

    def _calc_dissipation_generation_auxiliary_heating(self):

        auxiliary_energy_demand_boiler = None
        nominal_power_consumption_boiler = None

        if self.parent.heat_system == "oil":
            # iwu formula 5-6
            nominal_power_consumption_boiler = 170 + 1.95 * self.parent.parent.simulated_heat_load

        elif self.parent.heat_system == "gas":

            if self.parent.heat_generation == "circulating water heater":
                # iwu chapter 5-3
                auxiliary_energy_demand_boiler = (100 * self.parent.annual_operating_time_heating * 24 +
                                                  20 * self.parent.annual_operating_time_water * 24) / 1000
                # [kWh/a]

            else:
                # iwu formula 5-7
                nominal_power_consumption_boiler = 20 + 0.85 * self.parent.parent.simulated_heat_load

        elif self.parent.heat_generation in ["heatpump ground", "heatpump ground - no buffer storage"]:
            # DIN V 4701-10 table C3-4c
            auxiliary_energy_demand_boiler = 1.9 * self.parent.parent.net_leased_area ** (-0.1)

        else:
            auxiliary_energy_demand_boiler = 0

        if auxiliary_energy_demand_boiler is None:
            # DIN V 4701-10 formula 5.3.4.2-9 and 5.3.4.2-7
            auxiliary_energy_demand_boiler = (self.parent.parent.simulated_heat_load / self.parent.nominal_heat_output_boiler) * \
                                             self.parent.annual_operating_time_heating * 24 * nominal_power_consumption_boiler

        return auxiliary_energy_demand_boiler

    def calc_primary_energy_demand_heating(self):

        # DIN V 18599-1 table A.1
        if self.parent.heat_system in ["gas", "oil"]:
            primary_energy_factor = 1.1
        elif self.parent.heat_system == "electricity":
            primary_energy_factor = 1.8
        elif self.parent.heat_system == "district":
            if self.parent.heat_generation == "gas - high chp":
                primary_energy_factor = 0.7
            elif self.parent.heat_generation == "biomass":
                primary_energy_factor = 0
            else:
                primary_energy_factor = 1.3
        else:
            primary_energy_factor = 0.2

        # PE for heating
        if self.parent.heat_generation == "heatpump air":
            # coverage of heat generator from TABULA archetypes
            generator_one = 0.8 * (self._dissipation_heating() + self._calc_dissipation_generation_auxiliary_heating())\
                            + self._calc_dissipation_distribution_auxiliary_heating() + \
                            self._calc_dissipation_storage_auxiliary_heating()

            # DIN V 4701-10 table C.3-4a
            self.parent.heat_system = "gas"
            self.parent.heat_generation = "condensing"

            generator_two = 0.2 * (self._dissipation_heating() + self._calc_dissipation_generation_auxiliary_heating())

            # final_energy_demand_heating = generator_one + generator_two
            primary_energy_demand_heating = generator_one * 1.8 + generator_two * 1.1  # multiplied with PEF

        elif self.parent.heat_generation == "condensing - chp":
            # 0.53  natural gas, condensing, 0.47 chp
            generator_two = 0.47 * (self._dissipation_heating() + self._calc_dissipation_generation_auxiliary_heating())

            # DIN V 4701-10 table C.3-4a
            self.parent.heat_system = "gas"
            self.parent.heat_generation = "condensing"

            generator_one = 0.53 * (
                    self._dissipation_heating() + self._calc_dissipation_generation_auxiliary_heating()) + \
                            self._calc_dissipation_distribution_auxiliary_heating() + \
                            self._calc_dissipation_storage_auxiliary_heating()

            # final_energy_demand_heating = generator_one + generator_two
            primary_energy_demand_heating = generator_one * 0.7 + generator_two * 1.1  # multiplied with PEF

        else:
            final_energy_demand_heating = self._dissipation_heating() + \
                                          self._calc_dissipation_generation_auxiliary_heating() + \
                                          self._calc_dissipation_distribution_auxiliary_heating() + \
                                          self._calc_dissipation_storage_auxiliary_heating()

            primary_energy_demand_heating = final_energy_demand_heating * primary_energy_factor

        return primary_energy_demand_heating



    @property
    def parent(self):
        return self.__parent

    @parent.setter
    def parent(self, value):
        from teaser.teaser.logic.buildingobjects.buildingsystems.heat_supply_system import HeatSupplySystem
        import inspect
        if inspect.isclass(HeatSupplySystem):
            self.__parent = value
            self.__parent.heat_supply_system = self
