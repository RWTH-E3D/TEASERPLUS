# created November 2023
# by TEASER4 Development Team

"""This module includes a class for the Heating System
"""

import math
from teaser.teaser.logic.archetypebuildings.tabula.de.singlefamilyhouse import SingleFamilyHouse as Sfh
from teaser.teaser.logic.archetypebuildings.tabula.de.multifamilyhouse import MultiFamilyHouse as Mfh
from teaser.teaser.logic.archetypebuildings.tabula.de.terracedhouse import TerracedHouse as Th
from teaser.teaser.logic.archetypebuildings.tabula.de.apartmentblock import ApartmentBlock as Ab


class HeatingSystem(object):
    """HeatingSystem class

    This class holds information for the Heating System of the Building.
    The heat losses and materials are being set. This class doesn´t effect
    the calculation in Dymola. It uses the calculated heat load and adds
    heat losses for heating and hot water to calculate the primary energy demand.

    Parameters
        ----------

        parent: Building()

        Attributes
        ----------

    """

    def __init__(self, parent=None):
        """Constructor of HeatingSystem class
        """
        self.parent = parent
        
        self._length_char = self.parent.get_footprint_gml() / 10  # iwu chapter 4.4.1

        # setting values for generation
        self._heat_system = None
        self._heat_generation = None
        self._storage_water = None
        self._combined_water_heating = True
        self._nominal_heat_output_boiler = None
        self._temp_ambient = 20  # todo: für Heizung Wert anpassen, für Wasser so lassen
        self._annual_operating_time_heating = 350
        self._annual_operating_time_water = 350

        # setting values for distribution
        self._pipe_routing_heating = None
        self._pipe_routing_water = None
        self._avg_temp_distribution_heating = None
        self._avg_temp_distribution_water = None
        self._design_temp_flow = None
        self._oversizing_factor = 1.2  # standard for existing biuldings (iwu) # todo Anpassen für Neubau?
        self._heat_loss_distribution_heating = None
        self._daily_operating_time_pump = None

        # iwu formula 4-4
        if self.parent.net_leased_area < 10000:
            self._daily_operating_time_pump = 7.5 + 1 / (0.06 + 7 / self.parent.net_leased_area)
        else:
            self._daily_operating_time_pump = 24

        # iwu formula 2-3, rounded to 5 [kW] # todo check, ob simulated_heat_load in kW
        if (5 * round(self._oversizing_factor * self.parent.simulated_heat_load / 5)) < 15 or None:
            self._nominal_heat_output_boiler = 15
        else:
            self._nominal_heat_output_boiler = 5 * round(self._oversizing_factor * self.parent.simulated_heat_load / 5)

        # iwu 1.2 for existing buildings
        if self.parent.year_of_construction >=2016 or self.parent.year_of_retrofit >=2016:
            self._oversizing_factor = 1

    def setting_heating_system(self, type_heating_system):
        """
        Setting values from TABULA-DE for heating and warm water systems.
        Depending on the type and year of construction and type of retrofit.
        Type of heating system needs to be set.
        """
        if type_heating_system is None:
            if self.parent.year_of_construction >= 2016:  # todo Zeitpunt Neubau definieren
                type_heating_system = 3  # DENA report 2023 Abb. 41
            else:
                type_heating_system = 1  # DENA report 2023 Abb. 31

        if type(self.parent).__name__ in ["SingleFamilyHouse", "TerracedHouse"]:

            if self.parent.year_of_construction <= 1994:

                if Sfh.construction_type == "tabula_standard" or Th.construction_type == "tabula_standard":

                    if type_heating_system == 1:
                        self._heat_system = "gas"
                        self._heat_generation = "low temperature"
                        self._pipe_routing_water = "centralised with circulation"
                        self._heat_loss_distribution_heating = "high"
                    elif type_heating_system == 2:
                        self._heat_system = "oil"
                        self._heat_generation = "low temperature - not combined"
                        self._heat_loss_distribution_heating = "high"
                    elif type_heating_system == 3:
                        self._heat_system = "electricity"
                        self._heat_generation = "night storage"
                    elif type_heating_system == 4:
                        self._heat_system = "oil"
                        self._heat_generation = "low temperature"
                        self._pipe_routing_water = "centralised with circulation"
                        self._heat_loss_distribution_heating = "high"

                elif Sfh.construction_type == "tabula_retrofit" or Th.construction_type == "tabula_retrofit":

                    if type_heating_system == 1:
                        self._heat_system = "gas"
                        self._heat_generation = "condensing"
                        self._heat_loss_distribution_heating = "good"
                    elif type_heating_system == 2:
                        self._heat_system = "oil"
                        self._heat_generation = "condensing"
                        self._storage_water = "solar"
                        self._heat_loss_distribution_heating = "minimised"
                    elif type_heating_system == 3:
                        self._heat_system = "electricity"
                        self._heat_generation = "heatpump air"
                        self._storage_water = "solar"
                        self._heat_loss_distribution_heating = "good"
                    elif type_heating_system == 4:
                        self._heat_system = "oil"
                        self._heat_generation = "condensing"
                        self._storage_water = "solar"
                        self._heat_loss_distribution_heating = "minimised"

                elif Sfh.construction_type == "tabula_adv_retrofit" or Th.construction_type == "tabula_adv_retrofit":

                    self._heat_loss_distribution_heating = "minimised"
                    if type_heating_system == 1:
                        self._heat_system = "gas"
                        self._heat_generation = "condensing"
                        self._storage_water = "solar"
                    elif type_heating_system == 2:
                        self._heat_system = "biomass"
                        self._heat_generation = "woodpellets"
                        self._storage_water = "solar"
                    elif type_heating_system == 3:
                        self._heat_system = "electricity"
                        self._heat_generation = "heatpump ground"
                        self._storage_water = "water"
                    elif type_heating_system == 4:
                        self._heat_system = "biomass"
                        self._heat_generation = "woodpellets"
                        self._storage_water = "solar"

            elif self.parent.year_of_construction <= 2009:

                if Sfh.construction_type == "tabula_standard" or Th.construction_type == "tabula_standard":

                    if type_heating_system == 1:
                        self._heat_system = "gas"
                        self._heat_generation = "condensing"
                        self._heat_loss_distribution_heating = "minimised"
                    elif type_heating_system == 2:
                        self._heat_system = "biomass"
                        self._heat_generation = "woodpellets"
                        self._storage_water = "water"
                        self._pipe_routing_water = "centralised with circulation"
                        self._heat_loss_distribution_heating = "good"
                    elif type_heating_system == 3:
                        self._heat_system = "electricity"
                        self._heat_generation = "heatpump air"
                        self._storage_water = "solar"
                        self._heat_loss_distribution_heating = "good"

                elif Sfh.construction_type == "tabula_retrofit" or Th.construction_type == "tabula_retrofit":

                    self._heat_loss_distribution_heating = "minimised"
                    if type_heating_system == 1:
                        self._heat_system = "gas"
                        self._heat_generation = "condensing"
                        self._storage_water = "solar"
                        self._pipe_routing_water = "centralised with circulation"
                    elif type_heating_system == 2:
                        self._heat_system = "biomass"
                        self._heat_generation = "woodpellets"
                        self._storage_water = "water"
                        self._pipe_routing_water = "centralised with circulation"
                    elif type_heating_system == 3:
                        self._heat_system = "electricity"
                        self._heat_generation = "heatpump air"
                        self._storage_water = "water"
                        self._pipe_routing_water = "centralised with circulation"

                elif Sfh.construction_type == "tabula_adv_retrofit" or Th.construction_type == "tabula_adv_retrofit":

                    self._heat_loss_distribution_heating = "minimised"
                    if type_heating_system == 1:
                        self._heat_system = "gas"
                        self._heat_generation = "condensing"
                        self._storage_water = "solar"
                    elif type_heating_system == 2:
                        self._heat_system = "biomass"
                        self._heat_generation = "woodpellets"
                        self._storage_water = "water"
                    elif type_heating_system == 3:
                        self._heat_system = "electricity"
                        self._heat_generation = "heatpump ground"
                        self._storage_water = "water"

            elif self.parent.year_of_construction <= 2015:

                self._heat_loss_distribution_heating = "minimised"
                if Sfh.construction_type == "tabula_standard" or Th.construction_type == "tabula_standard":

                    if type_heating_system == 1:
                        self._heat_system = "gas"
                        self._heat_generation = "condensing"
                        self._storage_water = "solar"
                        self._pipe_routing_water = "centralised with circulation"
                    elif type_heating_system == 2:
                        self._heat_system = "biomass"
                        self._heat_generation = "woodpellets"
                        self._storage_water = "water"
                        self._pipe_routing_water = "centralised with circulation"
                    elif type_heating_system == 3:
                        self._heat_system = "electricity"
                        self._heat_generation = "heatpump air"
                        self._storage_water = "water"
                        self._pipe_routing_water = "centralised with circulation"

                elif Sfh.construction_type == "tabula_retrofit" or Th.construction_type == "tabula_retrofit":

                    if type_heating_system == 1:
                        self._heat_system = "gas"
                        self._heat_generation = "condensing"
                        self._storage_water = "solar"
                    elif type_heating_system == 2:
                        self._heat_system = "biomass"
                        self._heat_generation = "woodpellets"
                        self._storage_water = "water"
                    elif type_heating_system == 3:
                        self._heat_system = "electricity"
                        self._heat_generation = "heatpump ground - no buffer storage"
                        self._storage_water = "water"

                elif Sfh.construction_type == "tabula_adv_retrofit" or Th.construction_type == "tabula_adv_retrofit":

                    if type_heating_system == 1:
                        self._heat_system = "gas"
                        self._heat_generation = "condensing"
                        self._storage_water = "solar"
                    elif type_heating_system == 2:
                        self._heat_system = "biomass"
                        self._heat_generation = "woodpellets"
                        self._storage_water = "solar"
                    elif type_heating_system == 3:
                        self._heat_system = "electricity"
                        self._heat_generation = "heatpump ground - no buffer storage"
                        self._storage_water = "water"

            else:

                self._heat_loss_distribution_heating = "minimised"
                if Sfh.construction_type == "tabula_standard" or Th.construction_type == "tabula_standard":

                    if type_heating_system == 1:
                        self._heat_system = "gas"
                        self._heat_generation = "condensing"
                        self._storage_water = "solar"
                    elif type_heating_system == 2:
                        self._heat_system = "biomass"
                        self._heat_generation = "woodpellets"
                        self._storage_water = "water"
                        self._pipe_routing_water = "centralised with circulation"
                    elif type_heating_system == 3:
                        self._heat_system = "electricity"
                        self._heat_generation = "heatpump ground - no buffer storage"
                        self._storage_water = "water"

                elif Sfh.construction_type == "tabula_retrofit" or Th.construction_type == "tabula_retrofit":

                    if type_heating_system == 1:
                        self._heat_system = "gas"
                        self._heat_generation = "condensing"
                        self._storage_water = "solar"
                    elif type_heating_system == 2:
                        self._heat_system = "biomass"
                        self._heat_generation = "woodpellets"
                        self._storage_water = "water"
                    elif type_heating_system == 3:
                        self._heat_system = "electricity"
                        self._heat_generation = "heatpump ground - no buffer storage"
                        self._storage_water = "water"

                elif Sfh.construction_type == "tabula_adv_retrofit" or Th.construction_type == "tabula_adv_retrofit":

                    if type_heating_system == 1:
                        self._heat_system = "gas"
                        self._heat_generation = "condensing"
                        self._storage_water = "solar"
                    elif type_heating_system == 2:
                        self._heat_system = "biomass"
                        self._heat_generation = "woodpellets"
                        self._storage_water = "solar"
                    elif type_heating_system == 3:
                        self._heat_system = "electricity"
                        self._heat_generation = "heatpump ground - no buffer storage"
                        self._storage_water = "water"

        elif type(self.parent).__name__ in ["MultiFamilyHouse", "ApartmentBlock"]:

            if self.parent.year_of_construction <= 1994:

                if Mfh.construction_type == "tabula_standard" or Ab.construction_type == "tabula_standard":

                    self._heat_loss_distribution_heating = "high"
                    if type_heating_system == 1:
                        self._heat_system = "gas"
                        self._heat_generation = "low temperature"
                        self._storage_water = "water"
                    elif type_heating_system == 2:
                        self._heat_system = "oil"
                        self._heat_generation = "low temperature - not combined"
                    elif type_heating_system == 3:
                        self._heat_system = "electricity"
                        self._heat_generation = "night storage"
                    elif type_heating_system == 4:
                        self._heat_system = "district"
                        self._heat_generation = "gas - no chp"
                    elif type_heating_system == 5:
                        self._heat_system = "gas"
                        self._heat_generation = "circulating water heater"
                    elif type_heating_system == 6:
                        self._heat_system = "oil"
                        self._heat_generation = "low temperature"
                        self._storage_water = "water"

                elif Mfh.construction_type == "tabula_retrofit" or Ab.construction_type == "tabula_retrofit":

                    if type_heating_system == 1:
                        self._heat_system = "gas"
                        self._heat_generation = "condensing"
                        self._storage_water = "water"
                        self._heat_loss_distribution_heating = "small"
                    elif type_heating_system == 2:
                        self._heat_system = "oil"
                        self._heat_generation = "condensing"
                        self._storage_water = "solar"
                        self._heat_loss_distribution_heating = "minimised"
                    elif type_heating_system == 3:
                        self._heat_system = "gas"
                        self._heat_generation = "condensing - decentralised"
                        self._heat_loss_distribution_heating = "small"
                    elif type_heating_system == 4:
                        self._heat_system = "district"
                        self._heat_generation = "gas - high chp"
                        self._heat_loss_distribution_heating = "small"
                    elif type_heating_system == 5:
                        self._heat_system = "gas"
                        self._heat_generation = "condensing - decentralised"
                        self._heat_loss_distribution_heating = "small"
                    elif type_heating_system == 6:
                        self._heat_system = "oil"
                        self._heat_generation = "condensing"
                        self._storage_water = "solar"
                        self._heat_loss_distribution_heating = "minimised"

                elif Mfh.construction_type == "tabula_adv_retrofit" or Ab.construction_type == "tabula_adv_retrofit":

                    self._heat_loss_distribution_heating = "small"
                    if type_heating_system == 1:
                        self._heat_system = "gas"
                        self._heat_generation = "condensing"
                        self._storage_water = "solar"
                    elif type_heating_system == 2:
                        self._heat_system = "biomass"
                        self._heat_generation = "woodpellets"
                        self._storage_water = "solar"
                    elif type_heating_system == 3:
                        self._heat_system = "biomass"
                        self._heat_generation = "woodpellets"
                        self._storage_water = "water"
                    elif type_heating_system == 4:
                        self._heat_system = "district"
                        self._heat_generation = "biomass"
                    elif type_heating_system == 5:
                        self._heat_system = "gas"
                        self._heat_generation = "condensing - decentralised"
                    elif type_heating_system == 6:
                        self._heat_system = "biomass"
                        self._heat_generation = "woodpellets"
                        self._storage_water = "solar"

            elif self.parent.year_of_construction <= 2009:

                if Mfh.construction_type == "tabula_standard" or Ab.construction_type == "tabula_standard":

                    self._heat_loss_distribution_heating = "small"
                    if type_heating_system == 1:
                        self._heat_system = "gas"
                        self._heat_generation = "condensing"
                        self._storage_water = "water"
                    elif type_heating_system == 2:
                        self._heat_system = "biomass"
                        self._heat_generation = "woodpellets"
                        self._storage_water = "water"
                    elif type_heating_system == 3:
                        self._heat_system = "electricity"
                        self._heat_generation = "heatpump air"
                        self._storage_water = "water"

                elif Mfh.construction_type == "tabula_retrofit" or Ab.construction_type == "tabula_retrofit":

                    if type_heating_system == 1:
                        self._heat_system = "gas"
                        self._heat_generation = "condensing"
                        self._storage_water = "solar"
                        self._heat_loss_distribution_heating = "minimised"
                    elif type_heating_system == 2:
                        self._heat_system = "biomass"
                        self._heat_generation = "woodpellets"
                        self._storage_water = "water"
                        self._heat_loss_distribution_heating = "minimised"
                    elif type_heating_system == 3:
                        self._heat_system = "electricity"
                        self._heat_generation = "heatpump air"
                        self._storage_water = "water"
                        self._heat_loss_distribution_heating = "small"

                elif Mfh.construction_type == "tabula_adv_retrofit" or Ab.construction_type == "tabula_adv_retrofit":

                    self._heat_loss_distribution_heating = "minimised"
                    if type_heating_system == 1:
                        self._heat_system = "gas"
                        self._heat_generation = "condensing"
                        self._storage_water = "solar"
                    elif type_heating_system == 2:
                        self._heat_system = "biomass"
                        self._heat_generation = "woodpellets"
                        self._storage_water = "water"
                    elif type_heating_system == 3:
                        self._heat_system = "electricity"
                        self._heat_generation = "heatpump ground"
                        self._storage_water = "water"

            elif self.parent.year_of_construction <= 2015:

                if Mfh.construction_type == "tabula_standard" or Ab.construction_type == "tabula_standard":

                    if type_heating_system == 1:
                        self._heat_system = "gas"
                        self._heat_generation = "condensing"
                        self._storage_water = "solar"
                        self._heat_loss_distribution_heating = "minimised"
                    elif type_heating_system == 2:
                        self._heat_system = "biomass"
                        self._heat_generation = "woodpellets"
                        self._storage_water = "water"
                        self._heat_loss_distribution_heating = "minimised"
                    elif type_heating_system == 3:
                        self._heat_system = "electricity"
                        self._heat_generation = "heatpump air"
                        self._storage_water = "water"
                        self._heat_loss_distribution_heating = "small"

                elif Mfh.construction_type == "tabula_retrofit" or Ab.construction_type == "tabula_retrofit":

                    self._heat_loss_distribution_heating = "minimised"
                    if type_heating_system == 1:
                        self._heat_system = "gas"
                        self._heat_generation = "condensing"
                        self._storage_water = "solar"
                    elif type_heating_system == 2:
                        self._heat_system = "biomass"
                        self._heat_generation = "woodpellets"
                        self._storage_water = "water"
                    elif type_heating_system == 3:
                        self._heat_system = "electricity"
                        self._heat_generation = "heatpump ground"
                        self._storage_water = "water"

                elif Mfh.construction_type == "tabula_adv_retrofit" or Ab.construction_type == "tabula_adv_retrofit":

                    self._heat_loss_distribution_heating = "minimised"
                    if type_heating_system == 1:
                        self._heat_system = "gas"
                        self._heat_generation = "condensing - chp"
                        self._storage_water = "solar"
                    elif type_heating_system == 2:
                        self._heat_system = "biomass"
                        self._heat_generation = "chp"
                        self._storage_water = "solar"
                    elif type_heating_system == 3:
                        self._heat_system = "electricity"
                        self._heat_generation = "heatpump ground"
                        self._storage_water = "water"

            else:

                self._heat_loss_distribution_heating = "minimised"
                if Mfh.construction_type == "tabula_standard" or Ab.construction_type == "tabula_standard":

                    if type_heating_system == 1:
                        self._heat_system = "gas"
                        self._heat_generation = "condensing"
                        self._storage_water = "solar"
                    elif type_heating_system == 2:
                        self._heat_system = "biomass"
                        self._heat_generation = "woodpellets"
                        self._storage_water = "water"
                    elif type_heating_system == 3:
                        self._heat_system = "electricity"
                        self._heat_generation = "heatpump ground"
                        self._storage_water = "water"

                elif Mfh.construction_type == "tabula_retrofit" or Ab.construction_type == "tabula_retrofit":

                    if type_heating_system == 1:
                        self._heat_system = "gas"
                        self._heat_generation = "condensing"
                        self._storage_water = "solar"
                    elif type_heating_system == 2:
                        self._heat_system = "biomass"
                        self._heat_generation = "woodpellets"
                        self._storage_water = "water"
                    elif type_heating_system == 3:
                        self._heat_system = "electricity"
                        self._heat_generation = "heatpump ground"
                        self._storage_water = "water"

                elif Mfh.construction_type == "tabula_adv_retrofit" or Ab.construction_type == "tabula_adv_retrofit":

                    if type_heating_system == 1:
                        self._heat_system = "gas"
                        self._heat_generation = "condensing - chp"
                        self._storage_water = "solar"
                    elif type_heating_system == 2:
                        self._heat_system = "biomass"
                        self._heat_generation = "chp"
                        self._storage_water = "solar"
                    elif type_heating_system == 3:
                        self._heat_system = "electricity"
                        self._heat_generation = "heatpump ground"
                        self._storage_water = "water"

        if self._heat_generation in ["night storage", "low temperature - not combined"]:
            self._combined_water_heating = False  # todo wird die Angabe bei Berechnungen gebraucht?

        if (self._heat_system == "gas" and
            (self._heat_generation in ["circulating water heater", "condensing - decentralised"])) or \
                (self._heat_system == "electricity" and self._heat_generation == "night storage"):
            self._pipe_routing_heating = "decentralised"
        else:
            self._pipe_routing_heating = "centralised inside"
        # todo wann ist der Verlauf "centralised outside"? Soll überhaupt eine Unterscheidung vorgenommen werden?
        #  Macht einen Unterschied der doppelten Rohrlänge aus

        if type(self.parent).__name__ in ["SingleFamilyHouse", "TerracedHouse"] and self._pipe_routing_water is None:
            if self._pipe_routing_heating == "decentralised" or self._combined_water_heating is False:
                self._pipe_routing_water = "decentralised"
            else:
                self._pipe_routing_water = "centralised without circulation"
        elif type(self.parent).__name__ in ["MultiFamilyHouse", "ApartmentBlock"]:
            if self._pipe_routing_heating == "decentralised" or self._combined_water_heating is False:
                self._pipe_routing_water = "decentralised"
            else:
                self._pipe_routing_water = "centralised with circulation"

        if self._heat_generation in ["low temperature", "low temperature-not combined"]:
            self._design_temp_flow = 70
        elif self._heat_generation in ["heatpump ground", "heatpump ground - no buffer storage", "heatpump air"]:
            self._design_temp_flow = 35
        else:
            self._design_temp_flow = 55

    def calc_avg_temp_distribution_heating(self, heating_mode):
        # todo heating_mode muss von der Nutzer*in eingetragen werden
        # todo wie kann der oversizing_factor bestimmt werden?
        # todo 35 Grad VL integrieren
        """
        Calculation of the average temperature of the heat distribution.
        optimised = with hydraulic balancing
        typical = without hydraulic balancing
        """
        # iwu table 1

        if heating_mode == "optimised":

            if self._design_temp_flow == 90:

                if self._oversizing_factor == 1.0:
                    self._avg_temp_distribution_heating = 54
                elif self._oversizing_factor == 1.2:
                    self._avg_temp_distribution_heating = 50
                elif self._oversizing_factor == 1.5:
                    self._avg_temp_distribution_heating = 45
                elif self._oversizing_factor == 2.0:
                    self._avg_temp_distribution_heating = 40
                elif self._oversizing_factor == 3.0:
                    self._avg_temp_distribution_heating = 37

            elif self._design_temp_flow == 70:

                if self._oversizing_factor == 1.0:
                    self._avg_temp_distribution_heating = 44
                elif self._oversizing_factor == 1.2:
                    self._avg_temp_distribution_heating = 41
                elif self._oversizing_factor == 1.5:
                    self._avg_temp_distribution_heating = 38
                elif self._oversizing_factor == 2.0:
                    self._avg_temp_distribution_heating = 34
                elif self._oversizing_factor == 3.0:
                    self._avg_temp_distribution_heating = 32

            elif self._design_temp_flow == 55:

                if self._oversizing_factor == 1.0:
                    self._avg_temp_distribution_heating = 37
                elif self._oversizing_factor == 1.2:
                    self._avg_temp_distribution_heating = 35
                elif self._oversizing_factor == 1.5:
                    self._avg_temp_distribution_heating = 32
                elif self._oversizing_factor == 2.0:
                    self._avg_temp_distribution_heating = 30
                elif self._oversizing_factor == 3.0:
                    self._avg_temp_distribution_heating = 28

        elif heating_mode == "typical":

            if self._design_temp_flow == 90:

                if self._oversizing_factor == 1.0:
                    self._avg_temp_distribution_heating = 66
                elif self._oversizing_factor == 1.2:
                    self._avg_temp_distribution_heating = 63
                elif self._oversizing_factor == 1.5:
                    self._avg_temp_distribution_heating = 59
                elif self._oversizing_factor == 2.0:
                    self._avg_temp_distribution_heating = 56
                elif self._oversizing_factor == 3.0:
                    self._avg_temp_distribution_heating = 53

            elif self._design_temp_flow == 70:

                if self._oversizing_factor == 1.0:
                    self._avg_temp_distribution_heating = 53
                elif self._oversizing_factor == 1.2:
                    self._avg_temp_distribution_heating = 50
                elif self._oversizing_factor == 1.5:
                    self._avg_temp_distribution_heating = 48
                elif self._oversizing_factor == 2.0:
                    self._avg_temp_distribution_heating = 45
                elif self._oversizing_factor == 3.0:
                    self._avg_temp_distribution_heating = 44

            elif self._design_temp_flow == 55:

                if self._oversizing_factor == 1.0:
                    self._avg_temp_distribution_heating = 43
                elif self._oversizing_factor == 1.2:
                    self._avg_temp_distribution_heating = 41
                elif self._oversizing_factor == 1.5:
                    self._avg_temp_distribution_heating = 40
                elif self._oversizing_factor == 2.0:
                    self._avg_temp_distribution_heating = 38
                elif self._oversizing_factor == 3.0:
                    self._avg_temp_distribution_heating = 37

            else:

                print("heating_mode must be set to 'optimised' or 'typical'")

    def calc_avg_temp_distribution_water(self):
        # calculation of the average temperature of the water distribution
        # iwu chapter 1.2.2

        if self._pipe_routing_water == "centralised with circulation":
            self._avg_temp_distribution_water = 50

        elif self._pipe_routing_water in ["centralised without circulation", "decentralised"]:
            self._avg_temp_distribution_water = 32

    def _calc_dissipation_distribution_water_for_heating(self):
        # calculation of heat dissipation through distribution of hot water for heating

        # calculation of pipe length for hot water
        # iwu table 9
        if self._pipe_routing_water == "centralised with circulation":

            length_horizontal_water = 2 * self._length_char - 10
            length_strand_water = self._length_char * self.parent.number_of_floors / 2
            length_stubs_water = self._length_char * self.parent.number_of_floors / 2

        elif self._pipe_routing_water == "centralised without circulation":

            length_horizontal_water = self._length_char - 5
            length_strand_water = self._length_char * self.parent.number_of_floors / 4
            length_stubs_water = self._length_char * self.parent.number_of_floors / 2

        elif self._pipe_routing_water == "decentralised":

            length_stubs_water = self._length_char * self.parent.number_of_floors / 2

        # calculation of heat loss coefficient and factor for hot water
        # iwu table 10
        if self.parent.year_of_retrofit < 1950 or \
                (self.parent.year_of_retrofit is None and self.parent.year_of_construction < 1980):
            heat_loss_coefficient_horizontal_water = 0.4
        else:
            heat_loss_coefficient_horizontal_water = 0.2
        heat_loss_factor_horizontal_water = 1.0

        if self.parent.year_of_construction < 1980:
            heat_loss_coefficient_strand_water = 2.0
        else:
            heat_loss_coefficient_strand_water = 0.2
        heat_loss_factor_strand_water = 0.15

        if self.parent.year_of_construction < 2000:
            heat_loss_coefficient_stubs_water = 1.4
        else:
            heat_loss_coefficient_stubs_water = 0.2
        heat_loss_factor_stubs_water = 0.15

        # DIN V4701-10 formula 5.1.2-2 with iwu formula 4-2 and 4-3
        if self._pipe_routing_water == "centralised with circulation":

            during_circulation = (self._avg_temp_distribution_water - self._temp_ambient) * \
                                 self._daily_operating_time_pump
            during_interruption = 0.5 * (32 - self._temp_ambient) * (24 - self._daily_operating_time_pump)
            # 32 = avg_temp_distribution_water without circulation

            return 1 / 1000 * ((length_horizontal_water * heat_loss_coefficient_horizontal_water) *
                               (1 - heat_loss_factor_horizontal_water) +
                               (length_strand_water * heat_loss_coefficient_strand_water) *
                               (1 - heat_loss_factor_strand_water) +
                               (length_stubs_water * heat_loss_coefficient_stubs_water) *
                               (1 - heat_loss_factor_stubs_water)) * \
                   (during_circulation + during_interruption) * self._annual_operating_time_water * \
                   self._annual_operating_time_heating / self._annual_operating_time_water

        elif self._pipe_routing_water in ["centralised without circulation", "decentralised"]:

            return 1 / 1000 * \
                   ((length_horizontal_water * heat_loss_coefficient_horizontal_water) *
                    (1 - heat_loss_factor_horizontal_water) +
                    (length_strand_water * heat_loss_coefficient_strand_water) *
                    (1 - heat_loss_factor_strand_water) +
                    (length_stubs_water * heat_loss_coefficient_stubs_water) *
                    (1 - heat_loss_factor_stubs_water)) * \
                   (self._avg_temp_distribution_water - self._temp_ambient) * 24 * self._annual_operating_time_water * \
                   self._annual_operating_time_heating / self._annual_operating_time_water

    def _calc_dissipation_storage_water_for_heating(self):

        # DIN V 4701-10 table C.1-3a
        if self._pipe_routing_heating == "centralised inside":

            if self._pipe_routing_water == "decentralised":
                return 0.5 * self.parent.net_leased_area

            # DIN V 4701-10 formula 5.1.3-10
            else:
                return self._annual_operating_time_heating / self._annual_operating_time_water * \
                       (1 - 0.15) * self._calc_dissipation_storage_water()
                # 0.15 = Heat loss factor for components within the thermal envelope, DIN V 4701-10 table 5-2

        else:
            return 0

    def _calc_dissipation_controll_emission_heating(self):
        # iwu chapter 5.5
        if self._pipe_routing_heating == "decentralised":
            return 0

        else:
            if type(self.parent).__name__ in ["SingleFamilyHouse", "TerracedHouse"]:

                if self.parent.year_of_construction < 1980:
                    return 20 * 8760 / 1000
                elif self.parent.year_of_construction < 1990:
                    return 15 * 8760 / 1000
                else:
                    return 10 * 8760 / 1000
            elif type(self.parent).__name__ in ["MultiFamilyHouse", "ApartmentBlock"]:

                if self.parent.year_of_construction < 1980:
                    return 35 * 8760 / 1000
                elif self.parent.year_of_construction < 1990:
                    return 25 * 8760 / 1000
                else:
                    return 20 * 8760 / 1000

    def _calc_dissipation_distribution_heating(self):
        # calculation of heat dissipation through distribution of hot water

        # calculation of pipe length and heat loss coefficient and factor for heating
        # iwu table 9 and table 10
        # todo year of retrofit checken
        if self._pipe_routing_heating == "centralised outside":

            length_horizontal_heating = 4 * self._length_char - 10
            length_strand_heating = self._length_char * self.parent.number_of_floors
            length_tethers_heating = self._length_char * self.parent.number_of_floors * 2 / 3

            if self.parent.year_of_retrofit < 1950 or \
                    (self.parent.year_of_retrofit is None and self.parent.year_of_construction < 1980):
                heat_loss_coefficient_horizontal_heating = 0.4
            else:
                heat_loss_coefficient_horizontal_heating = 0.2
            heat_loss_factor_horizontal_heating = 1.0

            if self.parent.year_of_construction < 1980 and \
                    (self.parent.year_of_retrofit < 1950 or self.parent.year_of_retrofit is None):
                heat_loss_coefficient_strand_heating = 1.4
                heat_loss_factor_strand_heating = 0.48
            elif (self.parent.year_of_construction < 1980 and
                  self.parent.year_of_retrofit < 1980) or self.parent.year_of_retrofit >= 1950:
                heat_loss_coefficient_strand_heating = 1.0
                heat_loss_factor_strand_heating = 0.21
            elif self.parent.year_of_construction < 2000:
                heat_loss_coefficient_strand_heating = 0.8
                heat_loss_factor_strand_heating = 0.35
            else:
                heat_loss_coefficient_strand_heating = 0.26
                heat_loss_factor_strand_heating = 0.35

            if self.parent.year_of_construction < 1980:
                heat_loss_coefficient_tethers_heating = 1.0
                heat_loss_factor_tethers_heating = 0.1
            elif self.parent.year_of_construction < 2000:
                heat_loss_coefficient_tethers_heating = 0.8
                heat_loss_factor_tethers_heating = 0.32
            else:
                heat_loss_coefficient_tethers_heating = 0.26
                heat_loss_factor_tethers_heating = 0.32

        elif self._pipe_routing_heating == "centralised inside":

            length_horizontal_heating = 2 * self._length_char - 10
            length_strand_heating = self._length_char * self.parent.number_of_floors / 2
            length_tethers_heating = self._length_char * self.parent.number_of_floors * 4
            
            if self.parent.year_of_retrofit < 1950 or \
                    (self.parent.year_of_retrofit is None and self.parent.year_of_construction < 1980):
                heat_loss_coefficient_horizontal_heating = 0.4
            else:
                heat_loss_coefficient_horizontal_heating = 0.2
            heat_loss_factor_horizontal_heating = 1.0

            if self.parent.year_of_construction < 1980:
                heat_loss_coefficient_strand_heating = 2.0
            elif self.parent.year_of_construction < 2000:
                heat_loss_coefficient_strand_heating = 0.2
            else:
                heat_loss_coefficient_strand_heating = 0.26
            heat_loss_factor_strand_heating = 0.15

            if self.parent.year_of_construction < 1980:
                heat_loss_coefficient_tethers_heating = 1.0
            elif self.parent.year_of_construction < 2000:
                heat_loss_coefficient_tethers_heating = 0.3
            else:
                heat_loss_coefficient_tethers_heating = 0.26
            heat_loss_factor_tethers_heating = 0.1

        elif self._pipe_routing_heating == "decentralised":

            length_strand_heating = self._length_char * self.parent.number_of_floors * 6
            length_tethers_heating = self._length_char * self.parent.number_of_floors

            if self.parent.year_of_construction < 1980:
                heat_loss_coefficient_strand_heating = 1.0
                heat_loss_factor_strand_heating = 0.15
            elif self.parent.year_of_construction < 2000:
                heat_loss_coefficient_strand_heating = 0.8
                heat_loss_factor_strand_heating = 0.35
            else:
                heat_loss_coefficient_strand_heating = 0.26
                heat_loss_factor_strand_heating = 0.35

            if self.parent.year_of_construction < 1980:
                heat_loss_coefficient_tethers_heating = 0.6
                heat_loss_factor_tethers_heating = 0.1
            elif self.parent.year_of_construction < 2000:
                heat_loss_coefficient_tethers_heating = 0.8
                heat_loss_factor_tethers_heating = 0.32
            else:
                heat_loss_coefficient_tethers_heating = 0.26
                heat_loss_factor_tethers_heating = 0.32
        
        # TABULA values
        if self._heat_generation == "night storage":
            return 0

        # iwu formula 4-1
        else:
            return 1 / 1000 * ((length_horizontal_heating * heat_loss_coefficient_horizontal_heating) *
                               heat_loss_factor_horizontal_heating +
                               (length_strand_heating * heat_loss_coefficient_strand_heating) *
                               heat_loss_factor_strand_heating +
                               (length_tethers_heating * heat_loss_coefficient_tethers_heating) *
                               heat_loss_factor_tethers_heating * 0.8) * \
                   (self._avg_temp_distribution_heating - self._temp_ambient) * \
                   24 * self._annual_operating_time_heating
            # 24 = standard value of daily running time of circulation pump
            # 0.8 = partial heating factor acc. DIN V 4701-10 table 5.3-2 (= 1.0 for horizontal and strand pipes)

    def _calc_dissipation_storage_heating(self):

        # Condition from TABULA
        if self._heat_generation in ["heatpump air", "condensing - chp", "chp"] or \
                (self._heat_generation == "heatpump ground" and
                 type(self.parent).__name__ in ["SingleFamilyHouse", "TerracedHouse"]):

            # DIN V 4701-10 formula 5.3.3-2
            vol_storage = 4 * self.parent.net_leased_area ** 0.7
            standby_heat_loss_factor_tethers_heating = (0.5 + 0.25 * 1000 ** 0.4) * math.floor(vol_storage / 1000) + \
                               0.5 + 0.25 * (vol_storage % 1000) ** 0.4

            # DIN V 4701-10 formula 5.3.3-1
            return 1.2 * (self._avg_temp_distribution_heating - self._temp_ambient) / 45 * \
                   self._annual_operating_time_heating * 0.15 * standby_heat_loss_factor_tethers_heating
            # 0.15 = Heat loss factor for components within the thermal envelope, table 5-2 DIN V 4701-10

        else:
            return 0

    def _calc_dissipation_generation_heating(self):

        if self._heat_system == "electricity" and self._heat_generation != "night storage":

            # iwu chapter 2.2
            if self.parent.year_of_construction < 1980:
                if self._heat_generation == "heatpump air":
                    annual_performance_factor_heat_pump_55 = 2
                else:
                    annual_performance_factor_heat_pump_55 = 2.5
            elif self.parent.year_of_construction < 1990:
                if self._heat_generation == "heatpump air":
                    annual_performance_factor_heat_pump_55 = 2.3
                else:
                    annual_performance_factor_heat_pump_55 = 2.8
            else:
                if self._heat_generation == "heatpump air":
                    annual_performance_factor_heat_pump_55 = 2.6
                else:
                    annual_performance_factor_heat_pump_55 = 3.1
            annual_performance_factor_heat_pump = annual_performance_factor_heat_pump_55 * \
                                                  (1 - 0.0075 * (self._avg_temp_distribution_heating - 55))

            # DIN V 4701-10 formula 5.3.4.2-19
            expenditure_figure = 1 / annual_performance_factor_heat_pump

        else:
            # iwu table 5
            if self._heat_generation == "night storage":
                boiler_efficiency = 0.97
            elif self._heat_system == "district":
                boiler_efficiency = 0.98
            elif self._heat_system == "biomass":
                boiler_efficiency = 0.7

            else:

                # iwu formula B.1
                if self._heat_system == "circulating water heater":
                    # iwu table 5
                    if self.parent.year_of_construction < 1980:
                        boiler_efficiency = 0.79
                    elif self.parent.year_of_construction < 1990:
                        boiler_efficiency = 0.83
                    else:
                        # iwu table 7
                        standby_heat_loss_factor_tethers_heating_70_20kw = 0.015
                        boiler_efficiency_70_20kw = 0.92
                    # todo wenn nach 1990: wie NT - bzw. Brennwertkessel -> gibt es noch Heizungen vor 1990 ?

                else:
                    # iwu table 2
                    if self.parent.year_of_construction < 1990:
                        standby_heat_loss_factor_tethers_heating_70_20kw = 0.02
                        boiler_efficiency_70_20kw = 0.89
                    else:  # assumption: today´s values equal 1990-2000
                        standby_heat_loss_factor_tethers_heating_70_20kw = 0.015
                        boiler_efficiency_70_20kw = 0.92

                if self._nominal_heat_output_boiler == 20:
                    standby_heat_loss_factor_tethers_heating_70 = standby_heat_loss_factor_tethers_heating_70_20kw
                    boiler_efficiency_70 = boiler_efficiency_70_20kw
                else:
                    # iwu formula 2-1 and 2-2
                    standby_heat_loss_factor_tethers_heating_70 = standby_heat_loss_factor_tethers_heating_70_20kw * 2.456 * self._nominal_heat_output_boiler ** (-0.3)
                    boiler_efficiency_70 = boiler_efficiency_70_20kw - 0.0195 + 0.015 * \
                                           math.log10(self._nominal_heat_output_boiler)

                # avg_temp_boiler_heat_period = self._avg_temp_distribution_heating, no standard boiler in archetypes
                if self._avg_temp_distribution_heating < 70:
                    if self._heat_generation in ["low temperature", "low temperature - not combined"]:
                        efficiency_correction = 0.0004 * (70 - self._avg_temp_distribution_heating)
                    else:
                        if self._heat_system == "oil":
                            efficiency_correction = 0.0016 * (70 - self._avg_temp_distribution_heating)
                        else:
                            efficiency_correction = 0.0024 * (70 - self._avg_temp_distribution_heating)
                else:
                    efficiency_correction = 0

                if self._pipe_routing_heating == "centralised outside":
                    # assumption: if boiler outside, routing outside
                    utilisation_factor_heat_use = 0
                else:
                    utilisation_factor_heat_use = 0.85

                if boiler_efficiency is None:
                    avg_standby_heat_loss_factor_tethers_heating = standby_heat_loss_factor_tethers_heating_70 / 50 * \
                                           (self._avg_temp_distribution_heating - self._temp_ambient)
                    load_level_boiler = 0.3 * self.parent.simulated_heat_load / self._nominal_heat_output_boiler

                    boiler_efficiency = ((boiler_efficiency_70 + efficiency_correction) *
                                         (1 + utilisation_factor_heat_use * avg_standby_heat_loss_factor_tethers_heating /
                                          load_level_boiler)) / (1 + avg_standby_heat_loss_factor_tethers_heating * (1 / load_level_boiler - 1))

            # DIN V 4701-10 chapter 5.3.4.2
            if avg_standby_heat_loss_factor_tethers_heating is not None:
                # DIN V 4701-10 formula 5.3.4.2-6
                load_factor_boiler = (1 + (1 / 0.3 - 1) * avg_standby_heat_loss_factor_tethers_heating) / (1 + (1 / load_level_boiler - 1) *
                                                                                   avg_standby_heat_loss_factor_tethers_heating)

            else:
                load_factor_boiler = 1

            if self._heat_system in ["gas", "oil"] and \
                    self._heat_generation not in ["low temperature", "low temperature - not combined"]:

                expenditure_figure = 1 / (load_factor_boiler * (boiler_efficiency + 0.003 *
                                                                (30 - self._avg_temp_distribution_heating)))
                # 30°C = boiler temperature for condensing boilers at 30 % partial load efficiency - iwu table 3

            else:
                expenditure_figure = 1 / (load_factor_boiler * boiler_efficiency)

        return expenditure_figure

    def _dissipation_heating(self):
        return (self.parent.calc_simulated_annual_heat_energy() -
                self._calc_dissipation_distribution_water_for_heating() -
                self._calc_dissipation_storage_water_for_heating() +
                self._calc_dissipation_controll_emission_heating() +
                self._calc_dissipation_distribution_heating() +
                self._calc_dissipation_storage_heating()) * \
               self._calc_dissipation_generation_heating()

    def _calc_dissipation_distribution_auxiliary_heating(self):

        # DIN V 4701-10 table C.3-2d "night storage"
        # iwu chapter 5.3 "circulating water heater" already in calc_dissipation_generation_auxiliary_heating
        if self._heat_generation in ["night storage", "circulating water heater"]:
            return 0

        else:

            # iwu formula 5-16, 5-17 and 5-19
            if self._heat_loss_distribution_heating == "minimised":
                nominal_power_consumption_of_circulator = 7.1 + 0.53 * self.parent.simulated_heat_load
            elif self._heat_loss_distribution_heating == "small":
                nominal_power_consumption_of_circulator = 25 + 0.77 * self.parent.simulated_heat_load
            else:
                nominal_power_consumption_of_circulator = 163 + 3.7 * self.parent.simulated_heat_load - \
                                                          0.001 * self.parent.simulated_heat_load ** 2

            # iwu formula 5-8
            if self.parent.year_of_construction < 2016:
                # todo wenn hier Unterscheidung in Bestand und Neubau gemacht wird, wo sonst noch notwenig?
                # correction factor for controllable pumps in stock = 1
                return nominal_power_consumption_of_circulator * self._annual_operating_time_heating * \
                       self._daily_operating_time_pump / 1000

            # DIN V 4701-10 formula 5.3.2-4
            else:
                return nominal_power_consumption_of_circulator * self._annual_operating_time_heating * \
                       self._daily_operating_time_pump / ((1.4 - 20 / self.parent.net_leased_area) * 1000)

    def _calc_dissipation_storage_auxiliary_heating(self):

        # Condition from TABULA
        if self._heat_generation in ["heatpump air", "condensing - chp", "chp"] or \
                (self._heat_generation == "heatpump ground" and
                 type(self.parent).__name__ in ["SingleFamilyHouse", "TerracedHouse"]):

            # DIN V 4701-10 formula 5.3.3-3 and 5.3.3-4
            return (40 + 0.03 * self.parent.net_leased_area) * 0.3324 * self._annual_operating_time_heating / 1000
            # 0.3324 = simultaneous operation with heat generator (if not simultaneous, set tP = 24)

        else:
            return 0

    def _calc_dissipation_generation_auxiliary_heating(self):

        if self._heat_generation == "heatpump air":
            coverage_of_heat_generator_1 = 0.8  # ...*0.38 (off-peak electricity) +0.2 * 1 (zentraler Elektrospeicher)
        elif self._heat_generation == "condensing - chp":
            coverage_of_heat_generator_1 = 0.53  # ...*1.06 (natural gas, condensing) +1.48*0.47 (chp & solar)
        else:
            coverage_of_heat_generator_1 = 1

        if self._heat_system == "oil":
            # iwu formula 5-6
            nominal_power_consumption_boiler = 170 + 1.95 * self.parent.simulated_heat_load

        elif self._heat_system == "gas":

            if self._heat_generation == "circulating water heater":
                # iwu chapter 5-3
                auxiliary_energy_demand_boiler = (100 * self._annual_operating_time_heating * 24 +
                                                  20 * self._annual_operating_time_water * 24) / 1000
                # [kWh/a]

            else:
                # iwu formula 5-7
                nominal_power_consumption_boiler = 20 + 0.85 * self.parent.simulated_heat_load

        elif self._heat_generation in ["heatpump ground", "heatpump ground - no buffer storage"]:
            # DIN V 4701-10 table C3-4c
            auxiliary_energy_demand_boiler = 1.9 * self.parent.net_leased_area ** (-0.1)

        else:
            auxiliary_energy_demand_boiler = 0

        if auxiliary_energy_demand_boiler is None:
            # DIN V 4701-10 formula 5.3.4.2-9 and 5.3.4.2-7
            auxiliary_energy_demand_boiler = (self.parent.simulated_heat_load / self._nominal_heat_output_boiler) * \
                                             self._annual_operating_time_heating * 24 * nominal_power_consumption_boiler

        return auxiliary_energy_demand_boiler

    def _calc_dissipation_distribution_water(self):
        # calculation of heat dissipation through distribution of hot water

        # calculation of pipe length for hot water
        # iwu table 9
        if self._pipe_routing_water == "centralised with circulation":

            length_horizontal_water = 2 * self._length_char - 10
            length_strand_water = self._length_char * self.parent.number_of_floors / 2
            length_stubs_water = self._length_char * self.parent.number_of_floors / 2

        elif self._pipe_routing_water == "centralised without circulation":

            length_horizontal_water = self._length_char - 5
            length_strand_water = self._length_char * self.parent.number_of_floors / 4
            length_stubs_water = self._length_char * self.parent.number_of_floors / 2

        elif self._pipe_routing_water == "decentralised":

            length_stubs_water = self._length_char * self.parent.number_of_floors / 2

        # calculation of heat loss coefficient and factor for hot water
        # iwu table 10
        if self.parent.year_of_retrofit < 1950 or \
                (self.parent.year_of_retrofit is None and self.parent.year_of_construction < 1980):
            heat_loss_coefficient_horizontal_water = 0.4
        else:
            heat_loss_coefficient_horizontal_water = 0.2

        if self.parent.year_of_construction < 1980:
            heat_loss_coefficient_strand_water = 2.0
        else:
            heat_loss_coefficient_strand_water = 0.2

        if self.parent.year_of_construction < 2000:
            heat_loss_coefficient_stubs_water = 1.4
        else:
            heat_loss_coefficient_stubs_water = 0.2

        if self._pipe_routing_water == "centralised with circulation":
            # iwu formula 4-2 and 4-3
            during_circulation = (self._avg_temp_distribution_water - self._temp_ambient) * \
                                 self._daily_operating_time_pump
            during_interruption = 0.5 * (32 - self._temp_ambient) * (24 - self._daily_operating_time_pump)
            # 32 = avg_temp_distribution_water without circulation

            dissipation_distribution_water = 1 / 1000 * \
                                             (length_horizontal_water * heat_loss_coefficient_horizontal_water
                    + length_strand_water * heat_loss_coefficient_strand_water
                    + length_stubs_water * heat_loss_coefficient_stubs_water) \
                    * (during_circulation + during_interruption) * self._annual_operating_time_water

        elif self._pipe_routing_water == "centralised without circulation" or \
                self._pipe_routing_water == "decentralised":
            # iwu formula 4-5
            dissipation_distribution_water = 1 / 1000 * (length_horizontal_water *
                 heat_loss_coefficient_horizontal_water
                 + length_strand_water * heat_loss_coefficient_strand_water
                 + length_stubs_water * heat_loss_coefficient_stubs_water) \
                 * (self._avg_temp_distribution_water - self._temp_ambient) * 24 * self._annual_operating_time_water

        return dissipation_distribution_water

    def _calc_dissipation_storage_water(self):
        # iwu chapter 3
        # standby_heat_loss_factor_tethers_heating [kWh/d]
        if self._pipe_routing_water == "decentralised":

            vol_storage = round(self.parent.net_leased_area / 100) * (8 + 5)
            if vol_storage > 250:
                # calculation like indirectly heated warm water storage tanks
                if self.parent.year_of_construction < 1980:
                    standby_heat_loss_factor_tethers_heating = 0.5 + 0.25 * vol_storage ** 0.4
                elif self.parent.year_of_construction < 1990:
                    standby_heat_loss_factor_tethers_heating = 0.4 + 0.2 * vol_storage ** 0.4
                else:
                    standby_heat_loss_factor_tethers_heating = 0.2 + 0.19 * vol_storage ** 0.4

            else:
                # heated by electrical energy
                if self.parent.year_of_construction < 1980:
                    standby_heat_loss_factor_tethers_heating = 0.55 + 0.026 * vol_storage ** 0.8
                elif self.parent.year_of_construction < 1990:
                    standby_heat_loss_factor_tethers_heating = 0.36 + 0.024 * vol_storage ** 0.8
                else:
                    standby_heat_loss_factor_tethers_heating = 0.29 + 0.019 * vol_storage ** 0.8

        elif self._storage_water in ["water", "solar"]:
            # assumption: all water storage tanks are heated indirectly, because if not decentralised, combined with heating
            # water: iwu chapter 3.1, solar: iwu table 8

            if self.parent.year_of_construction < 1980:
                vol_storage = -4.2 * 10 ** (-6) * self.parent.net_leased_area ** 2 + \
                              0.42 * self.parent.net_leased_area + 205

                if self._storage_water == "water":
                    standby_heat_loss_factor_tethers_heating = 0.5 + 0.25 * vol_storage ** 0.4
                else:
                    standby_heat_loss_factor_tethers_heating = 0.3 + 0.2 * vol_storage ** 0.4

            else:
                vol_storage = -3.5 * 10 ** (-6) * self.parent.net_leased_area ** 2 + \
                              0.35 * self.parent.net_leased_area + 170

                if self.parent.year_of_construction < 1990:
                    if self._storage_water == "water":
                        standby_heat_loss_factor_tethers_heating = 0.4 + 0.2 * vol_storage ** 0.4
                    else:
                        standby_heat_loss_factor_tethers_heating = 0.3 + 0.2 * vol_storage ** 0.4
                else:
                    if self._storage_water == "water":
                        standby_heat_loss_factor_tethers_heating = 0.2 + 0.19 * vol_storage ** 0.4
                    else:
                        standby_heat_loss_factor_tethers_heating = 0.3 + 0.2 * vol_storage ** 0.4

        else:
            standby_heat_loss_factor_tethers_heating = 0

        return 1.2 * (50 - self._temp_ambient) / 45 * self._annual_operating_time_water * standby_heat_loss_factor_tethers_heating
        # DIN V 4701-10 formula 5.1.3-1

    def _calc_dissipation_generation_water(self):

        # setting values to None
        boiler_efficiency = None
        expenditure_figure = None

        if self._pipe_routing_water == "decentralised":

            # iwu table 6 and table 7
            if self._heat_system == "gas":
                if self._heat_generation == "circulating water heater":
                    if self.parent.year_of_construction >= 1990:
                        standby_heat_loss_factor_tethers_heating_70_20kw = 0.015
                        boiler_efficiency_70_20kw = 0.92
                else:
                    standby_heat_loss_factor_tethers_heating_70_20kw = 0
                    boiler_efficiency_70_20kw = 0.88  # worst case
            else:
                if self.parent.year_of_construction < 1980:
                    boiler_efficiency = 0.96
                elif self.parent.year_of_construction < 1990:
                    boiler_efficiency = 0.97
                else:
                    boiler_efficiency = 0.98

        elif self._heat_system == "electricity":

            # iwu chapter 2.2
            if self.parent.year_of_construction < 1980:
                if self._heat_generation == "heatpump air":
                    annual_performance_factor_heat_pump = 2
                else:
                    annual_performance_factor_heat_pump = 2.5
            elif self.parent.year_of_construction < 1990:
                if self._heat_generation == "heatpump air":
                    annual_performance_factor_heat_pump = 2.3
                else:
                    annual_performance_factor_heat_pump = 2.8
            else:
                if self._heat_generation == "heatpump air":
                    annual_performance_factor_heat_pump = 2.6
                else:
                    annual_performance_factor_heat_pump = 3.1

            expenditure_figure = 1 / annual_performance_factor_heat_pump

        # iwu table 5
        elif self._heat_system == "district":
            boiler_efficiency = 0.98

        elif self._heat_system == "biomass":
            boiler_efficiency = 0.7

        else:

            if self.parent.year_of_construction < 1990:
                standby_heat_loss_factor_tethers_heating_70_20kw = 0.02
                boiler_efficiency_70_20kw = 0.89

            else:  # assumption: today´s values equal 1990-2000
                standby_heat_loss_factor_tethers_heating_70_20kw = 0.015
                boiler_efficiency_70_20kw = 0.92

        # iwu formula B3
        load_factor_boiler = (12.5 * self.parent.net_leased_area + self._calc_dissipation_distribution_water() +
                              self._calc_dissipation_storage_water()) / (self._nominal_heat_output_boiler * 24 *
                                                                         self._annual_operating_time_water)

        if not self._combined_water_heating:
            operating_time_heating = 0
        else:
            operating_time_heating = self._annual_operating_time_heating

        if self._nominal_heat_output_boiler == 20:
            standby_heat_loss_factor_tethers_heating_70 = standby_heat_loss_factor_tethers_heating_70_20kw
            boiler_efficiency_70 = boiler_efficiency_70_20kw
        else:
            # iwu formula 2-1 and 2-2
            standby_heat_loss_factor_tethers_heating_70 = standby_heat_loss_factor_tethers_heating_70_20kw * 2.456 * self._nominal_heat_output_boiler ** (-0.3)
            boiler_efficiency_70 = boiler_efficiency_70_20kw - 0.0195 + 0.015 * \
                                   math.log10(self._nominal_heat_output_boiler)

        # iwu formula B2
        if self._avg_temp_distribution_heating < 70:
            if self._heat_generation in ["low temperature", "low temperature - not combined"]:
                efficiency_correction = 0.0004 * (70 - self._avg_temp_distribution_heating)
            else:
                if self._heat_system == "oil":
                    efficiency_correction = 0.0016 * (70 - self._avg_temp_distribution_heating)
                else:
                    efficiency_correction = 0.0024 * (70 - self._avg_temp_distribution_heating)
        else:
            efficiency_correction = 0

        avg_standby_heat_loss_factor_tethers_heating = standby_heat_loss_factor_tethers_heating_70 / 50 * (60 - self._temp_ambient)

        if boiler_efficiency and expenditure_figure is None:
            boiler_efficiency = boiler_efficiency_70 + efficiency_correction / (1 + avg_standby_heat_loss_factor_tethers_heating *
                                                                                (1 / load_factor_boiler - 1) * (
                                                                                        1 - operating_time_heating /
                                                                                        self._annual_operating_time_water))

        if expenditure_figure is None:
            # DIN V 4701-10 formula 5.1.4-17
            expenditure_figure = (1 + (1 / load_factor_boiler - 1) * (1 - operating_time_heating /
                                                                      self._annual_operating_time_water) * avg_standby_heat_loss_factor_tethers_heating) / boiler_efficiency

        return expenditure_figure

    def _dissipation_water(self):

        return (12.5 * self.parent.net_leased_area + self._calc_dissipation_distribution_water() +
                self._calc_dissipation_storage_water()) * self._calc_dissipation_generation_water()

    def _calc_dissipation_distribution_auxiliary_water(self):
        # todo vergleichen mit iwu zu Hilfsenergie
        if self._pipe_routing_water == "centralised with circulation":

            # iwu formula 5-23 and 5-24
            if self.parent.year_of_construction < 2016:  # todo Altbau / Neubau Definition
                return (30 + 5 * self.parent.net_leased_area / 100) * self._annual_operating_time_water * \
                       self._daily_operating_time_pump / 1000
            else:
                return (27 + 0.008 * self.parent.net_leased_area) * self._annual_operating_time_water * \
                       self._daily_operating_time_pump / 1000
        else:
            return 0

    def _calc_dissipation_storage_auxiliary_water(self):

        if self._storage_water == "water" or self._storage_water == "solar":

            if self._storage_water == "water":
                # iwu formula 5-20 to 5-22
                return (30 + 5 * self.parent.net_leased_area / 100) * 1.2 * (12.5 * self.parent.net_leased_area +
                                                                             self._calc_dissipation_distribution_water() + self._calc_dissipation_storage_water()) / \
                       self._nominal_heat_output_boiler / 1000
            elif self._storage_water == "solar":
                # iwu formula 5-25 and 5-26
                return (20 + 5 * self.parent.net_leased_area / 100) * 1750 / 1000

        else:
            return 0

    def _calc_dissipation_generation_auxiliary_water(self):

        if self._storage_water == "solar":
            # DIN V 4701-10 table C.1-4e
            auxiliary_energy_demand_solar = 1

        if self._heat_system == "electricity":

            if self._heat_generation in ["heatpump ground", "heatpump ground - no buffer storage"]:
                # DIN V 4701-10 formula 5.1.4-32
                time_pump = (12.5 * self.parent.net_leased_area + self._calc_dissipation_distribution_water() +
                             self._calc_dissipation_storage_water()) / self._nominal_heat_output_boiler

                # DIN V 4701-10 formula 5.1.4-31
                auxiliary_energy_demand_boiler = 1.2 * self.parent.net_leased_area ** 0.9 * time_pump / 1000

            else:
                # DIN V 4701-10 chapter 5.1.4.2.4 and table C.1-4d
                auxiliary_energy_demand_boiler = 0

        elif self._heat_system == "district":
            # DIN V 4701-10 table C.1-4e
            auxiliary_energy_demand_boiler = 0.4

        elif self._heat_system == "circulating water heater":
            # DIN V 4701-10 table C.1-4c
            auxiliary_energy_demand_boiler = 0

        else:
            # iwu formula B3
            load_factor_boiler = (12.5 * self.parent.net_leased_area + self._calc_dissipation_distribution_water() +
                                  self._calc_dissipation_storage_water()) / (self._nominal_heat_output_boiler * 24 *
                                                                             self._annual_operating_time_water)
            # DIN V 4701-10 formula 5.1.4-20 and 5.1.4-29
            auxiliary_energy_demand_boiler = load_factor_boiler + self._annual_operating_time_water * 24 * 0.045 * \
                                             self._nominal_heat_output_boiler ** 0.48

        return (auxiliary_energy_demand_solar + auxiliary_energy_demand_boiler) * self.parent.net_leased_area

    def calc_primary_energy_demand_heating(self):

        # DIN V 18599-1 table A.1
        if self._heat_system in ["gas", "oil"]:
            primary_energy_factor = 1.1
        elif self._heat_system == "electricity":
            primary_energy_factor = 1.8
        elif self._heat_system == "district":
            if self._heat_generation == "gas - high chp":
                primary_energy_factor = 0.7
            elif self._heat_generation == "biomass":
                primary_energy_factor = 0
            else:
                primary_energy_factor = 1.3
        else:
            primary_energy_factor = 0.2
        
        # PE for heating
        if self._heat_generation == "heatpump air":
            # coverage of heat generator from TABULA archetypes
            generator_one = 0.8 * (
                    self._dissipation_heating() + self._calc_dissipation_generation_auxiliary_heating()) + \
                            self._calc_dissipation_distribution_auxiliary_heating() + \
                            self._calc_dissipation_storage_auxiliary_heating()

            # DIN V 4701-10 table C.3-4a
            self._heat_system = "gas"
            self._heat_generation = "condensing"

            generator_two = 0.2 * (self._dissipation_heating() + self._calc_dissipation_generation_auxiliary_heating())

            final_energy_demand_heating = generator_one + generator_two
            primary_energy_demand_heating = generator_one * 1.8 + generator_two * 1.1  # multiplied with PEF

        elif self._heat_generation == "condensing - chp":
            # 0.53  natural gas, condensing, 0.47 chp
            generator_two = 0.47 * (self._dissipation_heating() + self._calc_dissipation_generation_auxiliary_heating())

            # DIN V 4701-10 table C.3-4a
            self._heat_system = "gas"
            self._heat_generation = "condensing"

            generator_one = 0.53 * (
                    self._dissipation_heating() + self._calc_dissipation_generation_auxiliary_heating()) + \
                            self._calc_dissipation_distribution_auxiliary_heating() + \
                            self._calc_dissipation_storage_auxiliary_heating()

            final_energy_demand_heating = generator_one + generator_two
            primary_energy_demand_heating = generator_one * 0.7 + generator_two * 1.1  # multiplied with PEF

        else:
            final_energy_demand_heating = self._dissipation_heating() + \
                                          self._calc_dissipation_generation_auxiliary_heating() + \
                                          self._calc_dissipation_distribution_auxiliary_heating() + \
                                          self._calc_dissipation_storage_auxiliary_heating()

            primary_energy_demand_heating = final_energy_demand_heating * primary_energy_factor

        return primary_energy_demand_heating

    def calc_primary_energy_demand_water(self):

        # DIN V 18599-1 table A.1
        if self._heat_system in ["gas", "oil"]:
            primary_energy_factor = 1.1
        elif self._heat_system == "electricity":
            primary_energy_factor = 1.8
        elif self._heat_system == "district":
            if self._heat_generation == "gas - high chp":
                primary_energy_factor = 0.7
            elif self._heat_generation == "biomass":
                primary_energy_factor = 0
            else:
                primary_energy_factor = 1.3
        else:
            primary_energy_factor = 0.2

        # PE for hot water
        if self._storage_water == "solar":
            # PEF solar = 0
            if type(self.parent).__name__ in ["MultiFamilyHouse", "ApartmentBlock"]:
                # TABULA values
                if self._heat_generation == "chp":
                    part_solar = 0.6
                else:
                    part_solar = 0.4
            else:
                part_solar = 0.6

        if self._heat_generation == "heatpump air":
            # TABULA values
            if self._storage_water == "solar":
                part_generator_one = 1 - part_solar - 0.1
            else:
                part_generator_one = 0.9

            generator_one = part_generator_one * (self._dissipation_water() +
                                                  self._calc_dissipation_generation_auxiliary_water()) + \
                            self._calc_dissipation_distribution_auxiliary_water() + \
                            self._calc_dissipation_storage_auxiliary_water()

            self._heat_system = "gas"
            self._heat_generation = "condensing"

            generator_two = 0.1 * (self._dissipation_water() + self._calc_dissipation_generation_auxiliary_water())

            final_energy_demand_water = generator_one + generator_two
            primary_energy_demand_water = generator_one * 1.8 + generator_two * 1.1  # multiplied with PEF

        elif self._heat_generation == "condensing - chp":
            # TABULA values
            # 0.58 % solar
            generator_two = 0.05 * (self._dissipation_water() +
                                    self._calc_dissipation_generation_auxiliary_water())

            # DIN V 4701-10 table C.3-4a
            self._heat_system = "gas"
            self._heat_generation = "condensing"

            generator_one = 0.37 * (self._dissipation_water() + self._calc_dissipation_generation_auxiliary_water()) + \
                            self._calc_dissipation_distribution_auxiliary_water() + \
                            self._calc_dissipation_storage_auxiliary_water()

            final_energy_demand_water = generator_one + generator_two
            primary_energy_demand_water = generator_one * 0.7 + generator_two * 1.1  # multiplied with PEF

        else:

            if self._storage_water == "solar":
                part_generator = 1 - part_solar
            else:
                part_generator = 1

            final_energy_demand_water = part_generator * (self._dissipation_water() +
                                                          self._calc_dissipation_generation_auxiliary_water()) + \
                                        self._calc_dissipation_distribution_auxiliary_water() + \
                                        self._calc_dissipation_storage_auxiliary_water()

            primary_energy_demand_water = final_energy_demand_water * primary_energy_factor

        return primary_energy_demand_water

    @property
    def parent(self):
        return self.__parent

    @parent.setter
    def parent(self, value):
        from teco.logic.buildingobjects.building import Building
        import inspect
        if inspect.isclass(Building):
            self.__parent = value
            self.__parent.heating_system = self
