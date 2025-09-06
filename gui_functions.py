"""
This code is taken from CityLDT.
Please contact Avichal Malhotra or Simon Raming for any questions.
Original Repo for CityLDT: https://gitlab.e3d.rwth-aachen.de/e3d-software-tools/cityldt/cityldt.git
"""

from PySide6 import QtWidgets, QtGui, QtCore

import os
import lxml.etree as ET
import numpy as np




def screenSizer(posx: int, posy: int, width: int, height: int, app: QtWidgets.QApplication):
    """
    func to get size of screen and scale window dimensions accordingly
    returns posx, posy, width, height, sizefactor
    """
    sizefactor = round(app.primaryScreen().size().height()*0.001)              # factor for scaling window, depending on height
    posx *= sizefactor
    posy *= sizefactor
    width *= sizefactor
    height *= sizefactor
    return posx, posy, width, height, sizefactor



def windowSetup(self, posx: int, posy, width, height, title, winFac = 1) -> None:
    """func for loading icon, setting size and title"""
    try:                                                                            # try to load e3d Icon
        self.setWindowIcon(QtGui.QIcon(r'../pictures/e3dIcon.png'))
    except:
        print('error finding file icon')
    self.setGeometry(posx, posy, width * winFac, height * winFac)                   # setting window size
    self.setFixedSize(width * winFac, height * winFac)                                                # fixing window size
    self.setWindowTitle(title)



def load_banner(self, path: str, sizefactor: float, banner_size: int = 150) -> None:
    """loading image from path to self.vbox"""
    try:
        self.banner = QtWidgets.QLabel(self)
        self.banner.setPixmap(QtGui.QPixmap(path))
        self.banner.setScaledContents(True)
        self.banner.setMinimumHeight(banner_size*sizefactor)
        self.banner.setMaximumHeight(banner_size*sizefactor)
        self.vbox.addWidget(self.banner)
    except:
        print('error finding banner picture')



def messageBox(self, header: str, message: str) -> None:
    """pop up message box with header and message"""
    self.message_complete = QtWidgets.QMessageBox.information(self, header, message)



def next_window(self, window: object, close : bool = True) -> None:
    """calls next window, closes current if True"""
    self.next_window_jump = window
    self.next_window_jump.show()
    if close == True:
        self.hide()


def windowPosition(self):
    """gets current window x and y position"""
    posx = self.geometry().x()
    posy = self.geometry().y()
    return posx, posy



def close_application(self) -> None:
    """quit dialog, to confirm exiting"""
    choice = QtWidgets.QMessageBox.question(self, 'Attention!', 'Do you want to quit?',
                                        QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
    if choice == QtWidgets.QMessageBox.Yes:
        QtCore.QCoreApplication.instance().quit()
    else:
        pass



def progressLoD(self, max: float) -> None:
    """setting up progress bar"""
    while self.completedLoD < max:
        self.completedLoD += 1
        self.pB_scanLoD.setValue(self.completedLoD)
    self.func_eco()


def setTableRowColor(self, colorCode: tuple, index: int) -> None:
    """sets the background color of a row with by index"""
    if self.gB_buildings.isChecked() and index >= 0:
        qColor = QtGui.QColor(*colorCode)
        for j in range(self.tbl_buildings.columnCount()-1):
            try:
                self.tbl_buildings.item(index, j).setBackground(qColor)
            except:
                print('error setting background color')

        self.cBoxes[index].setStyleSheet("QCheckBox {background-color: rgb" + str(colorCode) + "}")

def select_gml(self) -> str:
    """func to select file"""
    tup = QtWidgets.QFileDialog.getOpenFileName(self, 'Select .gml or .xml file', self.tr("*.gml;*.xml"))
    path = tup[0]
    if path.endswith('.gml') or path.endswith('.xml'):
        self.txtB_inPath.setText(path)
        return path
    else:
        self.txtB_inPath.setText('')
        messageBox(self, "Important", "Valid File not selected")
        return ""



def select_folder(self, textBox: QtWidgets.QLineEdit, message : str = "Select Directory") -> str:
    """func to select folder"""
    dirpath = QtWidgets.QFileDialog.getExistingDirectory(self, message)
    if dirpath:
        textBox.setText(dirpath)
        return dirpath
    else:
        messageBox(self, "Important", "Valid Folder not selected")
        return ""


def get_files(self) -> None:
    """func to loop through all the files and buildings and add them to the table widget for selection"""
    resultsDict = {}
    if os.path.isfile(self.inpPath):
        # case for single file
        resultsDict[os.path.basename(self.inpPath)] = get_info_from_file(self.inpPath)
        progressLoD(self, 100)
        pass
    else:
        messageBox(self, "ERROR!", "Input path is not a file.\nPlease reselect input data.")

    display_file_info(self, resultsDict)
    self.btn_next.setEnabled(True)


def get_info_from_file(filename: str) -> dict:
    """gets all files in a building"""
    # parsing file
    print("parsing", filename)
    parser = ET.XMLParser(remove_blank_text=True)
    tree = ET.parse(filename, parser)
    root = tree.getroot()
    nss = root.nsmap

    buildings = {}

    # getting all buildings in file
    buildings_in_file = root.findall('core:cityObjectMember/bldg:Building', nss)

    # iterating all buildings
    for building_E in buildings_in_file:
        buildingName = building_E.attrib['{http://www.opengis.net/gml}id']
        info = get_info_from_building(building_E, nss)
        if info != {}:
            buildings[buildingName] = info
        else:
            # no ground coordinates or LoD found -> can't work with building
            pass
        bps_in_bldg = building_E.findall('./bldg:consistsOfBuildingPart', nss)
        for co_bp_E in bps_in_bldg:
            bp_E = co_bp_E.find('bldg:BuildingPart', nss)
            buildingParIDJoinded = buildingName + '/' + bp_E.attrib['{http://www.opengis.net/gml}id']
            info = get_info_from_building(bp_E, nss)
            if info != {}:
                buildings[buildingParIDJoinded] = info
            else:
                # no ground coordinates or LoD found -> can't work with building
                pass

    return buildings



def display_file_info(self, filesDict: dict) -> None:
    """adds results from get_files to table"""
    self.tbl_buildings.setRowCount(0)
    self.tbl_buildings.horizontalHeader().show()
    self.cBoxes = []

    self.buildingDict = {}
    
    # iterating over files
    for filename in filesDict:
        buildings = filesDict[filename]

        # checking if buildings have been found in file
        if buildings == {}:
            continue

        for i, entry in enumerate(buildings):
            if buildings[entry]["area"] < 50:
                # don't consider buildings with a footprint smaller than 50sqm
                continue

            rowCount = self.tbl_buildings.rowCount()
            self.tbl_buildings.insertRow(rowCount)
            if i == 0:
                # with filename
                newItem = QtWidgets.QTableWidgetItem(str(filename))
                self.tbl_buildings.setItem(rowCount, 0, newItem)
            else:
                # without filename
                newItem = QtWidgets.QTableWidgetItem("")
                self.tbl_buildings.setItem(rowCount, 0, newItem) 
            
            newItem.setToolTip(filename)

            newItem = QtWidgets.QTableWidgetItem(str(entry))
            self.tbl_buildings.setItem(rowCount, 1, newItem)
            newItem.setToolTip(str(entry))

            newItem = QtWidgets.QTableWidgetItem(str(buildings[entry]["LoD"]))
            self.tbl_buildings.setItem(rowCount, 2, newItem)

            newItem = QtWidgets.QTableWidgetItem(str(buildings[entry]["YoC"]))
            self.tbl_buildings.setItem(rowCount, 3, newItem)
            
            newItem = QtWidgets.QTableWidgetItem(str(buildings[entry]["GLA"]))
            self.tbl_buildings.setItem(rowCount, 4, newItem)

            self.cBoxes.append(QtWidgets.QCheckBox(parent=self.tbl_buildings))
            self.cBoxes[-1].clicked.connect(self.onStateChanged)
            self.tbl_buildings.setCellWidget(rowCount, 5, self.cBoxes[-1])

            self.buildingDict[rowCount] = {"filename": filename, 'buildingname': entry, 'values': buildings[entry],
                                           "selected": False}

    # self.tbl_buildings.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
    # self.tbl_buildings.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
    # self.tbl_buildings.horizontalHeader().setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)
    return


def get_info_from_building(element: ET.Element, nss: dict) -> dict:
    """gathers necessary info on building"""
    # LoD, bHeight, rHeight, rHeading, rType, bFunction, YOC, SAG, SBG
    data = {}
    gS_list = getGroundSurfaceCoorOfBuild(element, nss)
    # getting coordinates of groundSurface of the building
    if gS_list == '':
        # no geometry found -> skipping building
        return {}
    else:
        # found geometry of building -> can continue
        data["area"] = round(calcArea(gS_list), 2)

    lod = get_lod(element, nss)
    if lod == -1:
        # lod is not defined -> can't continue with building
        return {}
    else:
        # found LoD -> can continue
        data["LoD"] = lod


    # getting year of construction
    yoc_E = element.find('bldg:yearOfConstruction', nss)
    if yoc_E != None:
        data["YoC"] = yoc_E.text
    else:
        data["YoC"] = ''

    
    # getting sum of storeys above and below ground
    sag_E = element.find('bldg:storeysAboveGround', nss)
    if sag_E != None:
        data["SAG"] = int(sag_E.text)
        data["GLA"] = round(data["area"] * data["SAG"], 2)
    else:
        data["SAG"] = ""
        data["GLA"] = ""


    # get floor height
    sag_height_E = element.find('bldg:storey_heights_above_ground', nss)
    if sag_height_E !=  None:
        data["storeyHeight"] = float(sag_height_E.text)
        if data["GLA"] == "":
            # getting building height
            measuredHeight_E = element.find('bldg:measuredHeight', nss)
            if measuredHeight_E != None:
                data["GLA"] = round(float(measuredHeight_E.text) // data["storeyHeight"] * data["area"], 2)
            
    else:
        data["storeyHeight"] = ""

    return data


def getGroundSurfaceCoorOfBuild(element: ET.Element, nss: dict) -> list:
    """returns the ground surface coor form element"""

    # LoD0
    for tagName in ['bldg:lod0FootPrint', 'bldg:lod0RoofEdge']:
        LoD_zero_E = element.find(tagName, nss)
        if LoD_zero_E != None:
            posList_E = LoD_zero_E.find('.//gml:posList', nss)

            if posList_E != None:
                return get_3dPosList_from_str(posList_E.text)

            else:  # case hamburg lod2 2020
                pos_Es = LoD_zero_E.findall('.//gml:pos', nss)
                polygon = []
                for pos_E in pos_Es:
                    polygon.append(pos_E.text)
                polyStr = ' '.join(polygon)
                return get_3dPosList_from_str(polyStr)

    groundSurface_E = element.find('bldg:boundedBy/bldg:GroundSurface', nss)
    if groundSurface_E != None:
        posList_E = groundSurface_E.find('.//gml:posList', nss)  # searching for list of coordinates

        if posList_E != None:  # case aachen lod2
            return get_3dPosList_from_str(posList_E.text)

        else:  # case hamburg lod2 2020
            pos_Es = groundSurface_E.findall('.//gml:pos', nss)
            polygon = []
            for pos_E in pos_Es:
                polygon.append(pos_E.text)
            polyStr = ' '.join(polygon)
            return get_3dPosList_from_str(polyStr)

    #  checking if no groundSurface element has been found
    else:  # case for lod1 files
        geometry = element.find('bldg:lod1Solid', nss)
        if geometry != None:
            poly_Es = geometry.findall('.//gml:Polygon', nss)
            all_poylgons = []
            for poly_E in poly_Es:
                polygon = []
                posList_E = element.find('.//gml:posList', nss)  # searching for list of coordinates
                if posList_E != None:
                    polyStr = posList_E.text
                else:
                    pos_Es = poly_E.findall('.//gml:pos', nss)  # searching for individual coordinates in polygon
                    for pos_E in pos_Es:
                        polygon.append(pos_E.text)
                    polyStr = ' '.join(polygon)
                coor_list = get_3dPosList_from_str(polyStr)
                all_poylgons.append(coor_list)

            # to get the groundSurface polygon, the average height of each polygon is calculated and the polygon with the lowest average height is considered the groundsurface
            averages = []
            for polygon in all_poylgons:
                # need to get polygon with lowest z coordinate here
                average = 0
                for i in range(len(polygon) - 1):
                    average -= - polygon[i][2]
                averages.append(average / (len(polygon) - 1))

            return all_poylgons[averages.index(min(averages))]
        else:
            return ''


def get_lod(element: ET.Element, nss: dict) -> int:
    """returns the first LoD found in an building or buildingPart"""
    lodFlags = {'bldg:lod0FootPrint': 0, 'bldg:lod1Solid': 1, 'bldg:lod2Solid': 2, 'bldg:lod3MultiSurface': 3,
                'bldg:lod4MultiSurface': 4}
    for flag in lodFlags:
        if element.find('./' + flag, nss) != None:
            return lodFlags[flag]
    return -1



def get_3dPosList_from_str(text: str) -> list:
    coor_list = [float(x) for x in text.split()]
    coor_list = [list(x) for x in zip(coor_list[0::3], coor_list[1::3], coor_list[2::3])]  # creating 2d coordinate array from 1d array
    return coor_list



def saveChangesToCityGML(self, filename: str, newFile: bool, buildingsToChange: dict) -> str:
    """saves changes from buildingsToChange, if wanted, to a new file or overwrites"""
    parser = ET.XMLParser(remove_blank_text=True)
    tree = ET.parse(filename, parser)
    root_E = tree.getroot()
    nss = root_E.nsmap

    for building_E in root_E.findall('core:cityObjectMember/bldg:Building', nss):
        buildingName = building_E.attrib['{http://www.opengis.net/gml}id']
        if buildingName in buildingsToChange.keys():
            valuesToChange = buildingsToChange[buildingName]
            for valueType in ["YoC", "SAG", "storeyHeight", "usage"]:
                if valueType in valuesToChange.keys():
                    setOrChangeValue(building_E, nss, valueType, valuesToChange[valueType])
        bps_in_bldg = building_E.findall('./bldg:consistsOfBuildingPart', nss)
        for co_bp_E in bps_in_bldg:
            bp_E = co_bp_E.find('bldg:BuildingPart', nss)
            buildingParIDJoinded = buildingName + '/' + bp_E.attrib['{http://www.opengis.net/gml}id']
            if buildingParIDJoinded in buildingsToChange.keys():
                valuesToChange = buildingsToChange[buildingParIDJoinded]
                for valueType in ["YoC", "SAG", "storeyHeight", "usage"]:
                    if valueType in valuesToChange.keys():
                        setOrChangeValue(bp_E, nss, valueType, valuesToChange[valueType])

    if newFile:
        expPath = QtWidgets.QFileDialog.getSaveFileName(self, "Select new file location", os.path.join(os.path.dirname(filename), 
                                os.path.splitext(os.path.basename(filename))[0] + "_enriched.gml") ,"CityGML file (*.gml)")[0]
        if expPath == "":
            print("failed to get valid path")
            return ""
    else:
        expPath = filename
    
    tree = ET.ElementTree(root_E)
    tree.write(expPath, pretty_print = True, xml_declaration=True, 
                encoding='utf-8', standalone='yes', method="xml")
    return expPath




def setOrChangeValue(building_E, nss, valueType: str, value:str) -> None:
    """changes (or sets) a value within a building element"""
    elementName = {"YoC": "bldg:yearOfConstruction", "SAG": 'bldg:storeysAboveGround', "storeyHeight": "bldg:storey_heights_above_ground", "usage": "bldg:usage"}
    target_E = building_E.find(elementName[valueType], nss)
    if target_E == None:
        # sBOrder list contains elements in the desired order. running the loop will add their last index if present to the dict, allowing other elements to be appended in the right place
        sBOrder = {'gml:description': -1, 'gml:name': -1, 'core:creationDate': -1, "core:externalReference": -1, 'core:relativeToTerrain': -1, 'gen:measureAttribute': -1, 'gen:stringAttribute': -1, 'bldg:class': -1, 'bldg:function': -1, 'bldg:usage': -1, 'bldg:yearOfConstruction': -1, 'bldg:roofType': -1, 'bldg:measuredHeight': -1, 'bldg:storeysAboveGround': -1, 'bldg:storeysBelowGround': -1, 'bldg:storey_heights_above_ground': -1, 'bldg:storey_heights_below_ground': -1, 'bldg:lod0FootPrint': -1, 'bldg:lod0RoofEdge': -1, 'bldg:lod1Solid': -1, 'bldg:lod2Solid': -1, 'bldg:boundedBy': -1, 'bldg:lod1TerrainIntersection': -1, 'bldg:lod2TerrainIntersection': -1, "bldg:address": -1}
        for tag in sBOrder:
            target = building_E.findall(tag, nss)
            if target != []:
                index = building_E.index(target[-1])
                sBOrder[tag] = index
        # running through all optional elements and adding their index if necessary
        preTag = elementName[valueType]

        found = False
        insertIndex = 0
        for tag in sBOrder:
            if tag == preTag:
                found = True
                sBOrder[tag] = insertIndex +1
                continue
            if not found:
                if sBOrder[tag] != -1 and sBOrder[tag] > insertIndex:
                    insertIndex = sBOrder[tag]
            else:
                if sBOrder[tag] != -1:
                    sBOrder[tag] -=- 1
        target_E = ET.Element(ET.QName(nss["bldg"], elementName[valueType].split(":")[-1]))
        building_E.insert(insertIndex + 1, target_E) 


    if valueType != "usage":
        target_E.text = str(value)
    else:
        archetypeMethod, usage = value.split("/", 1)
        if archetypeMethod == "IWU":
            if usage.startswith("custom") or usage == "office":
                target_E.text = "1120"
            elif usage == "singlefamilydwelling":
                target_E.text = "1000"
            else:
                print("unexpected value for IWU usage")
        elif archetypeMethod.startswith("tabula"):
            if usage == "apartmentblock":
                target_E.text = "1010"
            elif usage == "multifamilyhouse":
                target_E.text = "1010"
            elif usage == "singlefamilyhouse":
                target_E.text = "1000"
            elif usage == "terracedhouse":
                target_E.text = "1000"
            else:
                print("unexpected value for tabula usage")
        elif archetypeMethod == "urbanrenet":
            target_E.text = "1120"
        else:
            print("unexpected value for archetypeMethod")

        # save detailed usage as description
        describ_E = building_E.find("gml:description", nss)
        usageText = "usage: " + archetypeMethod + ", " + usage
        if describ_E != None:
            describ_E.text += "\n                       " + usageText
        else:
            describ_E = ET.Element(ET.QName(nss["gml"], 'description'))
            describ_E.text = usageText
            building_E.insert(0, describ_E)

            

def calcArea(points: list) -> float:
    """calculates the area of 2d polygon"""
    # getting all x and y coordiantes ins seperate lists
    x = [i[0]for i in points]
    y = [i[1]for i in points]
    return 0.5*np.abs(np.dot(x, np.roll(y, 1))-np.dot(y, np.roll(x, 1)))



def getDataFromTable(self) -> dict:
    """function to collect data from Table"""
    buildingsToChange = {}
    for i in range(self.tbl_selBuildings.rowCount()):
        buildingname = self.tbl_selBuildings.item(i, 0).text()
        valuesToChange = {}

        if self.tbl_selBuildings.item(i, 2).text() != "" and self.tbl_selBuildings.item(i, 2).text() != self.valueDict[buildingname]["YoC"]:
            inted = 0
            try:
                inted = int(self.tbl_selBuildings.item(i, 2).text())
            except:
                messageBox(self, "Error", "Failed to convert 'YoC' value (row " + str(i) + ") '" +  self.tbl_selBuildings.item(i, 2).text() + "' to an integer.\nPlease change the value.")
                return None
            valuesToChange["YoC"] = inted

        elif self.tbl_selBuildings.item(i, 2).text() == "" and self.tbl_selBuildings.cellWidget(i, 3).currentIndex() != -1:
            valuesToChange["YoC"] = sum([int(x) for x in self.tbl_selBuildings.cellWidget(i, 3).currentText().split("-")]) // 2

        if self.valueDict[buildingname]["SAG"] == "" and self.valueDict[buildingname]["storeyHeight"] == "":
            if self.tbl_selBuildings.item(i, 4).text() != "":
                inted = 0
                try:
                    inted = int(self.tbl_selBuildings.item(i, 4).text())
                except:
                    messageBox(self, "Error", "Failed to convert 'No. of floors value' (row " + str(i) + ") '" +  self.tbl_selBuildings.item(i, 4).text() + "' to an integer.\nPlease change the value.")
                    return None
                valuesToChange["SAG"] = inted
            elif self.tbl_selBuildings.item(i, 5).text() != "":
                floated = 0
                try:
                    floated = float(self.tbl_selBuildings.item(i, 5).text())
                except:
                    messageBox(self, "Error", "Failed to convert 'Floor height' value (row " + str(i) + ") '" +  self.tbl_selBuildings.item(i, 5).text() + "' to a float.\nPlease change the value.")
                    return None
                valuesToChange["storeyHeight"] = floated
        
        if self.tbl_selBuildings.cellWidget(i, 6).currentIndex() != -1:
            valuesToChange["usage"] = self.tbl_selBuildings.cellWidget(i, 6).currentText()

        if valuesToChange != {}:
            buildingsToChange[self.tbl_selBuildings.item(i, 0).text()] = valuesToChange
    
    return buildingsToChange



def getArchetypes(path: str) -> list:
        """returns a list archetypes in the given path"""
        archeTypes = []
        for entry in os.listdir(path):
            if os.path.isfile(os.path.join(path, entry)) and entry != '__init__.py' and entry.endswith(".py"):
                archeTypes.append(entry.rsplit(".")[0])
            elif os.path.isdir(os.path.join(path, entry)):
                for entry1 in os.listdir(os.path.join(path, entry)):
                    if os.path.isfile(os.path.join(path, entry, entry1)) and entry1 != '__init__.py' and entry1.endswith(".py"):
                        archeTypes.append(entry + "/" + entry1.rsplit(".")[0])
        return archeTypes