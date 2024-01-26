# created November 2023
# by Clara Schmitz (master thesis)

"""This module includes a class for the final energy calculation of the warm water system
"""
import math


class FEDemandWater(object):
    """FEDemandWater class

    This class holds information for the warm water System of the Building.
    The heat losses for the warm water system are being set. This class does
    not affect the calculation in Dymola. It uses the calculated heat
    load and adds heat losses for water to calculate the primary energy demand.

    Parameters
    ----------

    parent: HeatSupplySystem()
        The parent class of this object, the HeatSupplySystem the final
        energy demand belongs to. Allows for better control of hierarchical
        structures.
        Default is None

    Attributes
    ----------
    """

    def __init__(self, parent=None):
        """Constructor of FEDemandWater class
        """
        self.parent = parent

    def _calc_dissipation_distribution_water(self):
        """
        Calculation of heat dissipation through distribution of warm water.
        Dependent of the pipe routing and geometrical building values.

        Returns
        ----------
        result : float [kWh/a]
            dissipation distribution water
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

            # print("length pipes water: ", length_horizontal_water, length_strand_water, length_stubs_water)

        elif self.parent.pipe_routing_water == "centralised without circulation":

            length_horizontal_water = self.parent.length_char - 5
            length_strand_water = self.parent.length_char * self.parent.parent.number_of_floors / 4
            length_stubs_water = self.parent.length_char * self.parent.parent.number_of_floors / 2

        elif self.parent.pipe_routing_water == "decentralised":

            length_stubs_water = self.parent.length_char * self.parent.parent.number_of_floors / 2

        # calculation of heat loss coefficient and factor for hot water
        # iwu table 10
        heat_loss_coefficient_horizontal_water = 0.2  # [W/(m·K)]

        heat_loss_coefficient_strand_water = 0.2  # [W/(m·K)]

        if self.parent.parent.year_of_construction >= 2000 or self.parent.year_of_retrofit >= 2000:
            heat_loss_coefficient_stubs_water = 0.2  # [W/(m·K)]
        else:
            heat_loss_coefficient_stubs_water = 1.4  # [W/(m·K)]

        if self.parent.pipe_routing_water == "centralised with circulation":
            # iwu formula 4-2 and 4-3
            during_circulation = (self.parent.avg_temp_distribution_water - self.parent.temp_ambient) * \
                                 self.parent.daily_operating_time_pump
            # print("during_circulation", during_circulation)
            during_interruption = 0.5 * (32 - self.parent.temp_ambient) * (24 - self.parent.daily_operating_time_pump)
            # print("during_interruption", during_interruption)
            # 32 = avg_temp_distribution_water without circulation

            result = 1 / 1000 * (length_horizontal_water * heat_loss_coefficient_horizontal_water
                               + length_strand_water * heat_loss_coefficient_strand_water
                               + length_stubs_water * heat_loss_coefficient_stubs_water) \
                * (during_circulation + during_interruption) \
                * self.parent.annual_operating_time_water  # [kWh/a]

        else:
            # iwu formula 4-5
            result = 1 / 1000 * (length_horizontal_water * heat_loss_coefficient_horizontal_water
                               + length_strand_water * heat_loss_coefficient_strand_water
                               + length_stubs_water * heat_loss_coefficient_stubs_water) \
               * (self.parent.avg_temp_distribution_water - self.parent.temp_ambient) \
               * 24 * self.parent.annual_operating_time_water

        # print("_calc_dissipation_distribution_water: " + str(result))
        if result is None or result == 0:
            return 0
        else:
            return result  # [kWh/a]

    def calc_dissipation_storage_water(self):
        """
        Calculation of heat dissipation through storage of hot water.
        Dependent of the kind of the storage.

        Returns
        ----------
        result : float [kWh/a]
            dissipation storage water
        """

        # iwu chapter 3
        # standby_heat_loss_heating [kWh/d]
        if self.parent.pipe_routing_water == "decentralised":

            vol_storage = math.ceil(self.parent.parent.net_leased_area / 100) * (8 + 5)  # [l]
            if vol_storage > 250:
                # calculation like indirectly heated warm water storage tanks
                # all cases considered: decentralised or combined with heating
                standby_heat_loss_heating = 0.2 + 0.19 * vol_storage ** 0.4  # [kWh/d]

            else:
                # heated by electrical energy
                standby_heat_loss_heating = 0.29 + 0.019 * vol_storage ** 0.8

        elif self.parent.storage:
            # water: iwu chapter 3.1, solar: iwu table 8

            vol_storage = -3.5 * 10 ** (-6) * self.parent.parent.net_leased_area ** 2 + \
                          0.35 * self.parent.parent.net_leased_area + 170
            if self.parent.storage == "water":
                standby_heat_loss_heating = 0.2 + 0.19 * vol_storage ** 0.4  # [kWh/d]
            else:
                standby_heat_loss_heating = 0.3 + 0.2 * vol_storage ** 0.4

        else:
            standby_heat_loss_heating = 0  # [kWh/d]

        result = 1.2 * (50 - self.parent.temp_ambient) / 45 * self.parent.annual_operating_time_water \
            * standby_heat_loss_heating  # [kWh/a]
        # DIN V 4701-10 formula 5.1.3-1

        # print("_calc_dissipation_storage_water: " + str(result))
        if result is None or result == 0:
            return 0
        else:
            return result

    def _calc_dissipation_generation_water(self):
        """
        Calculation of heat dissipation through generation of hot water.
        Dependent of the heat system and generation of the  building.

        Returns
        ----------
        expenditure_figure : float [-]
            for dissipation generation water
        """

        # setting values to None
        boiler_efficiency = None
        expenditure_figure = None
        standby_heat_loss_heating_70_20kw = None
        boiler_efficiency_70_20kw = None

        if self.parent.pipe_routing_water == "decentralised":

            # iwu table 6 and table 7
            if self.parent.heat_system == "gas":
                if self.parent.heat_generation == "circulating water heater":
                    standby_heat_loss_heating_70_20kw = 0.015
                    boiler_efficiency_70_20kw = 0.92
                else:
                    standby_heat_loss_heating_70_20kw = 0
                    boiler_efficiency_70_20kw = 0.88  # worst case
            else:
                boiler_efficiency = 0.98

        elif self.parent.heat_system == "electricity":

            # iwu chapter 2.2
            if self.parent.heat_generation == "heatpump air":
                annual_performance_factor_heat_pump = 2.6
            else:
                annual_performance_factor_heat_pump = 3.1

            expenditure_figure = 1 / annual_performance_factor_heat_pump

        # iwu table 5
        elif self.parent.heat_system == "district":
            boiler_efficiency = 0.98

        elif self.parent.heat_system == "biomass":
            boiler_efficiency = 0.7

        else:
            # iwu table 3
            standby_heat_loss_heating_70_20kw = 0.015  # [kW/m^2]
            boiler_efficiency_70_20kw = 0.92  # [-]

        # iwu formula B3
        load_factor_boiler = (12.5 * self.parent.parent.net_leased_area +
                              self._calc_dissipation_distribution_water() + self.calc_dissipation_storage_water()) \
                             / (self.parent.nominal_heat_output_boiler * 24 *
                                self.parent.annual_operating_time_water)

        if self.parent.combined_water_heating is False:
            operating_time_heating = 0
        else:
            operating_time_heating = self.parent.annual_operating_time_heating

        if self.parent.nominal_heat_output_boiler == 20:
            standby_heat_loss_heating_70 = standby_heat_loss_heating_70_20kw
            boiler_efficiency_70 = boiler_efficiency_70_20kw
        else:
            # iwu formula 2-1 and 2-2
            if standby_heat_loss_heating_70_20kw is not None:
                standby_heat_loss_heating_70 = standby_heat_loss_heating_70_20kw * 2.456 * \
                                               self.parent.nominal_heat_output_boiler ** (-0.3)  # [-]
            else:
                standby_heat_loss_heating_70 = 0

            if boiler_efficiency_70_20kw is not None:
                boiler_efficiency_70 = boiler_efficiency_70_20kw - 0.0195 + 0.015 * \
                                       math.log10(self.parent.nominal_heat_output_boiler)  # [-]
            else:
                boiler_efficiency_70 = 0

        # print("boiler_efficiency_70", boiler_efficiency_70)
        # print("self.parent.nominal_heat_output_boiler", self.parent.nominal_heat_output_boiler)
        # print("standby_heat_loss_heating_70", standby_heat_loss_heating_70)

        # iwu formula B2
        if self.parent.avg_temp_distribution_heating < 70:
            if self.parent.heat_generation in ["low temperature", "low temperature - not combined"]:
                efficiency_correction = 0.0004 * (70 - self.parent.avg_temp_distribution_heating)  # [-]
            else:
                if self.parent.heat_system == "oil":
                    efficiency_correction = 0.0016 * (70 - self.parent.avg_temp_distribution_heating)
                else:
                    efficiency_correction = 0.0024 * (70 - self.parent.avg_temp_distribution_heating)
        else:
            efficiency_correction = 0

        # print("efficiency_correction", efficiency_correction)

        if standby_heat_loss_heating_70 is not None:
            avg_standby_heat_loss_heating = standby_heat_loss_heating_70 / 50 * (60 - self.parent.temp_ambient)  # [-]

            # print("avg_standby_heat_loss_heating: " + str(avg_standby_heat_loss_heating))
        else:
            avg_standby_heat_loss_heating = 0

        if boiler_efficiency is None and expenditure_figure is None:
            boiler_efficiency = boiler_efficiency_70 + efficiency_correction / \
                                (1 + avg_standby_heat_loss_heating * (1 / load_factor_boiler - 1)
                                 * (1 - operating_time_heating / self.parent.annual_operating_time_water))  # [-]
            # print("boiler_efficiency: " + str(boiler_efficiency))

        if expenditure_figure is None:
            # DIN V 4701-10 formula 5.1.4-17
            expenditure_figure = (1 + (1 / load_factor_boiler - 1) *
                                  (1 - operating_time_heating / self.parent.annual_operating_time_water)
                                  * avg_standby_heat_loss_heating) / boiler_efficiency  # [-]

        # print("expenditure_figure: " + str(expenditure_figure))
        if expenditure_figure is None or expenditure_figure == 0:
            return 0
        else:
            return expenditure_figure

    def _dissipation_water(self):
        """
        Sums up the heat demand without auxiliary energy.

        Returns
        ----------
        result : float [kWh/a]
            dissipation water without auxiliary
        """

        result = (12.5 * self.parent.parent.net_leased_area + self._calc_dissipation_distribution_water()
                  + self.calc_dissipation_storage_water()) * self._calc_dissipation_generation_water()

        # print("_dissipation_water: " + str(result))
        if result is None or result == 0:
            return 0
        else:
            return result

    def _calc_dissipation_distribution_auxiliary_water(self):
        """
        Calculation of heat dissipation through auxiliary energy for
        distribution of hot water.

        Returns
        ----------
        result : float [kWh/a]
            dissipation distribution auxiliary water
        """

        if self.parent.pipe_routing_water == "centralised with circulation":

            # iwu formula 5-23 and 5-24
            if self.parent.parent.year_of_construction >= 2016 or self.parent.year_of_retrofit >= 2016:
                result = (27 + 0.008 * self.parent.parent.net_leased_area) * self.parent.annual_operating_time_water * \
                       self.parent.daily_operating_time_pump / 1000

            else:
                result = (30 + 5 * self.parent.parent.net_leased_area / 100) * self.parent.annual_operating_time_water * \
                       self.parent.daily_operating_time_pump / 1000  # [kWh/a]

        else:
            result = 0

        # print("_calc_dissipation_distribution_auxiliary_water: " + str(result))
        return result

    def _calc_dissipation_storage_auxiliary_water(self):
        """
        Calculation of heat dissipation through auxiliary energy for
        storage of hot water.

        Returns
        ----------
        result : float [kWh/a]
            dissipation storage auxiliary water
        """

        if self.parent.storage:

            if self.parent.storage == "water":
                # iwu formula 5-20 to 5-22
                result = (30 + 5 * self.parent.parent.net_leased_area / 100) * 1.2 * \
                       (12.5 * self.parent.parent.net_leased_area + self._calc_dissipation_distribution_water() +
                        self.calc_dissipation_storage_water()) / self.parent.nominal_heat_output_boiler / 1000  # [kWh/a]
            else:
                # iwu formula 5-25 and 5-26
                result = (20 + 5 * self.parent.parent.net_leased_area / 100) * 1750 / 1000

        else:
            result = 0

        # print("_calc_dissipation_storage_auxiliary_water: " + str(result))
        return result

    def _calc_dissipation_generation_auxiliary_water(self):
        """
        Calculation of heat dissipation through auxiliary energy for
        generation of hot water.

        Returns
        ----------
        result : float [kWh/a]
            dissipation generation auxiliary water
        """

        auxiliary_energy_demand_solar = 0
        
        if self.parent.storage == "solar":
            # DIN V 4701-10 table C.1-4e
            auxiliary_energy_demand_solar = 1 * self.parent.parent.net_leased_area  # [kWh/a]

        if self.parent.heat_system == "electricity":

            if self.parent.heat_generation in ["heatpump ground", "heatpump ground - no buffer storage"]:
                # DIN V 4701-10 formula 5.1.4-32
                time_pump = (12.5 * self.parent.parent.net_leased_area + self._calc_dissipation_distribution_water() +
                             self.calc_dissipation_storage_water()) / self.parent.nominal_heat_output_boiler  # [h/a]

                # DIN V 4701-10 formula 5.1.4-31
                auxiliary_energy_demand_boiler = 1.2 * self.parent.parent.net_leased_area ** 0.9 * time_pump / 1000  # [kWh/a]

            else:
                # DIN V 4701-10 chapter 5.1.4.2.4 and table C.1-4d
                auxiliary_energy_demand_boiler = 0

        elif self.parent.heat_system == "district":
            # DIN V 4701-10 table C.1-4e
            auxiliary_energy_demand_boiler = 0.4 * self.parent.parent.net_leased_area  # [kWh/a]

        elif self.parent.heat_system == "circulating water heater":
            # DIN V 4701-10 table C.1-4c
            auxiliary_energy_demand_boiler = 0

        else:
            if self.parent.nominal_heat_output_boiler is not None and self.parent.annual_operating_time_water is not None:
                # iwu formula B3
                load_factor_boiler = (12.5 * self.parent.parent.net_leased_area + self._calc_dissipation_distribution_water() +
                                      self.calc_dissipation_storage_water()) / (
                                             self.parent.nominal_heat_output_boiler * 24 *
                                             self.parent.annual_operating_time_water)  # [-]
            else:
                # print("A required value for load_factor_boiler is None.")
                load_factor_boiler = 0

           # DIN V 4701-10 formula 5.1.4-20 and 5.1.4-29
            auxiliary_energy_demand_boiler = load_factor_boiler * self.parent.annual_operating_time_water * 24 * 0.045 \
                                             * self.parent.nominal_heat_output_boiler ** 0.48  # [kWh/a]

        if auxiliary_energy_demand_solar is not None and auxiliary_energy_demand_boiler is not None:
            result = auxiliary_energy_demand_solar + auxiliary_energy_demand_boiler
        elif auxiliary_energy_demand_solar is not None:
            result = auxiliary_energy_demand_solar
        elif auxiliary_energy_demand_boiler is not None:
            result = auxiliary_energy_demand_boiler
        else:
            result = 0

        # print("_calc_dissipation_generation_auxiliary_water: " + str(result))
        if result is None or result == 0:

            return 0

        else:

            return result

    def calc_final_energy_demand_water(self):
        """
        Sums up the final heat demand for warm water.
        It uses all the equations above and includes weighting for
        any additional heat generators.

        Returns
        ----------
        final energy demand water : float [kWh/a]
        """

        part_solar = 0

        # PE for hot water
        if self.parent.storage == "solar":
            # PEF solar = 0
            if self.parent.building_type == "mfh":
                # TABULA values
                if "chp" in self.parent.heat_generation:
                    part_solar = 0.6
                else:
                    part_solar = 0.4
            else:
                part_solar = 0.6

        if self.parent.heat_generation == "heatpump air":
            # TABULA values
            if self.parent.storage == "solar":
                part_generator_one = 1 - part_solar - 0.1
            else:
                part_generator_one = 0.9

            generator_one = part_generator_one * (self._dissipation_water() +
                                                  self._calc_dissipation_generation_auxiliary_water()) + \
                            self._calc_dissipation_distribution_auxiliary_water() + \
                            self._calc_dissipation_storage_auxiliary_water()

            self.parent.heat_system = "gas"
            self.parent.heat_generation = "condensing"
            self.parent.setting_derived_values()

            generator_two = 0.1 * (self._dissipation_water() + self._calc_dissipation_generation_auxiliary_water())

            final_energy_demand_water = generator_one + generator_two

        elif self.parent.heat_generation == "condensing - chp":
            # TABULA values
            # 0.58 % solar
            generator_two = 0.05 * (self._dissipation_water() + self._calc_dissipation_generation_auxiliary_water())

            # DIN V 4701-10 table C.3-4a
            self.parent.heat_system = "gas"
            self.parent.heat_generation = "condensing"
            self.parent.setting_derived_values()

            generator_one = 0.37 * (self._dissipation_water() + self._calc_dissipation_generation_auxiliary_water()) \
                            + self._calc_dissipation_distribution_auxiliary_water() \
                            + self._calc_dissipation_storage_auxiliary_water()

            final_energy_demand_water = generator_two + generator_one

        else:

            if self.parent.storage == "solar":
                part_generator = 1 - part_solar
            else:
                part_generator = 1

            final_energy_demand_water = part_generator * (self._dissipation_water() +
                                                          self._calc_dissipation_generation_auxiliary_water()) \
                                        + self._calc_dissipation_distribution_auxiliary_water() + \
                                        self._calc_dissipation_storage_auxiliary_water()

        print("final_energy_demand_water:", final_energy_demand_water)
        return final_energy_demand_water

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
