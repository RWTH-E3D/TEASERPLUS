import lxml.etree as ET
import collections
from teaser.logic.buildingobjects.building import Building
from teaser.logic.buildingobjects.thermalzone import ThermalZone
from teaser.logic.buildingobjects.buildingphysics.rooftop import Rooftop
from teaser.logic.buildingobjects.buildingphysics.outerwall import OuterWall
from teaser.logic.buildingobjects.buildingphysics.groundfloor import GroundFloor
from teaser.logic.buildingobjects.buildingphysics.layer import Layer
from teaser.logic.buildingobjects.buildingphysics.material import Material
from teaser.logic.buildingobjects.buildingphysics.buildingelement import BuildingElement
from teaser.logic.buildingobjects.buildingphysics.window import Window
from teaser.logic.buildingobjects.buildingphysics.innerwall import InnerWall
from teaser.logic.buildingobjects.buildingphysics.ceiling import Ceiling
from teaser.logic.buildingobjects.buildingphysics.floor import Floor
from teaser.logic.buildingobjects.buildingphysics.door import Door
from teaser.logic.buildingobjects.useconditions import UseConditions
from teaser.data.input.citygml_input import _set_attributes
import numpy as np


def load_ade_lxml(path, prj, chosen_gmls=None):
    """
    Function to load CityGML EnergyADE files cia lxml trees,
    loading CityGML CityObject and FeatureMembers and the
    namespace. Loops through list of chosen Building´s, checks for the
    names and start the extraction

    :param path: string
            path of CityGML EnergyADE file
    :param prj: Project()
            Teaser instance of Project()
    :param chosen_gmls: List[]
            List of chosen CityObject(Buildings)
    """
    if chosen_gmls is None:
        with open(path, 'r') as xml_file:
            tree = ET.parse(xml_file)
            root = tree.getroot()
            namespace = root.nsmap
            buildings = root.findall('core:cityObjectMember/bldg:Building', namespace)
            featureMembers = root.findall('gml:featureMember', namespace)
            construction_members = root.findall('gml:featureMember/energy:Construction', namespace)
            material_members = root.findall('gml:featureMember/energy:SolidMaterial', namespace)
            material_members.extend(root.findall('gml:featureMember/energy:Gas', namespace))
    else:
        buildings, namespace = chosen_gmls

    """Start Loop through selected Buildings in GML file"""

    for i, building_lxml in enumerate(buildings):

        """find building name, if not there, use building id"""
        if building_lxml.find('core:externalReference/core:externalObject/core:name', namespace) is not None:
            bldg_name = building_lxml.find('core:externalReference/core:externalObject/core:name', namespace).text
        else:
            try:
                bldg_name = building_lxml.find('gml:name', namespace).text
            except:
                bldg_name = building_lxml.attrib['{http://www.opengis.net/gml}id']
        print(bldg_name)

        """Create TEASER Building Object and get/set general attributes and Thermal Zone..."""
        bldg = Building(parent=prj)
        _set_attributes(bldg=bldg, gml_bldg=building_lxml, namespace=namespace, bldg_name=bldg_name)
        # bldg.set_gml_attributes()
        construction_dict, constr_win_dict = _get_construction(construction_members)
        material_dict = _get_materials(material_members)
        bldg_info_list, thermal_zone_lxml, usage_zone_lxml = _get_building_info(building_lxml)
        thermal_zone_dict = _get_thermal_zones(thermal_zone_lxml)
        usage_condition_dict = _get_usage_zones(usage_zone_lxml)

        # tz, usage_href, tzb_dict, tzb_dict_openings = _set_thermal_zones(bldg, thermal_zone_dict, construction_dict,
        #                                                                  constr_win_dict, material_dict)
        for tz, usage_href, tzb_dict, tzb_dict_openings in _set_thermal_zones(bldg, thermal_zone_dict,
                                                                              construction_dict):
            _set_building_elements(tz, tzb_dict, tzb_dict_openings, construction_dict,
                                   constr_win_dict, material_dict)
            _set_usage_conditions(prj, tz, usage_href, usage_condition_dict)
            _set_inner_walls(bldg, tz)


def _get_construction(construction_members):
    """
    Function to extract the construction information from EnergyADE files.
    Help python dictionaries:
        layer_dict:={layer_id:[comp_dict]}
        comp_dict:={comp_id:[area fraction, thickness, material #href]}

    :param construction_members: lxml Object
            CityGML EnergyADE FeatureMembers - Construction
    :return: constr_dict
            python dictionary containing the construction, layer information
            and material reference id for Walls, Roofs and Grounds
            {constr_id: [name, u-value,layer_dict]}
    :return: constr_win_dict
            python dictionary containing the construction and optical properties for windows
            {constr_id: [name, u-value, fraction, wave length range, glazing ratio]}
    """

    constr_win_dict = {}
    constr_dict = {}

    for construction in construction_members:
        constr_id = construction.attrib['{http://www.opengis.net/gml}id']
        constr_dict[constr_id] = []
        layer_dict = {}
        for features in construction:
            if features.tag == '{http://www.opengis.net/gml}name':
                constr_name = features.text
                constr_dict[constr_id].append(constr_name)
            elif features.tag == "{http://www.sig3d.org/citygml/2.0/energy/1.0}uValue":
                u_value = features.text
                constr_dict[constr_id].append(u_value)
            # Window Construction
            elif features.tag == "{http://www.sig3d.org/citygml/2.0/energy/1.0}opticalProperties":
                constr_dict.pop(constr_id, None)
                constr_win_dict[constr_id] = []
                constr_win_dict[constr_id].append(constr_name)
                constr_win_dict[constr_id].append(u_value)
                for opticporps in features.iter():
                    if opticporps.tag == "{http://www.sig3d.org/citygml/2.0/energy/1.0}fraction":
                        fraction = opticporps.text
                        constr_win_dict[constr_id].append(fraction)
                    if opticporps.tag == "{http://www.sig3d.org/citygml/2.0/energy/1.0}wavelengthRange":
                        wave_lenght_range = opticporps.text
                        constr_win_dict[constr_id].append(wave_lenght_range)
                    if opticporps.tag == "{http://www.sig3d.org/citygml/2.0/energy/1.0}glazingRatio":
                        glazing_ratio = opticporps.text
                        constr_win_dict[constr_id].append(glazing_ratio)
                pass
            # Wall, Roof and Ground Construction
            elif features.tag == "{http://www.sig3d.org/citygml/2.0/energy/1.0}layer":
                for layer in features:
                    layer_id = layer.attrib['{http://www.opengis.net/gml}id']
                    layer_dict[layer_id] = []
                    comp_dict = {}
                    for layer_comp in layer:
                        for comp in layer_comp:
                            comp_id = comp.attrib['{http://www.opengis.net/gml}id']
                            comp_dict[comp_id] = []
                            for comp_info in comp:
                                if comp_info.tag == "{http://www.sig3d.org/citygml/2.0/energy/1.0}areaFraction":
                                    comp_areaFraction = float(comp_info.text)
                                    comp_dict[comp_id].append(comp_areaFraction)
                                elif comp_info.tag == "{http://www.sig3d.org/citygml/2.0/energy/1.0}thickness":
                                    comp_thickness = float(comp_info.text)
                                    comp_dict[comp_id].append(comp_thickness)
                                elif comp_info.tag == "{http://www.sig3d.org/citygml/2.0/energy/1.0}material":
                                    material_href = comp_info.attrib["{http://www.w3.org/1999/xlink}href"].strip('#')
                                    comp_dict[comp_id].append(material_href)
                                else:
                                    print("Unknown Layer Component")
                    try:
                        layer_dict[layer_id].append(comp_dict)
                    except:
                        pass
        try:
            constr_dict[constr_id].append(layer_dict)
        except:
            pass
    return constr_dict, constr_win_dict


def _get_materials(material_members):
    """
    Function to extract the material information from EnergyADE files.

    :param material_members: lxml Object
            CityGML EnergyADE FeatureMembers - SolidMaterial, Gas
    :return: material_dict
            python dictionary containing the material information
            Solids -> {mat_id: [solid, name, conductivity, density, specific heat capacity]}
            Gases -> {mat_id: [gas, name, is vetilated, r Value]}
    """

    material_dict = {}

    for material in material_members:
        mat_id = material.attrib['{http://www.opengis.net/gml}id']
        material_dict[mat_id] = []
        if material.tag == "{http://www.sig3d.org/citygml/2.0/energy/1.0}SolidMaterial":
            for mat_info in material.iter():
                if mat_info.tag == '{http://www.opengis.net/gml}name':
                    mat_name = mat_info.text
                    material_dict[mat_id].append(mat_name)
                elif mat_info.tag == '{http://www.sig3d.org/citygml/2.0/energy/1.0}conductivity':
                    conductivity = mat_info.text
                    material_dict[mat_id].append(conductivity)
                elif mat_info.tag == '{http://www.sig3d.org/citygml/2.0/energy/1.0}density':
                    density = mat_info.text
                    material_dict[mat_id].append(density)
                elif mat_info.tag == '{http://www.sig3d.org/citygml/2.0/energy/1.0}specificHeat':
                    specific_heat_capacity = mat_info.text
                    material_dict[mat_id].append(specific_heat_capacity)
        elif material.tag == "{http://www.sig3d.org/citygml/2.0/energy/1.0}Gas":
            for mat_info in material.iter():
                if mat_info.tag == '{http://www.opengis.net/gml}name':
                    mat_name = mat_info.text
                    material_dict[mat_id].append(mat_name)
                elif mat_info.tag == '{http://www.sig3d.org/citygml/2.0/energy/1.0}isVentilated':
                    is_ventilated = mat_info.text
                    material_dict[mat_id].append(is_ventilated)
                elif mat_info.tag == '{http://www.sig3d.org/citygml/2.0/energy/1.0}rValue':
                    r_value = mat_info.text
                    material_dict[mat_id].append(r_value)

    return material_dict


def _get_building_info(building_lxml):
    """
    Function to extract volume, floor area and reference points from EnergyADE elements and returns them in
    a list. Additionally the pre-extraction and check for absence of thermalZone and usageZone EnergyADE elements
    is performed. If present they are return separately.

    :param building_lxml: lxml object
            CityGML City Object(Building)
    :return: bldg_info_list
    :return: thermal_zone_lxml
    :return: usage_zone_lxml
    """
    construction_weight = None
    gross_volume = None
    net_volume = None
    gross_floor_area = None
    net_floor_area = None
    reference_srs = None
    reference_point = None
    thermal_zone_lxml = None
    usage_zone_lxml = None

    for energy_member in building_lxml:
        if energy_member.tag == "{http://www.sig3d.org/citygml/2.0/energy/1.0}thermalZone":
            thermal_zone_lxml = energy_member
        elif energy_member.tag == "{http://www.sig3d.org/citygml/2.0/energy/1.0}usageZone":
            usage_zone_lxml = energy_member
        elif energy_member.tag == "{http://www.sig3d.org/citygml/2.0/energy/1.0}constructionWeight":
            construction_weight = energy_member.text
        elif energy_member.tag == "{http://www.sig3d.org/citygml/2.0/energy/1.0}floorArea":
            floorelements = energy_member.getchildren()
            if len(floorelements) > 1:
                print("There are more than one Floor Area in the EnergyADE Data")
            for floor_info in floorelements:
                if floor_info.findtext("{http://www.sig3d.org/citygml/2.0/energy/1.0}type") == "grossFloorArea":
                    gross_floor_area = float(floor_info.findtext("{http://www.sig3d.org/citygml/2.0/energy/1.0}value"))
                elif floor_info.findtext("{http://www.sig3d.org/citygml/2.0/energy/1.0}type") == "netFloorArea":
                    net_floor_area = float(floor_info.findtext("{http://www.sig3d.org/citygml/2.0/energy/1.0}value"))
                else:
                    print("unknown/New Floor Area Type")
                    gross_floor_area = float(floor_info.findtext("{http://www.sig3d.org/citygml/2.0/energy/1.0}value"))
        elif energy_member.tag == "{http://www.sig3d.org/citygml/2.0/energy/1.0}volume":
            volumeelements = energy_member.getchildren()
            if len(volumeelements) > 1:
                print("There are more than one Floor Area in the EnergyADE Data")
            for volume_info in volumeelements:
                if volume_info.findtext("{http://www.sig3d.org/citygml/2.0/energy/1.0}type") == "grossVolume":
                    gross_volume = float(volume_info.findtext("{http://www.sig3d.org/citygml/2.0/energy/1.0}value"))
                elif volume_info.findtext("{http://www.sig3d.org/citygml/2.0/energy/1.0}type") == "netVolume":
                    net_volume = float(volume_info.findtext("{http://www.sig3d.org/citygml/2.0/energy/1.0}value"))
                else:
                    print("unknown/New Volume Area Type")
                    gross_volume = float(volume_info.findtext("{http://www.sig3d.org/citygml/2.0/energy/1.0}value"))
        # may get usefull later :)
        elif energy_member.tag == "{http://www.sig3d.org/citygml/2.0/energy/1.0}referencePoint":
            for point in energy_member:
                reference_srs = point.attrib["srsName"]
                reference_point = point.getchildren()[0].text

    if thermal_zone_lxml is None:
        print("No thermal zones are present in the EnergyADE")
    if usage_zone_lxml is None:
        print("No usage zones are present in the EnergyADE")
    if construction_weight is None:
        print("No construction weight specified in the EnergyADE")
    if gross_volume is None:
        print("No gross volume specified in the EnergyADE")
    if net_volume is None:
        print("No net volume specified in the EnergyADE")
    if net_floor_area is None:
        print("No net floor area specified in the EnergyADE")
    if gross_floor_area is None:
        print("No gross floor area specified in the EnergyADE")
    if reference_srs is None:
        print("No reference SRS specified in the EnergyADE")
    if reference_point is None:
        print("No reference point specified in the EnergyADE")

    bldg_info_list = [construction_weight, gross_volume, net_volume, gross_floor_area, net_floor_area]

    return bldg_info_list, thermal_zone_lxml, usage_zone_lxml


def _get_thermal_zones(thermalzones):
    """
    This function loops through EnergyADE ThermalZone Objects in thermalZone to extract thermal Zone information
    like floor area, volume, iscooled and isheated. As well as extract the thermal boundaries (area, inclination,..)
    which are then sorted by gml ids in python dictionaries and collected in a list in the thermalzone_dict with
    the thermal zone id  as the key. If some values are missing they are substituted by None. There is a check for
    None values at the end of the function:
    thermalzone_dict ->  {tz_id: [usage_zone_href,floor area, floor area type, volume, volume type, isheated, iscooled,
                         Thermal_Zone_Boundary_dict, Thermal_Zone_Boundary_openings-dict]}
    tzb_dict ->          {tzb_id:[type, azimuth, inclination, area, constr_href]}
    tzb_openiongs_dict-> {tzb_opening_id:[tzb_id, opening_area, opening_constr_href]}

    :param thermalzones: lxml Object
            CityGML EnergyADE abstract thermalZone Object,
            which can contain multiple ThermalZone Objects
    :return: thermalzone_dict
            see doc
    """
    thermalzone_dict = {}

    for thermal_zone in thermalzones:

        tzb_dict = {}
        tzb_openings_dict = {}
        floor_type = None
        floor_area = None
        volume_type = None
        volume_area = None
        iscooled = None
        isheated = None
        usage_href = None
        tzb_type = None
        tzb_azimuth = None
        tzb_inclination = None
        tzb_area = None
        constr_href = None
        opening_area = None
        opening_constr_href = None

        tz_id = thermal_zone.attrib['{http://www.opengis.net/gml}id']
        thermalzone_dict[tz_id] = []

        for tz_info in thermal_zone:
            if tz_info.tag == "{http://www.sig3d.org/citygml/2.0/energy/1.0}floorArea":
                floorelements = tz_info.getchildren()
                for floor_info in floorelements:
                    floor_area = floor_info.findtext("{http://www.sig3d.org/citygml/2.0/energy/1.0}value")
                    floor_type = floor_info.findtext("{http://www.sig3d.org/citygml/2.0/energy/1.0}type")
                    # print(floor_type,floor_area)
            elif tz_info.tag == "{http://www.sig3d.org/citygml/2.0/energy/1.0}volume":
                volumeelements = tz_info.getchildren()
                for volume_info in volumeelements:
                    volume_area = float(volume_info.findtext("{http://www.sig3d.org/citygml/2.0/energy/1.0}value"))
                    volume_type = volume_info.findtext("{http://www.sig3d.org/citygml/2.0/energy/1.0}type")
                    # print(volume_area, volume_type)
            elif tz_info.tag == "{http://www.sig3d.org/citygml/2.0/energy/1.0}isCooled":
                iscooled = tz_info.text
            elif tz_info.tag == "{http://www.sig3d.org/citygml/2.0/energy/1.0}isHeated":
                isheated = tz_info.text
            elif tz_info.tag == "{http://www.sig3d.org/citygml/2.0/energy/1.0}contains":
                usage_href = tz_info.attrib["{http://www.w3.org/1999/xlink}href"].strip('#')
            elif tz_info.tag == "{http://www.sig3d.org/citygml/2.0/energy/1.0}boundedBy":
                for thermal_boundary in tz_info:
                    if thermal_boundary.tag == "{http://www.sig3d.org/citygml/2.0/energy/1.0}ThermalBoundary":
                        tzb_id = thermal_boundary.attrib['{http://www.opengis.net/gml}id']
                        tzb_dict[tzb_id] = []
                    for ThermalBoundary in thermal_boundary:
                        if ThermalBoundary.tag == "{http://www.sig3d.org/citygml/2.0/energy/1.0}thermalBoundaryType":
                            tzb_type = ThermalBoundary.text
                        elif ThermalBoundary.tag == "{http://www.sig3d.org/citygml/2.0/energy/1.0}azimuth":
                            tzb_azimuth = ThermalBoundary.text
                        elif ThermalBoundary.tag == "{http://www.sig3d.org/citygml/2.0/energy/1.0}inclination":
                            tzb_inclination = ThermalBoundary.text
                        elif ThermalBoundary.tag == "{http://www.sig3d.org/citygml/2.0/energy/1.0}area":
                            tzb_area = ThermalBoundary.text
                        elif ThermalBoundary.tag == "{http://www.sig3d.org/citygml/2.0/energy/1.0}construction":
                            constr_href = ThermalBoundary.attrib["{http://www.w3.org/1999/xlink}href"].strip('#')
                        elif ThermalBoundary.tag == "{http://www.sig3d.org/citygml/2.0/energy/1.0}contains":
                            for opening in ThermalBoundary.iter():
                                if opening.tag == "{http://www.sig3d.org/citygml/2.0/energy/1.0}ThermalOpening":
                                    tzb_opening_id = opening.attrib['{http://www.opengis.net/gml}id']
                                    tzb_openings_dict[tzb_opening_id] = [tzb_id]
                                elif opening.tag == "{http://www.sig3d.org/citygml/2.0/energy/1.0}area":
                                    opening_area = opening.text
                                elif opening.tag == "{http://www.sig3d.org/citygml/2.0/energy/1.0}construction":
                                    opening_constr_href = opening.attrib["{http://www.w3.org/1999/xlink}href"].strip(
                                        '#')
                            try:
                                tzb_openings_dict[tzb_opening_id].extend((opening_area, tzb_azimuth,
                                                                          tzb_inclination, opening_constr_href))
                            except(UnboundLocalError, KeyError):
                                pass
                    try:
                        tzb_dict[tzb_id].extend((tzb_type, tzb_azimuth, tzb_inclination, tzb_area, constr_href))
                    except(UnboundLocalError, KeyError):
                        pass
        thermalzone_dict[tz_id].extend((usage_href, floor_area, floor_type, volume_area,
                                        volume_type, isheated, iscooled, tzb_dict, tzb_openings_dict))

        for key, values in tzb_openings_dict.items():
            if None in values:
                print("Some value is missing in the Openings Dictionary")
        for key, values in tzb_dict.items():
            if None in values:
                print("Some value is missing in the Thermal Boundary Dictionary")
        for key, values in thermalzone_dict.items():
            if None in values:
                print("Some value is missing in the Thermal Zone Dictionary")

    return thermalzone_dict


def _get_usage_zones(usagezones):
    """
    This function loops through EnergyADE UsageZone Objects in usageZone and extracts the usage zone id and type.
    Furthermore the schedule extraction for heating, cooling and so on is triggered. The schedules are collected in
    separate python dictionaries and stored in the usage zone dict list of schedules with the key being the
    usage zone id. If schedule information is missing in the EnergyADE the schedule dict will be None.

    :param usagezones: lxml Object
            CityGML EnergyADE abstract usageZone Object,
            which can contain multiple UsageZone Objects
    :return: usagezone_dict
            -> {uz_id:[usage_type, heating_schedules_dict,cooling_schedules_dict, ventilation_schedule_dict,
                occupancy_schedule_dict, electrical_appliances_schedule_dict, lighting_schedule_dict]}
    """
    usagezone_dict = {}

    for usage_zone in usagezones:

        usagezone_type = None
        heating_schedules_dict = None
        cooling_schedules_dict = None
        occupancy_schedule_dict = None
        ventilation_schedule_dict = None
        electrical_appliances_schedule_dict = None
        lighting_schedule_dict = None

        uz_id = usage_zone.attrib['{http://www.opengis.net/gml}id']
        usagezone_dict[uz_id] = []
        for uz_info in usage_zone:
            if uz_info.tag == "{http://www.sig3d.org/citygml/2.0/energy/1.0}usageZoneType":
                usagezone_type = uz_info.text
            elif uz_info.tag == "{http://www.sig3d.org/citygml/2.0/energy/1.0}heatingSchedule":
                heating_schedules_dict = _get_schedules(uz_info)
            elif uz_info.tag == "{http://www.sig3d.org/citygml/2.0/energy/1.0}coolingSchedule":
                cooling_schedules_dict = _get_schedules(uz_info)
            elif uz_info.tag == "{http://www.sig3d.org/citygml/2.0/energy/1.0}ventilationSchedule":
                ventilation_schedule_dict = _get_schedules(uz_info)
            elif uz_info.tag == "{http://www.sig3d.org/citygml/2.0/energy/1.0}occupiedBy":
                occupancy_schedule_dict = _get_schedules(uz_info)
            elif uz_info.tag == "{http://www.sig3d.org/citygml/2.0/energy/1.0}equippedWith":
                for appliance in uz_info.iter():
                    if appliance.tag == "{http://www.sig3d.org/citygml/2.0/energy/1.0}ElectricalAppliances":
                        electrical_appliances_schedule_dict = _get_schedules(uz_info)
                    elif appliance.tag == "{http://www.sig3d.org/citygml/2.0/energy/1.0}LightingFacilities":
                        lighting_schedule_dict = _get_schedules(uz_info)

        usagezone_dict[uz_id].extend((usagezone_type, heating_schedules_dict, cooling_schedules_dict,
                                      ventilation_schedule_dict, occupancy_schedule_dict,
                                      electrical_appliances_schedule_dict, lighting_schedule_dict))
    return usagezone_dict


def _get_schedules(schedule):
    """
    Function that extracts the schedules and additional information from EnergyADE schedules Objects.

    :param schedule: lxml Object
            One CityGML EnergyADE schedule Object,
            either heatingSchedule, coolingSchedule, ventilationSchedule,
            occupiedBy or one of two possible equippedWith objects
    :return: schedule_dict
            heating/cooling/ventilation -> {'weekDay': [24 hourly values of Temperature in DegC or flow rate in 1/h],
                                            'weekEnd': [24 hourly values of Temperature in DegC or flow rate in 1/h]}
            occupancy ->                   {'convective_fraction': float in scale, 'radiant_fraction': float in scale,
                                            'total_value': float in Watt, 'number_of_occupants': int
                                            'weekDay': [24 hourly values of occupant present as scale],
                                            'weekEnd': [24 hourly values of occupant present as scale]}
            appliances ->                   {'convective_fraction': float in scale, 'radiant_fraction': float in scale,
                                            'total_value': float in Watt/m²,
                                            'weekDay': [24 hourly values of facility usage as scale],
                                            'weekEnd': [24 hourly values of facility usage as scale]}
            lighting->                      {'convective_fraction': float in scale, 'radiant_fraction': float in scale,
                                            'total_value': float in Watt/m²,
                                            'weekDay': [24 hourly values of lighting usage as scale],
                                            'weekEnd': [24 hourly values of lighting usage as scale]}

    """

    schedule_dict = {}

    for schedule_info in schedule.iter():
        # print(schedule_info.tag)
        if schedule_info.tag == "{http://www.sig3d.org/citygml/2.0/energy/1.0}convectiveFraction":
            convective_fraction = schedule_info.text
            schedule_dict["convective_fraction"] = convective_fraction
        elif schedule_info.tag == "{http://www.sig3d.org/citygml/2.0/energy/1.0}radiantFraction":
            radiant_fraction = schedule_info.text
            schedule_dict["radiant_fraction"] = radiant_fraction
        elif schedule_info.tag == "{http://www.sig3d.org/citygml/2.0/energy/1.0}totalValue":
            total_value = schedule_info.text
            schedule_dict["total_value"] = total_value
        elif schedule_info.tag == "{http://www.sig3d.org/citygml/2.0/energy/1.0}numberOfOccupants":
            number_of_occupants = schedule_info.text
            schedule_dict["number_of_occupants"] = number_of_occupants
        elif schedule_info.tag == "{http://www.sig3d.org/citygml/2.0/energy/1.0}dailySchedule":
            for day_type_info in schedule_info.iter():
                if day_type_info.tag == "{http://www.sig3d.org/citygml/2.0/energy/1.0}dayType":
                    if day_type_info.text == "weekDay":
                        for daily_schedule in schedule_info.iter():
                            if daily_schedule.tag == "{http://www.sig3d.org/citygml/2.0/energy/1.0}values":
                                schedule_weekday = []
                                day_type = "weekDay"
                                values = daily_schedule.text.splitlines()  # if there is a \n newline
                                for value in values:
                                    schedule_weekday.extend(list(map(float, value.split())))
                                schedule_dict["weekDay"] = schedule_weekday
                    elif day_type_info.text == "weekEnd":
                        for daily_schedule in schedule_info.iter():
                            if daily_schedule.tag == "{http://www.sig3d.org/citygml/2.0/energy/1.0}values":
                                schedule_weekend = []
                                day_type = "weekEnd"
                                values = daily_schedule.text.splitlines()  # if there is a \n newline
                                for value in values:
                                    schedule_weekend.extend(list(map(float, value.split())))
                                schedule_dict["weekEnd"] = schedule_weekday

                    else:
                        print("EnergyADE has unknown Day Type")
                        for daily_schedule in schedule_info.iter():
                            if daily_schedule.tag == "{http://www.sig3d.org/citygml/2.0/energy/1.0}values":
                                schedule_weekday = []
                                day_type = "weekDay"
                                values = daily_schedule.text.splitlines()  # if there is a \n newline
                                for value in values:
                                    schedule_weekday.extend(list(map(float, value.split())))
                                schedule_dict["weekDay"] = schedule_weekday

    return schedule_dict


def _set_thermal_zones(bldg, thermal_zone_dict, multizone_split=False):
    """
    Creates a TEASER Thermal Zone Objects for the TEASER Building and sets area and volume.

    Parameters
    ----------
    bldg: TEASER building()
            TEASER Building Object
    thermal_zone_dict: python Dict{}
            {tz_id: [usage_zone_href,floor area, floor area type, volume, volume type, isheated, iscooled,
                         Thermal_Zone_Boundary_dict, Thermal_Zone_Boundary_openings-dict]}
    multizone_split: Boolean
            For Office Buildings, should the single thermal zone from the ADE be only used for office space and
            the rest of the thermal zone split according to office building archetype
{tzb_id:[type, azimuth, inclination, area, constr_href]}
    -------
    tz: TEASER thermalzone()
            TEASER Thermal Zone Object(), holds usage zones and is attached to a TEASER Building Object
    thermal_zone_dict[key][0]: str
            GML Usage Zone ID for the Thermal Zone
    thermal_zone_dict[key][7]: python Dict{}
            Thermal Zone Boundary Information
            tzb_dict -> {tzb_id:[type, azimuth, inclination, area, constr_href]}
    thermal_zone_dict[key][8]: python Dict{}
            Thermal Zone Openings Information
            tzb_openiongs_dict-> {tzb_opening_id:[tzb_id, opening_area, opening_constr_href]}
    """

    net_factor = 1
    volume_factor = 1
    for key in thermal_zone_dict.keys():
        tz = ThermalZone(parent=bldg)
        tz.name = key
        # print(thermal_zone_dict[key])
        if thermal_zone_dict[key][2] is not "netFloorArea":
            tz.area = thermal_zone_dict[key][1] * net_factor
        else:
            tz.area = thermal_zone_dict[key][1]
        if thermal_zone_dict[key][4] is not "netVolume":
            tz.volume = thermal_zone_dict[key][3] * volume_factor
        else:
            tz.volume = thermal_zone_dict[key][3]
        # TODO: Find example for EnergyADE with set Infiltration rate and implement in thermal zone extraction,
        #  otherwise has to be set in usage zone

        """if infiltration rate is specifically set in EnergyADE, otherwise from schedules or default(0.4)"""
        # if tz_infiltration_rate is not None:
        #     tz.infiltration_rate = tz_infiltration_rate
        # else:
        #     pass

        yield tz, thermal_zone_dict[key][0], thermal_zone_dict[key][7], thermal_zone_dict[key][8]


def _set_building_elements(tz, tzb_dict, tzb_dict_openings, construction_dict,
                           constr_win_dict, material_dict, tz_factor=1):
    """
    Creates and set the Buildingelements(Wall, Floor, Roof).

    Parameters
    ----------
    tz: TEASER thermalzone()
            TEASER Thermal Zone Object(), holds usage zones and is attached to a TEASER Building Object
    tzb_dict: python Dict{}
            Thermal Zone Boundary Information
            tzb_dict -> {tzb_id:[type, azimuth, inclination, area, constr_href]}
    tzb_dict_openings: python Dict{}
            Thermal Zone Openings Information
            tzb_openiongs_dict-> {tzb_opening_id:[tzb_id, opening_area, opening_constr_href]}
    construction_dict: python Dict{}
            python dictionary containing the construction, layer information
            and material reference id for Walls, Roofs and Grounds
            {constr_id: [name, u-value,layer_dict]}
    constr_win_dict: python Dict{}
            python dictionary containing the construction and optical properties for windows
            {constr_id: [name, u-value, fraction, wave length range, glazing ratio]}
    material_dict: python Dict{}
            python dictionary containing the material information
            Solids -> {mat_id: [solid, name, conductivity, density, specific heat capacity]}
            Gases -> {mat_id: [gas, name, is vetilated, r Value]}
    tz_factor: float [0,1]
            factor for sizing the Thermal Zones if the option of Multi-zones is selected
    """

    buildingelements = {"roof": Rooftop(parent=tz), "outerWall": OuterWall(parent=tz),
                        "groundSlab": GroundFloor(parent=tz)}
    for key, value in tzb_dict.items():
        if value[0] in buildingelements.keys():
            b_element = buildingelements[value[0]]
            b_element.name = key
        else:
            print(f"Unknown thermalBoundaryType in EnergyADE: {value[0]}")
            raise AttributeError
        b_element.area = value[3] * tz_factor  # MultiZoneTest
        b_element.orientation = value[1]
        b_element.tilt = value[2]
        for key_openings, value_openings in tzb_dict_openings.items():
            if key == key_openings:
                b_element.area = value[3] - value_openings[1] * tz_factor  # MultiZoneTest
            else:
                pass

        """for the EnergyADE version 2.0"""
        # for concof in construction_dict[value[4]]:
        #     if concof[0] is not None:
        #         b_element.outer_convection = concof[0]
        #         # roof.outer_radiation = 0
        #     if concof[1] is not None:
        #         b_element.inner_convection = concof[1]

        for layer_key, comp_list in construction_dict[value[4]][2].items():
            for comp_dict in comp_list:
                for comp_key, comp in comp_dict.items():
                    layer = Layer(parent=b_element, id=comp_key)
                    print(comp[0])
                    if comp[0] != 1.0:
                        print("Layer component doesn't have full fraction!")
                    layer.thickness = comp[1]
                    material = Material(parent=layer)
                    # print(material_dict[comp[2]])
                    material.name = material_dict[comp[2]][0]
                    if len(material_dict[comp[2]]) < 4:
                        # if material_dict[layers[3]][0][0] == 'KIT-FZK-Haus-Luftschicht' or \
                        #     material_dict[layers[3]][0][0] == 'Bau05-Material-Air':
                        isvetilated = material_dict[comp[2]][1]
                        rvalue = material_dict[comp[2]][2]
                        material.thermal_conduc = 0.02225
                        material.density = 1.2041
                        material.heat_capac = 1
                    else:
                        material.density = material_dict[comp[2]][2]
                        material.thermal_conduc = material_dict[comp[2]][1]
                        material.heat_capac = material_dict[comp[2]][3]
                    BuildingElement.add_layer(b_element, layer=layer)

    print(tzb_dict_openings)
    for key, value in tzb_dict_openings.items():
        if value[4] == str("Door_Construction"):
            door = Door(parent=tz)
            door.name = key
            door.area = value[1]
            door.tilt = value[3]
            door.orientation = value[2]
            for layer_key, comp_list in construction_dict[value[4]][2].items():
                for comp_dict in comp_list:
                    for comp_key, comp in comp_dict.items():
                        layer = Layer(parent=door, id=comp_key)
                        if comp[0] != 1.0:
                            print("Layer component doesn't have full fraction!")
                        layer.thickness = comp[1]
                        material = Material(parent=layer)
                        # print(material_dict[comp[2]])
                        material.name = material_dict[comp[2]][0]
                        material.density = material_dict[comp[2]][2]
                        material.thermal_conduc = material_dict[comp[2]][1]
                        material.heat_capac = material_dict[comp[2]][3]
                        BuildingElement.add_layer(b_element, layer=layer)
        else:
            win = Window(parent=tz)
            win.area = value[1]
            win.tilt = value[3]
            win.orientation = value[2]
            # win.u_value = layers[1]
            print(value[4])
            win.g_value = 0.7
            win.a_conv = 0.3
            win.shading_g_total = 1
            win.shading_max_irr = 0.9
            win.name = value[0]
            layer = Layer(parent=win)
            layer.id = value[0]
            layer.thickness = 0.34
            material = Material(parent=layer)
            material.transmittance = 0.3
            material.thermal_conduc = 0.96
            material.solar_absorp = 0.5
            material.density = 2579
            BuildingElement.add_layer(win, layer=layer)


def _set_inner_walls(bldg, tz, construction="heavy"):

    """
    Creating and setting the Inner Walls(Ceiling, floor, inner wall)

    Parameters
    ----------
    bldg: TEASER building()
            TEASER Building Object
    tz: TEASER thermalzone()
            TEASER Thermal Zone Object(), holds usage zones and is attached to a TEASER Building Object
    construction: str
        "heavy" and "light" construction of the inner walls can be selected here
    """

    floor = Floor(parent=tz)
    floor.name = "floor"
    floor.tilt = 0
    floor.load_type_element(year=bldg.year_of_construction, construction=construction)

    ceiling = Ceiling(parent=tz)
    ceiling.name = "ceiling"
    ceiling.tilt = 180
    ceiling.load_type_element(year=bldg.year_of_construction, construction=construction)

    inner = InnerWall(parent=tz)
    inner.name = "innerWall"
    inner.tilt = 90
    inner.load_type_element(year=bldg.year_of_construction, construction=construction)
    tz.set_inner_wall_area()


def _set_usage_conditions(prj, tz, usage_href, usage_condition_dict):
    """
    setting the usage zone, schedules...
    Parameters
    ----------
    prj: Project()
            Teaser instance of Project()
    tz: TEASER thermalzone()
            TEASER Thermal Zone Object(), holds usage zones and is attached to a TEASER Building Object
    usage_href: str
            GML Usage Zone ID for the Thermal Zone
    usage_condition_dict:
            usagezone_dict-> {uz_id:[usage_type, heating_schedules_dict,cooling_schedules_dict,
            ventilation_schedule_dict, occupancy_schedule_dict, electrical_appliances_schedule_dict,
            lighting_schedule_dict]}
    """
    # TODO: Load Use Conditions if already saved, without reloading everything
    if usage_href is None:
        print("The Thermal Zone has no containing Usage Zone")
    else:
        print(usage_condition_dict[usage_href])
        use_cond = UseConditions(parent=tz)
        if usage_condition_dict[usage_href][0] == "residential":
            use_cond.load_use_conditions(zone_usage="Living")
        elif usage_condition_dict[usage_href][0] is None:
            print("No usage type is set, Living preset is used as bases")
            use_cond.load_use_conditions(zone_usage="Living")
        elif usage_condition_dict[usage_href][0] == "office":
            use_cond.load_use_conditions(zone_usage="Single office")
        else:
            print("Unknown usage type is set, Living preset is used as bases")
            use_cond.load_use_conditions(zone_usage="Living")

        use_cond.usage = usage_condition_dict[usage_href][0] + "" + usage_href


        """heating profile"""
        if usage_condition_dict[usage_href][1] is not None:
            print(list(usage_condition_dict[usage_href][1].keys()))
            if len(list(usage_condition_dict[usage_href][1].keys())) == 2:
                for key, value in usage_condition_dict[usage_href][1].items():
                    if key == "weekDay":
                        use_cond.heating_profile = [x + 273.15 for x in value]
                        for i in range(4):
                            use_cond.heating_profile.extend([x + 273.15 for x in value])
                    elif key == "weekEnd":
                        for i in range(2):
                            use_cond.heating_profile.extend([x + 273.15 for x in value])
                    else:
                        print(f"Unknown Day-type{key}")
            else:
                for key, value in usage_condition_dict[usage_href][1].items():
                    print(key)
                    use_cond.heating_profile = [x + 273.15 for x in value]
        else:
            print("No heating profile is defined, default is used")

        """cooling profile"""
        if usage_condition_dict[usage_href][2] is not None:
            use_cond.with_cooling = True
            if len(list(usage_condition_dict[usage_href][2].keys())) == 2:
                for key, value in usage_condition_dict[usage_href][2].items():
                    if key == "weekDay":
                        use_cond.cooling_profile = [x + 273.15 for x in value]
                        for i in range(4):
                            use_cond.cooling_profile.extend([x + 273.15 for x in value])
                    elif key == "weekEnd":
                        for i in range(2):
                            use_cond.cooling_profile.extend([x + 273.15 for x in value])
                    else:
                        print(f"Unknown Day-type{key}")
            else:
                for key, value in usage_condition_dict[usage_href][2].items():
                    print(key)
                    use_cond.cooling_profile = [x + 273.15 for x in value]

        """occupancy profile"""
        if usage_condition_dict[usage_href][4] is not None:
            use_cond.persons = int(usage_condition_dict[usage_href][4]["number_of_occupants"]) / tz.area
            use_cond.ratio_conv_rad_persons = float(usage_condition_dict[usage_href][4]["convective_fraction"]) / \
                                              float(usage_condition_dict[usage_href][4]["radiant_fraction"])
            use_cond.fixed_heat_flow_rate_persons = float(usage_condition_dict[usage_href][4]["total_value"])
            if len(list(usage_condition_dict[usage_href][4].keys())) == 2:
                for key, value in usage_condition_dict[usage_href][4].items():
                    if key == "weekDay":
                        use_cond.persons_profile = [x for x in value]
                        for i in range(4):
                            use_cond.persons_profile.extend([x for x in value])
                    elif key == "weekEnd":
                        for i in range(2):
                            use_cond.persons_profile.extend([x for x in value])
                    else:
                        print(f"Unknown Day-type{key}")
            else:
                for key, value in usage_condition_dict[usage_href][4].items():
                    print(key)
                    use_cond.persons_profile = [x for x in value]

        """machines profile"""
        if usage_condition_dict[usage_href][5] is not None:
            use_cond.machines = float(usage_condition_dict[usage_href][5]["total_value"])
            use_cond.ratio_conv_rad_machines = float(usage_condition_dict[usage_href][5]["convective_fraction"]) / \
                                               float(usage_condition_dict[usage_href][5]["radiant_fraction"])
            if len(list(usage_condition_dict[usage_href][5].keys())) == 2:
                for key, value in usage_condition_dict[usage_href][5].items():
                    if key == "weekDay":
                        use_cond.machines_profile = [x for x in value]
                        for i in range(4):
                            use_cond.machines_profile.extend([x for x in value])
                    elif key == "weekEnd":
                        for i in range(2):
                            use_cond.machines_profile.extend([x for x in value])
                    else:
                        print(f"Unknown Day-type{key}")
            else:
                for key, value in usage_condition_dict[usage_href][5].items():
                    print(key)
                    use_cond.machines_profile = [x for x in value]

        """lighting profile"""
        if usage_condition_dict[usage_href][6] is not None:
            use_cond.lighting_power = float(usage_condition_dict[usage_href][6]["total_value"])
            use_cond.ratio_conv_rad_lighting = float(usage_condition_dict[usage_href][6]["convective_fraction"]) / \
                                               float(usage_condition_dict[usage_href][6]["radiant_fraction"])
            if len(list(usage_condition_dict[usage_href][6].keys())) == 2:
                for key, value in usage_condition_dict[usage_href][6].items():
                    if key == "weekDay":
                        use_cond.lighting_profile = [x for x in value]
                        for i in range(4):
                            use_cond.lighting_profile.extend([x for x in value])
                    elif key == "weekEnd":
                        for i in range(2):
                            use_cond.lighting_profile.extend([x for x in value])
                    else:
                        print(f"Unknown Day-type{key}")
            else:
                for key, value in usage_condition_dict[usage_href][6].items():
                    print(key)
                    use_cond.lighting_profile = [x for x in value]
        tz.use_conditions = use_cond


def load_gmlade(path, prj, chosen_gmls=None):
    """This function loads buildings from a CityGML EnergyADE files

        This function is a proof of concept, be careful using it.

        Parameters
        ----------
        path: string
            path of CityGML file

        prj: Project()
            Teaser instance of Project()

        chosen_gmls: List[of chosen CityObject(Buildings)]

        tzb_dict: python dictionary containing the ThermalBoudary information
            {tzb_gid:[type, azimuth, inclination, area, construction_gid]}

        tzb_dict_openings: python dictionary containing the ThermalBoudaryOpening information
            {tzb_opening_gid:[tzb_gid, area inclination, azimuth, construction_gid]}

        layer_dict: python dictionary containing the layer component information
            {construction_gid:[layer_gid, layer_component_gid, layer_thickness, material_gid]}
            {construction_gid:[name, ,U-value, glazing_ratio, fraction]}

        material_dict: python dictionary containing the Material information
            {material_gid:[name, density, conductivity, heat capacity]}
        """
    if chosen_gmls is None:
        with open(path, 'r') as xml_file:
            gml_bind = citygml.CreateFromDocument(xml_file.read())
            featureMembers = gml_bind.featureMember
    else:
        # TODO: Won't work for multiple EnergyADE buildings (IDEA: save CityObjects_Building separate)
        featureMembers = enumerate(chosen_gmls)

    """Envelope Upper/Lower Corner"""

    # lowercorner = gml_bind.boundedBy.Envelope.lowerCorner.value()
    # uppercorner = gml_bind.boundedBy.Envelope.upperCorner.value()
    # print(f'The Lower Corner:{lowerorner} and Upper Corner:{uppercorner} of the City Object')

    """collects all Construction - and Materialtypes from the EnergyADE file"""

    layer_dict, material_dict, constr_dict = get_layers_materials_dicts(featureMembers=featureMembers)
    for i, city_object in enumerate(featureMembers):
        if isinstance(city_object.Feature, gmlbldg.BuildingType):
            bldg = Building(parent=prj)
            _set_attributes(bldg, gml_bldg=city_object.Feature)
            bldg.type_of_building = get_ade_usage_zone_type(city_object.Feature)
            bldgsizetype, volume, tz_id, tz_infiltration_rate, cooled, heated = \
                get_ade_generalinfo(generalinfo=city_object.Feature)

            """Trying to set ThermalZone"""
            # tz = ThermalZone(parent=bldg)
            # tz.name = tz_id
            # tz.area = get_ade_floor_area(city_object.Feature)
            # tz.volume = volume
            # if tz_infiltration_rate is not None:
            #     tz.infiltration_rate = tz_infiltration_rate
            # else:
            #     pass
            # tzb_dict, tzb_dict_openings = get_ade_thermal_boundaries(city_object.Feature)
            # schedule_heating, schedule_ventilation, schedule_person, schedule_machine, schedule_lighting, \
            # total_value_lighting, convective_fraction_lighting, radiant_fraction_lighting, number_of_occupants, \
            # convective_fraction_persons, radiant_fraction_persons, total_value_machines, convective_fraction_machines, \
            # radiant_fraction_machines = get_ade_schedules(city_object.Feature)
            #
            # set_ade_bldgelements(tz, tzb_dict, tzb_dict_openings, layer_dict, material_dict, constr_dict)
            # set_ade_boundary_conditions(prj, tz, tz_id, bldg.type_of_building, tz.area,
            #                             schedule_heating, schedule_ventilation, schedule_person, schedule_machine,
            #                             schedule_lighting, total_value_lighting, convective_fraction_lighting,
            #                             radiant_fraction_lighting, number_of_occupants, convective_fraction_persons,
            #                             radiant_fraction_persons, total_value_machines, convective_fraction_machines,
            #                             radiant_fraction_machines)
            # # TODO: Write separate function, including the case of Interior Walls already in EnergyADE
            # """Setting Inner Walls"""
            # floor = Floor(parent=tz)
            # floor.name = "floor"
            # floor.tilt = 0
            # floor.load_type_element(year=bldg.year_of_construction, construction='heavy')
            #
            # ceiling = Ceiling(parent=tz)
            # ceiling.name = "ceiling"
            # ceiling.tilt = 180
            # ceiling.load_type_element(year=bldg.year_of_construction, construction='heavy')
            #
            # inner = InnerWall(parent=tz)
            # inner.name = "innerWall"
            # inner.tilt = 90
            # inner.load_type_element(year=bldg.year_of_construction, construction='heavy')
            # tz.set_inner_wall_area()

            """Office building MultiZone model test"""
            zone_area_factors = collections.OrderedDict()
            zone_area_factors["Office"] = \
                [0.5, "Group Office (between 2 and 6 employees)"]
            zone_area_factors["Floor"] = \
                [0.25, "Traffic area"]
            zone_area_factors["Storage"] = \
                [0.15, "Stock, technical equipment, archives"]
            zone_area_factors["Meeting"] = \
                [0.04, "Meeting, Conference, seminar"]
            zone_area_factors["Restroom"] = \
                [0.04, "WC and sanitary rooms in non-residential buildings"]
            zone_area_factors["ICT"] = \
                [0.02, "Data center"]

            for key, value in zone_area_factors.items():
                print(key)
                if key == 'Office':

                    """Trying to set ThermalZone"""
                    tz = ThermalZone(parent=bldg)
                    tz.name = tz_id
                    tz.area = get_ade_floor_area(city_object.Feature) * value[0]
                    tz.volume = volume
                    if tz_infiltration_rate is not None:
                        tz.infiltration_rate = tz_infiltration_rate
                    else:
                        pass
                    tzb_dict, tzb_dict_openings = get_ade_thermal_boundaries(city_object.Feature)
                    schedule_heating, schedule_ventilation, schedule_person, schedule_machine, schedule_lighting, \
                    total_value_lighting, convective_fraction_lighting, radiant_fraction_lighting, number_of_occupants, \
                    convective_fraction_persons, radiant_fraction_persons, total_value_machines, convective_fraction_machines, \
                    radiant_fraction_machines = get_ade_schedules(city_object.Feature)

                    set_ade_bldgelements(tz, tzb_dict, tzb_dict_openings, layer_dict, material_dict, constr_dict,
                                         value[0])
                    set_ade_boundary_conditions(prj, tz, tz_id, bldg.type_of_building, tz.area,
                                                schedule_heating, schedule_ventilation, schedule_person,
                                                schedule_machine,
                                                schedule_lighting, total_value_lighting, convective_fraction_lighting,
                                                radiant_fraction_lighting, number_of_occupants,
                                                convective_fraction_persons,
                                                radiant_fraction_persons, total_value_machines,
                                                convective_fraction_machines,
                                                radiant_fraction_machines)

                    # TODO: Write separate function, including the case of Interior Walls already in EnergyADE
                    """Setting Inner Walls"""
                    floor = Floor(parent=tz)
                    floor.name = "floor"
                    floor.tilt = 0
                    floor.load_type_element(year=bldg.year_of_construction, construction='heavy')

                    ceiling = Ceiling(parent=tz)
                    ceiling.name = "ceiling"
                    ceiling.tilt = 180
                    ceiling.load_type_element(year=bldg.year_of_construction, construction='heavy')

                    inner = InnerWall(parent=tz)
                    inner.name = "innerWall"
                    inner.tilt = 90
                    inner.load_type_element(year=bldg.year_of_construction, construction='heavy')
                    tz.set_inner_wall_area()

                else:
                    tz = ThermalZone(parent=bldg)
                    tz.area = get_ade_floor_area(city_object.Feature) * value[0]
                    tz.name = key
                    tz.volume = volume * value[0]
                    tz.use_conditions = BoundaryConditions(parent=tz)
                    tz.use_conditions.load_use_conditions(value[1], prj.data)
                    tz.use_conditions.with_ahu = False
                    tz.use_conditions.persons *= tz.area * 0.01
                    tz.use_conditions.machines *= tz.area * 0.01
                    tzb_dict, tzb_dict_openings = get_ade_thermal_boundaries(city_object.Feature)
                    set_ade_bldgelements(tz, tzb_dict, tzb_dict_openings, layer_dict, material_dict, constr_dict,
                                         value[0])

                    # TODO: Write separate function, including the case of Interior Walls already in EnergyADE
                    """Setting Inner Walls"""
                    floor = Floor(parent=tz)
                    floor.name = "floor"
                    floor.tilt = 0
                    floor.load_type_element(year=bldg.year_of_construction, construction='heavy')

                    ceiling = Ceiling(parent=tz)
                    ceiling.name = "ceiling"
                    ceiling.tilt = 180
                    ceiling.load_type_element(year=bldg.year_of_construction, construction='heavy')

                    inner = InnerWall(parent=tz)
                    inner.name = "innerWall"
                    inner.tilt = 90
                    inner.load_type_element(year=bldg.year_of_construction, construction='heavy')
                    tz.set_inner_wall_area()


def set_ade_bldgelements(tz, tzb_dict, tzb_dict_openings, layer_dict, material_dict, constr_dict, tz_factor=1):
    """Trying to set Rooftop / with Layers/ Materials"""
    # TODO: Do something nice for Air and other gasses as Materials
    for key, value in tzb_dict.items():
        if value[0] == "roof":
            roof = Rooftop(parent=tz)
            roof.name = key
            for key_openings, value_openings in tzb_dict_openings.items():
                if key == key_openings:
                    roof.area = (value[3] - value_openings[1]) * tz_factor  # MultiZoneTest
                    break
                else:
                    roof.area = value[3] * tz_factor  # MultiZoneTest
            roof.area = value[3] * tz_factor  # MultiZoneTest
            roof.orientation = value[1]
            roof.tilt = value[2]
            for concof in constr_dict[value[4]]:
                if concof[0] is not None:
                    roof.outer_convection = concof[0]
                    # roof.outer_radiation = 0
                if concof[1] is not None:
                    roof.inner_convection = concof[1]
            for layers in layer_dict[value[4]]:
                layer = Layer(parent=roof, id=layers[0])
                layer.thickness = layers[2]
                material = Material(parent=layer)
                material.name = material_dict[layers[3]][0][0]
                if material_dict[layers[3]][0][0] == 'KIT-FZK-Haus-Luftschicht' or \
                        material_dict[layers[3]][0][0] == 'Bau05-Material-Air':
                    rvalue = material_dict[layers[3]][0][2]
                    material.thermal_conduc = 0.02225
                    material.density = 1.2041
                    material.heat_capac = 1
                else:
                    material.density = material_dict[layers[3]][0][1]
                    material.thermal_conduc = material_dict[layers[3]][0][2]
                    material.heat_capac = material_dict[layers[3]][0][3]
                BuildingElement.add_layer(roof, layer=layer)

            # roof.load_type_element(year=bldg.year_of_construction, construction='heavy')

    """trying to set the Outer Wall / with Layers/ Materials"""

    for key, value in tzb_dict.items():
        if value[0] == "outerWall":
            out_wall = OuterWall(parent=tz)
            out_wall.name = key
            openings_area_for_surface = 0
            # TODO: check again for correctness
            for key_openings, value_openings in tzb_dict_openings.items():
                if key == value_openings[0]:
                    openings_area_for_surface += value_openings[1]
            out_wall.area = (value[3] - openings_area_for_surface) * tz_factor  # MultiZoneTest
            print(out_wall.area, value[3])
            # else:
            #     out_wall.area = value[3] * tz_factor
            out_wall.orientation = value[1]
            out_wall.tilt = value[2]
            for concof in constr_dict[value[4]]:
                if concof[0] is not None:
                    out_wall.outer_convection = concof[0]
                    # out_wall.outer_radiation = 0
                if concof[1] is not None:
                    out_wall.inner_convection = concof[1]
            for layers in layer_dict[value[4]]:
                layer = Layer(parent=out_wall, id=layers[0])
                layer.thickness = layers[2]
                material = Material(parent=layer)
                material.name = material_dict[layers[3]][0][0]
                if material_dict[layers[3]][0][0] == 'KIT-FZK-Haus-Luftschicht' or \
                        material_dict[layers[3]][0][0] == 'Bau05-Material-Air':
                    print("went through here")
                    rvalue = material_dict[layers[3]][0][2]
                    material.thermal_conduc = 0.02225
                    material.density = 1.2041
                    material.heat_capac = 1
                else:
                    material.density = material_dict[layers[3]][0][1]
                    material.thermal_conduc = material_dict[layers[3]][0][2]
                    material.heat_capac = material_dict[layers[3]][0][3]
                BuildingElement.add_layer(out_wall, layer=layer)

            # out_wall.load_type_element(year=bldg.year_of_construction, construction='heavy')

    """trying to set the Ground Floor / with Layers/ Materials"""

    for key, value in tzb_dict.items():
        if value[0] == "groundSlab":
            ground = GroundFloor(parent=tz)
            ground.name = key
            ground.area = value[3] * tz_factor  # MultiZoneTest
            ground.orientation = value[1]
            ground.tilt = value[2]
            for concof in constr_dict[value[4]]:
                if concof[0] is not None:
                    ground.outer_convection = concof[0]
                    # ground.outer_radiation = 0
                if concof[1] is not None:
                    ground.inner_convection = concof[1]
            for layers in layer_dict[value[4]]:
                layer = Layer(parent=ground, id=layers[0])
                layer.thickness = layers[2]
                material = Material(parent=layer)
                material.name = material_dict[layers[3]][0][0]
                if material_dict[layers[3]][0][0] == 'KIT-FZK-Haus-Luftschicht' or \
                        material_dict[layers[3]][0][0] == 'Bau05-Material-Air':
                    rvalue = material_dict[layers[3]][0][2]
                    material.thermal_conduc = 0.02225
                    material.density = 1.2041
                    material.heat_capac = 1
                else:
                    material.density = material_dict[layers[3]][0][1]
                    material.thermal_conduc = material_dict[layers[3]][0][2]
                    material.heat_capac = material_dict[layers[3]][0][3]
                BuildingElement.add_layer(ground, layer=layer)

            # ground.load_type_element(year=bldg.year_of_construction, construction='heavy')

    """trying to set the Windows"""
    # todo how to use the information that is given:, glazingratio...

    for key, value in tzb_dict_openings.items():
        if value[4] == str("Door_Construction"):
            door = Door(parent=tz)
            door.name = key
            door.area = value[1]
            door.tilt = value[2]
            door.orientation = value[3]
            for layers in layer_dict[value[4]]:
                layer = Layer(parent=door, id=layers[0])
                layer.thickness = layers[2]
                material = Material(parent=layer)
                material.name = material_dict[layers[3]][0][0]
                material.density = material_dict[layers[3]][0][1]
                material.thermal_conduc = material_dict[layers[3]][0][2]
                material.heat_capac = material_dict[layers[3]][0][3]
            BuildingElement.add_layer(door, layer=layer)
        else:
            win = Window(parent=tz)
            win.area = value[1]
            win.tilt = value[2]
            win.orientation = value[3]
            # win.u_value = layers[1]
            print(value[4])
            for layers in layer_dict[value[4]]:
                win.g_value = 0.7
                win.a_conv = 0.3
                win.shading_g_total = 1
                win.shading_max_irr = 0.9
                win.name = layers[0]
                layer = Layer(parent=win)
                layer.id = value[0]
                layer.thickness = 0.34
                material = Material(parent=layer)
                material.transmittance = 0.3
                material.thermal_conduc = 0.96
                material.solar_absorp = 0.5
                material.density = 2579
            BuildingElement.add_layer(win, layer=layer)
        # win.load_type_element(year=bldg.year_of_construction, construction='heavy')


def set_ade_boundary_conditions(prj, tz, tz_id, type_of_usage, floorareavalue, schedule_heating, schedule_ventilation,
                                schedule_person, schedule_machine, schedule_lighting, total_value_lighting,
                                convective_fraction_lighting, radiant_fraction_lighting, number_of_occupants,
                                convective_fraction_persons, radiant_fraction_persons, total_value_machines,
                                convective_fraction_machines, radiant_fraction_machines):
    """Trying to set the Boundary Conditions"""
    # TODO: look once again over the Boundary Condition calculations and selection

    if tz.infiltration_rate is None:
        tz.infiltration_rate = sum(schedule_ventilation) / len(schedule_ventilation)

    tz.use_conditions = BoundaryConditions(parent=tz)
    tz.use_conditions.load_use_conditions(type_of_usage + "" + tz_id, prj.data)
    print(tz.use_conditions.usage)
    if tz.use_conditions.usage == "Single office":
        tz.use_conditions.load_use_conditions("Living", prj.data)
        tz.use_conditions.usage = type_of_usage + "" + tz_id
        BoundaryConditions.typical_length = np.sqrt(floorareavalue)
        BoundaryConditions.typical_width = np.sqrt(floorareavalue)
        BoundaryConditions.min_temp_heat = 273.15 + min(schedule_heating)
        BoundaryConditions.temp_set_back = max(schedule_heating) - min(schedule_heating)
        # BoundaryConditions.daily_usage_hours = 17
        BoundaryConditions.usage_time = [7, 23]
        BoundaryConditions.daily_operation_heating = 24
        BoundaryConditions.heating_time = [0, 23]
        BoundaryConditions.cooling_time = [0, 23]
        BoundaryConditions.max_temp_cool = 299.15
        BoundaryConditions.set_temp_heat = 273.15 + max(schedule_heating)
        BoundaryConditions.set_temp_cool = 299.15
        BoundaryConditions.min_air_exchange = tz.infiltration_rate

        """Occupants"""

        BoundaryConditions.persons = number_of_occupants
        BoundaryConditions.activity_type_persons = 0
        BoundaryConditions.ratio_conv_rad_persons = max(convective_fraction_persons, radiant_fraction_persons)

        """Machines"""
        # BoundaryConditions.machines = 7.82

        if total_value_machines * tz.area <= 50.0:
            tz.use_conditions.activity_type_machines = 1
        elif total_value_machines * tz.area > 50.0 and total_value_machines * tz.area <= 100.0:
            tz.use_conditions.activity_type_machines = 2
        else:
            tz.use_conditions.activity_type_machines = 3
        tz.use_conditions._ratio_conv_rad_machines = max(convective_fraction_machines, radiant_fraction_machines)

        """Lighting"""

        BoundaryConditions.lighting_power = total_value_lighting
        BoundaryConditions.ratio_conv_rad_lighting = max(convective_fraction_lighting, radiant_fraction_lighting)

        for (schedule, profile) in [(schedule_person, tz.use_conditions.profile_persons),
                                    (schedule_machine, tz.use_conditions.profile_machines),
                                    (schedule_lighting, tz.use_conditions.profile_lighting)]:
            print(schedule, profile)
            if not schedule:
                schedule = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                profile = schedule
            else:
                profile = schedule
            print(profile)
        tz.use_conditions.save_use_conditions(prj.data)
    else:
        tz.use_conditions.load_use_conditions(type_of_usage, prj.data)
