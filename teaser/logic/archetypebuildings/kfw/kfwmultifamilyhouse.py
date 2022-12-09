# created November 2022
# by Julian Körner

from teaser.logic.archetypebuildings.kfw.kfwsinglefamilyhouse import KfwSingleFamilyHouse


class KfwMultiFamilyHouse(KfwSingleFamilyHouse):
    """
    Archetype for the efficiency standards defined by KfW using the MultiFamilyHouse
    building type given by TABULA (see tabula archetypebuildings)

    This archetype subclass only defines the labeling to load the correct building
    elements, the estimation factors for the building type MultiFamilyHouse and the
    case with or without AHU.

    For more information see KfwSingleFamilyHouse-class

    Parameters
    ----------

    parent: Project()
        The parent class of this object, the Project the Building belongs to.
        Allows for better control of hierarchical structures. If not None it
        adds this Building instance to Project.buildings.
        (default: None)
    name : str
        Individual name
    year_of_construction : int
        Year of first construction
    height_of_floors : float [m]
        Average height of the buildings' floors
    number_of_floors : int
        Number of building's floors above ground
    net_leased_area : float [m2]
        Total net leased area of building. This is area is NOT the footprint
        of a building
    with_ahu : Boolean
        If set to True, an empty instance of BuildingAHU is instantiated and
        assigned to attribute central_ahu. This instance holds information for
        central Air Handling units. Default is False.
    internal_gains_mode: int [1, 2, 3]
        mode for the internal gains calculation done in AixLib:
        1: Temperature and activity degree dependent heat flux calculation for persons. The
           calculation is based on  SIA 2024 (default)
        2: Temperature and activity degree independent heat flux calculation for persons, the max.
           heatflowrate is prescribed by the parameter
           fixed_heat_flow_rate_persons.
        3: Temperature and activity degree dependent calculation with
           consideration of moisture and co2. The moisture calculation is
           based on SIA 2024 (2015) and regards persons and non-persons, the co2 calculation is based on
           Engineering ToolBox (2004) and regards only persons.
    construction_type : str
        Construction type of used wall constructions default is "kfw70_woodframe"
            possible construction types:
                "kfw40_woodframe", "kfw55_woodframe", "kfw70_woodframe", "kfw100_woodframe",
                "kfw40_tabula", "kfw55_tabula", "kfw70_tabula", "kfw100_tabula"
    """

    def __init__(
            self,
            parent,
            name=None,
            year_of_construction=None,
            number_of_floors=None,
            height_of_floors=None,
            net_leased_area=None,
            with_ahu=False,
            internal_gains_mode=1,
            construction_type=None):

        super(KfwMultiFamilyHouse, self).__init__(
            parent,
            name,
            year_of_construction,
            number_of_floors,
            height_of_floors,
            net_leased_area,
            with_ahu,
            internal_gains_mode,
            construction_type)

        self.construction_type = construction_type
        self.number_of_floors = number_of_floors
        self.height_of_floors = height_of_floors

        if "woodframe" in self.construction_type:
            self._construction_type_interior = "kfw_woodframe_standard"
            self._construction_type_1 = self.construction_type
            self._construction_type_2 = self.construction_type
        elif "tabula" in self.construction_type:
            self._construction_type_interior = "tabula_standard"
            if "kfw40" in self.construction_type:
                self._construction_type_1 = "tabula_adv_retrofit_1_MFH"
                self._construction_type_2 = "tabula_adv_retrofit_2_MFH"
            elif "kfw55" or "kfw70" in self.construction_type:
                # before: Tabula retrofit [2016, 2100] and Tabula retrofit [2010, 2015]
                self._construction_type_1 = self.construction_type + "_1_MFH"
                self._construction_type_2 = self.construction_type + "_2_MFH"
            elif "kfw100" in self.construction_type:
                self._construction_type_1 = "tabula_standard_1_MFH"
                self._construction_type_2 = "tabula_standard_2_MFH"

        self.zone_area_factors = {"SingleDwelling": [1, "Living"]}

        self._outer_wall_names_1 = {
            "ExteriorFacadeNorth_1": [90.0, 0.0],
            "ExteriorFacadeEast_1": [90.0, 90.0],
            "ExteriorFacadeSouth_1": [90.0, 180.0],
            "ExteriorFacadeWest_1": [90.0, 270.0]}

        self._outer_wall_names_2 = {
            "ExteriorFacadeNorth_2": [90.0, 0.0],
            "ExteriorFacadeEast_2": [90.0, 90.0],
            "ExteriorFacadeSouth_2": [90.0, 180.0],
            "ExteriorFacadeWest_2": [90.0, 270.0]}

        self.roof_names_1 = {"Rooftop_1": [0, -1]}  # [0, -1]

        self.roof_names_2 = {"Rooftop_2": [0, -1]}

        self.ground_floor_names_1 = {
            "GroundFloor_1": [0, -2]}  # [0, -2]

        self.ground_floor_names_2 = {
            "GroundFloor_2": [0, -2]}

        self.door_names = {"Door": [90.0, 270]}

        self.window_names_1 = {
            "WindowFacadeNorth_1": [90.0, 0.0],
            "WindowFacadeEast_1": [90.0, 90.0],
            "WindowFacadeSouth_1": [90.0, 180.0],
            "WindowFacadeWest_1": [90.0, 270.0]}
        self.window_names_2 = {
            "WindowFacadeNorth_2": [90.0, 0.0],
            "WindowFacadeEast_2": [90.0, 90.0],
            "WindowFacadeSouth_2": [90.0, 180.0],
            "WindowFacadeWest_2": [90.0, 270.0]}

        # [tilt, orientation]

        self.inner_wall_names = {"InnerWall": [90.0, 0.0]}

        self.ceiling_names = {"Ceiling": [0.0, -1]}

        self.floor_names = {"Floor": [0.0, -2]}

        self.facade_estimation_factors = {
            (1000, 3000): {
                'rt1': 0.24605,
                'rt2': 0.0,
                'ow1': 0.91433,
                'ow2': 0.0,
                'gf1': 0.24605,
                'gf2': 0.0,
                'win1': 0.18667,
                'win2': 0.0,
                'door': 0.0367}}

        self.building_age_group = None

        if self.with_ahu is True:
            self.central_ahu.temperature_profile = (
                7 * [293.15] +
                12 * [295.15] +
                5 * [293.15])
            self.central_ahu.min_relative_humidity_profile = (24 * [0.45])
            self.central_ahu.max_relative_humidity_profile = (24 * [0.55])
            self.central_ahu.v_flow_profile = (
                7 * [0.0] + 12 * [1.0] + 5 * [0.0])
