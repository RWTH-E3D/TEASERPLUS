# created November 2023

"""This module includes a class for the Final Energy Calculation of the Ventilation System
"""

# This class can be used to create the heat losses and auxiliary energy required for ventilation.
# It can be entered in the programme according to the scheme of PEDemandHeating and PEDemandWater.
class FEDemandVentilation(object):
    """FEDemandVentilation class

    This class holds information for the Ventilation System of the Building.
    The heat losses for the ventilation system are being set. This class does not affect
    the calculation in Dymola. It adds heat losses for ventilation to calculate the final energy demand.

    Parameters
        ----------

        parent: HeatSupplySystem()

        Attributes
        ----------

    """

    def __init__(self, parent=None):
        """Constructor of FEDemandVentilation class
        """

        self.parent = parent

    def calc_final_energy_demand_ventilation(self):
        return 0

    @property
    def parent(self):
        return self.__parent

    @parent.setter
    def parent(self, value):
        from teaser.teaser.logic.buildingobjects.buildingsystems.heatsupplysystem import HeatSupplySystem
        import inspect
        if inspect.isclass(HeatSupplySystem):
            self.__parent = value
            self.__parent.heat_supply_system = self
