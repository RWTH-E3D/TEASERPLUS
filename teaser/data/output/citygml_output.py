# Created October 2015
# TEASER Development Team

"""CityGML

This module contains function to save and load Projects in the non proprietary
CityGML file format .gml
"""
import re
import os
import lxml.etree as ET
from datetime import date, datetime
import uuid
import teaser.data.output.citygml_classes as cl
import pandas as pd


def save_gml_lxml(project, path, gml_copy=None, ref_coordinates=None, with_results=None):
    """Based on CityGML Building export from CityBIT"""

    crs = "urn:adv:crs:ETRS89_UTM32*DE_DHHN2016_NH*GCG2016"

    global nsClass
    nsClass = cl.CGML2

    # creating new namespacemap
    newNSmap = {'core': nsClass.core, 'gen': nsClass.gen, 'grp': nsClass.grp, 'app': nsClass.app, 'bldg': nsClass.bldg,
                'gml': nsClass.gml, 'xal': nsClass.xal, 'xlink': nsClass.xlink, 'xsi': nsClass.xsi,
                'energy': nsClass.energy}
    schemaLocation = "http://www.opengis.net/citygml/2.0 http://www.sig3d.org/citygml/2.0/energy/1.0/EnergyADE.xsd"

    # creating new root element
    global nroot_E
    nroot_E = ET.Element(ET.QName(nsClass.core, 'CityModel'),
                         attrib={"{" + nsClass.xsi + "}schemaLocation":schemaLocation}, nsmap=newNSmap)

    # creating name element
    name_E = ET.SubElement(nroot_E, ET.QName(nsClass.gml, 'name'), nsmap={'gml': nsClass.gml})
    name_E.text = 'created using the e3D TEASERplus'

    """set boundary box"""
    if ref_coordinates is not None:
        boundedBy = ET.SubElement(nroot_E, ET.QName(nsClass.gml, 'boundedBy'), nsmap={'gml': nsClass.gml})
        boundedBy.append(ref_coordinates)
    else:
        bldg_center = [0, 0, 0]
        pass

    """create new cityObjectMember here"""
    cityObjectMember_E = ET.SubElement(nroot_E, ET.QName(nsClass.core, 'cityObjectMember'))

    for i, bldg_count in enumerate(project.buildings):
        gmlID = "e3D_TEASERplus_" + str(bldg_count.internal_id)

        if gml_copy is None or re.match(r"(\w+)bt_", bldg_count.name):

            gml_bldg = ET.SubElement(cityObjectMember_E, ET.QName(nsClass.bldg, 'Building'),
                                       attrib={ET.QName(nsClass.gml, 'id'): gmlID})

            _set_gml_building_lxml(gml_bldg, nsClass, bldg_count, ET)

            """for testing the loop"""
            if with_results is True:
                if bldg_count.simulated_heat_load is not None:
                    _save_simulation_results(gml_bldg, results=bldg_count.simulated_heat_load)
                else:
                    print("Heating load is not yet simulated!")

            bldg_center = [i * 80, 0, 0]

            if type(bldg_count).__name__ == "SingleFamilyDwelling":
                building_length = (bldg_count.thermal_zones[0].area /
                                   bldg_count.thermal_zones[0].typical_width)
                building_width = bldg_count.thermal_zones[0].typical_width
                building_height = (bldg_count.number_of_floors *
                                   bldg_count.height_of_floors)

            else:
                building_width = 0.05 * (bldg_count.net_leased_area /
                                         bldg_count.number_of_floors)
                building_length = (bldg_count.net_leased_area /
                                   bldg_count.number_of_floors) / building_width
                building_height = (bldg_count.number_of_floors *
                                   bldg_count.height_of_floors)

            _set_lod_2_lxml(gml_bldg, building_length, building_width, building_height, bldg_center, nsClass, None)

        else:
            cityObjectMember_E.append(gml_copy[i])
            tree = ET.ElementTree(nroot_E)

            # writing file
            print('writing file temp file')
            tree.write(os.path.join(path), pretty_print=True, xml_declaration=True,
                       encoding='utf-8', standalone='yes', method="xml")
            with open(path, 'r') as xml_file:
                parser = ET.XMLParser(remove_blank_text=True)
                tree = ET.parse(xml_file, parser=parser)
                nroot_E = tree.getroot()
                namespace = nroot_E.nsmap
                gml_bldg = nroot_E.findall('core:cityObjectMember/bldg:Building', namespace)[0]

            if with_results is True:
                _save_simulation_results(gml_bldg)

        for zone_count in bldg_count.thermal_zones:
            _set_gml_volume_lxml(gml_bldg, nsClass, zone_count, ET)
            PolyIDs = _set_gml_thermal_zone_lxml(gml_bldg, nsClass, zone_count, ET)

            if gml_copy is None:
                tree = ET.ElementTree(nroot_E)

            """writing file"""
            print('writing file')
            tree.write(os.path.join(path), pretty_print=True, xml_declaration=True,
                       encoding='utf-8', standalone='yes', method="xml")


def _set_gml_building_lxml(gml_bldg, nsClass, teaser_building, ET):
    """Creates an instance of a citygml Building with attributes

        creates a citygml.building.Building object. And fills the attributes of
        this instance with attributes of the TEASER building

        Parameters
        ----------

        teaser_building : Building Object of TEASER
            Instance of a TEASER object with set attributes

        Returns
        -------

        gml_bldg : citygml.building.Building() object
            Returns a citygml Building with attributes
        """

# gml_bldg = ET.SubElement(cityObjectMember_E, ET.QName(nsClass.bldg, 'Building'),
#                                        attrib={ET.QName(nsClass.gml, 'id'): gmlID})

    ET.SubElement(gml_bldg, ET.QName(nsClass.gml,
                                       'description')).text = 'created using the e3D TEASER+'

    # building attributes
    ET.SubElement(gml_bldg, ET.QName(nsClass.gml, 'name')).text = teaser_building.name
    ET.SubElement(gml_bldg, ET.QName(nsClass.core, 'creationDate')).text = str(date.today())
    ET.SubElement(gml_bldg, ET.QName(nsClass.bldg, 'function')).text = str(teaser_building.type_of_building)
    ET.SubElement(gml_bldg, ET.QName(nsClass.bldg, 'yearOfConstruction')).text = \
        str(teaser_building.year_of_construction)
    ET.SubElement(gml_bldg, ET.QName(nsClass.bldg, 'roofType'), attrib={
        'codeSpace': 'http://www.sig3d.org/codelists/citygml/2.0/building/2.0/_AbstractBuilding_roofType.xml'})\
        .text = str(1000)
    ET.SubElement(gml_bldg, ET.QName(nsClass.bldg, 'measuredHeight'), attrib={'uom': "m"}).text = \
        str(teaser_building.number_of_floors * teaser_building.height_of_floors)
    ET.SubElement(gml_bldg, ET.QName(nsClass.bldg, 'storeysAboveGround')).text = \
        str(teaser_building.number_of_floors)


def _set_reference_boundary(gml_out, lower_coords, upper_coords):
    #TODO: rewrite for lxml

    """Adds a reference coordinate system with `Envelope`'s corners

    The gml file includes a reference coordinate system defined in the
    `boundedBy` object, within which the `Envelope` object contains both a
    `lowerCorner` and an `upperCorner`. Both corners extend
    `gml.DirectPositionType`. This method sets all necessary parts of the
    `boundedBy` in a given gml file.

    Parameters
    ----------

    gml_out : citygml.CityModel() object
        A CityModel object, where citygml is a reference to
        `pyxb.bundles.opengis.citygml.base`. The reference coordinate system
        will be added to this object.
    lower_coords : list
        A list that contains the coordinates of the point for the
        `lowerCorner` definition. It should contain 3 ints or floats for
        x, y, and z coordinates of the point.
    upper_coords : list
        A list that contains the coordinates of the point for the
        `upperCorner` definition. It should contain 3 ints or floats for
        x, y, and z coordinates of the point.

    Returns
    -------

    gml_out : citygml.CityModel() object
        Returns the modified CityModel object
    """
    assert len(lower_coords) == 3, 'lower_coords must contain 3 elements'
    assert len(upper_coords) == 3, 'lower_coords must contain 3 elements'

    # reference_bound = gml.boundedBy()
    #
    # reference_envelope = gml.Envelope()
    # reference_envelope.srsDimension = 3
    # reference_envelope.srsName = 'urn:adv:crs:ETRS89_UTM32'
    #
    # lower_corner = gml.DirectPositionType(lower_coords)
    # lower_corner.srsDimension = 3
    # reference_envelope.lowerCorner = lower_corner
    # upper_corner = gml.DirectPositionType(upper_coords)
    # upper_corner.srsDimension = 3
    # reference_envelope.upperCorner = upper_corner
    #
    # reference_bound.Envelope = reference_envelope
    # gml_out.boundedBy = reference_bound
    #
    # return gml_out


def _set_lod_2_lxml(gml_bldg, length, width, height, bldg_center, nsClass, PolyIDs):
    """Adds a LOD 2 representation of the building based on building length,
    width and height

    alternative way to handle building position

    Parameters
    ----------

    gml_bldg : bldg.Building() object
        A building object, where bldg is a reference to
        `pyxb.bundles.opengis.citygml.building`.
    length : float
        length of the building
    width : float
        width of the building
    height : float
        height of the building
    bldg_center : list
        coordinates in the reference system of the building center


    """

    # Ground surface

    boundedBy_E = ET.SubElement(gml_bldg, ET.QName(nsClass.bldg, 'boundedBy'))
    groundSurfaceID = "GML_" + str(uuid.uuid1())
    wallRoofGround_E = ET.SubElement(boundedBy_E, ET.QName(nsClass.bldg, 'GroundSurface'),
                                     attrib={ET.QName(nsClass.gml, 'id'): groundSurfaceID})
    ET.SubElement(wallRoofGround_E, ET.QName(nsClass.gml, 'name')).text = 'GroundSurface'
    lodnMultisurface_E = ET.SubElement(wallRoofGround_E, ET.QName(nsClass.bldg, 'lod2MultiSurface'))
    multiSurface_E = ET.SubElement(lodnMultisurface_E, ET.QName(nsClass.gml, 'MultiSurface'))
    surfaceMember_E = ET.SubElement(multiSurface_E, ET.QName(nsClass.gml, 'surfaceMember'))

    bldg_center[0] -= length / 2
    bldg_center[1] -= width / 2

    coords = [[bldg_center[0], bldg_center[1], bldg_center[2]],
              [length + bldg_center[0], bldg_center[1], bldg_center[2]],
              [length + bldg_center[0], width + bldg_center[1], bldg_center[2]],
              [bldg_center[0], width + bldg_center[1], bldg_center[2]]]

    polyID = str(uuid.uuid1())

    _add_surface_lxml(surfaceMember_E, nsClass, coords, polyID)

    # Roof surface

    boundedBy_E = ET.SubElement(gml_bldg, ET.QName(nsClass.bldg, 'boundedBy'))
    roofSurfaceID = "GML_" + str(uuid.uuid1())
    wallRoofGround_E = ET.SubElement(boundedBy_E, ET.QName(nsClass.bldg, 'RoofSurface'),
                                     attrib={ET.QName(nsClass.gml, 'id'): roofSurfaceID})
    ET.SubElement(wallRoofGround_E, ET.QName(nsClass.gml, 'name')).text = 'RoofSurface'
    lodnMultisurface_E = ET.SubElement(wallRoofGround_E, ET.QName(nsClass.bldg, 'lod2MultiSurface'))
    multiSurface_E = ET.SubElement(lodnMultisurface_E, ET.QName(nsClass.gml, 'MultiSurface'))
    surfaceMember_E = ET.SubElement(multiSurface_E, ET.QName(nsClass.gml, 'surfaceMember'))

    coords = [[bldg_center[0], bldg_center[1], bldg_center[2] + height],
              [length + bldg_center[0], bldg_center[1],
               bldg_center[2] + height],
              [length + bldg_center[0], width + bldg_center[1],
               bldg_center[2] + height],
              [bldg_center[0], width + bldg_center[1], bldg_center[2] + height]]

    polyID = str(uuid.uuid1())

    _add_surface_lxml(surfaceMember_E, nsClass, coords, polyID)

    # Side a surface

    boundedBy_E = ET.SubElement(gml_bldg, ET.QName(nsClass.bldg, 'boundedBy'))
    wall_a_SurfaceID = "GML_" + str(uuid.uuid1())
    wallRoofGround_E = ET.SubElement(boundedBy_E, ET.QName(nsClass.bldg, 'WallSurface'),
                                     attrib={ET.QName(nsClass.gml, 'id'): wall_a_SurfaceID})
    ET.SubElement(wallRoofGround_E, ET.QName(nsClass.gml, 'name')).text = 'WallSurface'
    lodnMultisurface_E = ET.SubElement(wallRoofGround_E, ET.QName(nsClass.bldg, 'lod2MultiSurface'))
    multiSurface_E = ET.SubElement(lodnMultisurface_E, ET.QName(nsClass.gml, 'MultiSurface'))
    surfaceMember_E = ET.SubElement(multiSurface_E, ET.QName(nsClass.gml, 'surfaceMember'))

    coords = [[bldg_center[0], bldg_center[1], bldg_center[2]],
              [length + bldg_center[0], bldg_center[1], bldg_center[2]],
              [length + bldg_center[0], bldg_center[1],
               bldg_center[2] + height],
              [bldg_center[0], bldg_center[1], bldg_center[2] + height]]

    polyID = str(uuid.uuid1())

    _add_surface_lxml(surfaceMember_E, nsClass, coords, polyID)

    # Side b surface

    boundedBy_E = ET.SubElement(gml_bldg, ET.QName(nsClass.bldg, 'boundedBy'))
    wall_b_SurfaceID = "GML_" + str(uuid.uuid1())
    wallRoofGround_E = ET.SubElement(boundedBy_E, ET.QName(nsClass.bldg, 'WallSurface'),
                                     attrib={ET.QName(nsClass.gml, 'id'): wall_b_SurfaceID})
    ET.SubElement(wallRoofGround_E, ET.QName(nsClass.gml, 'name')).text = 'WallSurface'
    lodnMultisurface_E = ET.SubElement(wallRoofGround_E, ET.QName(nsClass.bldg, 'lod2MultiSurface'))
    multiSurface_E = ET.SubElement(lodnMultisurface_E, ET.QName(nsClass.gml, 'MultiSurface'))
    surfaceMember_E = ET.SubElement(multiSurface_E, ET.QName(nsClass.gml, 'surfaceMember'))

    coords = [[bldg_center[0], width + bldg_center[1], bldg_center[2]],
              [length + bldg_center[0], width + bldg_center[1],
               bldg_center[2]],
              [length + bldg_center[0], width + bldg_center[1],
               bldg_center[2] + height],
              [bldg_center[0], width + bldg_center[1], bldg_center[2] + height]]

    polyID = str(uuid.uuid1())

    _add_surface_lxml(surfaceMember_E, nsClass, coords, polyID)

    # Side c surface

    boundedBy_E = ET.SubElement(gml_bldg, ET.QName(nsClass.bldg, 'boundedBy'))
    wall_c_SurfaceID = "GML_" + str(uuid.uuid1())
    wallRoofGround_E = ET.SubElement(boundedBy_E, ET.QName(nsClass.bldg, 'WallSurface'),
                                     attrib={ET.QName(nsClass.gml, 'id'): wall_c_SurfaceID})
    ET.SubElement(wallRoofGround_E, ET.QName(nsClass.gml, 'name')).text = 'WallSurface'
    lodnMultisurface_E = ET.SubElement(wallRoofGround_E, ET.QName(nsClass.bldg, 'lod2MultiSurface'))
    multiSurface_E = ET.SubElement(lodnMultisurface_E, ET.QName(nsClass.gml, 'MultiSurface'))
    surfaceMember_E = ET.SubElement(multiSurface_E, ET.QName(nsClass.gml, 'surfaceMember'))

    coords = [[bldg_center[0], bldg_center[1], bldg_center[2]],
              [bldg_center[0], width + bldg_center[1], bldg_center[2]],
              [bldg_center[0], width + bldg_center[1], bldg_center[2] + height],
              [bldg_center[0], bldg_center[1], bldg_center[2] + height]]

    polyID = str(uuid.uuid1())

    _add_surface_lxml(surfaceMember_E, nsClass, coords, polyID)

    # Side d surface

    boundedBy_E = ET.SubElement(gml_bldg, ET.QName(nsClass.bldg, 'boundedBy'))
    wall_d_SurfaceID = "GML_" + str(uuid.uuid1())
    wallRoofGround_E = ET.SubElement(boundedBy_E, ET.QName(nsClass.bldg, 'WallSurface'),
                                     attrib={ET.QName(nsClass.gml, 'id'): wall_d_SurfaceID})
    ET.SubElement(wallRoofGround_E, ET.QName(nsClass.gml, 'name')).text = 'WallSurface'
    lodnMultisurface_E = ET.SubElement(wallRoofGround_E, ET.QName(nsClass.bldg, 'lod2MultiSurface'))
    multiSurface_E = ET.SubElement(lodnMultisurface_E, ET.QName(nsClass.gml, 'MultiSurface'))
    surfaceMember_E = ET.SubElement(multiSurface_E, ET.QName(nsClass.gml, 'surfaceMember'))

    coords = [[length + bldg_center[0], bldg_center[1], bldg_center[2]],
              [length + bldg_center[0], width + bldg_center[1],
               bldg_center[2]],
              [length + bldg_center[0], width + bldg_center[1],
               bldg_center[2] + height],
              [length + bldg_center[0], bldg_center[1],
               bldg_center[2] + height]]

    polyID = str(uuid.uuid1())

    _add_surface_lxml(surfaceMember_E, nsClass, coords, polyID)


def _add_surface_lxml(multi_surface, nsClass, coords, polyID):
    assert len(coords) == 4, 'coords must contain 4 elements'
    for coord in coords:
        assert len(coord) == 3, 'Each coord list should contain 3 elements'

    surfaceMember_E = ET.SubElement(multi_surface, ET.QName(nsClass.gml, 'surfaceMember'))
    polygon_E = ET.SubElement(surfaceMember_E, ET.QName(nsClass.gml, 'Polygon'),
                              attrib={ET.QName(nsClass.gml, 'id'): polyID})
    exterior_E = ET.SubElement(polygon_E, ET.QName(nsClass.gml, 'exterior'))
    ring_id = polyID + '_0'
    linearRing_E = ET.SubElement(exterior_E, ET.QName(nsClass.gml, 'LinearRing'),
                                 attrib={ET.QName(nsClass.gml, 'id'): ring_id})

    input_list = []
    for coord in coords:
        for value in coord:
            input_list.append(value)
    for value in coords[0]:
        input_list.append(value)

    stringed = [str(j) for j in input_list]
    ET.SubElement(linearRing_E, ET.QName(nsClass.gml, 'posList')).text = ' '.join(stringed)


def _set_gml_volume_lxml(gml_bldg, nsClass, thermal_zone, ET):

    # declaring Volume Object

    gml_volume = ET.SubElement(gml_bldg, ET.QName(nsClass.energy, 'volume'))
    gml_volume_type = ET.SubElement(gml_volume, ET.QName(nsClass.energy, 'VolumeType'))
    ET.SubElement(gml_volume_type, ET.QName(nsClass.energy, 'type')).text = "grossVolume"
    ET.SubElement(gml_volume_type, ET.QName(nsClass.energy, 'value'), attrib={'uom': "m3"}).text \
        = str(thermal_zone.volume)


def _set_gml_floor_area_lxml(gml_bldg, nsClass,thermal_zone, ET):

    # declaring Floor Area Object

    gml_floor_area = ET.SubElement(gml_bldg, ET.QName(nsClass.energy, 'floorArea'))
    gml_floor_area_type = ET.SubElement(gml_floor_area, ET.QName(nsClass.energy, 'FloorArea'))
    ET.SubElement(gml_floor_area_type, ET.QName(nsClass.energy, 'type')).text = "grossFloorArea"
    ET.SubElement(gml_floor_area_type, ET.QName(nsClass.energy, 'value'), attrib={'uom': "m2"}).text \
        = str(thermal_zone.area)


def _set_gml_thermal_zone_lxml(gml_bldg, nsClass, thermal_zone, ET):

    thermal_zone_id = str("GML_" + str(thermal_zone.internal_id))
    usage_zone_id = str("GML_" + str(thermal_zone.use_conditions.internal_id))
    gml_thermal_zone = ET.SubElement(gml_bldg, ET.QName(nsClass.energy, 'thermalZone'))
    gml_Thermal_Zone = ET.SubElement(gml_thermal_zone, ET.QName(nsClass.energy, 'ThermalZone'),
                                     attrib={ET.QName(nsClass.gml, 'id'): thermal_zone_id})
    ET.SubElement(gml_Thermal_Zone, ET.QName(nsClass.energy, 'contains'),
                  attrib={ET.QName(nsClass.xlink, 'href'): str('#'+usage_zone_id)})
    _set_gml_floor_area_lxml(gml_Thermal_Zone, nsClass, thermal_zone, ET)
    _set_gml_volume_lxml(gml_Thermal_Zone, nsClass, thermal_zone, ET)
    ET.SubElement(gml_Thermal_Zone, ET.QName(nsClass.energy, 'isCooled')).text = "false"
    ET.SubElement(gml_Thermal_Zone, ET.QName(nsClass.energy, 'isHeated')).text = "true"
    gml_volume_geometry = ET.SubElement(gml_Thermal_Zone, ET.QName(nsClass.energy, 'volumeGeometry'))
    # solid = ET.SubElement(gml_volume_geometry, ET.QName(nsClass.gml, 'Solid'),
    #                                  attrib={ET.QName(nsClass.gml, 'id'): str(thermal_zone_id + "_solid")})

    polyIDs, exteriorSurfaces = _set_composite_surface(gml_volume_geometry, nsClass, thermal_zone, ET)

    """Set Usage zone for thermal zone"""
    _set_usage_zone_lxml(thermal_zone, gml_bldg, usage_zone_id)

    """Set boundary Surfaces"""

    construction_id_windows = None
    material_ids = []

    for i in range(len(exteriorSurfaces)):
        if i == 0:
            surfaceType = 'WallSurface'
            construction_id = None

        elif i == 1:
            surfaceType = 'RoofSurface'
            construction_id = None

        elif i == 2:
            surfaceType = 'GroundSurface'
            construction_id = None


        for surface in exteriorSurfaces[i]:
            thermal_openings = []

            for win_count in thermal_zone.windows:
                if surface.orientation == win_count.orientation and surface.tilt == win_count.tilt:
                    thermal_openings.append(win_count)
            construction_id, construction_id_windows = \
                _set_gml_thermal_boundary_lxml(gml_Thermal_Zone, surface, thermal_openings, nsClass, construction_id,
                                               construction_id_windows, material_ids, thermal_zone_id)

    return polyIDs


def _set_composite_surface(solid, nsClass, thermal_zone, ET):

    exteriorSurfaces = [thermal_zone.outer_walls, thermal_zone.rooftops, thermal_zone.ground_floors]
    polyIDs = []
    n = 0
    UUID = uuid.uuid1()
    for dictionary in exteriorSurfaces:
        for key in dictionary:
            ID = "PolyID" + str(UUID) + '_' + str(n)
            polyIDs.append(ID)
            hashtagedID = '#' + ID
            # ET.SubElement(solid, ET.QName(nsClass.gml, 'surfaceMember'),
            #               attrib={ET.QName(nsClass.xlink, 'href'): hashtagedID})
            n -= - 1
    return polyIDs, exteriorSurfaces


def _set_gml_thermal_boundary_lxml(gml_zone, wall, thermal_openings, nsClass, construction_id,
                                   construction_id_windows, material_ids, thermal_zone_id):
    """Control function to add a thermal boundary surface to the thermal zone

    The thermal zone instance of citygml is modified and thermal boundary
    surfaces are added. The thermal boundaries are chosen according to their
    type (OuterWall, InnerWall, Roof, etc.). For outer walls (including roof)
    the thermal boundary is returned to add windows (Thermal Openings).

    Parameters
    ----------

    gml_zone : energy.thermalZones() object
        A thermalZone object, where energy is a reference to
        `pyxb.bundles.opengis.citygml.energy`.

    wall : TEASER instance of Wall()
        Teaser instance of Wall or its inherited classes

    thermal_openings: List of TEASER instances of Window() or Door()
        Teaser instance of BuildingElement or its inherited classes
    Returns
    ----------

    _current_tb : energy.ThermalBoundarySurface()
        A ThermalBoundarySurface object with semantic information
        (area, azimuth, inclination etc.)

    """
    _current_tb = None
    if type(wall).__name__ == "OuterWall":

        thermal_boundary_type_value = "outerWall"


    elif type(wall).__name__ == "Rooftop":
        thermal_boundary_type_value = "roof"


    elif type(wall).__name__ == "GroundFloor":

        thermal_boundary_type_value = "groundSlab"

    elif type(wall).__name__ == "InnerWall":
        thermal_boundary_type_value = "intermediaryFloor"


    elif type(wall).__name__ == "Ceiling" or type(wall).__name__ == "Floor":

        thermal_boundary_type_value = "interiorWall"

    else:
        print("Strange Wall Surface detected!")

    boundedBy_E = ET.SubElement(gml_zone, ET.QName(nsClass.energy, 'boundedBy'))
    thermal_boundary_E = ET.SubElement(boundedBy_E, ET.QName(nsClass.energy, 'ThermalBoundary'),
                                       attrib={ET.QName(nsClass.gml, 'id'): str("GML_" + str(wall.internal_id))})
    ET.SubElement(thermal_boundary_E, ET.QName(nsClass.energy, "thermalBoundaryType")).text = \
        thermal_boundary_type_value
    ET.SubElement(thermal_boundary_E, ET.QName(nsClass.energy, "azimuth"), attrib={'uom': "deg"}).text = \
        str(wall.orientation)
    ET.SubElement(thermal_boundary_E, ET.QName(nsClass.energy, "inclination"), attrib={'uom': "deg"}).text = \
        str(wall.tilt)
    ET.SubElement(thermal_boundary_E, ET.QName(nsClass.energy, "area"), attrib={'uom': "m2"}).text = \
        str(wall.area)
    if construction_id is None:
        construction_id = _set_gml_construction_lxml(wall, material_ids)
    else:
        pass
    ET.SubElement(thermal_boundary_E, ET.QName(nsClass.energy, "construction"), attrib={ET.QName(nsClass.xlink, 'href'):
                                                                                        str("#" + str(construction_id))})

    if thermal_openings is not None:
        for thermal_opening in thermal_openings:
            contains = ET.SubElement(thermal_boundary_E, ET.QName(nsClass.energy, "contains"))
            thermal_opening_E = ET.SubElement(contains, ET.QName(nsClass.energy, "ThermalOpening"),
                                              attrib={ET.QName(nsClass.gml, 'id'): str("GML_" + str(thermal_opening.internal_id))})
            ET.SubElement(thermal_opening_E, ET.QName(nsClass.energy, "area"), attrib={'uom': "m2"}).text = \
                str(thermal_opening.area)
            if construction_id_windows is None:
                construction_id_windows = _set_gml_construction_lxml(thermal_opening, material_ids)
            else:
                pass
            ET.SubElement(thermal_opening_E, ET.QName(nsClass.energy, "construction"),
                          attrib={ET.QName(nsClass.xlink, 'href'): str("#" + construction_id_windows)})

    ET.SubElement(thermal_boundary_E, ET.QName(nsClass.energy, "delimits"),
                  attrib={ET.QName(nsClass.xlink, 'href'): str("#" + str(str(thermal_zone_id)))})

    return construction_id, construction_id_windows


# def _set_gml_window_construction(element, nsClass, win_uvalue, win_trans, win_glazing):
#     construction_id = str("GML_" + str(uuid.uuid1()))
#     feature_member = ET.SubElement(nroot_E, ET.QName(nsClass['gml'], 'featureMember'))
#     construction_gml = ET.SubElement(feature_member, ET.QName(nsClass['energy'], 'Construction'),
#                                      attrib={ET.QName(nsClass['gml'], 'id'): str(construction_id)})
#     ET.SubElement(construction_gml, ET.QName(nsClass['gml'], "description")).text = \
#         str(element + "_construction")
#     ET.SubElement(construction_gml, ET.QName(nsClass['gml'], "name")).text = \
#         str(element + "_construction")
#     ET.SubElement(construction_gml, ET.QName(nsClass['energy'], "uValue"), attrib={'uom': "W/K*m2"}).text = \
#         str(win_uvalue)
#     opticalProperties = ET.SubElement(construction_gml, ET.QName(nsClass['energy'], "opticalProperties"))
#     OpticalProperties = ET.SubElement(opticalProperties, ET.QName(nsClass['energy'], "OpticalProperties"))
#     transmittance = ET.SubElement(OpticalProperties, ET.QName(nsClass['energy'], "transmittance"))
#     Transmittance = ET.SubElement(transmittance, ET.QName(nsClass['energy'], "Transmittence"))
#     ET.SubElement(Transmittance, ET.QName(nsClass['energy'], "fraction"), attrib={'uom': "scale"}).text = \
#         str(win_trans)
#     ET.SubElement(Transmittance, ET.QName(nsClass['energy'], "wavelengthRange")).text = \
#         str("solar")
#     ET.SubElement(OpticalProperties, ET.QName(nsClass['energy'], "glazingRatio"), attrib={'uom': "scale"}).text = \
#         str(win_glazing)
#     return construction_id

def _set_gml_construction_lxml(element, material_ids):
    construction_id = str("GML_" + str(uuid.uuid1()))
    feature_member = ET.SubElement(nroot_E, ET.QName(nsClass.gml, 'featureMember'))
    construction_gml = ET.SubElement(feature_member, ET.QName(nsClass.energy, 'Construction'),
                                     attrib={ET.QName(nsClass.gml, 'id'): str(construction_id)})
    ET.SubElement(construction_gml, ET.QName(nsClass.gml, "description")).text = \
        str(type(element).__name__ +"_construction")
    ET.SubElement(construction_gml, ET.QName(nsClass.gml, "name")).text = \
        str(type(element).__name__ + "_construction")
    ET.SubElement(construction_gml, ET.QName(nsClass.energy, "uValue"), attrib={'uom': "W/K*m2"}).text = \
        str(element.ua_value / element.area)



    for layer_count in element.layer:
        layer_gml = ET.SubElement(construction_gml, ET.QName(nsClass.energy, "layer"))
        Layer_gml = ET.SubElement(layer_gml, ET.QName(nsClass.energy, "Layer"),
                                  attrib={ET.QName(nsClass.gml, 'id'): str("GML_" + str(layer_count.internal_id))})
        layer_comp = ET.SubElement(Layer_gml, ET.QName(nsClass.energy, "layerComponent"))
        Layer_comp = ET.SubElement(layer_comp, ET.QName(nsClass.energy, "LayerComponent"),
                                  attrib={ET.QName(nsClass.gml, 'id'):
                                              str("GML_" + str(layer_count.internal_id) + "_1")})
        ET.SubElement(Layer_comp, ET.QName(nsClass.energy, "areaFraction"), attrib={'uom': "scale"}).text = str(1)
        ET.SubElement(Layer_comp, ET.QName(nsClass.energy, "thickness"), attrib={'uom': "m"}).text = \
            str(layer_count.thickness)
        ET.SubElement(Layer_comp, ET.QName(nsClass.energy, 'material'),
                      attrib={ET.QName(nsClass.xlink, 'href'):
                                  str("#" + "GML_" + layer_count.material.material_id)})

        if layer_count.material.material_id in material_ids:
            pass
        else:
            material_ids.append(layer_count.material.material_id)

            feature_member_material = ET.SubElement(nroot_E, ET.QName(nsClass.gml, 'featureMember'))
            material_gml = ET.SubElement(feature_member_material, ET.QName(nsClass.energy, 'SolidMaterial'),
                                             attrib={ET.QName(nsClass.gml, 'id'):
                                                         str("GML_" + layer_count.material.material_id)})
            ET.SubElement(material_gml, ET.QName(nsClass.gml, "description")).text = \
                str(layer_count.material.name)
            ET.SubElement(material_gml, ET.QName(nsClass.gml, "name")).text = \
                str(layer_count.material.name)
            ET.SubElement(material_gml, ET.QName(nsClass.energy, "conductivity"), attrib={'uom': "W/K*m"}).text = \
                str(layer_count.material.thermal_conduc)
            ET.SubElement(material_gml, ET.QName(nsClass.energy, "density"), attrib={'uom': "kg/m3"}).text = \
                str(layer_count.material.density)
            ET.SubElement(material_gml, ET.QName(nsClass.energy, "specificHeat"), attrib={'uom': "kJ/K*kg"}).text = \
                str(layer_count.material.heat_capac)

    return construction_id


def _set_usage_zone_lxml(thermal_zone, gml_bldg, usage_zone_id):
    usage_zone = thermal_zone.use_conditions
    gml_usage_zone = ET.SubElement(gml_bldg, ET.QName(nsClass.energy, 'usageZone'))
    gml_Usage_Zone = ET.SubElement(gml_usage_zone, ET.QName(nsClass.energy, 'UsageZone'),
                                   attrib={ET.QName(nsClass.gml, 'id'): usage_zone_id})

    """Heating"""
    heating_schedule = ET.SubElement(gml_Usage_Zone, ET.QName(nsClass.energy, 'heatingSchedule'))
    _set_schedule(heating_schedule, usage_zone,  usage_zone_id, "heating")

    """type"""
    ET.SubElement(gml_Usage_Zone, ET.QName(nsClass.energy, 'usageZoneType')).text = str(usage_zone.usage)

    """Cooling"""
    # TODO: Check together with isCooled if AHU is used and set cooling

    """Ventilation"""
    # ventilation_schedule = ET.SubElement(gml_Usage_Zone, ET.QName(nsClass.energy, 'ventilationSchedule'))
    # _set_schedule(usage_zone, ventilation_schedule, usage_zone_id, "ventilation")

    """Occupiedby"""
    occupied_by = ET.SubElement(gml_Usage_Zone, ET.QName(nsClass.energy, 'occupiedBy'))
    occupants = ET.SubElement(occupied_by, ET.QName(nsClass.energy, 'Occupants'),
                              attrib={ET.QName(nsClass.gml, 'id'): (usage_zone_id + "_Occupants")})
    heat_dissipation = ET.SubElement(occupants, ET.QName(nsClass.energy, 'heatDissipation'))
    heat_exchange_type = ET.SubElement(heat_dissipation, ET.QName(nsClass.energy, 'HeatExchangeType'))
    ET.SubElement(heat_exchange_type, ET.QName(nsClass.energy, 'convectiveFraction'), attrib={'uom': "scale"}).text = \
        str(usage_zone.ratio_conv_rad_persons)
    ET.SubElement(heat_exchange_type, ET.QName(nsClass.energy, 'radiantFraction'), attrib={'uom': "scale"}).text = \
        str(1 - usage_zone.ratio_conv_rad_persons)
    ET.SubElement(heat_exchange_type, ET.QName(nsClass.energy, 'totalValue'), attrib={'uom': "W"}).text = \
        str(usage_zone.fixed_heat_flow_rate_persons)
    ET.SubElement(occupants, ET.QName(nsClass.energy, 'numberOfOccupants')).text = str(int(usage_zone.persons*thermal_zone.area))
    occupancy_rate = ET.SubElement(occupants, ET.QName(nsClass.energy, 'occupancyRate'))
    _set_schedule(occupancy_rate, usage_zone, usage_zone_id, "persons")

    """Machines"""
    equipped_with = ET.SubElement(gml_Usage_Zone, ET.QName(nsClass.energy, 'equippedWith'))
    electrical_app = ET.SubElement(equipped_with, ET.QName(nsClass.energy, 'ElectricalAppliances'),
                              attrib={ET.QName(nsClass.gml, 'id'): (usage_zone_id + "_Machines")})

    opperation_schedule = ET.SubElement(electrical_app, ET.QName(nsClass.energy, 'operationSchedule'))
    _set_schedule(opperation_schedule, usage_zone, usage_zone_id, "machines")

    heat_dissipation = ET.SubElement(electrical_app, ET.QName(nsClass.energy, 'heatDissipation'))
    heat_exchange_type = ET.SubElement(heat_dissipation, ET.QName(nsClass.energy, 'HeatExchangeType'))
    ET.SubElement(heat_exchange_type, ET.QName(nsClass.energy, 'convectiveFraction'), attrib={'uom': "scale"}).text = \
        str(usage_zone.ratio_conv_rad_machines)
    ET.SubElement(heat_exchange_type, ET.QName(nsClass.energy, 'radiantFraction'), attrib={'uom': "scale"}).text = \
        str(1 - usage_zone.ratio_conv_rad_machines)
    ET.SubElement(heat_exchange_type, ET.QName(nsClass.energy, 'totalValue'), attrib={'uom': "W/m2"}).text = \
        str(usage_zone.machines)



    """Lighting"""
    equipped_with = ET.SubElement(gml_Usage_Zone, ET.QName(nsClass.energy, 'equippedWith'))
    electrical_app = ET.SubElement(equipped_with, ET.QName(nsClass.energy, 'LightingFacilities'),
                              attrib={ET.QName(nsClass.gml, 'id'): (usage_zone_id + "_Lighting")})

    opperation_schedule = ET.SubElement(electrical_app, ET.QName(nsClass.energy, 'operationSchedule'))
    _set_schedule(opperation_schedule, usage_zone, usage_zone_id, "lighting")

    heat_dissipation = ET.SubElement(electrical_app, ET.QName(nsClass.energy, 'heatDissipation'))
    heat_exchange_type = ET.SubElement(heat_dissipation, ET.QName(nsClass.energy, 'HeatExchangeType'))
    ET.SubElement(heat_exchange_type, ET.QName(nsClass.energy, 'convectiveFraction'), attrib={'uom': "scale"}).text = \
        str(usage_zone.ratio_conv_rad_lighting)
    ET.SubElement(heat_exchange_type, ET.QName(nsClass.energy, 'radiantFraction'), attrib={'uom': "scale"}).text = \
        str(1 - usage_zone.ratio_conv_rad_lighting)
    ET.SubElement(heat_exchange_type, ET.QName(nsClass.energy, 'totalValue'), attrib={'uom': "W/m2"}).text = \
        str(usage_zone.lighting_power)


    # _set_gml_floor_area_lxml(gml_Usage_Zone, nsClass, thermal_zone, ET)


def _set_schedule(schedule_type, usage_zone, usage_zone_id, type_name):
    daily_pattern = ET.SubElement(schedule_type, ET.QName(nsClass.energy, 'DailyPatternSchedule'),
                                  attrib={ET.QName(nsClass.gml, 'id'): str(usage_zone_id + f"_{type_name}_schedule")})
    ET.SubElement(daily_pattern, ET.QName(nsClass.gml, "name")).text = str(type_name)
    period_of_year = ET.SubElement(daily_pattern, ET.QName(nsClass.energy, 'periodOfYear'))
    Period_of_year = ET.SubElement(period_of_year, ET.QName(nsClass.energy, 'PeriodOfYear'))
    period = ET.SubElement(Period_of_year, ET.QName(nsClass.energy, 'period'))

    time_period = ET.SubElement(period, ET.QName(nsClass.gml, 'TimePeriod'))
    ET.SubElement(time_period, ET.QName(nsClass.gml, 'beginPosition')).text = str("2023-01-01T00:00:00")
    ET.SubElement(time_period, ET.QName(nsClass.gml, 'endPosition')).text = str("2023-12-31T00:00:00")

    for day_type in ["weekDay", "weekEnd"]:
        daily_schedule = ET.SubElement(Period_of_year, ET.QName(nsClass.energy, 'dailySchedule'))
        Daily_schedule = ET.SubElement(daily_schedule, ET.QName(nsClass.energy, 'DailySchedule'))
        ET.SubElement(Daily_schedule, ET.QName(nsClass.energy, 'dayType')).text = str(day_type)
        schedule = ET.SubElement(Daily_schedule, ET.QName(nsClass.energy, 'schedule'))
        regular_ts = ET.SubElement(schedule, ET.QName(nsClass.energy, 'RegularTimeSeries'))

        variable_props = ET.SubElement(regular_ts, ET.QName(nsClass.energy, 'variableProperties'))
        time_value_prop = ET.SubElement(variable_props, ET.QName(nsClass.energy, 'TimeValuesProperties'))
        ET.SubElement(time_value_prop, ET.QName(nsClass.energy, 'acquisitionMethod')).text = str("estimation")
        ET.SubElement(time_value_prop, ET.QName(nsClass.energy, 'interpolationType')).text = \
            str("averageInSucceedingInterval")
        ET.SubElement(time_value_prop, ET.QName(nsClass.energy, 'thematicDescription')).text = str("Nominal" + type_name)

        temporal_extant = ET.SubElement(regular_ts, ET.QName(nsClass.energy, 'temporalExtent'))
        time_period = ET.SubElement(temporal_extant, ET.QName(nsClass.gml, 'TimePeriod'))
        ET.SubElement(time_period, ET.QName(nsClass.gml, 'beginPosition')).text = str("00:00:00")
        ET.SubElement(time_period, ET.QName(nsClass.gml, 'endPosition')).text = str("00:00:23")

        ET.SubElement(regular_ts, ET.QName(nsClass.energy, 'timeInterval'), attrib={'unit': "hour"}).text = str(1)

        if type_name == "heating" or "type"=="cooling":
            uom = "K"
        if type_name == "ventilation":
            uom = "1/h"
        else:
            uom = "scale"
#This should be more concise since the check is for a string, not object identity?
        if day_type == "weekDay":

            ET.SubElement(regular_ts, ET.QName(nsClass.energy, 'values'), attrib={'uom': uom}).text = str(usage_zone.schedules[f"{type_name}_profile"].iloc[0:23].values).strip('[]')

        if day_type == "weekEnd":

            ET.SubElement(regular_ts, ET.QName(nsClass.energy, 'values'), attrib={'uom': uom}).text = str(usage_zone.schedules[f"{type_name}_profile"].iloc[120:143].values).strip('[]')

    return


def _save_simulation_results(gml_bldg, results):

    demands = ET.SubElement(gml_bldg, ET.QName(nsClass.energy, 'demands'))
    EnergyDemand = ET.SubElement(demands, ET.QName(nsClass.energy, 'EnergyDemand'),
                                 attrib={ET.QName(nsClass.gml, 'id'): str("GML" + f"_{uuid.uuid1()}")})
    energyAmount = ET.SubElement(EnergyDemand, ET.QName(nsClass.energy, 'energyAmount'))
    regular_ts = ET.SubElement(energyAmount, ET.QName(nsClass.energy, 'RegularTimeSeries'))
    variable_props = ET.SubElement(regular_ts, ET.QName(nsClass.energy, 'variableProperties'))
    time_value_prop = ET.SubElement(variable_props, ET.QName(nsClass.energy, 'TimeValuesProperties'))
    ET.SubElement(time_value_prop, ET.QName(nsClass.energy, 'acquisitionMethod')).text = str("simulation")
    ET.SubElement(time_value_prop, ET.QName(nsClass.energy, 'interpolationType')).text = \
        str("averageInSucceedingInterval")
    ET.SubElement(time_value_prop, ET.QName(nsClass.energy, 'source')).text = \
        str("ROM-AixLib model simulated with Dymola")
    ET.SubElement(time_value_prop, ET.QName(nsClass.energy, 'thematicDescription')).text = str("heating load")
    temporal_extant = ET.SubElement(regular_ts, ET.QName(nsClass.energy, 'temporalExtent'))
    time_period = ET.SubElement(temporal_extant, ET.QName(nsClass.gml, 'TimePeriod'))
    ET.SubElement(time_period, ET.QName(nsClass.gml, 'beginPosition')).text = str("2022-01-01T00:00:00")
    ET.SubElement(time_period, ET.QName(nsClass.gml, 'endPosition')).text = str("2022-12-31T00:00:23")
    ET.SubElement(regular_ts, ET.QName(nsClass.energy, 'timeInterval'), attrib={'unit': "hour"}).text = str(1)
    ET.SubElement(regular_ts, ET.QName(nsClass.energy, 'values'), attrib={'unit': "kWh"}).text = ' '.join(map(str, results))
    ET.SubElement(EnergyDemand, ET.QName(nsClass.energy, 'endUse')).text = str("space heating")

    gml_bldg.insert(3, demands) # insert the demands right after name and description
    return

