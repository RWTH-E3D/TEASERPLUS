"""
This code is taken from CityLDT.
Please contact Avichal Malhotra or Simon Raming for any questions.
Original Repo for CityLDT: https://gitlab.e3d.rwth-aachen.de/e3d-software-tools/cityldt/cityldt.git
"""

from PySide6 import QtWidgets, QtGui, QtCore



def screenSizer(posx: int, posy: int, width: int, height: int, app: QtWidgets.QApplication) -> tuple[int, int, int, int, float]:
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
        self.setWindowIcon(QtGui.QIcon(r'pictures\e3dIcon.png'))
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


def windowPosition(self) -> tuple[int, int]:
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

