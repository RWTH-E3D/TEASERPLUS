# created December 2023
# by Clara Schmitz (master thesis)

"""This module includes a class for the Heat Supply System
"""
# todo Einfügen bei input data?

from teaser.teaser.logic.archetypebuildings.tabula.de.singlefamilyhouse import SingleFamilyHouse as Sfh
from teaser.teaser.logic.archetypebuildings.tabula.de.multifamilyhouse import MultiFamilyHouse as Mfh
from teaser.teaser.logic.archetypebuildings.tabula.de.terracedhouse import TerracedHouse as Th
from teaser.teaser.logic.archetypebuildings.tabula.de.apartmentblock import ApartmentBlock as Ab


class HeatSupplySystem(object):

    """HeatingSystem_PE class

        This class holds information for the Heating System of the Building.
        The materials are being set according to the tabula-de values.

        Parameters
            ----------

            parent: Building()

            Attributes
            ----------

        """

    def __init__(self, parent=None):
        """Constructor of HeatSupplySystem class
        """
        self.parent = parent
        self._year_of_retrofit = self.parent.year_of_retrofit
        self._type_of_retrofit = None
        if "adv_retrofit" in [Sfh.construction_type, Th.construction_type, Mfh.construction_type, Ab.construction_type]:
            self._type_of_retrofit = "adv_retrofit"
        elif "retrofit" in [Sfh.construction_type, Th.construction_type, Mfh.construction_type, Ab.construction_type]:
            self._type_of_retrofit = "retrofit"
        else:
            self._type_of_retrofit = "standard"

        self._length_char = self.parent.get_footprint_gml() / 10  # iwu chapter 4.4.1

        # setting values for generation
        self._heat_system = None
        self._heat_generation = None
        self._storage_water = None
        self._combined_water_heating = True
        self._nominal_heat_output_boiler = None
        self._temp_ambient = 20
        self._annual_operating_time_heating = 350
        self._annual_operating_time_water = 350

        # setting values for distribution
        self._pipe_routing_heating = None
        self._pipe_routing_water = None
        self._design_temp_flow = None
        self._avg_temp_distribution_water = None
        self._avg_temp_distribution_heating = None
        self._oversizing_factor = 1.2  # standard for existing buildings (iwu)
        if self.parent.year_of_construction >= 2016 or self._year_of_retrofit >= 2016:
            self._oversizing_factor = 1
        self._heat_loss_distribution_heating = None
        self._daily_operating_time_pump = None

    def setting_values(self, type_heat_supply_system=None):
        """
        Setting values from TABULA-DE for heating and warm water systems.
        Depending on the type and year of construction and type of retrofit.
        Type of heating system needs to be set.
        If TABULA-values are being used, this function is mandatory to call.

        Calculation of the average temperature of the heat distribution.
        optimised = with hydraulic balancing
        typical = without hydraulic balancing

        Parameters
        ----------
        type_heat_supply_system : int (optional)
            defines ....
            Default one (gas) for existing buildings and 3 (electricity)
            for new buildings
        """
        if type_heat_supply_system in None:
            if self.parent.year_of_construction >= 2016 or self._year_of_retrofit >= 2016:
                type_heat_supply_system = 3  # DENA report 2023 Abb. 41
            else:
                type_heat_supply_system = 1  # DENA report 2023 Abb. 31
        
        if type(self.parent).__name__ in ["SingleFamilyHouse", "TerracedHouse"]:

            if self.parent.year_of_construction <= 1994:

                if self._type_of_retrofit == "standard":

                    if type_heat_supply_system == 1:
                        self._heat_system = "gas"
                        self._heat_generation = "low temperature"
                        self._pipe_routing_water = "centralised with circulation"
                        self._heat_loss_distribution_heating = "high"
                    elif type_heat_supply_system == 2:
                        self._heat_system = "oil"
                        self._heat_generation = "low temperature - not combined"
                        self._heat_loss_distribution_heating = "high"
                    elif type_heat_supply_system == 3:
                        self._heat_system = "electricity"
                        self._heat_generation = "night storage"
                    elif type_heat_supply_system == 4:
                        self._heat_system = "oil"
                        self._heat_generation = "low temperature"
                        self._pipe_routing_water = "centralised with circulation"
                        self._heat_loss_distribution_heating = "high"
                    else:
                        raise ValueError(
                            "type_heat_supply_system has to be a number between"
                            "1 and 3. For SFH or TH older than 1995 1 to 4 and "
                            "for MFH and AB older than 1995 1 to 6 is possible."
                        )

                elif self._type_of_retrofit == "retrofit":

                    if type_heat_supply_system == 1:
                        self._heat_system = "gas"
                        self._heat_generation = "condensing"
                        self._heat_loss_distribution_heating = "good"
                    elif type_heat_supply_system == 2:
                        self._heat_system = "oil"
                        self._heat_generation = "condensing"
                        self._storage_water = "solar"
                        self._heat_loss_distribution_heating = "minimised"
                    elif type_heat_supply_system == 3:
                        self._heat_system = "electricity"
                        self._heat_generation = "heatpump air"
                        self._storage_water = "solar"
                        self._heat_loss_distribution_heating = "good"
                    elif type_heat_supply_system == 4:
                        self._heat_system = "oil"
                        self._heat_generation = "condensing"
                        self._storage_water = "solar"
                        self._heat_loss_distribution_heating = "minimised"
                    else:
                        raise ValueError(
                            "type_heat_supply_system has to be a number between"
                            "1 and 3. For SFH or TH older than 1995 1 to 4 and "
                            "for MFH and AB older than 1995 1 to 6 is possible."
                        )

                elif self._type_of_retrofit == "adv_retrofit":

                    self._heat_loss_distribution_heating = "minimised"
                    if type_heat_supply_system == 1:
                        self._heat_system = "gas"
                        self._heat_generation = "condensing"
                        self._storage_water = "solar"
                        self._pipe_routing_heating = "centralised inside"
                    elif type_heat_supply_system == 2:
                        self._heat_system = "biomass"
                        self._heat_generation = "woodpellets"
                        self._storage_water = "solar"
                    elif type_heat_supply_system == 3:
                        self._heat_system = "electricity"
                        self._heat_generation = "heatpump ground"
                        self._storage_water = "water"
                    elif type_heat_supply_system == 4:
                        self._heat_system = "biomass"
                        self._heat_generation = "woodpellets"
                        self._storage_water = "solar"
                    else:
                        raise ValueError(
                            "type_heat_supply_system has to be a number between"
                            "1 and 3. For SFH or TH older than 1995 1 to 4 and "
                            "for MFH and AB older than 1995 1 to 6 is possible."
                        )

                else:
                    raise ValueError(
                        "Construction_type has to be tabula_standard,"
                        "tabula_retrofit, "
                        "tabula_adv_retrofit"
                    )

            elif self.parent.year_of_construction <= 2009:

                if self._type_of_retrofit == "standard":

                    if type_heat_supply_system == 1:
                        self._heat_system = "gas"
                        self._heat_generation = "condensing"
                        self._heat_loss_distribution_heating = "minimised"
                    elif type_heat_supply_system == 2:
                        self._heat_system = "biomass"
                        self._heat_generation = "woodpellets"
                        self._storage_water = "water"
                        self._pipe_routing_water = "centralised with circulation"
                        self._heat_loss_distribution_heating = "good"
                    elif type_heat_supply_system == 3:
                        self._heat_system = "electricity"
                        self._heat_generation = "heatpump air"
                        self._storage_water = "solar"
                        self._heat_loss_distribution_heating = "good"
                    else:
                        raise ValueError(
                            "type_heat_supply_system has to be a number between"
                            "1 and 3. For SFH or TH older than 1995 1 to 4 and "
                            "for MFH and AB older than 1995 1 to 6 is possible."
                        )

                elif self._type_of_retrofit == "retrofit":

                    self._heat_loss_distribution_heating = "minimised"
                    if type_heat_supply_system == 1:
                        self._heat_system = "gas"
                        self._heat_generation = "condensing"
                        self._storage_water = "solar"
                        self._pipe_routing_water = "centralised with circulation"
                        self._pipe_routing_heating = "centralised inside"
                    elif type_heat_supply_system == 2:
                        self._heat_system = "biomass"
                        self._heat_generation = "woodpellets"
                        self._storage_water = "water"
                        self._pipe_routing_water = "centralised with circulation"
                    elif type_heat_supply_system == 3:
                        self._heat_system = "electricity"
                        self._heat_generation = "heatpump air"
                        self._storage_water = "water"
                        self._pipe_routing_water = "centralised with circulation"
                    else:
                        raise ValueError(
                            "type_heat_supply_system has to be a number between"
                            "1 and 3. For SFH or TH older than 1995 1 to 4 and "
                            "for MFH and AB older than 1995 1 to 6 is possible."
                        )

                elif self._type_of_retrofit == "adv_retrofit":

                    self._heat_loss_distribution_heating = "minimised"
                    if type_heat_supply_system == 1:
                        self._heat_system = "gas"
                        self._heat_generation = "condensing"
                        self._storage_water = "solar"
                        self._pipe_routing_heating = "centralised inside"
                    elif type_heat_supply_system == 2:
                        self._heat_system = "biomass"
                        self._heat_generation = "woodpellets"
                        self._storage_water = "water"
                    elif type_heat_supply_system == 3:
                        self._heat_system = "electricity"
                        self._heat_generation = "heatpump ground"
                        self._storage_water = "water"
                    else:
                        raise ValueError(
                            "type_heat_supply_system has to be a number between"
                            "1 and 3. For SFH or TH older than 1995 1 to 4 and "
                            "for MFH and AB older than 1995 1 to 6 is possible."
                        )

                else:
                    raise ValueError(
                        "Construction_type has to be tabula_standard,"
                        "tabula_retrofit, "
                        "tabula_adv_retrofit"
                    )

            elif self.parent.year_of_construction <= 2015:

                self._heat_loss_distribution_heating = "minimised"
                if self._type_of_retrofit == "standard":

                    if type_heat_supply_system == 1:
                        self._heat_system = "gas"
                        self._heat_generation = "condensing"
                        self._storage_water = "solar"
                        self._pipe_routing_water = "centralised with circulation"
                        self._pipe_routing_heating = "centralised inside"
                    elif type_heat_supply_system == 2:
                        self._heat_system = "biomass"
                        self._heat_generation = "woodpellets"
                        self._storage_water = "water"
                        self._pipe_routing_water = "centralised with circulation"
                    elif type_heat_supply_system == 3:
                        self._heat_system = "electricity"
                        self._heat_generation = "heatpump air"
                        self._storage_water = "water"
                        self._pipe_routing_water = "centralised with circulation"
                    else:
                        raise ValueError(
                            "type_heat_supply_system has to be a number between"
                            "1 and 3. For SFH or TH older than 1995 1 to 4 and "
                            "for MFH and AB older than 1995 1 to 6 is possible."
                        )

                elif self._type_of_retrofit == "retrofit":

                    if type_heat_supply_system == 1:
                        self._heat_system = "gas"
                        self._heat_generation = "condensing"
                        self._storage_water = "solar"
                        self._pipe_routing_heating = "centralised inside"
                    elif type_heat_supply_system == 2:
                        self._heat_system = "biomass"
                        self._heat_generation = "woodpellets"
                        self._storage_water = "water"
                    elif type_heat_supply_system == 3:
                        self._heat_system = "electricity"
                        self._heat_generation = "heatpump ground - no buffer storage"
                        self._storage_water = "water"
                    else:
                        raise ValueError(
                            "type_heat_supply_system has to be a number between"
                            "1 and 3. For SFH or TH older than 1995 1 to 4 and "
                            "for MFH and AB older than 1995 1 to 6 is possible."
                        )

                elif self._type_of_retrofit == "adv_retrofit":

                    if type_heat_supply_system == 1:
                        self._heat_system = "gas"
                        self._heat_generation = "condensing"
                        self._storage_water = "solar"
                        self._pipe_routing_heating = "centralised inside"
                    elif type_heat_supply_system == 2:
                        self._heat_system = "biomass"
                        self._heat_generation = "woodpellets"
                        self._storage_water = "solar"
                    elif type_heat_supply_system == 3:
                        self._heat_system = "electricity"
                        self._heat_generation = "heatpump ground - no buffer storage"
                        self._storage_water = "water"
                    else:
                        raise ValueError(
                            "type_heat_supply_system has to be a number between"
                            "1 and 3. For SFH or TH older than 1995 1 to 4 and "
                            "for MFH and AB older than 1995 1 to 6 is possible."
                        )

                else:
                    raise ValueError(
                        "Construction_type has to be tabula_standard,"
                        "tabula_retrofit, "
                        "tabula_adv_retrofit"
                    )

            else:

                self._heat_loss_distribution_heating = "minimised"
                if self._type_of_retrofit == "standard":

                    if type_heat_supply_system == 1:
                        self._heat_system = "gas"
                        self._heat_generation = "condensing"
                        self._storage_water = "solar"
                        self._pipe_routing_heating = "centralised inside"
                    elif type_heat_supply_system == 2:
                        self._heat_system = "biomass"
                        self._heat_generation = "woodpellets"
                        self._storage_water = "water"
                        self._pipe_routing_water = "centralised with circulation"
                    elif type_heat_supply_system == 3:
                        self._heat_system = "electricity"
                        self._heat_generation = "heatpump ground - no buffer storage"
                        self._storage_water = "water"
                    else:
                        raise ValueError(
                            "type_heat_supply_system has to be a number between"
                            "1 and 3. For SFH or TH older than 1995 1 to 4 and "
                            "for MFH and AB older than 1995 1 to 6 is possible."
                        )

                elif self._type_of_retrofit == "retrofit":

                    if type_heat_supply_system == 1:
                        self._heat_system = "gas"
                        self._heat_generation = "condensing"
                        self._storage_water = "solar"
                        self._pipe_routing_heating = "centralised inside"
                    elif type_heat_supply_system == 2:
                        self._heat_system = "biomass"
                        self._heat_generation = "woodpellets"
                        self._storage_water = "water"
                    elif type_heat_supply_system == 3:
                        self._heat_system = "electricity"
                        self._heat_generation = "heatpump ground - no buffer storage"
                        self._storage_water = "water"
                    else:
                        raise ValueError(
                            "type_heat_supply_system has to be a number between"
                            "1 and 3. For SFH or TH older than 1995 1 to 4 and "
                            "for MFH and AB older than 1995 1 to 6 is possible."
                        )

                elif self._type_of_retrofit == "adv_retrofit":

                    if type_heat_supply_system == 1:
                        self._heat_system = "gas"
                        self._heat_generation = "condensing"
                        self._storage_water = "solar"
                        self._pipe_routing_heating = "centralised inside"
                    elif type_heat_supply_system == 2:
                        self._heat_system = "biomass"
                        self._heat_generation = "woodpellets"
                        self._storage_water = "solar"
                    elif type_heat_supply_system == 3:
                        self._heat_system = "electricity"
                        self._heat_generation = "heatpump ground - no buffer storage"
                        self._storage_water = "water"
                    else:
                        raise ValueError(
                            "type_heat_supply_system has to be a number between"
                            "1 and 3. For SFH or TH older than 1995 1 to 4 and "
                            "for MFH and AB older than 1995 1 to 6 is possible."
                        )

                else:
                    raise ValueError(
                        "Construction_type has to be tabula_standard,"
                        "tabula_retrofit, "
                        "tabula_adv_retrofit"
                    )

        elif type(self.parent).__name__ in ["MultiFamilyHouse", "ApartmentBlock"]:

            if self.parent.year_of_construction <= 1994:

                if self._type_of_retrofit == "standard":

                    self._heat_loss_distribution_heating = "high"
                    if type_heat_supply_system == 1:
                        self._heat_system = "gas"
                        self._heat_generation = "low temperature"
                        self._storage_water = "water"
                    elif type_heat_supply_system == 2:
                        self._heat_system = "oil"
                        self._heat_generation = "low temperature - not combined"
                    elif type_heat_supply_system == 3:
                        self._heat_system = "electricity"
                        self._heat_generation = "night storage"
                    elif type_heat_supply_system == 4:
                        self._heat_system = "district"
                        self._heat_generation = "gas - no chp"
                    elif type_heat_supply_system == 5:
                        self._heat_system = "gas"
                        self._heat_generation = "circulating water heater"
                    elif type_heat_supply_system == 6:
                        self._heat_system = "oil"
                        self._heat_generation = "low temperature"
                        self._storage_water = "water"
                    else:
                        raise ValueError(
                            "type_heat_supply_system has to be a number between"
                            "1 and 3. For SFH or TH older than 1995 1 to 4 and "
                            "for MFH and AB older than 1995 1 to 6 is possible."
                        )

                elif self._type_of_retrofit == "retrofit":

                    if type_heat_supply_system == 1:
                        self._heat_system = "gas"
                        self._heat_generation = "condensing"
                        self._storage_water = "water"
                        self._heat_loss_distribution_heating = "small"
                    elif type_heat_supply_system == 2:
                        self._heat_system = "oil"
                        self._heat_generation = "condensing"
                        self._storage_water = "solar"
                        self._heat_loss_distribution_heating = "minimised"
                    elif type_heat_supply_system == 3:
                        self._heat_system = "gas"
                        self._heat_generation = "condensing - decentralised"
                        self._heat_loss_distribution_heating = "small"
                    elif type_heat_supply_system == 4:
                        self._heat_system = "district"
                        self._heat_generation = "gas - high chp"
                        self._heat_loss_distribution_heating = "small"
                    elif type_heat_supply_system == 5:
                        self._heat_system = "gas"
                        self._heat_generation = "condensing - decentralised"
                        self._heat_loss_distribution_heating = "small"
                    elif type_heat_supply_system == 6:
                        self._heat_system = "oil"
                        self._heat_generation = "condensing"
                        self._storage_water = "solar"
                        self._heat_loss_distribution_heating = "minimised"
                    else:
                        raise ValueError(
                            "type_heat_supply_system has to be a number between"
                            "1 and 3. For SFH or TH older than 1995 1 to 4 and "
                            "for MFH and AB older than 1995 1 to 6 is possible."
                        )

                elif self._type_of_retrofit == "adv_retrofit":

                    self._heat_loss_distribution_heating = "small"
                    if type_heat_supply_system == 1:
                        self._heat_system = "gas"
                        self._heat_generation = "condensing"
                        self._storage_water = "solar"
                    elif type_heat_supply_system == 2:
                        self._heat_system = "biomass"
                        self._heat_generation = "woodpellets"
                        self._storage_water = "solar"
                    elif type_heat_supply_system == 3:
                        self._heat_system = "biomass"
                        self._heat_generation = "woodpellets"
                        self._storage_water = "water"
                    elif type_heat_supply_system == 4:
                        self._heat_system = "district"
                        self._heat_generation = "biomass"
                    elif type_heat_supply_system == 5:
                        self._heat_system = "gas"
                        self._heat_generation = "condensing - decentralised"
                    elif type_heat_supply_system == 6:
                        self._heat_system = "biomass"
                        self._heat_generation = "woodpellets"
                        self._storage_water = "solar"
                    else:
                        raise ValueError(
                            "type_heat_supply_system has to be a number between"
                            "1 and 3. For SFH or TH older than 1995 1 to 4 and "
                            "for MFH and AB older than 1995 1 to 6 is possible."
                        )

                else:
                    raise ValueError(
                        "Construction_type has to be tabula_standard,"
                        "tabula_retrofit, "
                        "tabula_adv_retrofit"
                    )

            elif self.parent.year_of_construction <= 2009:

                if self._type_of_retrofit == "standard":

                    self._heat_loss_distribution_heating = "small"
                    if type_heat_supply_system == 1:
                        self._heat_system = "gas"
                        self._heat_generation = "condensing"
                        self._storage_water = "water"
                    elif type_heat_supply_system == 2:
                        self._heat_system = "biomass"
                        self._heat_generation = "woodpellets"
                        self._storage_water = "water"
                    elif type_heat_supply_system == 3:
                        self._heat_system = "electricity"
                        self._heat_generation = "heatpump air"
                        self._storage_water = "water"
                    else:
                        raise ValueError(
                            "type_heat_supply_system has to be a number between"
                            "1 and 3. For SFH or TH older than 1995 1 to 4 and "
                            "for MFH and AB older than 1995 1 to 6 is possible."
                        )

                elif self._type_of_retrofit == "retrofit":

                    if type_heat_supply_system == 1:
                        self._heat_system = "gas"
                        self._heat_generation = "condensing"
                        self._storage_water = "solar"
                        self._heat_loss_distribution_heating = "minimised"
                    elif type_heat_supply_system == 2:
                        self._heat_system = "biomass"
                        self._heat_generation = "woodpellets"
                        self._storage_water = "water"
                        self._heat_loss_distribution_heating = "minimised"
                    elif type_heat_supply_system == 3:
                        self._heat_system = "electricity"
                        self._heat_generation = "heatpump air"
                        self._storage_water = "water"
                        self._heat_loss_distribution_heating = "small"
                    else:
                        raise ValueError(
                            "type_heat_supply_system has to be a number between"
                            "1 and 3. For SFH or TH older than 1995 1 to 4 and "
                            "for MFH and AB older than 1995 1 to 6 is possible."
                        )

                elif self._type_of_retrofit == "adv_retrofit":

                    self._heat_loss_distribution_heating = "minimised"
                    if type_heat_supply_system == 1:
                        self._heat_system = "gas"
                        self._heat_generation = "condensing"
                        self._storage_water = "solar"
                    elif type_heat_supply_system == 2:
                        self._heat_system = "biomass"
                        self._heat_generation = "woodpellets"
                        self._storage_water = "water"
                    elif type_heat_supply_system == 3:
                        self._heat_system = "electricity"
                        self._heat_generation = "heatpump ground"
                        self._storage_water = "water"
                    else:
                        raise ValueError(
                            "type_heat_supply_system has to be a number between"
                            "1 and 3. For SFH or TH older than 1995 1 to 4 and "
                            "for MFH and AB older than 1995 1 to 6 is possible."
                        )

                else:
                    raise ValueError(
                        "Construction_type has to be tabula_standard,"
                        "tabula_retrofit, "
                        "tabula_adv_retrofit"
                    )

            elif self.parent.year_of_construction <= 2015:

                if self._type_of_retrofit == "standard":

                    if type_heat_supply_system == 1:
                        self._heat_system = "gas"
                        self._heat_generation = "condensing"
                        self._storage_water = "solar"
                        self._heat_loss_distribution_heating = "minimised"
                    elif type_heat_supply_system == 2:
                        self._heat_system = "biomass"
                        self._heat_generation = "woodpellets"
                        self._storage_water = "water"
                        self._heat_loss_distribution_heating = "minimised"
                    elif type_heat_supply_system == 3:
                        self._heat_system = "electricity"
                        self._heat_generation = "heatpump air"
                        self._storage_water = "water"
                        self._heat_loss_distribution_heating = "small"
                    else:
                        raise ValueError(
                            "type_heat_supply_system has to be a number between"
                            "1 and 3. For SFH or TH older than 1995 1 to 4 and "
                            "for MFH and AB older than 1995 1 to 6 is possible."
                        )

                elif self._type_of_retrofit == "retrofit":

                    self._heat_loss_distribution_heating = "minimised"
                    if type_heat_supply_system == 1:
                        self._heat_system = "gas"
                        self._heat_generation = "condensing"
                        self._storage_water = "solar"
                    elif type_heat_supply_system == 2:
                        self._heat_system = "biomass"
                        self._heat_generation = "woodpellets"
                        self._storage_water = "water"
                    elif type_heat_supply_system == 3:
                        self._heat_system = "electricity"
                        self._heat_generation = "heatpump ground"
                        self._storage_water = "water"
                    else:
                        raise ValueError(
                            "type_heat_supply_system has to be a number between"
                            "1 and 3. For SFH or TH older than 1995 1 to 4 and "
                            "for MFH and AB older than 1995 1 to 6 is possible."
                        )

                elif self._type_of_retrofit == "adv_retrofit":

                    self._heat_loss_distribution_heating = "minimised"
                    if type_heat_supply_system == 1:
                        self._heat_system = "gas"
                        self._heat_generation = "condensing - chp"
                        self._storage_water = "solar"
                    elif type_heat_supply_system == 2:
                        self._heat_system = "biomass"
                        self._heat_generation = "chp"
                        self._storage_water = "solar"
                    elif type_heat_supply_system == 3:
                        self._heat_system = "electricity"
                        self._heat_generation = "heatpump ground"
                        self._storage_water = "water"
                    else:
                        raise ValueError(
                            "type_heat_supply_system has to be a number between"
                            "1 and 3. For SFH or TH older than 1995 1 to 4 and "
                            "for MFH and AB older than 1995 1 to 6 is possible."
                        )

                else:
                    raise ValueError(
                        "Construction_type has to be tabula_standard,"
                        "tabula_retrofit, "
                        "tabula_adv_retrofit"
                    )

            else:

                self._heat_loss_distribution_heating = "minimised"
                if self._type_of_retrofit == "standard":

                    if type_heat_supply_system == 1:
                        self._heat_system = "gas"
                        self._heat_generation = "condensing"
                        self._storage_water = "solar"
                    elif type_heat_supply_system == 2:
                        self._heat_system = "biomass"
                        self._heat_generation = "woodpellets"
                        self._storage_water = "water"
                    elif type_heat_supply_system == 3:
                        self._heat_system = "electricity"
                        self._heat_generation = "heatpump ground"
                        self._storage_water = "water"
                    else:
                        raise ValueError(
                            "type_heat_supply_system has to be a number between"
                            "1 and 3. For SFH or TH older than 1995 1 to 4 and "
                            "for MFH and AB older than 1995 1 to 6 is possible."
                        )

                elif self._type_of_retrofit == "retrofit":

                    if type_heat_supply_system == 1:
                        self._heat_system = "gas"
                        self._heat_generation = "condensing"
                        self._storage_water = "solar"
                    elif type_heat_supply_system == 2:
                        self._heat_system = "biomass"
                        self._heat_generation = "woodpellets"
                        self._storage_water = "water"
                    elif type_heat_supply_system == 3:
                        self._heat_system = "electricity"
                        self._heat_generation = "heatpump ground"
                        self._storage_water = "water"
                    else:
                        raise ValueError(
                            "type_heat_supply_system has to be a number between"
                            "1 and 3. For SFH or TH older than 1995 1 to 4 and "
                            "for MFH and AB older than 1995 1 to 6 is possible."
                        )

                elif self._type_of_retrofit == "adv_retrofit":

                    if type_heat_supply_system == 1:
                        self._heat_system = "gas"
                        self._heat_generation = "condensing - chp"
                        self._storage_water = "solar"
                    elif type_heat_supply_system == 2:
                        self._heat_system = "biomass"
                        self._heat_generation = "chp"
                        self._storage_water = "solar"
                    elif type_heat_supply_system == 3:
                        self._heat_system = "electricity"
                        self._heat_generation = "heatpump ground"
                        self._storage_water = "water"
                    else:
                        raise ValueError(
                            "type_heat_supply_system has to be a number between"
                            "1 and 3. For SFH or TH older than 1995 1 to 4 and "
                            "for MFH and AB older than 1995 1 to 6 is possible."
                        )

                else:
                    raise ValueError(
                        "Construction_type has to be tabula_standard,"
                        "tabula_retrofit, "
                        "tabula_adv_retrofit"
                    )

        if self._heat_generation in ["night storage", "low temperature - not combined"]:
            self._combined_water_heating = False

        if self._pipe_routing_heating is None:
            if (self._heat_system == "gas" and
                (self._heat_generation in ["circulating water heater", "condensing - decentralised"])) or \
                    (self._heat_system == "electricity" and self._heat_generation == "night storage"):
                self._pipe_routing_heating = "decentralised"
            else:
                self._pipe_routing_heating = "centralised outside"

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

        self._setting_derived_values()

    def _setting_derived_values(self):

        # todo definieren anhand NGF und Heizkörper
        if self._heat_generation in ["low temperature", "low temperature-not combined"]:
            self._design_temp_flow = 70
        elif self._heat_generation in ["heatpump ground", "heatpump ground - no buffer storage", "heatpump air"]:
            self._design_temp_flow = 35
        else:
            self._design_temp_flow = 55

        # iwu formula 4-4
        if self.parent.net_leased_area < 10000:
            self._daily_operating_time_pump = 7.5 + 1 / (0.06 + 7 / self.parent.net_leased_area)
        else:
            self._daily_operating_time_pump = 24

        # iwu formula 2-3, rounded to 5 [kW] # todo check, ob simulated_heat_load in kW
        if (5 * round(self._oversizing_factor * self.parent.simulated_heat_load / 5)) < 15 or None:
            self._nominal_heat_output_boiler = 15
        else:
            self._nominal_heat_output_boiler = 5 * \
                                               round(self._oversizing_factor * self.parent.simulated_heat_load / 5)

        # calculation of the average temperature of the water distribution
        # iwu chapter 1.2.2
        if self._pipe_routing_water == "centralised with circulation":
            self._avg_temp_distribution_water = 50

        elif self._pipe_routing_water in ["centralised without circulation", "decentralised"]:
            self._avg_temp_distribution_water = 32

        # todo 35 Grad VL integrieren
        # calculation of the average temperature of the heating distribution
        # iwu table 1
        if self.parent.net_leased_area / 100 >= 10:  # todo ">= 6" after September 2024
            # heating mode "optimised": hydraulic balancing
            if self._design_temp_flow == 90:

                if self._oversizing_factor == 1.0:
                    self._avg_temp_distribution_heating = 54
                elif self._oversizing_factor == 1.2:
                    self._avg_temp_distribution_heating = 50

            elif self._design_temp_flow == 70:

                if self._oversizing_factor == 1.0:
                    self._avg_temp_distribution_heating = 44
                elif self._oversizing_factor == 1.2:
                    self._avg_temp_distribution_heating = 41

            elif self._design_temp_flow == 55:

                if self._oversizing_factor == 1.0:
                    self._avg_temp_distribution_heating = 37
                elif self._oversizing_factor == 1.2:
                    self._avg_temp_distribution_heating = 35

        else:
            # heating_mode "typical": no hydraulic balancing
            if self._design_temp_flow == 90:

                if self._oversizing_factor == 1.0:
                    self._avg_temp_distribution_heating = 66
                elif self._oversizing_factor == 1.2:
                    self._avg_temp_distribution_heating = 63

            elif self._design_temp_flow == 70:

                if self._oversizing_factor == 1.0:
                    self._avg_temp_distribution_heating = 53
                elif self._oversizing_factor == 1.2:
                    self._avg_temp_distribution_heating = 50

            elif self._design_temp_flow == 55:

                if self._oversizing_factor == 1.0:
                    self._avg_temp_distribution_heating = 43
                elif self._oversizing_factor == 1.2:
                    self._avg_temp_distribution_heating = 41

    def retrofit_heat_supply_system(self, year_of_retrofit, type_of_retrofit=None, type_heat_supply_system=None):
        """Retrofits all parameters in the system.

        Function call for all elements facing the ambient or ground.
        Distinguishes if the parent building is a archetype of type 'iwu' or
        'tabula_de'. If TABULA is used, it will use the pre-defined wall
        constructions of TABULA.

        Parameters
        ----------
        year_of_retrofit : int
            Year of last retrofit
        type_of_retrofit : str
            The classification of retrofit, if the archetype building
            approach of TABULA is used.
        type_heat_supply_system: int
            Type of the heat supply system
        """

        if year_of_retrofit < 1995:
            self._year_of_retrofit = 1995
            raise ValueError("You are using a year of retrofit not supported\
                    by teaser. We will change your year of retrofit to 1995\
                    for the calculation. Be careful!")

        if type_of_retrofit in ["adv_retrofit", "retrofit", "standard", "tabula_adv_retrofit", "tabula_retrofit", 
                                "tabula_standard"]:
            self._type_of_retrofit = type_of_retrofit
        else:
            raise ValueError("You are using a type of retrofit not supported\
                                by teaser. We will change your type of retrofit \
                                to the next highest type. Be careful!")
            if self._type_of_retrofit == "adv_retrofit":
                raise ValueError("already highest available standard of heat_supply_system")
                self._type_of_retrofit = "adv_retrofit"
            elif self._type_of_retrofit == "retrofit":
                self._type_of_retrofit = "adv_retrofit"
            else:
                self._type_of_retrofit = "retrofit"

        self.setting_values(type_heat_supply_system)


    """def load_type_element(
            self,
            year,
            construction,
            data_class=None):
        ""Typical element loader.

        Loads typical building elements according to their construction
        year and their construction type from a json.

        This function will only work if the parents to Building are set.

        Parameters
        ----------
        year : int
            Year of construction

        construction : str
            Construction type, code list ('heavy', 'light')

        data_class : DataClass()
            DataClass containing the bindings for TypeBuildingElement and
            Material (typically this is the data class stored in prj.data,
            but the user can individually change that. Default is
            self.parent.parent.parent.data (which is data_class in current
            project)

        ""

        if data_class is None:
            data_class = self.parent.parent.parent.data
        else:
            data_class = data_class

        self.layer = None
        self._inner_convection = None
        self._inner_radiation = None
        self._outer_convection = None
        self._outer_radiation = None

        buildingelement_input.load_type_element(element=self,
                                                year=year,
                                                construction=construction,
                                                data_class=data_class)

    def save_type_element(self, data_class=None):
        ""Typical element saver.

        Saves typical building elements according to their construction
        year and their construction type in the json file for type building
        elements. If the Project parent is set, it automatically saves it to
        the file given in Project.data. Alternatively you can specify a path to
        a file of TypeBuildingElements. If this file does not exist,
        a new file is created.

        Parameters
        ----------

        data_class : DataClass()
            DataClass containing the bindings for TypeBuildingElement and
            Material (typically this is the data class stored in prj.data,
            but the user can individually change that. Default is
            self.parent.parent.parent.data (which is data_class in current
            project)

        ""

        if data_class is None:
            data_class = self.parent.parent.parent.data
        else:
            data_class = data_class

        import teaser.teaser.data.output.buildingelement_output as \
            buildingelement_output

        buildingelement_output.save_type_element(element=self,
                                                 data_class=data_class)

    def delete_type_element(self, data_class=None):
        ""Deletes typical element.

        Deletes typical building elements according to their construction
        year and their construction type in the json file for type building
        elements. If the Project parent is set, it automatically saves it to
        the file given in Project.data. Alternatively you can specify a path to
        a file of TypeBuildingElements. If this file does not exist,
        a new file is created.

        Parameters
        ----------

        data_class : DataClass()
            DataClass containing the bindings for TypeBuildingElement and
            Material (typically this is the data class stored in prj.data,
            but the user can individually change that. Default is
            self.parent.parent.parent.data (which is data_class in current
            project)

        ""

        if data_class is None:
            data_class = self.parent.parent.parent.data
        else:
            data_class = data_class

        import teaser.teaser.data.output.buildingelement_output as \
            buildingelement_output

        buildingelement_output.delete_type_element(element=self,
                                                   data_class=data_class)"""

    """
    def delete(self):
        ""Deletes the actual thermal zone safely.

        This deletes the current thermal Zone and also refreshes the
        thermal_zones list in the parent Building.
        ""
        for index, tz in enumerate(self.parent.thermal_zones):
            if tz.internal_id == self.internal_id:
                self.parent.net_leased_area -= self.area
                self.parent.thermal_zones.pop(index)

                break"""

    """@property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if isinstance(value, str):

            if value:
                regex = re.compile('[^a-zA-z0-9]')
                self._name = regex.sub('', value)
                if self._name == "None":
                    self._name = "BuildinElement" + str(
                        random.randint(1, 500000))
        elif value is None:
            self._value = "BuildinElement" + str(random.randint(1, 500000))
        else:
            try:
                value = str(value)
                regex = re.compile('[^a-zA-z0-9]')
                self._name = regex.sub('', value)
            except ValueError:
                print("Can't convert name to string")

    @property
    def year_of_retrofit(self):
        return self._year_of_retrofit

    @year_of_retrofit.setter
    def year_of_retrofit(self, value):

        if isinstance(value, int):
            pass
        elif value is None:
            pass
        else:
            try:
                value = int(value)
            except:
                raise ValueError("Can't convert year of retrofit to float")

        if value is not None:
            if self.year_of_construction is not None:
                self._year_of_retrofit = value
            else:
                raise ValueError("Specify year of construction first")
                
    @property
    def year_of_construction(self):
        return self._year_of_construction

    @year_of_construction.setter
    def year_of_construction(self, value):

        if isinstance(value, float):
            self._year_of_construction = value
        elif value is None:
            self._year_of_construction = value
        else:
            try:
                value = int(value)
                self._year_of_construction = value
            except:
                raise ValueError("Can't convert year to int")

    @property
    def construction_type(self):
        return self._construction_type

    @construction_type.setter
    def construction_type(self, value):

        self._construction_type = value
        
    @property
    def use_conditions(self):
        return self._use_conditions

    @use_conditions.setter
    def use_conditions(self, value):
        ass_error_1 = "Use condition has to be an instance of UseConditions()"

        assert type(value).__name__ == "UseConditions", ass_error_1

        if value is not None:
            self._use_conditions = value
            self.typical_length = value.typical_length
            self.typical_width = value.typical_width
        self._use_conditions = value
"""

    @property
    def parent(self):
        return self.__parent

    @parent.setter
    def parent(self, value):
        from teco.logic.buildingobjects.building import Building
        import inspect
        if inspect.isclass(Building):
            self.__parent = value
            self.__parent.building = self

    @property
    def length_char(self):
        return self._length_char

    @length_char.setter
    def length_char(self, value):

        if isinstance(value, float):
            self._length_char = value
        elif value is None:
            self._length_char = value
        else:
            try:
                value = float(value)
                self._length_char = value
            except:
                raise ValueError("Can't convert length_char to float")

    @property
    def heat_system(self):
        return self._heat_system

    @heat_system.setter
    def heat_system(self, value):

        if value in ["gas", "oil", "electricity", "biomass", "district"]:
            self._heat_system = value
        else:
            raise ValueError("heat_system no defined value")

    @property
    def heat_generation(self):
        return self._heat_generation

    @heat_generation.setter
    def heat_generation(self, value):

        if value in ["low temperature", "condensing", "condensing - decentralised", "condensing - chp",
                     "circulating water heater", "low temperature - not combined", "night storage", "heatpump air",
                     "heatpump ground", "heatpump ground - no buffer storage", "woodpellets", "chp", "gas - no chp",
                     "gas - high chp", "biomass"]:
            self._heat_generation = value
        else:
            raise ValueError("heat_generation no defined value")

    @property
    def storage_water(self):
        return self._storage_water

    @storage_water.setter
    def storage_water(self, value):

        if value in ["water", "solar"]:
            self._storage_water = value
        elif value is None:
            self._storage_water = value
        else:
            raise ValueError("storage_water no defined value")

    @property
    def combined_water_heating(self):
        return self._combined_water_heating

    @combined_water_heating.setter
    def combined_water_heating(self, value):

        if isinstance(value, bool):
            self._combined_water_heating = value
        else:
            try:
                value = bool(value)
                self._combined_water_heating = value
            except:
                raise ValueError("Can't convert combined_water_heating to boolean")

    @property
    def nominal_heat_output_boiler(self):
        return self._nominal_heat_output_boiler

    @nominal_heat_output_boiler.setter
    def nominal_heat_output_boiler(self, value):

        if isinstance(value, float):
            self._nominal_heat_output_boiler = value
        elif value is None:
            self._nominal_heat_output_boiler = value
        else:
            try:
                value = float(value)
                self._nominal_heat_output_boiler = value
            except:
                raise ValueError("Can't convert nominal_heat_output_boiler to float")

    @property
    def temp_ambient(self):
        return self._temp_ambient

    @temp_ambient.setter
    def temp_ambient(self, value):

        if isinstance(value, float):
            self._temp_ambient = value
        else:
            try:
                value = float(value)
                self._temp_ambient = value
            except:
                raise ValueError("Can't convert temp_ambient to float")

    @property
    def annual_operating_time_heating(self):
        return self._annual_operating_time_heating

    @annual_operating_time_heating.setter
    def annual_operating_time_heating(self, value):

        if isinstance(value, int):
            self._annual_operating_time_heating = value
        elif value is None:
            self._annual_operating_time_heating = value
        else:
            try:
                value = int(value)
                self._annual_operating_time_heating = value
            except:
                raise ValueError("Can't convert annual_operating_time_heating to integer")

    @property
    def annual_operating_time_water(self):
        return self._annual_operating_time_water

    @annual_operating_time_water.setter
    def annual_operating_time_water(self, value):

        if isinstance(value, int):
            self._annual_operating_time_water = value
        elif value is None:
            self._annual_operating_time_water = value
        else:
            try:
                value = int(value)
                self._annual_operating_time_water = value
            except:
                raise ValueError("Can't convert annual_operating_time_water to integer")

    @property
    def pipe_routing_heating(self):
        return self._pipe_routing_heating

    @pipe_routing_heating.setter
    def pipe_routing_heating(self, value):

        if value in ["centralised outside", "centralised inside", "decentralised"]:
            self._pipe_routing_heating = value
        else:
            raise ValueError("pipe_routing_heating no defined value")

    @property
    def pipe_routing_water(self):
        return self._pipe_routing_water

    @pipe_routing_water.setter
    def pipe_routing_water(self, value):

        if value in ["centralised with circulation", "centralised without circulation", "decentralised"]:
            self._pipe_routing_water = value
        else:
            raise ValueError("pipe_routing_water no defined value")

    @property
    def design_temp_flow(self):
        return self._design_temp_flow

    @design_temp_flow.setter
    def design_temp_flow(self, value):

        if value in [90, 70, 55, 35]:
            self._design_temp_flow = value
        else:
            raise ValueError("design_temp_flow no defined value")

    @property
    def avg_temp_distribution_water(self):
        return self._avg_temp_distribution_water

    @avg_temp_distribution_water.setter
    def avg_temp_distribution_water(self, value):

        if isinstance(value, float):
            self._avg_temp_distribution_water = value
        elif value is None:
            self._avg_temp_distribution_water = value
        else:
            try:
                value = float(value)
                self._avg_temp_distribution_water = value
            except:
                raise ValueError("Can't convert avg_temp_distribution_water to float")

    @property
    def avg_temp_distribution_heating(self):
        return self._avg_temp_distribution_heating

    @avg_temp_distribution_heating.setter
    def avg_temp_distribution_heating(self, value):

        if isinstance(value, float):
            self._avg_temp_distribution_heating = value
        elif value is None:
            self._avg_temp_distribution_heating = value
        else:
            try:
                value = float(value)
                self._avg_temp_distribution_heating = value
            except:
                raise ValueError("Can't convert avg_temp_distribution_heating to float")

    @property
    def oversizing_factor(self):
        return self._oversizing_factor

    @oversizing_factor.setter
    def oversizing_factor(self, value):

        if isinstance(value, float):
            self._oversizing_factor = value
        else:
            try:
                value = float(value)
                self._oversizing_factor = value
            except:
                raise ValueError("Can't convert oversizing_factor to float")

    @property
    def heat_loss_distribution_heating(self):
        return self._heat_loss_distribution_heating

    @heat_loss_distribution_heating.setter
    def heat_loss_distribution_heating(self, value):

        if value in ["minimised", "small", "high"]:
            self._heat_loss_distribution_heating = value
        else:
            raise ValueError("heat_loss_distribution_heating no defined value")

    @property
    def daily_operating_time_pump(self):
        return self._daily_operating_time_pump

    @daily_operating_time_pump.setter
    def daily_operating_time_pump(self, value):

        if isinstance(value, float):
            self._daily_operating_time_pump = value
        else:
            try:
                value = float(value)
                self._daily_operating_time_pump = value
            except:
                raise ValueError("Can't convert daily_operating_time_pump to float")
