# Created April 2016
# TEASER Development Team
#
#

"""CityGML

This module contains function to load Buildings in the non proprietary
CityGML file format .gml
"""

import lxml.etree as ET
import statistics
from pyproj import Proj, transform
from teaser.data.dataclass import DataClass
from teaser.data.surfacegml import SurfaceGML
from teaser.logic.archetypebuildings.bmvbs.singlefamilydwelling \
                         import SingleFamilyDwelling
from teaser.logic.archetypebuildings.bmvbs.office import Office
from teaser.logic.archetypebuildings.bmvbs.custom.institute import Institute
from teaser.logic.archetypebuildings.bmvbs.custom.institute4 import Institute4
from teaser.logic.archetypebuildings.tabula.de.singlefamilyhouse import SingleFamilyHouse
from teaser.logic.archetypebuildings.tabula.de.multifamilyhouse import MultiFamilyHouse
from teaser.logic.archetypebuildings.tabula.de.terracedhouse import TerracedHouse
from teaser.logic.archetypebuildings.tabula.de.apartmentblock import ApartmentBlock
from teaser.logic.buildingobjects.building import Building

import copy


"""Alkis Building Function Codes Lists"""
alkis_sfh_codes = ["1000", "31001_1000"] #Single Famuly House
alkis_mfh_codes = ["1010", "31001_1010"] #MultiFamilyHouse
alkis_th_codes = [] #TerracedHouse
alkis_office_codes = [] #Offices


def choose_gml_lxml(path, bldg_ids=None, bldg_names=None, bldg_addresses=None):
    """This function loads buildings from a CityGML file and
        selects specific buildings by Id, name ore address

        This function is a proof of concept, be careful using it.

    :param path:string
            path of CityGML file
    :param prj:Project()
            Teaser instance of Project()
    :param bldg_ids:list[string]
            users choice
    :param bldg_names:list[string]
            users choice
    :param bldg_addresses:list[(string,string)]
            users choice

    :return chosen_gmls: list[etree.Element]
    """
    with open(path, 'r') as xml_file:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        namespace = root.nsmap
        buildings_in_file = root.findall('core:cityObjectMember/bldg:Building', namespace)
        boundary_box = root.find("gml:boundedBy/gml:Envelope", namespace)

    chosen_gmls = []

    if bldg_ids is not None:

        for building_lxml in buildings_in_file:
            if building_lxml.attrib['{http://www.opengis.net/gml}id'] is not None and \
                    building_lxml.attrib['{http://www.opengis.net/gml}id'] in bldg_ids:
                chosen_gmls.append(building_lxml)

    if bldg_names is not None:

        for building_lxml in buildings_in_file:
            if building_lxml.find('core:externalReference/core:externalObject/core:name', namespace) is not None and \
            building_lxml.find('core:externalReference/core:externalObject/core:name', namespace).text in bldg_names:
                chosen_gmls.append(building_lxml)

            if building_lxml.find('gml:name', namespace) is not None and \
                    building_lxml.find('gml:name', namespace).text in bldg_names:
                chosen_gmls.append(building_lxml)

    if bldg_addresses is not None:
        for building_lxml in buildings_in_file:
            if building_lxml.find('bldg:address', namespace) is not None and \
                    (building_lxml.find('bldg:address/core:Address/core:xalAddress/xal:AddressDetails/xal:Country'
                                        '/xal:Locality/xal:Thoroughfare/xal:ThoroughfareName', namespace).text,
                     building_lxml.find('bldg:address/core:Address/core:xalAddress/xal:AddressDetails/xal:Country'
                                        '/xal:Locality/xal:Thoroughfare/xal:ThoroughfareNumber', namespace).text) \
                    in bldg_addresses:

                chosen_gmls.append(building_lxml)
    return chosen_gmls, namespace, boundary_box


def load_gml_lxml(path, prj, method, chosen_gmls=None, yoc_list=None):
    """
    This function loads buildings from a CityGML file, checks for a name, BuildingParts and
    start GML surface extraction and consequent building genaration.

    This function is a proof of concept, be careful using it.

    :param path:string
            path of CityGML file
    :param prj:Project()
            Teaser instance of Project()
    :param method: Str
            method for enrichment of single family dwellings
            either default="iwu" or "tabula_de"
            offices always use "iwu"= BMVBS and other residential
            buildings will be always using "tabula_de"
    :param chosen_gmls: List[]
            List of chosen CityObject(Buildings)
    :param yoc_list: List[]
            List of year of construction for chosen gml buildings
    :return: gml_copy_list
    :return: boundary_box
    """

    if chosen_gmls is None:
        with open(path, 'r') as xml_file:
            tree = ET.parse(xml_file)
            root = tree.getroot()
            namespace = root.nsmap
            buildings = root.findall('core:cityObjectMember/bldg:Building', namespace)
            boundary_box = root.find("gml:boundedBy/gml:Envelope", namespace)
    else:
        buildings, namespace, boundary_box = chosen_gmls

    gml_copy_list = []
    """Start Loop through selected Buildings in GML file, assign Archetype by Function and create TEASER building"""

    for i, building_lxml in enumerate(buildings):
        gml_copy_list.append(copy.copy(building_lxml))


        """find building name, if not there, use building id"""
        if building_lxml.find('core:externalReference/core:externalObject/core:name', namespace) is not None:
            bldg_name = building_lxml.find('core:externalReference/core:externalObject/core:name', namespace).text
        else:
            try:
                bldg_name = building_lxml.find('gml:name', namespace).text
            except:
                bldg_name = building_lxml.attrib['{http://www.opengis.net/gml}id']

        """Check for BuildingParts"""
        if building_lxml.find('./bldg:consistsOfBuildingPart', namespace) is not None:
            load_gml_buildingparts_lxml(prj=prj, gml_bldg=building_lxml, boundary_box=boundary_box, namespace=namespace,
                                        bldg_name=bldg_name, method=method)
            continue

        """Assign Archetype"""
        bldg = assign_archetype(prj=prj, building_lxml=building_lxml, namespace=namespace,
                                bldg_name=bldg_name, method=method)

        """Extract GML surface from File"""
        get_gml_surfaces(bldg=bldg, city_object=building_lxml, namespace=namespace)

        """Set Building Attribute"""
        if yoc_list is not None:
            _set_attributes(bldg=bldg, gml_bldg=building_lxml, boundary_box=boundary_box, bldg_yoc=yoc_list[i])
        else:
            _set_attributes(bldg=bldg, gml_bldg=building_lxml, boundary_box=boundary_box,
                            namespace=namespace, bldg_name=bldg_name)

        """Calculate building height through GML surfaces, overwrites measured height from GML Building"""
        bldg.set_height_gml()

        """Calculates net_floor_area and number of toreys in Building with default storey height"""
        try:
            bldg.set_gml_attributes()
        except (UserWarning, AttributeError):
            print(f"{bldg.name} bldg.set_gml_attributes() did not work")
            pass
        """Sets Building Elements"""
        try:
            bldg.generate_from_gml()
        except (UserWarning, AttributeError):
            print(f"{bldg.name} bldg.generate_from_gml() did not work")
            pass

    return gml_copy_list, boundary_box


def load_gml_buildingparts_lxml(prj, gml_bldg, boundary_box, namespace, bldg_name, method, yoc=None, calc_sep=True):
    """
    This function loads buildings parts from a CityGML Buildings,
    assigns archetypes by gml function and creates TEASER building
    instances.

    :param prj: Project()
            Teaser instance of Project()
    :param gml_bldg: lxml object
            CityGML City Object(Building)
    :param namespace:lxml.msmap()
            Original namespaces from CityGML file (root)
    :param bldg_name: Str
            Pass through Building Name extracted from CityGML Building
    :param method: Str
            method for enrichment of single family dwellings
            either default="iwu" or "tabula_de"
            offices always use "iwu"= BMVBS and other residential
            buildings will be always using "tabula_de"
    :param yoc: Int
            year of construction for chosen gml buildings
    :param calc_sep: Boolean
            Decision variable for buildingPart handling, if False BuildingParts are
            calculated as separate Buildings inheriting only function and yoc. If True,
            BuildingsParts are merged together with calculation on the mean measured Height
    """

    building_parts = gml_bldg.findall('./bldg:consistsOfBuildingPart/bldg:BuildingPart', namespace)
    if calc_sep:
        for number_of_buildpart, gml_bldg_part in enumerate(building_parts):
            bldg = assign_archetype(prj=prj, building_lxml=gml_bldg, namespace=namespace,
                                    bldg_name=bldg_name, method=method)

            get_gml_surfaces(bldg=bldg, city_object=gml_bldg_part, namespace=namespace)

            if yoc is not None:
                _set_attributes(bldg=bldg, gml_bldg=gml_bldg,boundary_box=boundary_box, namespace=namespace, bldg_yoc=yoc)
            else:
                _set_attributes(bldg=bldg, gml_bldg=gml_bldg, boundary_box=boundary_box, namespace=namespace, bldg_name=bldg_name,
                                gml_bldg_part=gml_bldg_part, bldg_part=number_of_buildpart)

            bldg.set_height_gml()

            try:
                bldg.set_gml_attributes()
            except (UserWarning, AttributeError):
                print(f"{bldg.name} bldg.set_gml_attributes() did not work")
                pass
            try:
                bldg.generate_from_gml()
            except (UserWarning, AttributeError):
                print(f"{bldg.name} bldg.generate_from_gml() did not work")
                pass

        """BuildingParts are merged"""
        #TODO: Needs testing! Also take a look at called functions in building and set_gml_height()
    else:
        bldg = assign_archetype(prj=prj, building_lxml=gml_bldg, namespace=namespace,
                                bldg_name=bldg_name, method=method)

        measured_heights = []
        for number_of_buildpart, gml_bldg_part in enumerate(building_parts):
            get_gml_surfaces(bldg=bldg, city_object=gml_bldg_part, namespace=namespace)
            measured_heights.append(float(gml_bldg_part.find(".//bldg:measuredHeight", namespace).text))

        if yoc is not None:
            _set_attributes(bldg=bldg, gml_bldg=gml_bldg, namespace=namespace, bldg_name=bldg_name,
                            gml_bldg_part=gml_bldg_part,
                            measured_mean_height=measured_heights.mean(), bldg_yoc=yoc)
        else:
            _set_attributes(bldg=bldg, gml_bldg=gml_bldg, namespace=namespace, bldg_name=bldg_name,
                            gml_bldg_part=gml_bldg_part,
                            measured_mean_height=statistics.mean(measured_heights))

        #bldg.set_height_gml()

        try:
            bldg.set_gml_attributes(merge_building_part=True)
        except (UserWarning, AttributeError):
            print(f"{bldg.name} bldg.set_gml_attributes() did not work")
            pass
        try:
            bldg.generate_from_gml()
        except (UserWarning, AttributeError):
            print(f"{bldg.name} bldg.generate_from_gml() did not work")
            pass


def assign_archetype(prj, building_lxml, namespace, bldg_name, method):
    """
    Assigns a archetype and creates a TEASER building on bases of Bilding Function scrapped from CityGML Building.

    :param prj: Project()
            Teaser instance of Project()
    :param building_lxml: lxml object
            CityGML City Object(Building)
    :param namespace: lxml.msmap()
            Original namespaces from CityGML file (root)
    :param bldg_name: Str
            Pass through Building Name extracted from CityGML Building
    :param method: Str
            method for enrichment of single family dwellings
            either default="iwu" or "tabula_de"
            offices always use "iwu"= BMVBS and other residential
            buildings will be always using "tabula_de"
    :return: bldg - TEASER Building
            An Instant of a TEASER Building in the Project with Name
    """

    if building_lxml.find('bldg:function', namespace) is not None:
        bldg_function = building_lxml.find('bldg:function', namespace).text

        if bldg_function in alkis_sfh_codes:  # Single Family Buildings
            if method == "tabula_de":
                prj.data = DataClass(used_statistic="tabula_de")
                bldg = SingleFamilyHouse(parent=prj, name=bldg_name)
            else:
                prj.data = DataClass(used_statistic='iwu')
                bldg = SingleFamilyDwelling(parent=prj, name=bldg_name)

        elif bldg_function in alkis_mfh_codes:  # Multi Family Buildings
            prj.data = DataClass(used_statistic="tabula_de")
            bldg = MultiFamilyHouse(parent=prj, name=bldg_name)

        elif bldg_function in alkis_mfh_codes:  # Offices
            prj.data = DataClass(used_statistic="iwu")
            bldg = Office(parent=prj, name=bldg_name)

        else:
            bldg = Building(parent=prj,
                            name=bldg_name)
    else:
        bldg = Building(parent=prj, name=bldg_name)
    return bldg


def calc_lat_long(boundary_box, namespace):
    """
    Calculates the latitude and longitude for the middle point of the Boundary Box (City Model Envelope)
    Currently only for epsg:25832
    ToDO: extract srs or crs from envelope name and set into inProj
    Parameters
    ----------
    boundary_box:
    namespace: lxml.msmap()
                Original namespaces from CityGML file (root)

    Returns
    -------
    Rounded Latitude and Longitude of the boundary box
    """
    print(boundary_box.find(".//gml:lowerCorner", namespace).text.split())
    low_cor = boundary_box.find(".//gml:lowerCorner", namespace).text.split()
    upp_cor = boundary_box.find(".//gml:upperCorner", namespace).text.split()
    x1 = (float(low_cor[0]) + float(upp_cor[0]))/2
    y1 = (float(low_cor[1]) + float(upp_cor[1]))/2
    inProj = Proj('epsg:25832')
    outProj = Proj('epsg:4326')
    x2, y2 = transform(inProj, outProj, x1, y1)
    return round(x2, 2), round(y2,2)


def get_gml_surfaces(bldg, city_object, namespace):
    """
    This Function extracts the position coordinates of CityGML Building surfaces and passes them to the SurfaceGML
    class for processing and finally populates the TEASER building gml_surfaces list for further calculation.

    :param namespace: lxml.msmap()
            Original namespaces from CityGML file (root)
    :param bldg: TEASER building()
            TEASER Building Object
    :param city_object: lxml object
            CityGML City Object(Building)
    """

    lod = get_lod(city_object=city_object)
    if lod == 0:
        if city_object.find(".//bldg:measuredHeight", namespace) is not None:
            from itertools import chain
            height = float(city_object.find(".//bldg:measuredHeight", namespace).text)
            a_list = city_object.find("bldg:lod0FootPrint/gml:MultiSurface/gml:surfaceMember/gml:Polygon/"
                                      "gml:exterior/gml:LinearRing/gml:posList", namespace).text.split()
            map_object = map(float, a_list)
            coord_list = list(map_object)
            base = coord_list
            roof = [base[0], base[1], base[2] + height, base[9], base[10], base[11] + height, base[6], base[7],
                    base[8] + height, base[3], base[4], base[5] + height, base[12], base[13], base[14] + height]

            help_list_base = list(zip(*[iter(base)] * 3))
            help_list_roof = list(zip(*[iter(roof)] * 3))

            wall_help_1 = [help_list_base[0], help_list_base[1], help_list_roof[3], help_list_roof[0],
                           help_list_base[0]]
            wall_list_1 = list(chain(*wall_help_1))

            wall_help_2 = [help_list_base[0], help_list_base[3], help_list_roof[1], help_list_roof[0],
                           help_list_base[0]]
            wall_list_2 = list(chain(*wall_help_2))

            wall_help_3 = [help_list_base[2], help_list_base[1], help_list_roof[3], help_list_roof[2],
                           help_list_base[2]]
            wall_list_3 = list(chain(*wall_help_3))

            wall_help_4 = [help_list_base[2], help_list_base[3], help_list_roof[1], help_list_roof[2],
                           help_list_base[2]]
            wall_list_4 = list(chain(*wall_help_4))

            bldg.gml_surfaces.append(SurfaceGML(base))
            bldg.gml_surfaces.append(SurfaceGML(roof))
            bldg.gml_surfaces.append(SurfaceGML(wall_list_1))
            bldg.gml_surfaces.append(SurfaceGML(wall_list_2))
            bldg.gml_surfaces.append(SurfaceGML(wall_list_3))
            bldg.gml_surfaces.append(SurfaceGML(wall_list_4))

        else:
            print("The LoD0 Model, no building-height is defined, set a height or no calculations are possible")

    elif lod == 1:
        boundary_surfaces = city_object.findall('./bldg:lod1Solid', namespace)

    elif lod == 2 or lod == 3:
        boundary_surfaces = city_object.findall('./bldg:boundedBy', namespace)

    if not lod == 0:
        for bound_surf in boundary_surfaces:
            for surf_member in bound_surf.iter():

                # if surf_member.tag == "{http://www.opengis.net/gml}name":
                #     print("Surface Name:", surf_member.text)

                # modelling option 1
                if surf_member.tag == "{http://www.opengis.net/gml}exterior":
                    for surf_pos in surf_member.iter():
                        if "{http://www.opengis.net/gml}posList" in surf_member:
                            if surf_pos.tag == "{http://www.opengis.net/gml}posList":
                                a_list = surf_pos.text.split()
                                map_object = map(float, a_list)
                                coord_list = list(map_object)
                                help = SurfaceGML(coord_list)
                                if help.surface_area > 1:
                                    bldg.gml_surfaces.append(help)

                        # modelling option 2
                        else:
                            if surf_pos.tag == "{http://www.opengis.net/gml}LinearRing":
                                position_list_help = []
                                for pos in surf_pos.iter():
                                    a_list = pos.text.split()
                                    map_object = map(float, a_list)
                                    coord_list = list(map_object)
                                    position_list_help.extend(coord_list)
                                help = SurfaceGML(position_list_help)
                                if help.surface_area > 1:
                                    bldg.gml_surfaces.append(help)
    if lod == 3 or lod == 4:
        openings_name = "Window"
        for bound_surf in boundary_surfaces:
            for surf_member in bound_surf.iter():
                if surf_member.tag == "{http://www.opengis.net/citygml/building/2.0}opening":
                    # if surf_member.tag == "{http://www.opengis.net/gml}name":
                    #     openings_name = surf_member.text
                    #     print("Opening Name:", surf_member.text)
                    for openings in surf_member.iter():
                        if openings.tag == "{http://www.opengis.net/gml}exterior":
                            for openings_pos in openings.iter():
                                if "{http://www.opengis.net/gml}posList" in surf_member:
                                    # modelling option 1
                                    if openings_pos.tag == "{http://www.opengis.net/gml}posList":
                                        a_list = openings_pos.text.split()
                                        map_object = map(float, a_list)
                                        coord_list = list(map_object)
                                        opening = SurfaceGML(coord_list)
                                        opening.name = openings_name
                                        # print(opening.surface_area)
                                        bldg.gml_surfaces.append(opening)
                                else:
                                    # modelling option 2
                                    if openings_pos.tag == "{http://www.opengis.net/gml}LinearRing":
                                        position_list_help = []
                                        for pos in openings_pos.iter():
                                            a_list = pos.text.split()
                                            map_object = map(float, a_list)
                                            coord_list = list(map_object)
                                            position_list_help.extend(coord_list)
                                        help = SurfaceGML(position_list_help)
                                        help.name = openings_name
                                        # print(help.surface_area)
                                        bldg.gml_surfaces.append(help)


def get_lod(city_object):
    """
    Help Function, gets and returns the Level of Detail of a CityGML Building.
    By Simon Raming CityATB

    :param city_object: lxml CityGML City Object(Building)
    :return: CityGML City Object Level of Detail
    """
    lods = []
    for elem in city_object.iter():
        # print(elem)
        try:
            if elem.tag.split("}")[1].startswith('lod'):
                lods.append(elem.tag.split('}')[1][3])
        except:
            pass

    if lods != []:
        lods = list(set(lods))
        if len(lods) > 1:
            print("Check file for LoDs!!!")
        lods.sort()
        lod = int(lods[0])
    return lod


def _set_attributes(bldg, gml_bldg, boundary_box, namespace, bldg_name, gml_bldg_part=None, bldg_part=None,
                    measured_mean_height=None, bldg_yoc=None):
    """This function tries to set attributes for type building generation.

    :param bldg: TEASER building()
            TEASER Building Object
    :param gml_bldg: lxml object
            CityGML City Object(Building)
    :param namespace: lxml.msmap()
            Original namespaces from CityGML file (root)
    :param bldg_name: Str
            Pass through Building Name extracted from CityGML Building
    :param gml_bldg_part:lxml object
            CityGML Building - BuildingPart
    :param bldg_part: int
            Number of BuildingPart in Building (specifically for naming scheme)
    :param measured_mean_height: float
            measured mean height of buildingparts of a GML Building
    :param bldg_yoc: Integer
            Element of yoc_list, past on year of construction

    """
    try:
        # bldg.name = gml_bldg.name[0].value()
        # bldg.name = gml_bldg.id
        if bldg_part is None:
            try:
                bldg.name = bldg_name
            except:
                bldg.name = gml_bldg.name[0].value()
        else:
            try:
                bldg.name = f'{bldg_name}bt_{bldg_part}'
            except:
                bldg.name = gml_bldg.name[0].value()
    except UserWarning:
        bldg.name = gml_bldg.id
        print("no name specified in gml file")
        pass
    try:
        bldg.latitude, bldg.longitude = calc_lat_long(boundary_box=boundary_box, namespace=namespace)
    except (UserWarning, AttributeError):
        print("no Envelope Boundary Box is specified in gml file")
        pass
    try:
        bldg.number_of_floors = int(gml_bldg.find(".//bldg:storeysAboveGround", namespace).text)
    except (UserWarning, AttributeError):
        print("no storeysAboveGround specified in gml file")
        pass
    try:
        bldg.height_of_floors = float(gml_bldg.find(".//bldg:storeyHeightsAboveGround", namespace).text)
    except (UserWarning, AttributeError):
        print("no storeyHeightsAboveGround specified in gml file")
        pass
    if bldg_yoc is None:
        try:
            bldg.year_of_construction = int(gml_bldg.find(".//bldg:yearOfConstruction", namespace).text)
        except (UserWarning, AttributeError):
            print("no yearOfConstruction specified in gml file")
            print("default is set to 1980")
            bldg.year_of_construction = 1980
            pass
    else:
        bldg.year_of_construction = bldg_yoc
    if gml_bldg_part is None:
        try:
            bldg.bldg_height = float(gml_bldg.find(".//bldg:measuredHeight", namespace).text)
        except (UserWarning, AttributeError):
            print("no measuredHeight specified in gml file")
            pass
    elif gml_bldg_part and measured_mean_height is not None:
        bldg.bldg_height = measured_mean_height
    else:
        try:
            bldg.bldg_height = float(gml_bldg_part.find(".//bldg:measuredHeight", namespace).text)
        except (UserWarning, AttributeError):
            print("no measuredHeight specified in gml file")
            pass
