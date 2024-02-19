# created December 2023
# by Clara Schmitz (master thesis)

"""This module includes a class for the Heat Supply System
"""
import math

class HeatSupplySystem(object):

    """HeatSupplySystem class

    This class holds information for the Heat Supply System of a Building.
    The characteristics are being set according to tabula values. This class
    sets the parameter needed for the LCA final energy demand calculation.

    Parameters
        ----------

    parent: Building()
        The parent class of this object, the Building the heat supply system
        belongs to. Allows for better control of hierarchical structures. If
        not None it adds this HeatSupplySystem instance to Building.HeatSupplySystem.
        Default is None

    Attributes
    ----------
    building_type : str
        Checks TABULA type of the building and if this is none, it refers to
        building area / number of residential units.
        values: "sfh" for TerracedHouse and SingleFamilyHouse, "mfh" for
        ApartmentBlock and MultiFamilyHouse.
    usable_area : float [m^2]
        Usable area of the building. Depentent on the heated volume or the
        living area.
    length_char : float [m]
        Characteristic length of the building. Dependent on the footprint of the
        building.
    n_res_units : int [-]
        Number of residential units in the building. Dependent on the living
        area.
    heat_load : float [kW]
        Equals simulated_heat_load of building class. If this is none, it
        is calculated as a function of the area.
    nominal_heat_output_boiler_heating : int [kW]
        Dependent on oversizing_factor and heat_load.
    nominal_heat_output_boiler_water : int [kW]
        Dependent on number of residential units.
    year_of_retrofit : int [a]
        Equals year of retrofit of building class. If this is none, it is 1.
    heat_system : str
        Contains information on which supply system is assigned (e.g. gas /
        oil / electricity...). Dependent on _type_heat_supply_system.
    heat_generation : str
        Contains information on which heat generator is assigned.
    storage : str
        Contains information on whether the supply system has a storage
        and if so, which one (solar/water).
    combined_water_heating : bool
        Contains information on whether the warm water and heating system
        use one common generator.
    temp_ambient : int [degC]
        Holds the surrounding temperature of the heat system.
    annual_operating_time_heating : int [d/a]
        Contains information on how many days per year the heating system
        is used.
    annual_operating_time_water : int [d/a]
        Contains information on how many days per year the water system
        is used.
    pipe_routing_heating : str
        Contains information on how the pipes of the heating system run.
    pipe_routing_water : str
        Contains information on how the pipes of the warm water system run.
    design_temp_flow : int [degC]
        Holds the design temperature flow of the heat supply system.
        Default is 70.
    avg_temp_distribution_water : float [degC]
        Holds the average temperature of the distribution of warm water.
    avg_temp_distribution_heating : float [degC]
        Holds the average temperature of the distribution of heating.
    oversizing_factor : float [-]
        This value is set to 1.2 for existing buildings and 1.0 for new
        buildings. The heat supply system of existing buildings is often
        overdimensioned due to changes in use.
    heat_loss_distribution_heating : str
        Contains information on how the pipes are insulated.
    daily_operating_time_pump : float [h/d]
        Holds how many hours per day the pump of the heat supply system
        needs to work.
    """

    def __init__(self, parent=None):
        """Constructor of HeatSupplySystem class
        """
        self.parent = parent

        self._building_type = None

        self._usable_area = None
        self._length_char = None
        self._n_res_units = None

        self._heat_load = None
        self._nominal_heat_output_boiler_heating = None
        self._nominal_heat_output_boiler_water = None
            
        if self.parent.year_of_retrofit is None:
            self._year_of_retrofit = 1
        else:
            self._year_of_retrofit = self.parent.year_of_retrofit

        # setting values for generation
        self._heat_system = None
        self._heat_generation = None
        self._storage = None
        self._combined_water_heating = True
        self._temp_ambient = 20
        self._annual_operating_time_heating = 185
        self._annual_operating_time_water = 350

        # setting values for distribution
        self._pipe_routing_heating = None
        self._pipe_routing_water = None
        self._design_temp_flow = None
        self._avg_temp_distribution_water = None
        self._avg_temp_distribution_heating = None
        self._oversizing_factor = None

        self._heat_loss_distribution_heating = None
        self._daily_operating_time_pump = None

    def setting_values(self, type_heat_supply_system=None, type_of_retrofit=None):
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
            Contains information on which supply system is assigned. Most buildings
            have 3 options. For building_type "sfh" older than 1995, 4 options are
            possible. For "mfh" older than 1995, 6 options are possible.
            Default: 1 (gas) for existing buildings and 3 (electricity) for new
            buildings.
        type_of_retrofit : str (optional)
            Can contain three values: standard, retrofit, adv_retrofit derived from
            TABULA values. Default is standard
        """
        if self.parent.net_leased_area != 0:
            self._usable_area = self.parent.net_leased_area * 1.25  # chapter 6 iwu
        else:
            print("net_leased_area has to have a value.")

        if type_heat_supply_system is None:
            if self.parent.year_of_construction >= 2016 or self._year_of_retrofit >= 2016:
                type_heat_supply_system = 3  # DENA report 2023 Abb. 41
            else:
                type_heat_supply_system = 1  # DENA report 2023 Abb. 31

        if type_of_retrofit is not None and "adv_retrofit" in type_of_retrofit:
            retrofit_type = "adv_retrofit"
        elif type_of_retrofit is not None and "retrofit" in type_of_retrofit:
            retrofit_type = "retrofit"
        else:
            retrofit_type = "standard"

        if (self.parent.year_of_construction is not None and self._year_of_retrofit is not None and
                (self.parent.year_of_construction >= 2016 or self._year_of_retrofit >= 2016)):
            self._oversizing_factor = 1  # standard for new buildings (iwu)
        else:
            self._oversizing_factor = 1.2  # standard for existing buildings (iwu)

        self._n_res_units = math.ceil(self.parent.net_leased_area / 80) # formula 4-14 and 4-15 iwu

        if type(self.parent).__name__:
            if any(substring.replace("_", "").lower() in type(self.parent).__name__.replace("_", "").lower() for
                   substring in ["singlefamily", "terraced"]):
                self._building_type = "sfh"
            elif any(substring.replace("_", "").lower() in type(self.parent).__name__.replace("_", "").lower() for
                   substring in ["multifamily", "apartment"]):
                self._building_type = "mfh"
        else:
            if self._n_res_units <= 2:
                self._building_type = "sfh"
            else:
                self._building_type = "mfh"

        if self._building_type == "sfh":

            if self.parent.year_of_construction <= 1994:

                if retrofit_type == "standard":

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
                            "type_heat_supply_system has to be a number between "
                            "1 and 3. For SFH or TH before 1995, 1 to 4 is possible. "
                            "For MFH and AB before 1995, 1 to 6 is possible."
                        )

                elif retrofit_type == "retrofit":

                    if type_heat_supply_system == 1:
                        self._heat_system = "gas"
                        self._heat_generation = "condensing"
                        self._heat_loss_distribution_heating = "good"
                    elif type_heat_supply_system == 2:
                        self._heat_system = "oil"
                        self._heat_generation = "condensing"
                        self._storage = "solar"
                        self._heat_loss_distribution_heating = "minimised"
                    elif type_heat_supply_system == 3:
                        self._heat_system = "electricity"
                        self._heat_generation = "heatpump air"
                        self._storage = "solar"
                        self._heat_loss_distribution_heating = "good"
                    elif type_heat_supply_system == 4:
                        self._heat_system = "oil"
                        self._heat_generation = "condensing"
                        self._storage = "solar"
                        self._heat_loss_distribution_heating = "minimised"
                    else:
                        raise ValueError(
                            "type_heat_supply_system has to be a number between "
                            "1 and 3. For SFH or TH before 1995, 1 to 4 is possible. "
                            "For MFH and AB before 1995, 1 to 6 is possible."
                        )

                elif retrofit_type == "adv_retrofit":

                    self._heat_loss_distribution_heating = "minimised"
                    if type_heat_supply_system == 1:
                        self._heat_system = "gas"
                        self._heat_generation = "condensing"
                        self._storage = "solar"
                        self._pipe_routing_heating = "centralised inside"
                    elif type_heat_supply_system == 2:
                        self._heat_system = "biomass"
                        self._heat_generation = "woodpellets"
                        self._storage = "solar"
                    elif type_heat_supply_system == 3:
                        self._heat_system = "electricity"
                        self._heat_generation = "heatpump ground"
                        self._storage = "water"
                    elif type_heat_supply_system == 4:
                        self._heat_system = "biomass"
                        self._heat_generation = "woodpellets"
                        self._storage = "solar"
                    else:
                        raise ValueError(
                            "type_heat_supply_system has to be a number between "
                            "1 and 3. For SFH or TH before 1995, 1 to 4 is possible. "
                            "For MFH and AB before 1995, 1 to 6 is possible."
                        )

                else:
                    raise ValueError(
                        "Construction_type has to be tabula_standard, "
                        "tabula_retrofit, "
                        "tabula_adv_retrofit"
                    )

            elif self.parent.year_of_construction <= 2009:

                if retrofit_type == "standard":

                    if type_heat_supply_system == 1:
                        self._heat_system = "gas"
                        self._heat_generation = "condensing"
                        self._heat_loss_distribution_heating = "minimised"
                    elif type_heat_supply_system == 2:
                        self._heat_system = "biomass"
                        self._heat_generation = "woodpellets"
                        self._storage = "water"
                        self._pipe_routing_water = "centralised with circulation"
                        self._heat_loss_distribution_heating = "good"
                    elif type_heat_supply_system == 3:
                        self._heat_system = "electricity"
                        self._heat_generation = "heatpump air"
                        self._storage = "solar"
                        self._heat_loss_distribution_heating = "good"
                    else:
                        raise ValueError(
                            "type_heat_supply_system has to be a number between "
                            "1 and 3. For SFH or TH before 1995, 1 to 4 is possible. "
                            "For MFH and AB before 1995, 1 to 6 is possible."
                        )

                elif retrofit_type == "retrofit":

                    self._heat_loss_distribution_heating = "minimised"
                    if type_heat_supply_system == 1:
                        self._heat_system = "gas"
                        self._heat_generation = "condensing"
                        self._storage = "solar"
                        self._pipe_routing_water = "centralised with circulation"
                        self._pipe_routing_heating = "centralised inside"
                    elif type_heat_supply_system == 2:
                        self._heat_system = "biomass"
                        self._heat_generation = "woodpellets"
                        self._storage = "water"
                        self._pipe_routing_water = "centralised with circulation"
                    elif type_heat_supply_system == 3:
                        self._heat_system = "electricity"
                        self._heat_generation = "heatpump air"
                        self._storage = "water"
                        self._pipe_routing_water = "centralised with circulation"
                    else:
                        raise ValueError(
                            "type_heat_supply_system has to be a number between "
                            "1 and 3. For SFH or TH before 1995, 1 to 4 is possible. "
                            "For MFH and AB before 1995, 1 to 6 is possible."
                        )

                elif retrofit_type == "adv_retrofit":

                    self._heat_loss_distribution_heating = "minimised"
                    if type_heat_supply_system == 1:
                        self._heat_system = "gas"
                        self._heat_generation = "condensing"
                        self._storage = "solar"
                        self._pipe_routing_heating = "centralised inside"
                    elif type_heat_supply_system == 2:
                        self._heat_system = "biomass"
                        self._heat_generation = "woodpellets"
                        self._storage = "water"
                    elif type_heat_supply_system == 3:
                        self._heat_system = "electricity"
                        self._heat_generation = "heatpump ground"
                        self._storage = "water"
                    else:
                        raise ValueError(
                            "type_heat_supply_system has to be a number between "
                            "1 and 3. For SFH or TH before 1995, 1 to 4 is possible. "
                            "For MFH and AB before 1995, 1 to 6 is possible."
                        )

                else:
                    raise ValueError(
                        "Construction_type has to be tabula_standard, "
                        "tabula_retrofit, "
                        "tabula_adv_retrofit"
                    )

            elif self.parent.year_of_construction <= 2015:

                self._heat_loss_distribution_heating = "minimised"
                if retrofit_type == "standard":

                    if type_heat_supply_system == 1:
                        self._heat_system = "gas"
                        self._heat_generation = "condensing"
                        self._storage = "solar"
                        self._pipe_routing_water = "centralised with circulation"
                        self._pipe_routing_heating = "centralised inside"
                    elif type_heat_supply_system == 2:
                        self._heat_system = "biomass"
                        self._heat_generation = "woodpellets"
                        self._storage = "water"
                        self._pipe_routing_water = "centralised with circulation"
                    elif type_heat_supply_system == 3:
                        self._heat_system = "electricity"
                        self._heat_generation = "heatpump air"
                        self._storage = "water"
                        self._pipe_routing_water = "centralised with circulation"
                    else:
                        raise ValueError(
                            "type_heat_supply_system has to be a number between "
                            "1 and 3. For SFH or TH before 1995, 1 to 4 is possible. "
                            "For MFH and AB before 1995, 1 to 6 is possible."
                        )

                elif retrofit_type == "retrofit":

                    if type_heat_supply_system == 1:
                        self._heat_system = "gas"
                        self._heat_generation = "condensing"
                        self._storage = "solar"
                        self._pipe_routing_heating = "centralised inside"
                    elif type_heat_supply_system == 2:
                        self._heat_system = "biomass"
                        self._heat_generation = "woodpellets"
                        self._storage = "water"
                    elif type_heat_supply_system == 3:
                        self._heat_system = "electricity"
                        self._heat_generation = "heatpump ground - no buffer storage"
                        self._storage = "water"
                    else:
                        raise ValueError(
                            "type_heat_supply_system has to be a number between "
                            "1 and 3. For SFH or TH before 1995, 1 to 4 is possible. "
                            "For MFH and AB before 1995, 1 to 6 is possible."
                        )

                elif retrofit_type == "adv_retrofit":

                    if type_heat_supply_system == 1:
                        self._heat_system = "gas"
                        self._heat_generation = "condensing"
                        self._storage = "solar"
                        self._pipe_routing_heating = "centralised inside"
                    elif type_heat_supply_system == 2:
                        self._heat_system = "biomass"
                        self._heat_generation = "woodpellets"
                        self._storage = "solar"
                    elif type_heat_supply_system == 3:
                        self._heat_system = "electricity"
                        self._heat_generation = "heatpump ground - no buffer storage"
                        self._storage = "water"
                    else:
                        raise ValueError(
                            "type_heat_supply_system has to be a number between "
                            "1 and 3. For SFH or TH before 1995, 1 to 4 is possible. "
                            "For MFH and AB before 1995, 1 to 6 is possible."
                        )

                else:
                    raise ValueError(
                        "Construction_type has to be tabula_standard, "
                        "tabula_retrofit, "
                        "tabula_adv_retrofit"
                    )

            else:

                self._heat_loss_distribution_heating = "minimised"
                if retrofit_type == "standard":

                    if type_heat_supply_system == 1:
                        self._heat_system = "gas"
                        self._heat_generation = "condensing"
                        self._storage = "solar"
                        self._pipe_routing_heating = "centralised inside"
                    elif type_heat_supply_system == 2:
                        self._heat_system = "biomass"
                        self._heat_generation = "woodpellets"
                        self._storage = "water"
                        self._pipe_routing_water = "centralised with circulation"
                    elif type_heat_supply_system == 3:
                        self._heat_system = "electricity"
                        self._heat_generation = "heatpump ground - no buffer storage"
                        self._storage = "water"
                    else:
                        raise ValueError(
                            "type_heat_supply_system has to be a number between "
                            "1 and 3. For SFH or TH before 1995, 1 to 4 is possible. "
                            "For MFH and AB before 1995, 1 to 6 is possible."
                        )

                elif retrofit_type == "retrofit":

                    if type_heat_supply_system == 1:
                        self._heat_system = "gas"
                        self._heat_generation = "condensing"
                        self._storage = "solar"
                        self._pipe_routing_heating = "centralised inside"
                    elif type_heat_supply_system == 2:
                        self._heat_system = "biomass"
                        self._heat_generation = "woodpellets"
                        self._storage = "water"
                    elif type_heat_supply_system == 3:
                        self._heat_system = "electricity"
                        self._heat_generation = "heatpump ground - no buffer storage"
                        self._storage = "water"
                    else:
                        raise ValueError(
                            "type_heat_supply_system has to be a number between "
                            "1 and 3. For SFH or TH before 1995, 1 to 4 is possible. "
                            "For MFH and AB before 1995, 1 to 6 is possible."
                        )

                elif retrofit_type == "adv_retrofit":

                    if type_heat_supply_system == 1:
                        self._heat_system = "gas"
                        self._heat_generation = "condensing"
                        self._storage = "solar"
                        self._pipe_routing_heating = "centralised inside"
                    elif type_heat_supply_system == 2:
                        self._heat_system = "biomass"
                        self._heat_generation = "woodpellets"
                        self._storage = "solar"
                    elif type_heat_supply_system == 3:
                        self._heat_system = "electricity"
                        self._heat_generation = "heatpump ground - no buffer storage"
                        self._storage = "water"
                    else:
                        raise ValueError(
                            "type_heat_supply_system has to be a number between "
                            "1 and 3. For SFH or TH before 1995, 1 to 4 is possible. "
                            "For MFH and AB before 1995, 1 to 6 is possible."
                        )

                else:
                    raise ValueError(
                        "Construction_type has to be tabula_standard, "
                        "tabula_retrofit, "
                        "tabula_adv_retrofit"
                    )

        elif self._building_type == "mfh":

            if self.parent.year_of_construction <= 1994:

                if retrofit_type == "standard":

                    self._heat_loss_distribution_heating = "high"
                    if type_heat_supply_system == 1:
                        self._heat_system = "gas"
                        self._heat_generation = "low temperature"
                        self._storage = "water"
                    elif type_heat_supply_system == 2:
                        self._heat_system = "oil"
                        self._heat_generation = "low temperature - not combined"
                    elif type_heat_supply_system == 3:
                        self._heat_system = "electricity"
                        self._heat_generation = "night storage"
                    elif type_heat_supply_system == 4:
                        self._heat_system = "district"
                        self._heat_generation = "district"
                    elif type_heat_supply_system == 5:
                        self._heat_system = "gas"
                        self._heat_generation = "circulating water heater"
                    elif type_heat_supply_system == 6:
                        self._heat_system = "oil"
                        self._heat_generation = "low temperature"
                        self._storage = "water"
                    else:
                        raise ValueError(
                            "type_heat_supply_system has to be a number between "
                            "1 and 3. For SFH or TH before 1995, 1 to 4 is possible. "
                            "For MFH and AB before 1995, 1 to 6 is possible."
                        )

                elif retrofit_type == "retrofit":

                    if type_heat_supply_system == 1:
                        self._heat_system = "gas"
                        self._heat_generation = "condensing"
                        self._storage = "water"
                        self._heat_loss_distribution_heating = "small"
                    elif type_heat_supply_system == 2:
                        self._heat_system = "oil"
                        self._heat_generation = "condensing"
                        self._storage = "solar"
                        self._heat_loss_distribution_heating = "minimised"
                    elif type_heat_supply_system == 3:
                        self._heat_system = "gas"
                        self._heat_generation = "condensing - decentralised"
                        self._heat_loss_distribution_heating = "small"
                    elif type_heat_supply_system == 4:
                        self._heat_system = "district"
                        self._heat_generation = "district"
                        self._heat_loss_distribution_heating = "small"
                    elif type_heat_supply_system == 5:
                        self._heat_system = "gas"
                        self._heat_generation = "condensing - decentralised"
                        self._heat_loss_distribution_heating = "small"
                    elif type_heat_supply_system == 6:
                        self._heat_system = "oil"
                        self._heat_generation = "condensing"
                        self._storage = "solar"
                        self._heat_loss_distribution_heating = "minimised"
                    else:
                        raise ValueError(
                            "type_heat_supply_system has to be a number between "
                            "1 and 3. For SFH or TH before 1995, 1 to 4 is possible. "
                            "For MFH and AB before 1995, 1 to 6 is possible."
                        )

                elif retrofit_type == "adv_retrofit":

                    self._heat_loss_distribution_heating = "small"
                    if type_heat_supply_system == 1:
                        self._heat_system = "gas"
                        self._heat_generation = "condensing"
                        self._storage = "solar"
                    elif type_heat_supply_system == 2:
                        self._heat_system = "biomass"
                        self._heat_generation = "woodpellets"
                        self._storage = "solar"
                    elif type_heat_supply_system == 3:
                        self._heat_system = "biomass"
                        self._heat_generation = "woodpellets"
                        self._storage = "water"
                    elif type_heat_supply_system == 4:
                        self._heat_system = "district"
                        self._heat_generation = "district"
                    elif type_heat_supply_system == 5:
                        self._heat_system = "gas"
                        self._heat_generation = "condensing - decentralised"
                    elif type_heat_supply_system == 6:
                        self._heat_system = "biomass"
                        self._heat_generation = "woodpellets"
                        self._storage = "solar"
                    else:
                        raise ValueError(
                            "type_heat_supply_system has to be a number between "
                            "1 and 3. For SFH or TH before 1995, 1 to 4 is possible. "
                            "For MFH and AB before 1995, 1 to 6 is possible."
                        )

                else:
                    raise ValueError(
                        "Construction_type has to be tabula_standard, "
                        "tabula_retrofit, "
                        "tabula_adv_retrofit"
                    )

            elif self.parent.year_of_construction <= 2009:

                if retrofit_type == "standard":

                    self._heat_loss_distribution_heating = "small"
                    if type_heat_supply_system == 1:
                        self._heat_system = "gas"
                        self._heat_generation = "condensing"
                        self._storage = "water"
                    elif type_heat_supply_system == 2:
                        self._heat_system = "biomass"
                        self._heat_generation = "woodpellets"
                        self._storage = "water"
                    elif type_heat_supply_system == 3:
                        self._heat_system = "electricity"
                        self._heat_generation = "heatpump air"
                        self._storage = "water"
                    else:
                        raise ValueError(
                            "type_heat_supply_system has to be a number between "
                            "1 and 3. For SFH or TH before 1995, 1 to 4 is possible. "
                            "For MFH and AB before 1995, 1 to 6 is possible."
                        )

                elif retrofit_type == "retrofit":

                    if type_heat_supply_system == 1:
                        self._heat_system = "gas"
                        self._heat_generation = "condensing"
                        self._storage = "solar"
                        self._heat_loss_distribution_heating = "minimised"
                    elif type_heat_supply_system == 2:
                        self._heat_system = "biomass"
                        self._heat_generation = "woodpellets"
                        self._storage = "water"
                        self._heat_loss_distribution_heating = "minimised"
                    elif type_heat_supply_system == 3:
                        self._heat_system = "electricity"
                        self._heat_generation = "heatpump air"
                        self._storage = "water"
                        self._heat_loss_distribution_heating = "small"
                    else:
                        raise ValueError(
                            "type_heat_supply_system has to be a number between "
                            "1 and 3. For SFH or TH before 1995, 1 to 4 is possible. "
                            "For MFH and AB before 1995, 1 to 6 is possible."
                        )

                elif retrofit_type == "adv_retrofit":

                    self._heat_loss_distribution_heating = "minimised"
                    if type_heat_supply_system == 1:
                        self._heat_system = "gas"
                        self._heat_generation = "condensing"
                        self._storage = "solar"
                    elif type_heat_supply_system == 2:
                        self._heat_system = "biomass"
                        self._heat_generation = "woodpellets"
                        self._storage = "water"
                    elif type_heat_supply_system == 3:
                        self._heat_system = "electricity"
                        self._heat_generation = "heatpump ground"
                        self._storage = "water"
                    else:
                        raise ValueError(
                            "type_heat_supply_system has to be a number between "
                            "1 and 3. For SFH or TH before 1995, 1 to 4 is possible. "
                            "For MFH and AB before 1995, 1 to 6 is possible."
                        )

                else:
                    raise ValueError(
                        "Construction_type has to be tabula_standard, "
                        "tabula_retrofit, "
                        "tabula_adv_retrofit"
                    )

            elif self.parent.year_of_construction <= 2015:

                if retrofit_type == "standard":

                    if type_heat_supply_system == 1:
                        self._heat_system = "gas"
                        self._heat_generation = "condensing"
                        self._storage = "solar"
                        self._heat_loss_distribution_heating = "minimised"
                    elif type_heat_supply_system == 2:
                        self._heat_system = "biomass"
                        self._heat_generation = "woodpellets"
                        self._storage = "water"
                        self._heat_loss_distribution_heating = "minimised"
                    elif type_heat_supply_system == 3:
                        self._heat_system = "electricity"
                        self._heat_generation = "heatpump air"
                        self._storage = "water"
                        self._heat_loss_distribution_heating = "small"
                    else:
                        raise ValueError(
                            "type_heat_supply_system has to be a number between "
                            "1 and 3. For SFH or TH before 1995, 1 to 4 is possible. "
                            "For MFH and AB before 1995, 1 to 6 is possible."
                        )

                elif retrofit_type == "retrofit":

                    self._heat_loss_distribution_heating = "minimised"
                    if type_heat_supply_system == 1:
                        self._heat_system = "gas"
                        self._heat_generation = "condensing"
                        self._storage = "solar"
                    elif type_heat_supply_system == 2:
                        self._heat_system = "biomass"
                        self._heat_generation = "woodpellets"
                        self._storage = "water"
                    elif type_heat_supply_system == 3:
                        self._heat_system = "electricity"
                        self._heat_generation = "heatpump ground"
                        self._storage = "water"
                    else:
                        raise ValueError(
                            "type_heat_supply_system has to be a number between "
                            "1 and 3. For SFH or TH before 1995, 1 to 4 is possible. "
                            "For MFH and AB before 1995, 1 to 6 is possible."
                        )

                elif retrofit_type == "adv_retrofit":

                    self._heat_loss_distribution_heating = "minimised"
                    if type_heat_supply_system == 1:
                        self._heat_system = "gas"
                        self._heat_generation = "condensing - chp"
                        self._storage = "solar"
                    elif type_heat_supply_system == 2:
                        self._heat_system = "biomass"
                        self._heat_generation = "chp"
                        self._storage = "solar"
                    elif type_heat_supply_system == 3:
                        self._heat_system = "electricity"
                        self._heat_generation = "heatpump ground"
                        self._storage = "water"
                    else:
                        raise ValueError(
                            "type_heat_supply_system has to be a number between "
                            "1 and 3. For SFH or TH before 1995, 1 to 4 is possible. "
                            "For MFH and AB before 1995, 1 to 6 is possible."
                        )

                else:
                    raise ValueError(
                        "Construction_type has to be tabula_standard, "
                        "tabula_retrofit, "
                        "tabula_adv_retrofit"
                    )

            else:

                self._heat_loss_distribution_heating = "minimised"
                if retrofit_type == "standard":

                    if type_heat_supply_system == 1:
                        self._heat_system = "gas"
                        self._heat_generation = "condensing"
                        self._storage = "solar"
                    elif type_heat_supply_system == 2:
                        self._heat_system = "biomass"
                        self._heat_generation = "woodpellets"
                        self._storage = "water"
                    elif type_heat_supply_system == 3:
                        self._heat_system = "electricity"
                        self._heat_generation = "heatpump ground"
                        self._storage = "water"
                    else:
                        raise ValueError(
                            "type_heat_supply_system has to be a number between "
                            "1 and 3. For SFH or TH before 1995, 1 to 4 is possible. "
                            "For MFH and AB before 1995, 1 to 6 is possible."
                        )

                elif retrofit_type == "retrofit":

                    if type_heat_supply_system == 1:
                        self._heat_system = "gas"
                        self._heat_generation = "condensing"
                        self._storage = "solar"
                    elif type_heat_supply_system == 2:
                        self._heat_system = "biomass"
                        self._heat_generation = "woodpellets"
                        self._storage = "water"
                    elif type_heat_supply_system == 3:
                        self._heat_system = "electricity"
                        self._heat_generation = "heatpump ground"
                        self._storage = "water"
                    else:
                        raise ValueError(
                            "type_heat_supply_system has to be a number between "
                            "1 and 3. For SFH or TH before 1995, 1 to 4 is possible. "
                            "For MFH and AB before 1995, 1 to 6 is possible."
                        )

                elif retrofit_type == "adv_retrofit":

                    if type_heat_supply_system == 1:
                        self._heat_system = "gas"
                        self._heat_generation = "condensing - chp"
                        self._storage = "solar"
                    elif type_heat_supply_system == 2:
                        self._heat_system = "biomass"
                        self._heat_generation = "chp"
                        self._storage = "solar"
                    elif type_heat_supply_system == 3:
                        self._heat_system = "electricity"
                        self._heat_generation = "heatpump ground"
                        self._storage = "water"
                    else:
                        raise ValueError(
                            "type_heat_supply_system has to be a number between "
                            "1 and 3. For SFH or TH before 1995, 1 to 4 is possible. "
                            "For MFH and AB before 1995, 1 to 6 is possible."
                        )

                else:
                    raise ValueError(
                        "Construction_type has to be tabula_standard, "
                        "tabula_retrofit, "
                        "tabula_adv_retrofit"
                    )

        else:
            print("No heat supply system added due to missing building type!")

        if self._heat_generation in ["night storage", "low temperature - not combined"]:  # TABULA
            self._combined_water_heating = False

        if self._pipe_routing_heating is None:  # TABULA
            if (self._heat_system == "gas" and
                (self._heat_generation in ["circulating water heater", "condensing - decentralised"])) or \
                    (self._heat_system == "electricity" and self._heat_generation == "night storage"):
                self._pipe_routing_heating = "decentralised"
            else:
                self._pipe_routing_heating = "centralised outside"

        if self._building_type == "sfh" and self._pipe_routing_water is None:  # TABULA
            if self._pipe_routing_heating == "decentralised" or self._combined_water_heating is False:
                self._pipe_routing_water = "decentralised"
            else:
                self._pipe_routing_water = "centralised without circulation"

        else:  # TABULA
            if self._pipe_routing_heating == "decentralised" or self._combined_water_heating is False:
                self._pipe_routing_water = "decentralised"
            else:
                self._pipe_routing_water = "centralised with circulation"

        self.setting_derived_values()

    def setting_derived_values(self):
        """
        Depending on the type of heat supply system, derived values are set here.
        Like the characteristic length of the building, average temperatures etc.

        Parameters
        ----------
        """

        try:
            result = self.parent.get_footprint_gml()
            if result is not None:

                self._length_char = self.parent.get_footprint_gml() / 10  # iwu chapter 4.4.1

        except:
            self._length_char = (self.parent.net_leased_area / 0.256) / (self._n_res_units * 2.8 * 10)
            # 2.8 = height_of_floors

            print("Mistake while function get_footprint_gml() in Building class.")

        if "condensing" in self._heat_generation:
            self._design_temp_flow = 55
        elif "heatpump" in self._heat_generation:
            self._design_temp_flow = 35
        else:
            self._design_temp_flow = 70

        # iwu formula 4-4
        if self._usable_area != 0 and self._usable_area < 10000:
            self._daily_operating_time_pump = 7.5 + 1 / (0.06 + 7 / self._usable_area)
        else:
            self._daily_operating_time_pump = 24

        if self.parent.simulated_heat_load is None:
            # DIN EN 15378-1:2017-09 table B.38
            if self._building_type == "sfh":
                self._heat_load = 100 * self._usable_area / (self._annual_operating_time_heating *
                                                                       self._daily_operating_time_pump)
            else:
                self._heat_load = 60 * self._usable_area / (self._annual_operating_time_heating *
                                                                      self._daily_operating_time_pump)

        else:
            self._heat_load = self.parent.simulated_heat_load # todo check, if simulated_heat_load in kW
            print("self.parent.simulated_heat_load: ", self.parent.simulated_heat_load)

        # calculation of nominal heat output
        # iwu formula 2-3 [kW]
        if (self._oversizing_factor * self._heat_load / 5) <= 15 or self._heat_load is None:
            self._nominal_heat_output_boiler_heating = 15
        else:
            self._nominal_heat_output_boiler_heating = self._oversizing_factor * self._heat_load

        # iwu formula 2-5 [kW]
        self._nominal_heat_output_boiler_water = -0.0014 * self._n_res_units ** 2 + 1.4 * self._n_res_units + 7

        if self._combined_water_heating:
            max_result = max(self._nominal_heat_output_boiler_heating, self._nominal_heat_output_boiler_water)
            self._nominal_heat_output_boiler_heating = max_result
            self._nominal_heat_output_boiler_water = max_result

        # calculation of the average temperature of the water distribution
        # iwu chapter 1.2.2
        if self._pipe_routing_water == "centralised with circulation":
            self._avg_temp_distribution_water = 50

        else:
            self._avg_temp_distribution_water = 32

        # calculation of the average temperature of the heating distribution
        # iwu table 1
        if self._n_res_units >= 10:  # todo ">= 6" after September 2024
            # heating mode "optimised": hydraulic balancing

            if self._design_temp_flow == 70:

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
                if self._oversizing_factor == 1.0:
                    self._avg_temp_distribution_heating = 27
                elif self._oversizing_factor == 1.2:
                    self._avg_temp_distribution_heating = 26

        else:
            # heating_mode "typical": no hydraulic balancing

            if self._design_temp_flow == 70:

                if self._oversizing_factor == 1.0:
                    self._avg_temp_distribution_heating = 53
                elif self._oversizing_factor == 1.2:
                    self._avg_temp_distribution_heating = 50

            elif self._design_temp_flow == 55:

                if self._oversizing_factor == 1.0:
                    self._avg_temp_distribution_heating = 43
                elif self._oversizing_factor == 1.2:
                    self._avg_temp_distribution_heating = 41

            else:
                if self._oversizing_factor == 1.0:
                    self._avg_temp_distribution_heating = 29
                elif self._oversizing_factor == 1.2:
                    self._avg_temp_distribution_heating = 29

    def retrofit_heat_supply_system(self, year_of_retrofit, type_heat_supply_system=None, type_of_retrofit=None):
        """Retrofits all parameters in the system.

        This function retrofits the heat supply system and sets the new values of
        the system as well as the derived values automatically.

        Parameters
        ----------
        year_of_retrofit : int
            Year of last retrofit. Due to legal reasons, last possible year is 1995.
            Older systems should already be retrofitted.
        type_heat_supply_system : int (optional)
            Contains information on which supply system is assigned. Most buildings
            have 3 options. For building_type "sfh" older than 1995, 4 options are
            possible. For "mfh" older than 1995, 6 options are possible.
            Default: 1 (gas) for existing buildings and 3 (electricity) for new
            buildings.
        type_of_retrofit : str (optional)
            Can contain three values: standard, retrofit, adv_retrofit derived from
            TABULA values. Default is standard.
        """

        if year_of_retrofit < 1995:
            self._year_of_retrofit = 1995
            print("You are using a year of retrofit not supported\
                    by teaser. We will change your year of retrofit to 1995\
                    for the calculation. Be careful!")
        else:
            self._year_of_retrofit = year_of_retrofit

        if type_of_retrofit and "adv_retrofit" in type_of_retrofit:
            retrofit_type = "adv_retrofit"

            print("already highest available standard of heat_supply_system, type_of_retrofit stays 'adv_retrofit'.")

        elif type_of_retrofit and "retrofit" in type_of_retrofit:
            retrofit_type = "adv_retrofit"

        else:
            retrofit_type = "retrofit"

        if type_heat_supply_system is None:
            if self.parent.year_of_construction >= 2016 or self._year_of_retrofit >= 2016:
                type_heat_supply_system = 3  # DENA report 2023 Abb. 41
            else:
                type_heat_supply_system = 1  # DENA report 2023 Abb. 31

        self.setting_values(type_heat_supply_system, retrofit_type)

    @property
    def parent(self):
        return self.__parent

    @parent.setter
    def parent(self, value):
        from teaser.teaser.logic.buildingobjects.building import Building
        import inspect
        if value is not None:
            if inspect.isclass(Building):
                self.__parent = value
                self.__parent.heat_supply_system = self

    @property
    def building_type(self):
        return self._building_type

    @building_type.setter
    def building_type(self, value):
        if value in ["mfh", "sfh"]:
            self._building_type = value
        else:
            raise ValueError("building_type no defined value")

    @property
    def usable_area(self):
        return self._usable_area

    @usable_area.setter
    def usable_area(self, value):

        if isinstance(value, float):
            self._usable_area = value
        elif value is None:
            self._usable_area = value
        else:
            try:
                value = float(value)
                self._usable_area = value
            except:
                raise ValueError("Can't convert usable_area to float")

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
    def n_res_units(self):
        return self._n_res_units

    @n_res_units.setter
    def n_res_units(self, value):

        if isinstance(value, int):
            self._n_res_units = value
        elif value is None:
            self._n_res_units = value
        else:
            try:
                value = int(value)
                self._n_res_units = value
            except:
                raise ValueError("Can't convert n_res_units to int")

    @property
    def heat_load(self):
        return self._heat_load

    @heat_load.setter
    def heat_load(self, value):

        if isinstance(value, float):
            self._heat_load = value
        else:
            try:
                value = float(value)
                self._heat_load = value
            except:
                raise ValueError("Can't convert heat_load to float")

    @property
    def nominal_heat_output_boiler_heating(self):
        return self._nominal_heat_output_boiler_heating

    @nominal_heat_output_boiler_heating.setter
    def nominal_heat_output_boiler_heating(self, value):

        if isinstance(value, float):
            self._nominal_heat_output_boiler_heating = value
        elif value is None:
            self._nominal_heat_output_boiler_heating = value
        else:
            try:
                value = float(value)
                self._nominal_heat_output_boiler_heating = value
            except:
                raise ValueError("Can't convert nominal_heat_output_boiler_heating to float")

    @property
    def nominal_heat_output_boiler_water(self):
        return self._nominal_heat_output_boiler_water

    @nominal_heat_output_boiler_water.setter
    def nominal_heat_output_boiler_water(self, value):

        if isinstance(value, float):
            self._nominal_heat_output_boiler_water = value
        elif value is None:
            self._nominal_heat_output_boiler_water = value
        else:
            try:
                value = float(value)
                self._nominal_heat_output_boiler_water = value
            except:
                raise ValueError("Can't convert nominal_heat_output_boiler_water to float")

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
            if self.parent.year_of_construction is not None:
                self._year_of_retrofit = value
            else:
                raise ValueError("Specify year of construction first")

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
                     "heatpump ground", "heatpump ground - no buffer storage", "woodpellets", "chp", "district"]:
            self._heat_generation = value
        else:
            raise ValueError("heat_generation no defined value")

    @property
    def storage(self):
        return self._storage

    @storage.setter
    def storage(self, value):

        if value in ["water", "solar"]:
            self._storage = value
        elif value is None:
            self._storage = value
        else:
            raise ValueError("storage no defined value")

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
    def temp_ambient(self):
        return self._temp_ambient

    @temp_ambient.setter
    def temp_ambient(self, value):

        if isinstance(value, int):
            self._temp_ambient = value
        else:
            try:
                value = int(value)
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

        if value in [70, 55, 35]:
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
