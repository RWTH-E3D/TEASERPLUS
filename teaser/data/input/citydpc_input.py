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


def load_dpc_buildings(prj, citydpc_dataset, common_walls, method):

    for dpc_building in citydpc_dataset.get_building_list():
        # you can get the id by
        bldg_id = dpc_building.gml_id

        """Assign Archetype"""

        bldg = assign_archetype(prj=prj, building=dpc_building,
                                    bldg_name=bldg_id, method=method)

        """Extract GML surface from File"""
        # TODO: is there longer a need for that?
        # get_gml_surfaces(bldg=bldg, city_object=building)
        bldg.gml_surfaces = dpc_building.get_surfaces()
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

    pass


def assign_archetype(prj, building, bldg_name, method, archetype=None):
    """
    Assigns a archetype and creates a TEASER building on bases of Building Function scrapped from CityGML Building.

    :param prj: Project()
            Teaser instance of Project()
    :param building_lxml: lxml object
            CityGML City Object(Building)
    :param bldg_name: Str
            Pass through Building Name extracted from CityGML Building
    :param method: Str
            method for enrichment of single family dwellings
            either default="iwu" or "tabula_de"
            offices always use "iwu"= BMVBS and other residential
            buildings will be always using "tabula_de"
    :param archetype: string
            selected archetype
    :return: bldg - TEASER Building
            An Instant of a TEASER Building in the Project with Name
    """
    if archetype is not None:
        if method == "tabula_de":
            prj.data = DataClass(used_statistic="tabula_de")
            if archetype == "sfh":
                bldg = SingleFamilyHouse(parent=prj, name=bldg_name)
            elif archetype == "mfh":
                bldg = MultiFamilyHouse(parent=prj, name=bldg_name)
            elif archetype == "th":
                bldg = TerracedHouse(parent=prj, name=bldg_name)
            elif archetype == "ap":
                bldg = ApartmentBlock(parent=prj, name=bldg_name)
            else:
                print("Unknown Archetype")
                bldg = Building(parent=prj, name=bldg_name)

        elif method == "iwu":
            prj.data = DataClass(used_statistic='iwu')
            if archetype == "sfd":
                bldg = SingleFamilyDwelling(parent=prj, name=bldg_name)
            elif archetype == "office":
                bldg = Office(parent=prj, name=bldg_name)
            else:
                print("Unknown Archetype")
                bldg = Building(parent=prj, name=bldg_name)

        elif method == "urbanrenet":
            prj.data = DataClass(used_statistic='iwu')
            pass

    elif building.usage is not None:
        bldg_function = building.usage

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
