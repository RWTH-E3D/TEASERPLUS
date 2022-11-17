# -*- coding: utf-8 -*-
"""
TEASER+
Contact:
M.Sc. Avichal Malhotra: malhotra@e3d.rwth-aachen.de
M.Sc. Maxim Shamovich: shamovich@e3d.rwth-aachen.de

www.e3d.rwth-aachen.de
Mathieustr. 30
52074 Aachen

Some GUI functions taken from CityLDT.
Please contact Avichal Malhotra or Simon Raming for any questions.
Original Repo for CityLDT: https://gitlab.e3d.rwth-aachen.de/e3d-software-tools/cityldt/cityldt.git
"""

# import of libraries
import os
import sys
from PySide6 import QtWidgets, QtCore
import gui_functions as gf
import tplusselection as sel

# positions and dimensions of window
POSX = 275
POSY = 100
WIDTH = 650
HEIGHT = 700
SIZEFACTOR = 0
SIZER = True



class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        #initiate the parent
        super(MainWindow,self).__init__()
        self.initUI()


    def initUI(self):
        global POSX, POSY, WIDTH, HEIGHT, SIZEFACTOR, SIZER

        # setup of gui / layout
        if SIZER:
            POSX, POSY, WIDTH, HEIGHT, SIZEFACTOR = gf.screenSizer(POSX, POSY, WIDTH, HEIGHT, app)
            SIZER = False
        gf.windowSetup(self, POSX, POSY, WIDTH, HEIGHT, 'TEASER+')

        # Setting main layout
        self.vbox = QtWidgets.QVBoxLayout(self)
        self.setLayout(self.vbox)

        # Loading banner
        gf.load_banner(self, r'pictures/TEASER+_header.png', SIZEFACTOR)

        #Setting Layout
        self.uGrid = QtWidgets.QGridLayout()

        self.btn_selFile = QtWidgets.QPushButton('Select file')
        self.uGrid.addWidget(self.btn_selFile, 0, 0, 1, 1)

        self.txtB_inPath = QtWidgets.QLineEdit()
        self.txtB_inPath.setPlaceholderText('Path to file or folder')
        self.txtB_inPath.setReadOnly(True)
        self.uGrid.addWidget(self.txtB_inPath, 0, 1, 1, 5)

        self.lbl_scanLoD = QtWidgets.QLabel('LoD scan progress:')
        self.uGrid.addWidget(self.lbl_scanLoD, 1, 0, 1, 1)

        self.pB_scanLoD = QtWidgets.QProgressBar(self)
        self.uGrid.addWidget(self.pB_scanLoD, 1, 1, 1, 5)

        self.vbox.addLayout(self.uGrid)

        # for selecting all or individual buildings
        self.gB_buildings = QtWidgets.QGroupBox('')
        self.vbox.addWidget(self.gB_buildings)
        # self.gB_buildings.setToolTip('When unchecked transformation will be done for all buildings in the file(s)')

        self.bGrid = QtWidgets.QGridLayout()
        self.gB_buildings.setLayout(self.bGrid)

        self.rb_allBuildings = QtWidgets.QRadioButton('Transform all buildings')
        self.bGrid.addWidget(self.rb_allBuildings, 0, 0, 1, 1)
        self.rb_allBuildings.setChecked(True)

        self.rb_selectBuildings = QtWidgets.QRadioButton('Select individual buildings')
        self.bGrid.addWidget(self.rb_selectBuildings, 0, 3, 1, 1)


        self.tbl_buildings = QtWidgets.QTableWidget()
        self.tbl_buildings.setColumnCount(6)
        self.tbl_buildings.setHorizontalHeaderLabels(['File Name', 'Name of Building', 'Level of Detail (LoD)', 'Year of Construction (YoC)', 'Gross Leased Area (GLA)', ''])
        self.tbl_buildings.verticalHeader().hide()
        # self.tbl_buildings.horizontalHeader().hide()
        self.tbl_buildings.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.tbl_buildings.setEnabled(False)
        # self.tbl_buildings.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        # self.tbl_buildings.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        # self.tbl_buildings.horizontalHeader().setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)
        self.tbl_buildings.resizeColumnsToContents()
        self.bGrid.addWidget(self.tbl_buildings, 1, 0, 1, 6)

        # Gridbox for lower grid
        self.lGrid = QtWidgets.QGridLayout()
        self.btn_next = QtWidgets.QPushButton('TEASER Enrichment')
        self.lGrid.addWidget(self.btn_next, 0, 0, 1, 1)
        self.btn_next.setEnabled(False)

        self.btn_teasereco = QtWidgets.QPushButton('TEASEREco')
        self.lGrid.addWidget(self.btn_teasereco, 0, 2, 1, 1)
        self.btn_teasereco.setEnabled(False)

        self.btn_about = QtWidgets.QPushButton('About')
        self.lGrid.addWidget(self.btn_about, 1, 0, 1, 1)

        self.btn_reset = QtWidgets.QPushButton('Reset')
        self.lGrid.addWidget(self.btn_reset, 1, 1, 1, 1)

        self.btn_exit = QtWidgets.QPushButton('Exit')
        self.lGrid.addWidget(self.btn_exit, 1, 2, 1, 1)

        self.vbox.addLayout(self.lGrid)
        self.btn_selFile.clicked.connect(self.func_selectFile)
        self.rb_selectBuildings.toggled.connect(self.func_selB)
        self.btn_about.clicked.connect(self.func_about)
        self.btn_reset.clicked.connect(self.func_reset)
        self.btn_exit.clicked.connect(self.func_exit)
        self.btn_next.clicked.connect(self.func_next)
        self.btn_teasereco.clicked.connect(self.func_eco)


        # setting some defaults
        self.inpPath = ''
        self.expPath = ''
        self.completedLoD = 0
        self.buildingDict = {}

        # table row index to comboBox index
        self.tableDict = {}


    def func_selectFile(self) -> None:
        res = sel.select_gml(self)
        if res:
            self.inpPath = res
            sel.get_files(self)
        else:
            pass


    def func_selB(self) -> None:
        if self.rb_selectBuildings.isChecked():
            self.tbl_buildings.setEnabled(True)
        else:
            self.tbl_buildings.setEnabled(False)

    def func_about(self) -> None:
        global POSX, POSY
        POSX, POSY = gf.windowPosition(self)
        gf.next_window(self, about(), False)

    def func_reset(self) -> None:
        global POSX, POSY
        self.reset_variables()
        POSX, POSY = gf.windowPosition(self)
        gf.next_window(self, MainWindow())

    def reset_variables(self) -> None:
        self.inpPath = ''
        self.completedLoD = 0

    def func_exit(self) -> None:
        gf.close_application(self)

    def func_next(self) -> None:
        """gets current position of """
        global POSX, POSY
        selection = 0
        for key in self.buildingDict:
            if self.rb_allBuildings.isChecked():
                self.buildingDict[key]["selected"] = True
            selection += self.buildingDict[key]["selected"]
        if selection > 0:
            POSX, POSY = gf.windowPosition(self)
            gf.next_window(self, TeaserEnrichment(self.buildingDict, self.inpPath, self))
        else:
            gf.messageBox(self, "Warning", "Please select at least one building!")


    def func_eco(self) -> None:
        self.btn_teasereco.setEnabled(True)

    def onStateChanged(self) -> None:
        """gets called when a checkbox for a building is (un)checked to update the buildingDict"""
        ch = self.sender()
        ix = self.tbl_buildings.indexAt(ch.pos())
        self.buildingDict[ix.row()]["selected"] = ch.isChecked()
        curText = self.tbl_buildings.item(ix.row(), 1).text().split('/')[0]
        for i in range(self.tbl_buildings.rowCount()):
            if i != ix.row():
                if self.tbl_buildings.item(i, 1).text().split('/')[0] == curText:
                    self.cBoxes[i].setChecked(ch.isChecked())
                    self.buildingDict[i]["selected"] = ch.isChecked()
                    self.checkBoxChange(i, ch.isChecked())
        self.checkBoxChange(ix.row(), ch.isChecked())

    def checkBoxChange(self, row: int, state: bool) -> None:
        """changes Table"""
        if state:
            colorCode = (251, 255, 0)

        else:
            colorCode = (255, 255, 255)
            
        gf.setTableRowColor(self, colorCode, row)



class TeaserEnrichment(QtWidgets.QWidget):
    """window to enrich / change building information"""
    def __init__(self, buildingDict: dict, inpPath: str, mainWindow):
        super(TeaserEnrichment, self).__init__()
        self.buildingDict = buildingDict
        self.inpPath = inpPath
        self.mW = mainWindow
        self.initUI()

    def initUI(self):
        global POSX, POSY, WIDTH, HEIGHT, SIZEFACTOR, SIZER
        gf.windowSetup(self, POSX, POSY, WIDTH, HEIGHT, 'TEASER+ - Enrichment')

        self.vbox = QtWidgets.QVBoxLayout(self)
        self.setLayout(self.vbox)

        gf.load_banner(self, r'pictures/TEASER+_header.png', SIZEFACTOR)

        self.tbl_selBuildings = QtWidgets.QTableWidget()
        self.tbl_selBuildings.setColumnCount(7)
        self.tbl_selBuildings.setHorizontalHeaderLabels(['Name of building/utility', 'LoD', 'YoC', 'YoC Class', 'No. of floors', 'Floor height', 'Usage Type'])
        self.tbl_selBuildings.setEditTriggers(QtWidgets.QAbstractItemView.DoubleClicked)
        self.tbl_selBuildings.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.vbox.addWidget(self.tbl_selBuildings)


        self.lGrid = QtWidgets.QGridLayout()
        
        self.comB_method = QtWidgets.QComboBox()
        self.comB_method.addItems(["Choose method", "IWU", "tabula_de", "tabula_dk", "urbanrenet"])
        self.lGrid.addWidget(self.comB_method, 0, 0, 1, 1)

        self.btn_saveToCityGML = QtWidgets.QPushButton("Save to CityGML file")
        self.lGrid.addWidget(self.btn_saveToCityGML, 1, 0, 1, 1)

        self.btn_saveToNewCityGML = QtWidgets.QPushButton("Save to new CityGML file")
        self.lGrid.addWidget(self.btn_saveToNewCityGML, 1, 1, 1, 1)

        self.btn_setupSim = QtWidgets.QPushButton("Setup simulation")
        self.btn_setupSim.setToolTip("Please save changes first")
        self.lGrid.addWidget(self.btn_setupSim, 2, 0, 1, 1)

        self.btn_returnMain = QtWidgets.QPushButton("Return to main window")
        self.lGrid.addWidget(self.btn_returnMain, 2, 1, 1, 1)

        self.vbox.addLayout(self.lGrid)

        self.btn_saveToCityGML.clicked.connect(lambda: self.func_saveToCityGML(False))
        self.btn_saveToNewCityGML.clicked.connect(lambda: self.func_saveToCityGML(True))
        self.btn_returnMain.clicked.connect(self.func_returnToMain)
        self.btn_setupSim.clicked.connect(self.func_setupSim)

        self.comB_method.currentTextChanged.connect(self.func_methodChanged)

        self.valueDict = {}

        self.combBoxesYoc = []
        self.combBoxesUse = []

        # for storing path to file
        self.fileToSimulate = ""
        # for checking if recent changes are identical to saved changes
        self.savedChanges = {}

        for key in self.buildingDict:
            # make sure that the building is selected
            if not self.buildingDict[key]["selected"]:
                continue

            rowCount = self.tbl_selBuildings.rowCount()
            self.tbl_selBuildings.insertRow(rowCount)
            
            newItem = QtWidgets.QTableWidgetItem(self.buildingDict[key]["buildingname"])
            newItem.setFlags(newItem.flags() & ~QtCore.Qt.ItemIsEditable)
            newItem.setToolTip(self.buildingDict[key]["buildingname"])
            self.tbl_selBuildings.setItem(rowCount, 0, newItem)


            newItem = QtWidgets.QTableWidgetItem(str(self.buildingDict[key]["values"]["LoD"]))
            newItem.setFlags(newItem.flags() & ~QtCore.Qt.ItemIsEditable)
            self.tbl_selBuildings.setItem(rowCount, 1, newItem)

            newItem = QtWidgets.QTableWidgetItem(str(self.buildingDict[key]["values"]["YoC"]))
            self.tbl_selBuildings.setItem(rowCount, 2, newItem)

            self.combBoxesYoc.append(QtWidgets.QComboBox(parent=self.tbl_selBuildings))
            self.combBoxesYoc[-1].addItems(["choose method first"])
            self.tbl_selBuildings.setCellWidget(rowCount, 3, self.combBoxesYoc[-1])

            newItem = QtWidgets.QTableWidgetItem(str(self.buildingDict[key]["values"]["SAG"]))
            self.tbl_selBuildings.setItem(rowCount, 4, newItem)
            
            newItem = QtWidgets.QTableWidgetItem(str(self.buildingDict[key]["values"]["storeyHeight"]))
            self.tbl_selBuildings.setItem(rowCount, 5, newItem)

            self.combBoxesUse.append(QtWidgets.QComboBox(parent=self.tbl_selBuildings))
            self.combBoxesUse[-1].addItems(["choose method first"])
            self.tbl_selBuildings.setCellWidget(rowCount, 6, self.combBoxesUse[-1])

            # make changes to editabiltiy of the table items
            if self.buildingDict[key]["values"]["YoC"] != "":
                self.tbl_selBuildings.cellWidget(rowCount, 3).setEnabled(False)

            if self.buildingDict[key]["values"]["SAG"] != "" or self.buildingDict[key]["values"]["storeyHeight"] != "":
                self.tbl_selBuildings.item(rowCount, 5).setFlags(self.tbl_selBuildings.item(rowCount, 5).flags() & ~QtCore.Qt.ItemIsEditable)
                self.tbl_selBuildings.item(rowCount, 4).setFlags(self.tbl_selBuildings.item(rowCount, 4).flags() & ~QtCore.Qt.ItemIsEditable)


            self.valueDict[self.buildingDict[key]["buildingname"]] = self.buildingDict[key]["values"]


        self.tbl_selBuildings.itemChanged.connect(self.tableUpdater)



    def func_saveToCityGML(self, newFile: bool) -> None:
        """function to save changes from self.tbl_selBuildings to either the exisitng or a new file"""
        buildingsToChange = sel.getDataFromTable(self)
        
        if buildingsToChange == None:
            # failed to get values -> abort
            return
        elif buildingsToChange == {}:
            gf.messageBox(self, "Important", "Please make changes before saving.")
            return

        path = sel.saveChangesToCityGML(self, self.inpPath, newFile, buildingsToChange)
        if path != "":
            self.savedChanges = buildingsToChange
            self.fileToSimulate = path
            self.btn_setupSim.setEnabled(True)
            self.btn_setupSim.setToolTip("")



    def tableUpdater(self, item: QtWidgets.QTableWidgetItem) -> None:
        """function, called when something is changed within the table, to update QTableWidgetItem flags"""
        if item.column() == 2:
            if item.text() != "":
                self.tbl_selBuildings.cellWidget(item.row(), 3).setCurrentIndex(0)
                self.tbl_selBuildings.cellWidget(item.row(), 3).setEnabled(False)
            else:
                self.tbl_selBuildings.cellWidget(item.row(), 3).setEnabled(True)
        elif item.column() == 4:
            if item.text() == "":
                self.tbl_selBuildings.item(item.row(), 5).setFlags(self.tbl_selBuildings.item(item.row(), 5).flags() | QtCore.Qt.ItemIsEditable)



    def func_methodChanged(self) -> None:
        """function to update comboBoxes when method is changed"""
        if self.comB_method.itemText(0) == "Choose method":
            self.comB_method.removeItem(0)

        # yoc_classes default from TypeBuildingElements.json
        yoc_classes = ["0-1918", "1919-1948", "1949-1968", "1969-1978", "1979-1983", "1984-1994", "1995-2015"]


        if self.comB_method.currentText() == "IWU":
            basepath = os.path.join("teaser/logic/archetypebuildings/bmvbs")
                    
        elif self.comB_method.currentText() == "tabula_de":
            basepath = os.path.join("teaser/logic/archetypebuildings/tabula/de")
            yoc_classes = ["0-1859", "1860-1918", "1919-1948", "1949-1957", "1958-1968", "1969-1978", "1979-1983", "1984-1994", "1995-2001", "2002-2009", "2010-2015", "2016-2100"]

        elif self.comB_method.currentText() == "tabula_dk":
            basepath = os.path.join("teaser/logic/archetypebuildings/tabula/dk")
            yoc_classes = ["0-1850", "1851-1931", "1931-1950" "1951-1960", "1961-1972", "1973-1978", "1979-1998", "1999-2006", "2007-2010"]
            
        elif self.comB_method.currentText() == "urbanrenet":
            basepath = os.path.join("teaser/logic/archetypebuildings/urbanrenet")

        for combBox in self.combBoxesYoc:
            if combBox.count() == 1:
                combBox.removeItem(0)
                combBox.addItem("click to select")
            i = combBox.currentIndex()
            toRemove = list(range(1, combBox.count()))
            if i != 0:
                toRemove.remove(i)
            toRemove.reverse()
            for y in toRemove:
                combBox.removeItem(y)
            combBox.addItems(yoc_classes)

        archeTypes = sel.getArchetypes(basepath)
        archeTypes = [self.comB_method.currentText() + "/" + x for x in archeTypes]
        for combBox in self.combBoxesUse:
            if combBox.count() == 1:
                combBox.removeItem(0)
                combBox.addItem("click to select")
            i = combBox.currentIndex()
            toRemove = list(range(1, combBox.count()))
            if i != 0:
                toRemove.remove(i)
            toRemove.reverse()
            for y in toRemove:
                combBox.removeItem(y)
            
            combBox.addItems(archeTypes)
            


    def func_setupSim(self) -> None:
        """ first checks if there is info that would have needed to be saved"""

        buildingsToChange = sel.getDataFromTable(self)

        if buildingsToChange == {} and self.savedChanges == {}:
            # got no changes to save -> can continue with original file
            fileToSimulate = self.inpPath
        elif buildingsToChange == None:
            # failed to get values -> abort
            return
        elif buildingsToChange != self.savedChanges:
            gf.messageBox(self, "Important - unsaved changes!",
                          "Please make sure to save your changes before continuing!")
            return
        else:
            # changed values are all saved
            fileToSimulate = self.fileToSimulate
        global POSX, POSY
        POSX, POSY = gf.windowPosition(self)
        gf.next_window(self, SetupSimulation(self, self.buildingDict, buildingsToChange, fileToSimulate))


    def func_returnToMain(self) -> None:
        self.hide()
        self.mW.show()


        

class SetupSimulation(QtWidgets.QWidget):
    """Window to setup simulation"""
    def __init__(self, enrich: object, buildingDict: dict, buildingsToChange:dict, fileToSimulate: str):
        super(SetupSimulation, self).__init__()
        self.enrich = enrich
        self.buildingDict = buildingDict
        self.buildingsToChange = buildingsToChange
        self.fileToSimulate = fileToSimulate
        self.initUI()

    def initUI(self):
        global POSX, POSY, WIDTH, HEIGHT, SIZEFACTOR, SIZER
        gf.windowSetup(self, POSX, POSY, WIDTH, HEIGHT - (350 *SIZEFACTOR),
                       'TEASER+ - Setup simulation')

        self.vbox = QtWidgets.QVBoxLayout(self)
        self.setLayout(self.vbox)

        self.gB_categories = QtWidgets.QGroupBox("Select categories for impact assessment (LCIA)")
        self.vbox.addWidget(self.gB_categories)

        self.uGrid = QtWidgets.QGridLayout()
        self.gB_categories.setLayout(self.uGrid)

        self.chB_gwp = QtWidgets.QCheckBox("GWP")
        self.uGrid.addWidget(self.chB_gwp, 0, 0, 1, 1)

        self.chB_odp = QtWidgets.QCheckBox("ODP")
        self.uGrid.addWidget(self.chB_odp, 0, 1, 1, 1)

        self.chB_ToDo = QtWidgets.QCheckBox("ToDo")
        self.uGrid.addWidget(self.chB_ToDo, 0, 2, 1, 1)

        self.mGrid = QtWidgets.QGridLayout()
        self.vbox.addLayout(self.mGrid)

        self.btn_heatloadPath = QtWidgets.QPushButton("Select TEASER Heatload output path")
        self.mGrid.addWidget(self.btn_heatloadPath, 0, 0, 1, 1)

        self.txtB_heatloadPath = QtWidgets.QLineEdit("")
        self.txtB_heatloadPath.setPlaceholderText("Path to heatload file")
        self.txtB_heatloadPath.setEnabled(False)
        self.mGrid.addWidget(self.txtB_heatloadPath, 0, 1, 1, 4)

        self.btn_tecoLCApath = QtWidgets.QPushButton("Select Teco LCA .CSV output path")
        self.mGrid.addWidget(self.btn_tecoLCApath, 1, 0, 1, 1)

        self.txtB_tecoLCApath = QtWidgets.QLineEdit("")
        self.txtB_tecoLCApath.setPlaceholderText("Path to .csv output path")
        self.txtB_tecoLCApath.setEnabled(False)
        self.mGrid.addWidget(self.txtB_tecoLCApath, 1, 1, 1, 4)

        self.lbl_weatherFile = QtWidgets.QLabel("Select weather file")
        self.mGrid.addWidget(self.lbl_weatherFile, 2, 0, 1, 1)

        self.comB_weatherFile = QtWidgets.QComboBox()
        self.mGrid.addWidget(self.comB_weatherFile, 2, 1, 1, 4)

        self.comB_weatherFile.addItem("select weather file")
        weatherpath = os.path.join("teaser", "data", "input", "inputdata", "weatherdata")
        for candidate in os.listdir(weatherpath):
            if os.path.isfile(os.path.join(weatherpath, candidate)) and candidate.endswith(".mos"):
                self.comB_weatherFile.addItem(candidate)

        self.btn_expPath = QtWidgets.QPushButton("Select export path")
        self.mGrid.addWidget(self.btn_expPath, 3, 0, 1, 1)

        self.txtB_expPath = QtWidgets.QLineEdit("")
        self.txtB_expPath.setEnabled(False)
        self.txtB_expPath.setPlaceholderText("path to simulation results")
        self.mGrid.addWidget(self.txtB_expPath, 3, 1, 1, 4)

        self.lGrid = QtWidgets.QGridLayout()
        self.vbox.addLayout(self.lGrid)
        self.lGrid.setColumnMinimumWidth(1, 20)

        self.lbl_epdElectircal = QtWidgets.QLabel("Enter EPD for electrical energy")
        self.lGrid.addWidget(self.lbl_epdElectircal, 0, 0, 1, 1)

        self.lbl_spacer = QtWidgets.QLabel("")
        self.lGrid.addWidget(self.lbl_spacer, 0, 1, 1, 1)

        self.lbl_epdCarries = QtWidgets.QLabel("Enter EPDs and primary energy factors for heat energy carriers")
        self.lGrid.addWidget(self.lbl_epdCarries, 0, 2, 1, 4)

        self.txtB_epdElectrical = QtWidgets.QLineEdit("")
        self.txtB_epdElectrical.setPlaceholderText("UUID from OEKOBAUDAT.de")
        self.lGrid.addWidget(self.txtB_epdElectrical, 1, 0, 1, 1)

        self.lbl_carrier1 = QtWidgets.QLabel("Carrier1")
        self.lGrid.addWidget(self.lbl_carrier1, 1, 2, 1, 1)

        self.comB_carrier1 = QtWidgets.QComboBox()
        self.comB_carrier1.addItems(["UUID from OEKOBAUDAT.de"])
        self.lGrid.addWidget(self.comB_carrier1, 1, 3, 1, 2)
        
        self.txtB_carrier1PEF = QtWidgets.QLineEdit("")
        self.txtB_carrier1PEF.setPlaceholderText("PEF")
        self.lGrid.addWidget(self.txtB_carrier1PEF, 1, 5, 1, 1)


        self.lbl_carrier2 = QtWidgets.QLabel("Carrier2")
        self.lGrid.addWidget(self.lbl_carrier2, 2, 2, 1, 1)

        self.comB_carrier2 = QtWidgets.QComboBox()
        self.comB_carrier2.addItems(["UUID from OEKOBAUDAT.de"])
        self.lGrid.addWidget(self.comB_carrier2, 2, 3, 1, 2)
        
        self.txtB_carrier2PEF = QtWidgets.QLineEdit("")
        self.txtB_carrier2PEF.setPlaceholderText("PEF")
        self.lGrid.addWidget(self.txtB_carrier2PEF, 2, 5, 1, 1)


        self.lbl_temporalBoundary = QtWidgets.QLabel("Enter temporal boundary [a]")
        self.lGrid.addWidget(self.lbl_temporalBoundary, 3, 0, 1, 1)


        self.lbl_carrierN = QtWidgets.QLabel("CarrierN")
        self.lGrid.addWidget(self.lbl_carrierN, 3, 2, 1, 1)

        self.comB_carrierN = QtWidgets.QComboBox()
        self.comB_carrierN.addItems(["UUID from OEKOBAUDAT.de"])
        self.lGrid.addWidget(self.comB_carrierN, 3, 3, 1, 2)
        
        self.txtB_carrierNPEF = QtWidgets.QLineEdit("")
        self.txtB_carrierNPEF.setPlaceholderText("PEF")
        self.lGrid.addWidget(self.txtB_carrierNPEF, 3, 5, 1, 1)

        self.txtB_temporalBoundary = QtWidgets.QLineEdit("")
        self.txtB_temporalBoundary.setPlaceholderText("Time in years")
        self.lGrid.addWidget(self.txtB_temporalBoundary, 4, 0, 1, 1)

        self.btn_startSim = QtWidgets.QPushButton("Start simulation")
        self.lGrid.addWidget(self.btn_startSim, 5, 0, 1, 1)

        self.btn_returnEnrich = QtWidgets.QPushButton("Return to Enrichment window")
        self.lGrid.addWidget(self.btn_returnEnrich, 5, 5, 1, 1)


        self.btn_startSim.clicked.connect(self.func_startSimulation)
        self.btn_returnEnrich.clicked.connect(self.func_returnToEnrich)

        self.btn_expPath.clicked.connect(self.func_expPath)

        self.expPath = ""


    def func_expPath(self) -> None:
        """select export path"""
        path = sel.select_folder(self, self.txtB_expPath, "Select export folder")
        if path:
            self.expPath = path
        else:
            pass


    def func_startSimulation(self) -> None:
        """starts simulation proccess"""

        if self.expPath == "":
            gf.messageBox(self, "Error", "Please select an export path before continuing")
            return

        if self.comB_weatherFile.currentIndex() == 0:
            gf.messageBox(self, "Error", "Please select a weather file before continuing")
            return
        
        bld_IWU = []
        bld_tabula_de = []
        bld_tabula_dk = []
        bld_urbanrenet = []
        bld_undefined = []
        for key in self.buildingDict:
            if self.buildingDict[key]["selected"]:
                buildingname = self.buildingDict[key]["buildingname"]
                if buildingname in self.buildingsToChange.keys():
                    if "usage" in self.buildingsToChange[buildingname]:
                        if self.buildingsToChange[buildingname]["usage"].startswith("IWU"):
                            bld_IWU.append(buildingname)
                        elif self.buildingsToChange[buildingname]["usage"].startswith("tabula_de"):
                            bld_tabula_de.append(buildingname)
                        elif self.buildingsToChange[buildingname]["usage"].startswith("tabula_dk"):
                            bld_tabula_dk.append(buildingname)
                        elif self.buildingsToChange[buildingname]["usage"].startswith("urbanrenet"):
                            bld_urbanrenet.append(buildingname)
                        else:
                            print(f"Error getting the right method for {buildingname}")
                            bld_undefined.append(buildingname)
                    else:
                        bld_undefined.append(buildingname)
                else:
                    bld_undefined.append(buildingname)


        weatherfile = self.comB_weatherFile.currentText()


        print(f"simulate file {self.fileToSimulate}")
        
        print(f"IWU for these buildings: {bld_IWU}")
        print(f"tabula_de for these buildings: {bld_tabula_de}")
        print(f"tabula_dk for these buildings: {bld_tabula_dk}")
        print(f"urbanrenet for these buildings: {bld_urbanrenet}")
        print(f"undefined method: {bld_undefined}")

        print(f"using the weatherfile {weatherfile}")

        print(f"and exporting to {self.expPath}")

        return

        from teaser.project import Project
        import teaser.logic.utilities as utilities
        import teaser.data.input.citygml_input as cg

        # create project
        prj = Project(load_data=True)
        prj.name = "TEASER+_GUI"


        # add buildings here
        gml_copy_list = cg.choose_gml_lxml(self.fileToSimulate, buildingIDs)
        cg.load_gml_lxml(self.fileToSimulate, prj, method="To-Do", chosen_gmls=gml_copy_list)



        # To-Do
        """additional parameters"""
        path = utilities.get_default_path()
        prj.number_of_elements_calc = 2 # To-Do oder doch = 4?
        prj.calc_all_buildings(raise_errors=True)
        # prj.export_parameters_txt()
        prj.weather_file_name = utilities.get_full_path(
            os.path.join("data", "input", "inputdata", "weatherdata", weatherfile)
        )
        # the line above me needs to be changed - QLineEdit for path to weather file
        prj.export_aixlib()

        prj.save_citygml(path="Dummy/value", gml_copy="To-Do")



    def func_returnToEnrich(self) -> None:
        self.hide()
        self.enrich.show()




class about(QtWidgets.QWidget):
    def __init__(self):
        super(about, self).__init__()
        self.initUI()

    def initUI(self):
        global POSX, POSY, WIDTH, HEIGHT, SIZEFACTOR

        gf.windowSetup(self, POSX + 10, POSY + 10, WIDTH, HEIGHT, 'CityBIT - About')

        # creating main layout
        self.vbox = QtWidgets.QVBoxLayout(self)
        self.setLayout(self.vbox)

        gf.load_banner(self, r'pictures/e3dHeader.png', SIZEFACTOR)

        self.textwidget = QtWidgets.QTextBrowser()
        self.vbox.addWidget(self.textwidget)
        self.textwidget.setFontPointSize(14)
        with open('about/about.txt', 'r') as file:
            text = file.read()
        self.textwidget.setText(text)

        self.lGrid = QtWidgets.QGridLayout()

        self.btn_repo = QtWidgets.QPushButton('Open repository')
        self.lGrid.addWidget(self.btn_repo, 0, 0, 1, 1)

        self.btn_close = QtWidgets.QPushButton('Close')
        self.lGrid.addWidget(self.btn_close, 0, 1, 1, 1)

        self.vbox.addLayout(self.lGrid)

        self.btn_repo.clicked.connect(self.open_repo)
        self.btn_close.clicked.connect(self.close_about)

    def open_repo(self):
        os.startfile('www.e3d.rwth-aachen.de')

    def close_about(self):
        self.hide()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle('Fusion')
    widget = MainWindow()
    widget.show()
    sys.exit(app.exec())