# created November 2022
# by Julian Körner

from teaser.logic.archetypebuildings.residential import Residential
from teaser.logic.buildingobjects.useconditions import UseConditions as UseCond
from teaser.logic.buildingobjects.buildingphysics.ceiling import Ceiling
from teaser.logic.buildingobjects.buildingphysics.floor import Floor
from teaser.logic.buildingobjects.buildingphysics.groundfloor import GroundFloor
from teaser.logic.buildingobjects.buildingphysics.innerwall import InnerWall
from teaser.logic.buildingobjects.buildingphysics.outerwall import OuterWall
from teaser.logic.buildingobjects.buildingphysics.rooftop import Rooftop
from teaser.logic.buildingobjects.buildingphysics.window import Window
from teaser.logic.buildingobjects.buildingphysics.door import Door
from teaser.logic.buildingobjects.thermalzone import ThermalZone


class KfwSingleFamilyHouse(Residential):
    """
    Archetype for the efficiency standards defined by KfW using the SingleFamilyHouse
    building type given by TABULA (see tabula archetypebuildings)

    The assumptions made to make the reference buildings from TABULA available for a
    generation of multiple individual buildings, as intended by TEASER, are copied
    from the SingleFamilyHouse archetype of the tabula module:

    "Each building has four orientations for outer walls and windows (north,
    east, south and west), two orientations for rooftops (south and north), with
    tilt of 35 degree and one orientation for ground floors and one door (
    default
    orientation is west). The area of each surface is calculated using the
    product of the given net_leased_area and specific estimation factors. These
    estimation factors where build by dividing the given 'surface area' by the
    'reference floor area' in TABULA. The estimation factors are calculated for
    each building period ('construction year class'). Please note that the
    number and height of the floors given in TEASER does not have any effect on
    the surface area for heat transmission, but is only used to calculate the
    interior wall area, which is not specified in TABULA at all. Further, TABULA
    does not specify any specific user profile, by default the SingleFamilyHouse
    class has exactly one usage zone, which is 'Living'. TABULA also does not
    always specify the exact construction of building elements, but always
    provides a prescribed U-Value. We used the U-Value and the given material
    information to determine thickness of each layer and implemented it into
    elements json ('teaser.data.input.inputdata.TypeElements_TABULA_DE.json'). The
    material properties have been taken from MASEA Material data base
    (http://www.masea-ensan.de/). As there might be some differences in the
    assumptions for material properties from TABULA and MASEA the U-Value might
    not always be exactly the same as in TABULA but is always in an acceptable
    range. The U-Value has been calculated using combined constant values for
    interior and exterior heat transmission, we used a resistance of 0.17
    (m2*K)/W for outer walls, windows, flat roofs and doors; 0.34 (m2*K)/W  for
    ground floors to unheated cellars and 0.17 (m2*K)/W  to direct ground
    coupled floors, 0.21 (m2*K)/W  was taken for pitched roofs."

    The categorization of the tabula archetypes according to kfw efficiency levels
    was based on given information of the 'Deutsche Wohngebäudetypologie' of the IWU.

    Regarding the new wood frame archetypes, the U-Values used for the KfW efficiency
    levels were derived from research on current building standards and monitorings of
    KfW programs carried out by IWU.
    The components and some materials (if not already available in TEASER) used
    were mostly taken from the wood-components-catalog 'dataholz.eu' and components
    not available in the catalog (window, door, ground floor) were calculated using
    building elements from the existing tabula module while maintaining the required
    U-Values.

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
        construction_type=None,
    ):

        super(KfwSingleFamilyHouse, self).__init__(
            parent,
            name,
            year_of_construction,
            net_leased_area,
            with_ahu,
            internal_gains_mode
        )

        self.construction_type = construction_type
        self.number_of_floors = number_of_floors
        self.height_of_floors = height_of_floors

        # Labeling to load the correct components from TypeElements_kfw.json depending on given
        # construction_type
        # To avoid having to change all the names of the tabula components, the labeling
        # taken from the tabula module differs in Comparison to the new woodframe components
        # and is assigned by the following if-statements

        if "woodframe" in self.construction_type:
            self._construction_type_interior = "kfw_woodframe_standard"
            self._construction_type_1 = self.construction_type
            self._construction_type_2 = self.construction_type
        elif "tabula" in self.construction_type:
            self._construction_type_interior = "tabula_standard"
            if "kfw40" in self.construction_type:
                self._construction_type_1 = "tabula_adv_retrofit_1_SFH"
                self._construction_type_2 = "tabula_adv_retrofit_2_SFH"
            elif "kfw55" or "kfw70" in self.construction_type:
                # before: Tabula retrofit [2016, 2100] (now kfw55)
                # and Tabula retrofit [2010, 2015] (now kfw70)
                self._construction_type_1 = self.construction_type + "_1_SFH"
                self._construction_type_2 = self.construction_type + "_2_SFH"
            elif "kfw100" in self.construction_type:
                self._construction_type_1 = "tabula_standard_1_SFH"
                self._construction_type_2 = "tabula_standard_2_SFH"

        self.zone_area_factors = {"SingleDwelling": [1, "Living"]}

        # Defining Names for every building element twice (except door and interior components)
        # for the case of two given surface areas by TABULA for one building element (e.g. Wall1
        # and Wall2)

        self._outer_wall_names_1 = {
            "ExteriorFacadeNorth_1": [90.0, 0.0],
            "ExteriorFacadeEast_1": [90.0, 90.0],
            "ExteriorFacadeSouth_1": [90.0, 180.0],
            "ExteriorFacadeWest_1": [90.0, 270.0],
        }

        self._outer_wall_names_2 = {
            "ExteriorFacadeNorth_2": [90.0, 0.0],
            "ExteriorFacadeEast_2": [90.0, 90.0],
            "ExteriorFacadeSouth_2": [90.0, 180.0],
            "ExteriorFacadeWest_2": [90.0, 270.0],
        }

        self.roof_names_1 = {
            "RooftopNorth_1": [35.0, 0.0],
            "RooftopSouth_1": [35.0, 90.0],
        }

        self.roof_names_2 = {
            "RooftopNorth_2": [35.0, 0.0],
            "RooftopSouth_2": [35.0, 90.0],
        }

        self.ground_floor_names_1 = {"GroundFloor_1": [0, -2]}

        self.ground_floor_names_2 = {"GroundFloor_2": [0, -2]}

        self.door_names = {"Door": [90.0, 270]}

        self.window_names_1 = {
            "WindowFacadeNorth_1": [90.0, 0.0],
            "WindowFacadeEast_1": [90.0, 90.0],
            "WindowFacadeSouth_1": [90.0, 180.0],
            "WindowFacadeWest_1": [90.0, 270.0],
        }
        self.window_names_2 = {
            "WindowFacadeNorth_2": [90.0, 0.0],
            "WindowFacadeEast_2": [90.0, 90.0],
            "WindowFacadeSouth_2": [90.0, 180.0],
            "WindowFacadeWest_2": [90.0, 270.0],
        }

        # [tilt, orientation]

        self.inner_wall_names = {"InnerWall": [90.0, 0.0]}

        self.ceiling_names = {"Ceiling": [0.0, -1]}

        self.floor_names = {"Floor": [0.0, -2]}

        """
        Same estimation factors as for the individual TABULA Archetypes and building age groups
        within 2010-2100 (see TABULA Archetypes) are assumed, so one building age group 
        [1000, 3000] containing every possible year for all efficiency standards is enough 
        for now
        
        The Estimation factors for the other Archetypes (KfwTerracedHouse, KfwMultiFamilyHouse)
        are located in the corresponding archetype classes
        """

        self.facade_estimation_factors = {
            (1000, 3000): {
                "rt1": 0.70535,
                "rt2": 0.0,
                "ow1": 1.217,
                "ow2": 0.0,
                "gf1": 0.57647,
                "gf2": 0.0,
                "win1": 0.2246,
                "win2": 0.0,
                "door": 0.014,
            }
        }

        self.building_age_group = None

        # Calculation of ahu in the case of a building with air handling unit

        if self.with_ahu is True:
            self.central_ahu.temperature_profile = (
                    7 * [293.15] + 12 * [295.15] + 5 * [293.15]
            )
            self.central_ahu.min_relative_humidity_profile = 24 * [0.45]
            self.central_ahu.max_relative_humidity_profile = 24 * [0.55]
            self.central_ahu.v_flow_profile = 7 * [0.0] + 12 * [1.0] + 5 * [0.0]

        self.internal_gains_mode = internal_gains_mode

    def _check_year_of_construction(self):
        """Assigns the building age group according to year of construction, although there is
        only one possible building age group ranging from [1000, 3000] for the available
        KfW Archetypes"""

        for key in self.facade_estimation_factors:
            if (
                    self.year_of_construction in range(key[0], key[1])
                    or self.year_of_construction == key[1]
            ):
                self.building_age_group = (key[0], key[1])

        if self.building_age_group is None:
            raise RuntimeError(
                "Year of construction not supported for this archetype" "building"
            )

    def generate_archetype(self):
        """
        Generates a KfW archetype building

        With given values, this function generates an archetype building for
        KfW Type of Building using TABULAs area estimation factors.
        """
        self.thermal_zones = None
        self._check_year_of_construction()
        # help area for the correct building area setting while using typeBldgs
        type_bldg_area = self.net_leased_area
        self.net_leased_area = 0.0

        for key, value in self.zone_area_factors.items():
            zone = ThermalZone(parent=self)
            zone.name = key
            zone.area = type_bldg_area * value[0]
            use_cond = UseCond(parent=zone)
            use_cond.load_use_conditions(zone_usage=value[1])
            zone.use_conditions = use_cond

            zone.use_conditions.with_ahu = False

        # Calculating the building component areas
        # All Values for the second estimation factors = 0 for SFH
        # TH estimation factors != 0 and TH inherits from SFH to use the area calculations below
        # among other things

        if self.facade_estimation_factors[self.building_age_group]["ow1"] != 0:
            for key, value in self._outer_wall_names_1.items():
                for zone in self.thermal_zones:
                    outer_wall = OuterWall(zone)
                    outer_wall.load_type_element(
                        year=self.year_of_construction,
                        construction=self._construction_type_1,
                        data_class=self.parent.data,
                    )
                    outer_wall.name = key
                    outer_wall.tilt = value[0]
                    outer_wall.orientation = value[1]
                    outer_wall.area = (
                        self.facade_estimation_factors[self.building_age_group]["ow1"]
                        * zone.area
                    ) / len(self._outer_wall_names_1)

        if self.facade_estimation_factors[self.building_age_group]["ow2"] != 0:
            for key, value in self._outer_wall_names_2.items():
                for zone in self.thermal_zones:
                    outer_wall = OuterWall(zone)
                    outer_wall.load_type_element(
                        year=self.year_of_construction,
                        construction=self._construction_type_2,
                        data_class=self.parent.data,
                    )
                    outer_wall.name = key
                    outer_wall.tilt = value[0]
                    outer_wall.orientation = value[1]
                    outer_wall.area = (
                        self.facade_estimation_factors[self.building_age_group]["ow2"]
                        * zone.area
                    ) / len(self._outer_wall_names_2)

        if self.facade_estimation_factors[self.building_age_group]["win1"] != 0:
            for key, value in self.window_names_1.items():
                for zone in self.thermal_zones:
                    window = Window(zone)
                    window.load_type_element(
                        self.year_of_construction,
                        construction=self._construction_type_1,
                        data_class=self.parent.data,
                    )
                    window.name = key
                    window.tilt = value[0]
                    window.orientation = value[1]
                    window.area = (
                        self.facade_estimation_factors[self.building_age_group]["win1"]
                        * zone.area
                    ) / len(self.window_names_1)

        if self.facade_estimation_factors[self.building_age_group]["win2"] != 0:
            for key, value in self.window_names_2.items():
                for zone in self.thermal_zones:
                    window = Window(zone)
                    window.load_type_element(
                        self.year_of_construction,
                        construction=self._construction_type_2,
                        data_class=self.parent.data,
                    )
                    window.name = key
                    window.tilt = value[0]
                    window.orientation = value[1]
                    window.area = (
                        self.facade_estimation_factors[self.building_age_group]["win2"]
                        * zone.area
                    ) / len(self.window_names_2)

        if self.facade_estimation_factors[self.building_age_group]["gf1"] != 0:
            for key, value in self.ground_floor_names_1.items():

                for zone in self.thermal_zones:
                    gf = GroundFloor(zone)
                    gf.load_type_element(
                        year=self.year_of_construction,
                        construction=self._construction_type_1,
                        data_class=self.parent.data,
                    )
                    gf.name = key
                    gf.tilt = value[0]
                    gf.orientation = value[1]
                    gf.area = (
                        self.facade_estimation_factors[self.building_age_group]["gf1"]
                        * zone.area
                    ) / len(self.ground_floor_names_1)

        if self.facade_estimation_factors[self.building_age_group]["gf2"] != 0:
            for key, value in self.ground_floor_names_2.items():

                for zone in self.thermal_zones:
                    gf = GroundFloor(zone)
                    gf.load_type_element(
                        year=self.year_of_construction,
                        construction=self._construction_type_2,
                        data_class=self.parent.data,
                    )
                    gf.name = key
                    gf.tilt = value[0]
                    gf.orientation = value[1]
                    gf.area = (
                        self.facade_estimation_factors[self.building_age_group]["gf2"]
                        * zone.area
                    ) / len(self.ground_floor_names_2)

        if self.facade_estimation_factors[self.building_age_group]["rt1"] != 0:
            for key, value in self.roof_names_1.items():

                for zone in self.thermal_zones:
                    rt = Rooftop(zone)
                    rt.load_type_element(
                        year=self.year_of_construction,
                        construction=self._construction_type_1,
                        data_class=self.parent.data,
                    )
                    rt.name = key
                    rt.tilt = value[0]
                    rt.orientation = value[1]
                    rt.area = (
                        self.facade_estimation_factors[self.building_age_group]["rt1"]
                        * zone.area
                    ) / len(self.roof_names_1)

        if self.facade_estimation_factors[self.building_age_group]["rt2"] != 0:
            for key, value in self.roof_names_2.items():

                for zone in self.thermal_zones:
                    rt = Rooftop(zone)
                    rt.load_type_element(
                        year=self.year_of_construction,
                        construction=self._construction_type_2,
                        data_class=self.parent.data,
                    )
                    rt.name = key
                    rt.tilt = value[0]
                    rt.orientation = value[1]
                    rt.area = (
                        self.facade_estimation_factors[self.building_age_group]["rt2"]
                        * zone.area
                    ) / len(self.roof_names_2)

        if self.facade_estimation_factors[self.building_age_group]["door"] != 0:
            for key, value in self.door_names.items():

                for zone in self.thermal_zones:
                    door = Door(zone)
                    door.load_type_element(
                        year=self.year_of_construction,
                        construction=self._construction_type_1,
                        data_class=self.parent.data,
                    )
                    door.name = key
                    door.tilt = value[0]
                    door.orientation = value[1]
                    door.area = (
                        self.facade_estimation_factors[self.building_age_group]["door"]
                        * zone.area
                    ) / len(self.door_names)

        # Define all Innerwall areas and components
        # Construction types for interior components labeled "tabula_standard" or "kfw_standard"

        for key, value in self.inner_wall_names.items():

            for zone in self.thermal_zones:
                inner_wall = InnerWall(zone)
                inner_wall.load_type_element(
                    year=self.year_of_construction,
                    construction=self._construction_type_interior,
                    data_class=self.parent.data,
                )
                inner_wall.name = key
                inner_wall.tilt = value[0]
                inner_wall.orientation = value[1]

        if self.number_of_floors > 1:

            for key, value in self.ceiling_names.items():

                for zone in self.thermal_zones:
                    ceiling = Ceiling(zone)
                    ceiling.load_type_element(
                        year=self.year_of_construction,
                        construction=self._construction_type_interior,
                        data_class=self.parent.data,
                    )
                    ceiling.name = key
                    ceiling.tilt = value[0]
                    ceiling.orientation = value[1]

            for key, value in self.floor_names.items():

                for zone in self.thermal_zones:
                    floor = Floor(zone)
                    floor.load_type_element(
                        year=self.year_of_construction,
                        construction=self._construction_type_interior,
                        data_class=self.parent.data,
                    )
                    floor.name = key
                    floor.tilt = value[0]
                    floor.orientation = value[1]

        for zone in self.thermal_zones:
            zone.set_inner_wall_area()
            zone.set_volume_zone()

    # Copied from tabula's singlefamilyhouse archetype
    # Because of the changed Approach with the construction type being the main differentiation
    # instead of the year of construction, the CityGML input won't work as intended
    # !There is no Information about the efficiency standards of buildings in a CityGML File!

    def generate_from_gml(self):
        """Enriches lod1 or lod2 data from CityGML

        Adds Zones, BoundaryConditions, Material settings for walls and
        windows to the geometric representation of CityGML

        Enrichment of LoD3 and LoD4 added, parallel to original.
        """

        type_bldg_area = self.net_leased_area
        self.net_leased_area = 0.0
        self._check_year_of_construction()
        print(self.building_age_group)

        # my variable: decider for inner_wall calculation method
        lod4_innerwalls = False
        # create zones with their corresponding area, name and usage

        for key, value in self.zone_area_factors.items():
            zone = ThermalZone(self)
            zone.area = type_bldg_area * value[0]
            zone.name = key
            use_cond = UseCond(zone)
            use_cond.load_use_conditions(value[1],
                                         data_class=self.parent.data)
            zone.use_conditions = use_cond
            zone.use_conditions.with_ahu = False
            zone.use_conditions.persons *= zone.area * 0.01
            zone.use_conditions.machines *= zone.area * 0.01

            # TODO: fix with or without Windows scenario 2

            print(self.parent.data.used_statistic)
            for surface in self.gml_surfaces:
                if surface.surface_tilt is not None and surface.name is None:
                    if surface.surface_tilt == 90:
                        outer_wall = OuterWall(zone)
                        outer_wall.load_type_element(
                            year=self.year_of_construction,
                            construction=self._construction_type_1,
                            data_class=self.parent.data)
                        # print(outer_wall.layer)
                        # print(self.construction_type)
                        outer_wall.name = surface.name
                        outer_wall.tilt = surface.surface_tilt
                        outer_wall.orientation = surface.surface_orientation

                        window = Window(zone)
                        window.load_type_element(self.year_of_construction,
                                                 construction=self._construction_type_1,
                                                 data_class=self.parent.data)
                        window.name = "asd" + str(surface.surface_tilt)
                        window.tilt = surface.surface_tilt
                        window.orientation = surface.surface_orientation
                        # print("comes through here")
                        # print(window.layer)

                    elif surface.surface_tilt == 0 and \
                            surface.surface_orientation == \
                            -2:
                        outer_wall = GroundFloor(zone)
                        outer_wall.load_type_element(
                            year=self.year_of_construction,
                            construction=self._construction_type_1,
                            data_class=self.parent.data)
                        outer_wall.name = surface.name
                        outer_wall.tilt = surface.surface_tilt
                        outer_wall.orientation = surface.surface_orientation
                    else:
                        outer_wall = Rooftop(zone)
                        outer_wall.load_type_element(
                            year=self.year_of_construction,
                            construction=self._construction_type_1,
                            data_class=self.parent.data)
                        outer_wall.name = surface.name
                        outer_wall.tilt = surface.surface_tilt
                        outer_wall.orientation = surface.surface_orientation

                # If Window / Interior Wall area is provided separately

                else:
                    if surface.surface_tilt == 90:
                        if surface.name != "Window" and surface.name != "InnerWall":
                            outer_wall = OuterWall(zone)
                            outer_wall.load_type_element(
                                year=self.year_of_construction,
                                construction=self.construction_type,
                                data_class=self.parent.data)
                            outer_wall.name = surface.name
                            outer_wall.tilt = surface.surface_tilt
                            outer_wall.orientation = surface.surface_orientation
                        elif surface.name == "Window":
                            window = Window(zone)
                            window.load_type_element(self.year_of_construction,
                                                     self._construction_type_1,
                                                     data_class=self.parent.data)
                            window.name = surface.name + str(surface.surface_orientation)
                            window.area = surface.surface_area
                            window.tilt = surface.surface_tilt
                            window.orientation = surface.surface_orientation
                        elif surface.name == "InnerWall":
                            lod4_innerwalls = True
                            inner_wall = InnerWall(zone)
                            inner_wall.load_type_element(
                                year=self.year_of_construction,
                                construction="tabula_standard",
                                data_class=self.parent.data)
                            inner_wall.name = surface.name + str(surface.surface_orientation) \
                                              + str(surface.surface_area)
                            inner_wall.tilt = surface.surface_tilt
                            inner_wall.orientation = surface.surface_orientation
                            # print(inner_wall.layer)

                    elif surface.surface_tilt == 0 and \
                            surface.surface_orientation == \
                            -2 and surface.name != "InnerWall":
                        outer_wall = GroundFloor(zone)
                        outer_wall.load_type_element(
                            year=self.year_of_construction,
                            construction=self._construction_type_1,
                            data_class=self.parent.data)
                        outer_wall.name = surface.name
                        outer_wall.tilt = surface.surface_tilt
                        outer_wall.orientation = surface.surface_orientation

                    elif surface.surface_tilt == 0 and \
                            surface.surface_orientation == \
                            -2 and surface.name == "InnerWall":
                        lod4_innerwalls = True
                        floor = Floor(zone)
                        floor.load_type_element(
                            year=self.year_of_construction,
                            construction="tabula_standard",
                            data_class=self.parent.data)
                        floor.name = "floor" + str(surface.surface_orientation) \
                                     + str(surface.surface_area)
                        floor.tilt = surface.surface_tilt
                        floor.orientation = surface.surface_orientation

                    else:
                        if surface.name != "InnerWall":
                            outer_wall = Rooftop(zone)
                            outer_wall.load_type_element(
                                year=self.year_of_construction,
                                construction=self._construction_type_1,
                                data_class=self.parent.data)
                            outer_wall.name = surface.name
                            outer_wall.tilt = surface.surface_tilt
                            outer_wall.orientation = surface.surface_orientation

                        elif surface.name == "InnerWall":
                            lod4_innerwalls = True
                            ceiling = Ceiling(zone)
                            ceiling.load_type_element(
                                year=self.year_of_construction,
                                construction="tabula_standard",
                                data_class=self.parent.data)
                            ceiling.name = "ceiling" + str(surface.surface_orientation) \
                                           + str(surface.surface_area)
                            ceiling.tilt = surface.surface_tilt
                            ceiling.orientation = surface.surface_orientation

            if lod4_innerwalls is False:

                for key, value in self.inner_wall_names.items():
                    for zone in self.thermal_zones:
                        inner_wall = InnerWall(zone)
                        inner_wall.load_type_element(
                            year=self.year_of_construction,
                            construction="tabula_standard",
                            data_class=self.parent.data)
                        inner_wall.name = key
                        inner_wall.tilt = value[0]
                        inner_wall.orientation = value[1]

                if self.number_of_floors > 1:

                    for key, value in self.ceiling_names.items():
                        for zone in self.thermal_zones:
                            ceiling = Ceiling(zone)
                            ceiling.load_type_element(
                                year=self.year_of_construction,
                                construction="tabula_standard",
                                data_class=self.parent.data)
                            ceiling.name = key
                            ceiling.tilt = value[0]
                            ceiling.orientation = value[1]

                    for key, value in self.floor_names.items():
                        for zone in self.thermal_zones:
                            floor = Floor(zone)
                            floor.load_type_element(
                                year=self.year_of_construction,
                                construction="tabula_standard",
                                data_class=self.parent.data)
                            floor.name = key
                            floor.tilt = value[0]
                            floor.orientation = value[1]
                else:
                    pass
            else:
                pass
        for surface in self.gml_surfaces:
            # print(surface.name)
            if surface.name is None:  # LoD0-2
                if surface.surface_tilt != 0 and surface.surface_orientation != -2 \
                        and surface.surface_orientation != -1:  # Walls/Windows
                    self.set_outer_wall_area(surface.surface_area *
                                             (1 - self.facade_estimation_factors[self.building_age_group]['win1']),
                                             surface.surface_orientation)
                    # self.set_outer_wall_area(surface.surface_area,
                    #                          surface.surface_orientation, surface.surface_tilt)
                    self.set_window_area(
                        surface.surface_area * self.facade_estimation_factors[self.building_age_group]['win1'],
                        surface.surface_orientation)
                    # self.set_window_area(
                    #     surface.surface_area,
                    #     surface.surface_orientation)
                else:  # Ground/Floor
                    self.set_outer_wall_area(surface.surface_area,
                                             surface.surface_orientation, surface.surface_tilt)
            else:  # LoD3-4
                if surface.name != "Window" and surface.name != "InnerWall":
                    self.set_outer_wall_area(surface.surface_area, surface.surface_orientation, surface.surface_tilt)
                elif surface.name == "Window":

                    # TODO: fix window area calc in here or in building.py: sum before attribution!?

                    self.set_window_area(surface.surface_area, surface.surface_orientation)
                    # print(surface.surface_area)
                elif surface.name == "InnerWall":
                    self.set_inner_wall_area_lod4(surface.surface_area, surface.surface_orientation)

        if lod4_innerwalls is False:
            for zone in self.thermal_zones:
                zone.set_inner_wall_area()
                zone.set_volume_zone()
        else:
            for zone in self.thermal_zones:
                zone.set_volume_zone()


    @property
    def construction_type(self):
        return self._construction_type

    # Changed possible construction types to fit the selectable kfw standards

    @construction_type.setter
    def construction_type(self, value):
        if value is not None:
            if value in ["kfw40_tabula", "kfw55_tabula", "kfw70_tabula", "kfw100_tabula",
                         "kfw40_woodframe", "kfw55_woodframe", "kfw70_woodframe",
                         "kfw100_woodframe"]:
                self._construction_type = value
            else:
                raise ValueError(
                    "Construction_type has to be "
                    "kfw40_woodframe, "
                    "kfw55_woodframe, "
                    "kfw70_woodframe, "
                    "kfw100_woodframe, "
                    "kfw40_tabula, "
                    "kfw55_tabula, "
                    "kfw70_tabula or "
                    "kfw100_tabula"
                )
        else:
            self._construction_type = "kfw70_woodframe"

