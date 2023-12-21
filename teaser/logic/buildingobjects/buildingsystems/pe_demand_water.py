# created November 2023
# by Clara Schmitz (master thesis)

"""This module includes a class for the primary energy calculation of the warm water system
"""
import math


class PEDemandWater(object):
    """PEDemandWater class

    This class holds information for the Heating System of the Building.
    The heat losses for the heating system are being set. This class does not affect
    the calculation in Dymola. It uses the calculated heat load and adds
    heat losses for water to calculate the primary energy demand.

    Parameters
        ----------

        parent: HeatSupplySystem()

        Attributes
        ----------

    """

    def __init__(self, parent=None):
        """Constructor of PEDemandWater class
        """
        self.parent = parent

    def _calc_dissipation_distribution_water(self):
        # calculation of heat dissipation through distribution of hot water
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

        heat_loss_coefficient_strand_water = 0.2

        if self.parent.parent.year_of_construction >= 2000 or self.parent.parent.year_of_retrofit >= 2000:
            heat_loss_coefficient_stubs_water = 0.2
        else:
            heat_loss_coefficient_stubs_water = 1.4

        if self.parent.pipe_routing_water == "centralised with circulation":
            # iwu formula 4-2 and 4-3
            during_circulation = (self.parent.avg_temp_distribution_water - self.parent.temp_ambient) * \
                                 self.parent.daily_operating_time_pump
            during_interruption = 0.5 * (32 - self.parent.temp_ambient) * (24 - self.parent.daily_operating_time_pump)
            # 32 = avg_temp_distribution_water without circulation

            return 1 / 1000 * (length_horizontal_water * heat_loss_coefficient_horizontal_water
                               + length_strand_water * heat_loss_coefficient_strand_water
                               + length_stubs_water * heat_loss_coefficient_stubs_water) \
                * (during_circulation + during_interruption) \
                * self.parent.annual_operating_time_water

        elif self.parent.pipe_routing_water == "centralised without circulation" or \
                self.parent.pipe_routing_water == "decentralised":
            # iwu formula 4-5
            return 1 / 1000 * (length_horizontal_water * heat_loss_coefficient_horizontal_water
                               + length_strand_water * heat_loss_coefficient_strand_water
                               + length_stubs_water * heat_loss_coefficient_stubs_water) \
               * (self.parent.avg_temp_distribution_water - self.parent.temp_ambient) \
               * 24 * self.parent.annual_operating_time_water

    def calc_dissipation_storage_water(self):
        # iwu chapter 3
        # standby_heat_loss_heating [kWh/d]
        if self.parent.pipe_routing_water == "decentralised":

            vol_storage = round(self.parent.parent.net_leased_area / 100) * (8 + 5)
            if vol_storage > 250:
                # calculation like indirectly heated warm water storage tanks
                # all cases considered: decentralised or combined with heating
                standby_heat_loss_heating = 0.2 + 0.19 * vol_storage ** 0.4

            else:
                # heated by electrical energy
                standby_heat_loss_heating = 0.29 + 0.019 * vol_storage ** 0.8

        elif self.parent.storage_water in ["water", "solar"]:
            # water: iwu chapter 3.1, solar: iwu table 8

            vol_storage = -3.5 * 10 ** (-6) * self.parent.parent.net_leased_area ** 2 + \
                          0.35 * self.parent.parent.net_leased_area + 170
            if self.parent.storage_water == "water":
                standby_heat_loss_heating = 0.2 + 0.19 * vol_storage ** 0.4
            else:
                standby_heat_loss_heating = 0.3 + 0.2 * vol_storage ** 0.4

        else:
            standby_heat_loss_heating = 0

        return 1.2 * (50 - self.parent.temp_ambient) / 45 * self.parent.annual_operating_time_water \
            * standby_heat_loss_heating
        # DIN V 4701-10 formula 5.1.3-1

    def _calc_dissipation_generation_water(self):

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

            standby_heat_loss_heating_70_20kw = 0.015
            boiler_efficiency_70_20kw = 0.92

        # iwu formula B3
        load_factor_boiler = (12.5 * self.parent.parent.net_leased_area + self._calc_dissipation_distribution_water() +
                              self.calc_dissipation_storage_water()) / (self.parent.nominal_heat_output_boiler * 24 *
                                                                         self.parent.annual_operating_time_water)

        if not self.parent.combined_water_heating:
            operating_time_heating = 0
        else:
            operating_time_heating = self.parent.annual_operating_time_heating

        if self.parent.nominal_heat_output_boiler == 20:
            standby_heat_loss_heating_70 = standby_heat_loss_heating_70_20kw
            boiler_efficiency_70 = boiler_efficiency_70_20kw
        else:
            # iwu formula 2-1 and 2-2
            standby_heat_loss_heating_70 = standby_heat_loss_heating_70_20kw * 2.456 * self.parent.nominal_heat_output_boiler ** (
                -0.3)
            boiler_efficiency_70 = boiler_efficiency_70_20kw - 0.0195 + 0.015 * \
                                   math.log10(self.parent.nominal_heat_output_boiler)

        # iwu formula B2
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

        avg_standby_heat_loss_heating = standby_heat_loss_heating_70 / 50 * (60 - self.parent.temp_ambient)

        if boiler_efficiency and expenditure_figure is None:
            boiler_efficiency = boiler_efficiency_70 + efficiency_correction / \
                                (1 + avg_standby_heat_loss_heating * (1 / load_factor_boiler - 1)
                                 * (1 - operating_time_heating / self.parent.annual_operating_time_water))

        if expenditure_figure is None:
            # DIN V 4701-10 formula 5.1.4-17
            expenditure_figure = (1 + (1 / load_factor_boiler - 1) *
                                  (1 - operating_time_heating / self.parent.annual_operating_time_water)
                                  * avg_standby_heat_loss_heating) / boiler_efficiency

        return expenditure_figure

    def _dissipation_water(self):

        return (12.5 * self.parent.parent.net_leased_area + self._calc_dissipation_distribution_water() +
                self.calc_dissipation_storage_water()) * self._calc_dissipation_generation_water()

    def _calc_dissipation_distribution_auxiliary_water(self):

        if self.parent.pipe_routing_water == "centralised with circulation":

            # iwu formula 5-23 and 5-24
            if self.parent.parent.year_of_construction >= 2016 or self.parent.parent.year_of_retrofit >= 2016:
                return (27 + 0.008 * self.parent.parent.net_leased_area) * self.parent.annual_operating_time_water * \
                       self.parent.daily_operating_time_pump / 1000

            else:
                return (30 + 5 * self.parent.parent.net_leased_area / 100) * self.parent.annual_operating_time_water * \
                       self.parent.daily_operating_time_pump / 1000
        else:
            return 0

    def _calc_dissipation_storage_auxiliary_water(self):

        if self.parent.storage_water:

            if self.parent.storage_water == "water":
                # iwu formula 5-20 to 5-22
                return (30 + 5 * self.parent.parent.net_leased_area / 100) * 1.2 * \
                       (12.5 * self.parent.parent.net_leased_area + self._calc_dissipation_distribution_water() +
                        self.calc_dissipation_storage_water()) / self.parent.nominal_heat_output_boiler / 1000
            elif self.parent.storage_water == "solar":
                # iwu formula 5-25 and 5-26
                return (20 + 5 * self.parent.parent.net_leased_area / 100) * 1750 / 1000

        else:
            return 0

    def _calc_dissipation_generation_auxiliary_water(self):

        auxiliary_energy_demand_solar = 0
        
        if self.parent.storage_water == "solar":
            # DIN V 4701-10 table C.1-4e
            auxiliary_energy_demand_solar = 1

        if self.parent.heat_system == "electricity":

            if self.parent.heat_generation in ["heatpump ground", "heatpump ground - no buffer storage"]:
                # DIN V 4701-10 formula 5.1.4-32
                time_pump = (12.5 * self.parent.parent.net_leased_area + self._calc_dissipation_distribution_water() +
                             self.calc_dissipation_storage_water()) / self.parent.nominal_heat_output_boiler

                # DIN V 4701-10 formula 5.1.4-31
                auxiliary_energy_demand_boiler = 1.2 * self.parent.parent.net_leased_area ** 0.9 * time_pump / 1000

            else:
                # DIN V 4701-10 chapter 5.1.4.2.4 and table C.1-4d
                auxiliary_energy_demand_boiler = 0

        elif self.parent.heat_system == "district":
            # DIN V 4701-10 table C.1-4e
            auxiliary_energy_demand_boiler = 0.4

        elif self.parent.heat_system == "circulating water heater":
            # DIN V 4701-10 table C.1-4c
            auxiliary_energy_demand_boiler = 0

        else:
            # iwu formula B3
            load_factor_boiler = (12.5 * self.parent.parent.net_leased_area + self._calc_dissipation_distribution_water() +
                                  self.calc_dissipation_storage_water()) / (
                                             self.parent.nominal_heat_output_boiler * 24 *
                                             self.parent.annual_operating_time_water)
            # DIN V 4701-10 formula 5.1.4-20 and 5.1.4-29
            auxiliary_energy_demand_boiler = load_factor_boiler + self.parent.annual_operating_time_water * 24 * 0.045 \
                                             * self.parent.nominal_heat_output_boiler ** 0.48

        return (auxiliary_energy_demand_solar + auxiliary_energy_demand_boiler) * self.parent.parent.net_leased_area

    def calc_primary_energy_demand_water(self):

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

        part_solar = 0

        # PE for hot water
        if self.parent.storage_water == "solar":
            # PEF solar = 0
            if type(self.parent).__name__ in ["MultiFamilyHouse", "ApartmentBlock"]:
                # TABULA values
                if self.parent.heat_generation == "chp":
                    part_solar = 0.6
                else:
                    part_solar = 0.4
            else:
                part_solar = 0.6

        if self.parent.heat_generation == "heatpump air":
            # TABULA values
            if self.parent.storage_water == "solar":
                part_generator_one = 1 - part_solar - 0.1
            else:
                part_generator_one = 0.9

            generator_one = part_generator_one * (self._dissipation_water() +
                                                  self._calc_dissipation_generation_auxiliary_water()) + \
                            self._calc_dissipation_distribution_auxiliary_water() + \
                            self._calc_dissipation_storage_auxiliary_water()

            self.parent.heat_system = "gas"
            self.parent.heat_generation = "condensing"

            generator_two = 0.1 * (self._dissipation_water() + self._calc_dissipation_generation_auxiliary_water())

            # final_energy_demand_water = generator_one + generator_two
            primary_energy_demand_water = generator_one * 1.8 + generator_two * 1.1  # multiplied with PEF

        elif self.parent.heat_generation == "condensing - chp":
            # TABULA values
            # 0.58 % solar
            generator_two = 0.05 * (self._dissipation_water() +
                                    self._calc_dissipation_generation_auxiliary_water())

            # DIN V 4701-10 table C.3-4a
            self.parent.heat_system = "gas"
            self.parent.heat_generation = "condensing"

            generator_one = 0.37 * (self._dissipation_water() + self._calc_dissipation_generation_auxiliary_water()) \
                            + self._calc_dissipation_distribution_auxiliary_water() \
                            + self._calc_dissipation_storage_auxiliary_water()

            # final_energy_demand_water = generator_one + generator_two
            primary_energy_demand_water = generator_one * 0.7 + generator_two * 1.1  # multiplied with PEF

        else:

            if self.parent.storage_water == "solar":
                part_generator = 1 - part_solar
            else:
                part_generator = 1

            final_energy_demand_water = part_generator * (self._dissipation_water() +
                                                          self._calc_dissipation_generation_auxiliary_water()) \
                                        + self._calc_dissipation_distribution_auxiliary_water() + \
                                        self._calc_dissipation_storage_auxiliary_water()

            primary_energy_demand_water = final_energy_demand_water * primary_energy_factor

        return primary_energy_demand_water

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
