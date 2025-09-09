"""
This is a parametric study of internal walls in single family houses (SFH) to determine a meaningful range of internal wall length, volume,
mass (LCI), and environmental impacts from life cycle phases A, C, and D (LCIA) according to ISO 14040/14044 and EN 15804.
It currently runs stand-alone and will soon be implemented into the workflow of Teco.



Please contact Maximilian Schildt (schildt@e3d.rwth-aachen.de) for any questions.

www.e3d.rwth-aachen.de
Mathieustrasse 30
52074 Aachen
Germany
"""

# import of libraries
import pandas as pd
import os
import random
import numpy as np
from pyDOE import lhs

class IntWallAreaSFH_analytical:
    def __init__(self, NLA, number_of_storeys, storey_height):

        """
        Constructor of IntWallArea class

        NLA: Net Leased Area
        number_of_storeys: number of storeys in the building
        has_basement: Boolean
        storey_height: average height of storeys
        n_samples: No. of samples produced in Latin Hypercube Sampling for each variable

        The basic floor layout is assumed to consist of a basement, first floor, second floor, and third floor (attic).
        Each floor has a number of rooms of different usage types, assumed to be the common denominator of SFH in Germany.
        """

        self.NLA = NLA
        self.number_of_storeys = number_of_storeys
        self.storey_height = storey_height
        self.area_of_floor = self.NLA / self.number_of_storeys

        self.door_width = 1.1
        self.n_sample = 200

    def small_SFH(self):
        # The share of room area per floor
        self.area_b_Room1 = 0.40 * self.area_of_floor
        self.area_b_Room2 = 0.39 * self.area_of_floor
        self.area_b_Hallway = 0.08 * self.area_of_floor
        self.area_b_Staircase = 0.13 * self.area_of_floor

        self.area_1f_Livingroom = 0.50 * self.area_of_floor
        self.area_1f_Kitchen = 0.18 * self.area_of_floor
        self.area_1f_Staircase = 0.13 * self.area_of_floor
        self.area_1f_GuestWC = 0.075 * self.area_of_floor
        self.area_1f_Entrance = 0.115 * self.area_of_floor

        self.area_2f_Bedroom1 = 0.34 * self.area_of_floor
        self.area_2f_Bedroom2 = 0.33 * self.area_of_floor
        self.area_2f_Staircase = 0.13 * self.area_of_floor
        self.area_2f_Bathroom = 0.12 * self.area_of_floor
        self.area_2f_Hallway = 0.08 * self.area_of_floor

        self.area_3f_Atticroom1 = 0.40 * self.area_of_floor
        self.area_3f_Atticroom2 = 0.39 * self.area_of_floor
        self.area_3f_Hallway = 0.08 * self.area_of_floor
        self.area_3f_Staircase = 0.13 * self.area_of_floor

        # The extwall ratio (the length in y direction to the length in x direction) is [1, 1.5].
        # The length in y direction is always longer to ensure the reasonability of layout.
        # Considering the minimal lengths of different rooms, expected minimal external wall length is given.
        self.length_extwall_x = [max(6, np.sqrt(self.area_of_floor / 1.5)),
                                 max(6, np.sqrt(self.area_of_floor / 1.0))]
        self.length_extwall_y = [self.area_of_floor / self.length_extwall_x[1],
                                 self.area_of_floor / self.length_extwall_x[0]]

        # The room length ratio is set from 1 to 1.5, except for the Entrance are set at 1.5m.
        # Each room has a door to entrance, hallway or living room.
        self.length_intwall_b_Room1_x = [max(2.7, np.sqrt(self.area_b_Room1 / 1.5)),
                                         max(2.7, np.sqrt(self.area_b_Room1 / 1.0))]
        self.length_intwall_b_Room1_y = [self.area_b_Room1/self.length_intwall_b_Room1_x[1],
                                         self.area_b_Room1/self.length_intwall_b_Room1_x[0]]
        self.length_intwall_b_Room2_x = [max(2.7, np.sqrt(self.area_b_Room2 / 1.5)),
                                         max(2.7, np.sqrt(self.area_b_Room2 / 1.0))]
        self.length_intwall_b_Room2_y = [self.area_b_Room2 / self.length_intwall_b_Room2_x[1],
                                         self.area_b_Room2 / self.length_intwall_b_Room2_x[0]]
        self.length_intwall_b_Hallway_x = [1.1, 1.1]
        self.length_intwall_b_Hallway_y = [self.area_b_Hallway / 1.1, self.area_b_Hallway / 1.1]
        self.length_intwall_b_Staircase_x = [np.sqrt(self.area_b_Staircase / 1.5),
                                             np.sqrt(self.area_b_Staircase / 1.0)]
        self.length_intwall_b_Staircase_y = [self.area_b_Staircase / self.length_intwall_b_Staircase_x[1],
                                             self.area_b_Staircase / self.length_intwall_b_Staircase_x[0]]

        self.length_intwall_1f_Livingroom_x = [max(3.5, np.sqrt(self.area_1f_Livingroom / 1.5)),
                                               max(3.5, np.sqrt(self.area_1f_Livingroom / 1.0))]
        self.length_intwall_1f_Livingroom_y = [self.area_1f_Livingroom / self.length_intwall_1f_Livingroom_x[1],
                                               self.area_1f_Livingroom / self.length_intwall_1f_Livingroom_x[0]]
        self.length_intwall_1f_Kitchen_x = [max(1.8, np.sqrt(self.area_1f_Kitchen / 1.5)),
                                            max(1.8, np.sqrt(self.area_1f_Kitchen / 1.0))]
        self.length_intwall_1f_Kitchen_y = [self.area_1f_Kitchen / self.length_intwall_1f_Kitchen_x[1],
                                            self.area_1f_Kitchen / self.length_intwall_1f_Kitchen_x[0]]
        self.length_intwall_1f_GuestWC_x = [max(0.9, np.sqrt(self.area_1f_GuestWC / 1.5)),
                                            max(0.9, np.sqrt(self.area_1f_GuestWC / 1.0))]
        self.length_intwall_1f_GuestWC_y = [self.area_1f_GuestWC / self.length_intwall_1f_GuestWC_x[1],
                                            self.area_1f_GuestWC / self.length_intwall_1f_GuestWC_x[0]]
        self.length_intwall_1f_Entrance_x = [1.5, 1.5]
        self.length_intwall_1f_Entrance_y = [self.area_1f_Entrance / 1.5, self.area_1f_Entrance / 1.5]
        self.length_intwall_1f_Staircase_x = [np.sqrt(self.area_1f_Staircase / 1.5),
                                              np.sqrt(self.area_1f_Staircase / 1.0)]
        self.length_intwall_1f_Staircase_y = [self.area_1f_Staircase / self.length_intwall_1f_Staircase_x[1],
                                              self.area_1f_Staircase / self.length_intwall_1f_Staircase_x[0]]

        self.length_intwall_2f_Bedroom1_x = [max(2.7, np.sqrt(self.area_2f_Bedroom1 / 1.5)),
                                             max(2.7, np.sqrt(self.area_2f_Bedroom1 / 1.0))]
        self.length_intwall_2f_Bedroom1_y = [self.area_2f_Bedroom1 / self.length_intwall_2f_Bedroom1_x[1],
                                             self.area_2f_Bedroom1 / self.length_intwall_2f_Bedroom1_x[0]]
        self.length_intwall_2f_Bedroom2_x = [max(2.7, np.sqrt(self.area_2f_Bedroom2 / 1.5)),
                                             max(2.7, np.sqrt(self.area_2f_Bedroom2 / 1.0))]
        self.length_intwall_2f_Bedroom2_y = [self.area_2f_Bedroom2 / self.length_intwall_2f_Bedroom2_x[1],
                                             self.area_2f_Bedroom2 / self.length_intwall_2f_Bedroom2_x[0]]
        self.length_intwall_2f_Bathroom_x = [max(1.65, np.sqrt(self.area_2f_Bathroom / 1.5)),
                                             max(1.65, np.sqrt(self.area_2f_Bathroom / 1.0))]
        self.length_intwall_2f_Bathroom_y = [self.area_2f_Bathroom / self.length_intwall_2f_Bathroom_x[1],
                                             self.area_2f_Bathroom / self.length_intwall_2f_Bathroom_x[0]]
        self.length_intwall_2f_Hallway_x = [1.1, 1.1]
        self.length_intwall_2f_Hallway_y = [self.area_2f_Hallway / 1.1, self.area_2f_Hallway / 1.1]
        self.length_intwall_2f_Staircase_x = [np.sqrt(self.area_2f_Staircase / 1.5),
                                             np.sqrt(self.area_2f_Staircase / 1.0)]
        self.length_intwall_2f_Staircase_y = [self.area_2f_Staircase / self.length_intwall_2f_Staircase_x[1],
                                              self.area_2f_Staircase / self.length_intwall_2f_Staircase_x[0]]

        self.length_intwall_3f_Atticroom1_x = [max(2.7, np.sqrt(self.area_3f_Atticroom1 / 1.5)),
                                               max(2.7, np.sqrt(self.area_3f_Atticroom1 / 1.0))]
        self.length_intwall_3f_Atticroom1_y = [self.area_3f_Atticroom1 / self.length_intwall_3f_Atticroom1_x[1],
                                               self.area_3f_Atticroom1 / self.length_intwall_3f_Atticroom1_x[0]]
        self.length_intwall_3f_Atticroom2_x = [max(2.7, np.sqrt(self.area_3f_Atticroom2 / 1.5)),
                                               max(2.7, np.sqrt(self.area_3f_Atticroom2 / 1.0))]
        self.length_intwall_3f_Atticroom2_y = [self.area_3f_Atticroom2 / self.length_intwall_3f_Atticroom2_x[1],
                                               self.area_3f_Atticroom2 / self.length_intwall_3f_Atticroom2_x[0]]
        self.length_intwall_3f_Hallway_x = [1.1, 1.1]
        self.length_intwall_3f_Hallway_y = [self.area_3f_Hallway / 1.1, self.area_3f_Hallway / 1.1]
        self.length_intwall_3f_Staircase_x = [np.sqrt(self.area_3f_Staircase / 1.5),
                                              np.sqrt(self.area_3f_Staircase / 1.0)]
        self.length_intwall_3f_Staircase_y = [self.area_3f_Staircase / self.length_intwall_3f_Staircase_x[1],
                                              self.area_3f_Staircase / self.length_intwall_3f_Staircase_x[0]]

        # Create list of all input variables to simplify LH sampling and rescaling depending on number of floors and (non-)available basement
        self.list_of_input_variables = [['length_extwall_x', self.length_extwall_x],
                                        ['length_extwall_y', self.length_extwall_y],
                                        ['length_intwall_base_Room1_x', self.length_intwall_b_Room1_x],
                                        ['length_intwall_base_Room1_y', self.length_intwall_b_Room1_y],
                                        ['length_intwall_base_Room2_x', self.length_intwall_b_Room2_x],
                                        ['length_intwall_base_Room2_y', self.length_intwall_b_Room2_y],
                                        ['length_intwall_base_Hallway_x', self.length_intwall_b_Hallway_x],
                                        ['length_intwall_base_Hallway_y', self.length_intwall_b_Hallway_y],
                                        ['length_intwall_base_Staircase_x', self.length_intwall_b_Staircase_x],
                                        ['length_intwall_base_Staircase_y', self.length_intwall_b_Staircase_y],
                                        ['length_intwall_1f_Livingroom_x', self.length_intwall_1f_Livingroom_x],
                                        ['length_intwall_1f_Livingroom_y', self.length_intwall_1f_Livingroom_y],
                                        ['length_intwall_1f_Kitchen_x', self.length_intwall_1f_Kitchen_x],
                                        ['length_intwall_1f_Kitchen_y', self.length_intwall_1f_Kitchen_y],
                                        ['length_intwall_1f_GuestWC_x', self.length_intwall_1f_GuestWC_x],
                                        ['length_intwall_1f_GuestWC_y', self.length_intwall_1f_GuestWC_y],
                                        ['length_intwall_1f_Entrance_x', self.length_intwall_1f_Entrance_x],
                                        ['length_intwall_1f_Entrance_y', self.length_intwall_1f_Entrance_y],
                                        ['length_intwall_1f_Staircase_x', self.length_intwall_1f_Staircase_x],
                                        ['length_intwall_1f_Staircase_y', self.length_intwall_1f_Staircase_y],
                                        ['length_intwall_2f_Bedroom1_x', self.length_intwall_2f_Bedroom1_x],
                                        ['length_intwall_2f_Bedroom1_y', self.length_intwall_2f_Bedroom1_y],
                                        ['length_intwall_2f_Bedroom2_x', self.length_intwall_2f_Bedroom2_x],
                                        ['length_intwall_2f_Bedroom2_y', self.length_intwall_2f_Bedroom2_y],
                                        ['length_intwall_2f_Bathroom_x', self.length_intwall_2f_Bathroom_x],
                                        ['length_intwall_2f_Bathroom_y', self.length_intwall_2f_Bathroom_y],
                                        ['length_intwall_2f_Hallway_x', self.length_intwall_2f_Hallway_x],
                                        ['length_intwall_2f_Hallway_y', self.length_intwall_2f_Hallway_y],
                                        ['length_intwall_2f_Staircase_x', self.length_intwall_2f_Staircase_x],
                                        ['length_intwall_2f_Staircase_y', self.length_intwall_2f_Staircase_y],
                                        ['length_intwall_3f_Atticroom1_x', self.length_intwall_3f_Atticroom1_x],
                                        ['length_intwall_3f_Atticroom1_y', self.length_intwall_3f_Atticroom1_y],
                                        ['length_intwall_3f_Atticroom2_x', self.length_intwall_3f_Atticroom2_x],
                                        ['length_intwall_3f_Atticroom2_y', self.length_intwall_3f_Atticroom2_y],
                                        ['length_intwall_3f_Hallway_x', self.length_intwall_3f_Hallway_x],
                                        ['length_intwall_3f_Hallway_y', self.length_intwall_3f_Hallway_y],
                                        ['length_intwall_3f_Staircase_x', self.length_intwall_3f_Staircase_x],
                                        ['length_intwall_3f_Staircase_y', self.length_intwall_3f_Staircase_y]
                                        ]
        return self.list_of_input_variables

    def normal_SFH(self):

        self.area_b_Room1 = 0.50 * self.area_of_floor
        self.area_b_Room2 = 0.36 * self.area_of_floor
        self.area_b_Hallway = 0.05 * self.area_of_floor
        self.area_b_Staircase = 0.09 * self.area_of_floor

        self.area_1f_Livingroom = 0.50 * self.area_of_floor
        self.area_1f_Kitchen = 0.175 * self.area_of_floor
        self.area_1f_Staircase = 0.09 * self.area_of_floor
        self.area_1f_GuestWC = 0.06 * self.area_of_floor
        self.area_1f_Entrance = 0.10 * self.area_of_floor
        self.area_1f_Guestroom = 0.075 * self.area_of_floor

        self.area_2f_Bedroom1 = 0.225 * self.area_of_floor
        self.area_2f_Bedroom2 = 0.25 * self.area_of_floor
        self.area_2f_Bedroom3 = 0.25 * self.area_of_floor
        self.area_2f_Staircase = 0.09 * self.area_of_floor
        self.area_2f_Bathroom = 0.11 * self.area_of_floor
        self.area_2f_Hallway = 0.075 * self.area_of_floor

        self.area_3f_Atticroom1 = 0.50 * self.area_of_floor
        self.area_3f_Atticroom2 = 0.36 * self.area_of_floor
        self.area_3f_Hallway = 0.05 * self.area_of_floor
        self.area_3f_Staircase = 0.09 * self.area_of_floor

        # The extwall ratio (the length in y direction to the length in x direction) is [1, 1.5].
        # The length in y direction is always longer.
        self.length_extwall_x = [np.sqrt(self.area_of_floor / 1.5),
                                 np.sqrt(self.area_of_floor / 1.0)]
        self.length_extwall_y = [self.area_of_floor / self.length_extwall_x[1],
                                 self.area_of_floor / self.length_extwall_x[0]]

        # The room length ratio is set from 1 to 1.5, except for the Entrance are set at 1.5m.
        # Each room has a door to entrance, hallway or living room.
        self.length_intwall_b_Room1_x = [max(2.7, np.sqrt(self.area_b_Room1 / 1.5)),
                                         max(2.7, np.sqrt(self.area_b_Room1 / 1.0))]
        self.length_intwall_b_Room1_y = [self.area_b_Room1 / self.length_intwall_b_Room1_x[1],
                                         self.area_b_Room1 / self.length_intwall_b_Room1_x[0]]
        self.length_intwall_b_Room2_x = [max(2.7, np.sqrt(self.area_b_Room2 / 1.5)),
                                         max(2.7, np.sqrt(self.area_b_Room2 / 1.0))]
        self.length_intwall_b_Room2_y = [self.area_b_Room2 / self.length_intwall_b_Room2_x[1],
                                         self.area_b_Room2 / self.length_intwall_b_Room2_x[0]]
        self.length_intwall_b_Hallway_x = [1.1, 1.1]
        self.length_intwall_b_Hallway_y = [self.area_b_Hallway / 1.1, self.area_b_Hallway / 1.1]
        self.length_intwall_b_Staircase_x = [np.sqrt(self.area_b_Staircase / 1.5),
                                             np.sqrt(self.area_b_Staircase / 1.0)]
        self.length_intwall_b_Staircase_y = [self.area_b_Staircase / self.length_intwall_b_Staircase_x[1],
                                             self.area_b_Staircase / self.length_intwall_b_Staircase_x[0]]

        self.length_intwall_1f_Livingroom_x = [max(3.5, np.sqrt(self.area_1f_Livingroom / 1.5)),
                                               max(3.5, np.sqrt(self.area_1f_Livingroom / 1.0))]
        self.length_intwall_1f_Livingroom_y = [self.area_1f_Livingroom / self.length_intwall_1f_Livingroom_x[1],
                                               self.area_1f_Livingroom / self.length_intwall_1f_Livingroom_x[0]]
        self.length_intwall_1f_Kitchen_x = [max(1.8, np.sqrt(self.area_1f_Kitchen / 1.5)),
                                            max(1.8, np.sqrt(self.area_1f_Kitchen / 1.0))]
        self.length_intwall_1f_Kitchen_y = [self.area_1f_Kitchen / self.length_intwall_1f_Kitchen_x[1],
                                            self.area_1f_Kitchen / self.length_intwall_1f_Kitchen_x[0]]
        self.length_intwall_1f_GuestWC_x = [max(0.9, np.sqrt(self.area_1f_GuestWC / 1.5)),
                                            max(0.9, np.sqrt(self.area_1f_GuestWC / 1.0))]
        self.length_intwall_1f_GuestWC_y = [self.area_1f_GuestWC / self.length_intwall_1f_GuestWC_x[1],
                                            self.area_1f_GuestWC / self.length_intwall_1f_GuestWC_x[0]]
        self.length_intwall_1f_Guestroom_x = [max(2, np.sqrt(self.area_1f_Guestroom / 1.5)),
                                              max(2, np.sqrt(self.area_1f_Guestroom / 1.0))]
        self.length_intwall_1f_Guestroom_y = [self.area_1f_Guestroom / self.length_intwall_1f_Guestroom_x[1],
                                              self.area_1f_Guestroom / self.length_intwall_1f_Guestroom_x[0]]
        self.length_intwall_1f_Entrance_x = [1.5, 1.5]
        self.length_intwall_1f_Entrance_y = [self.area_1f_Entrance / 1.5, self.area_1f_Entrance / 1.5]
        self.length_intwall_1f_Staircase_x = [np.sqrt(self.area_1f_Staircase / 1.5),
                                              np.sqrt(self.area_1f_Staircase / 1.0)]
        self.length_intwall_1f_Staircase_y = [self.area_1f_Staircase / self.length_intwall_1f_Staircase_x[1],
                                              self.area_1f_Staircase / self.length_intwall_1f_Staircase_x[0]]

        self.length_intwall_2f_Bedroom1_x = [max(2.7, np.sqrt(self.area_2f_Bedroom1 / 1.5)),
                                             max(2.7, np.sqrt(self.area_2f_Bedroom1 / 1.0))]
        self.length_intwall_2f_Bedroom1_y = [self.area_2f_Bedroom1 / self.length_intwall_2f_Bedroom1_x[1],
                                             self.area_2f_Bedroom1 / self.length_intwall_2f_Bedroom1_x[0]]
        self.length_intwall_2f_Bedroom2_x = [max(2.7, np.sqrt(self.area_2f_Bedroom2 / 1.5)),
                                             max(2.7, np.sqrt(self.area_2f_Bedroom2 / 1.0))]
        self.length_intwall_2f_Bedroom2_y = [self.area_2f_Bedroom2 / self.length_intwall_2f_Bedroom2_x[1],
                                             self.area_2f_Bedroom2 / self.length_intwall_2f_Bedroom2_x[0]]
        self.length_intwall_2f_Bedroom3_x = [max(2.7, np.sqrt(self.area_2f_Bedroom3 / 1.5)),
                                             max(2.7, np.sqrt(self.area_2f_Bedroom3 / 1.0))]
        self.length_intwall_2f_Bedroom3_y = [self.area_2f_Bedroom3 / self.length_intwall_2f_Bedroom3_x[1],
                                             self.area_2f_Bedroom3 / self.length_intwall_2f_Bedroom3_x[0]]
        self.length_intwall_2f_Bathroom_x = [max(1.65, np.sqrt(self.area_2f_Bathroom / 1.5)),
                                             max(1.65, np.sqrt(self.area_2f_Bathroom / 1.0))]
        self.length_intwall_2f_Bathroom_y = [self.area_2f_Bathroom / self.length_intwall_2f_Bathroom_x[1],
                                             self.area_2f_Bathroom / self.length_intwall_2f_Bathroom_x[0]]
        self.length_intwall_2f_Hallway_x = [1.1, 1.1]
        self.length_intwall_2f_Hallway_y = [self.area_2f_Hallway / 1.1, self.area_2f_Hallway / 1.1]
        self.length_intwall_2f_Staircase_x = [np.sqrt(self.area_2f_Staircase / 1.5),
                                              np.sqrt(self.area_2f_Staircase / 1.0)]
        self.length_intwall_2f_Staircase_y = [self.area_2f_Staircase / self.length_intwall_2f_Staircase_x[1],
                                              self.area_2f_Staircase / self.length_intwall_2f_Staircase_x[0]]

        self.length_intwall_3f_Atticroom1_x = [max(2.7, np.sqrt(self.area_3f_Atticroom1 / 1.5)),
                                               max(2.7, np.sqrt(self.area_3f_Atticroom1 / 1.0))]
        self.length_intwall_3f_Atticroom1_y = [self.area_3f_Atticroom1 / self.length_intwall_3f_Atticroom1_x[1],
                                               self.area_3f_Atticroom1 / self.length_intwall_3f_Atticroom1_x[0]]
        self.length_intwall_3f_Atticroom2_x = [max(2.7, np.sqrt(self.area_3f_Atticroom2 / 1.5)),
                                               max(2.7, np.sqrt(self.area_3f_Atticroom2 / 1.0))]
        self.length_intwall_3f_Atticroom2_y = [self.area_3f_Atticroom2 / self.length_intwall_3f_Atticroom2_x[1],
                                               self.area_3f_Atticroom2 / self.length_intwall_3f_Atticroom2_x[0]]
        self.length_intwall_3f_Hallway_x = [1.1, 1.1]
        self.length_intwall_3f_Hallway_y = [self.area_3f_Hallway / 1.1, self.area_3f_Hallway / 1.1]
        self.length_intwall_3f_Staircase_x = [np.sqrt(self.area_3f_Staircase / 1.5),
                                              np.sqrt(self.area_3f_Staircase / 1.0)]
        self.length_intwall_3f_Staircase_y = [self.area_3f_Staircase / self.length_intwall_3f_Staircase_x[1],
                                              self.area_3f_Staircase / self.length_intwall_3f_Staircase_x[0]]

        # Create list of all input variables to simplify LH sampling and rescaling depending on number of floors and (non-)available basement
        self.list_of_input_variables = [['length_extwall_x', self.length_extwall_x],
                                        ['length_extwall_y', self.length_extwall_y],
                                        ['length_intwall_base_Room1_x', self.length_intwall_b_Room1_x],
                                        ['length_intwall_base_Room1_y', self.length_intwall_b_Room1_y],
                                        ['length_intwall_base_Room2_x', self.length_intwall_b_Room2_x],
                                        ['length_intwall_base_Room2_y', self.length_intwall_b_Room2_y],
                                        ['length_intwall_base_Hallway_x', self.length_intwall_b_Hallway_x],
                                        ['length_intwall_base_Hallway_y', self.length_intwall_b_Hallway_y],
                                        ['length_intwall_base_Staircase_x', self.length_intwall_b_Staircase_x],
                                        ['length_intwall_base_Staircase_y', self.length_intwall_b_Staircase_y],
                                        ['length_intwall_1f_Livingroom_x', self.length_intwall_1f_Livingroom_x],
                                        ['length_intwall_1f_Livingroom_y', self.length_intwall_1f_Livingroom_y],
                                        ['length_intwall_1f_Kitchen_x', self.length_intwall_1f_Kitchen_x],
                                        ['length_intwall_1f_Kitchen_y', self.length_intwall_1f_Kitchen_y],
                                        ['length_intwall_1f_GuestWC_x', self.length_intwall_1f_GuestWC_x],
                                        ['length_intwall_1f_GuestWC_y', self.length_intwall_1f_GuestWC_y],
                                        ['length_intwall_1f_Guestroom_x', self.length_intwall_1f_Guestroom_x],
                                        ['length_intwall_1f_Guestroom_y', self.length_intwall_1f_Guestroom_y],
                                        ['length_intwall_1f_Entrance_x', self.length_intwall_1f_Entrance_x],
                                        ['length_intwall_1f_Entrance_y', self.length_intwall_1f_Entrance_y],
                                        ['length_intwall_1f_Staircase_x', self.length_intwall_1f_Staircase_x],
                                        ['length_intwall_1f_Staircase_y', self.length_intwall_1f_Staircase_y],
                                        ['length_intwall_2f_Bedroom1_x', self.length_intwall_2f_Bedroom1_x],
                                        ['length_intwall_2f_Bedroom1_y', self.length_intwall_2f_Bedroom1_y],
                                        ['length_intwall_2f_Bedroom2_x', self.length_intwall_2f_Bedroom2_x],
                                        ['length_intwall_2f_Bedroom2_y', self.length_intwall_2f_Bedroom2_y],
                                        ['length_intwall_2f_Bedroom3_x', self.length_intwall_2f_Bedroom3_x],
                                        ['length_intwall_2f_Bedroom3_y', self.length_intwall_2f_Bedroom3_y],
                                        ['length_intwall_2f_Bathroom_x', self.length_intwall_2f_Bathroom_x],
                                        ['length_intwall_2f_Bathroom_y', self.length_intwall_2f_Bathroom_y],
                                        ['length_intwall_2f_Hallway_x', self.length_intwall_2f_Hallway_x],
                                        ['length_intwall_2f_Hallway_y', self.length_intwall_2f_Hallway_y],
                                        ['length_intwall_2f_Staircase_x', self.length_intwall_2f_Staircase_x],
                                        ['length_intwall_2f_Staircase_y', self.length_intwall_2f_Staircase_y],
                                        ['length_intwall_3f_Atticroom1_x', self.length_intwall_3f_Atticroom1_x],
                                        ['length_intwall_3f_Atticroom1_y', self.length_intwall_3f_Atticroom1_y],
                                        ['length_intwall_3f_Atticroom2_x', self.length_intwall_3f_Atticroom2_x],
                                        ['length_intwall_3f_Atticroom2_y', self.length_intwall_3f_Atticroom2_y],
                                        ['length_intwall_3f_Hallway_x', self.length_intwall_3f_Hallway_x],
                                        ['length_intwall_3f_Hallway_y', self.length_intwall_3f_Hallway_y],
                                        ['length_intwall_3f_Staircase_x', self.length_intwall_3f_Staircase_x],
                                        ['length_intwall_3f_Staircase_y', self.length_intwall_3f_Staircase_y]
                                        ]

        return self.list_of_input_variables

    def large_SFH(self):

        self.area_b_Room1 = 0.50 * self.area_of_floor
        self.area_b_Room2 = 0.375 * self.area_of_floor
        self.area_b_Hallway = 0.05 * self.area_of_floor
        self.area_b_Staircase = 0.075 * self.area_of_floor

        self.area_1f_Livingroom = 0.45 * self.area_of_floor
        self.area_1f_Kitchen = 0.14 * self.area_of_floor
        self.area_1f_Staircase = 0.075 * self.area_of_floor
        self.area_1f_GuestWC = 0.045 * self.area_of_floor
        self.area_1f_Entrance = 0.09 * self.area_of_floor
        self.area_1f_Guestroom = 0.20 * self.area_of_floor

        self.area_2f_Bedroom1 = 0.20 * self.area_of_floor
        self.area_2f_Bedroom2 = 0.20 * self.area_of_floor
        self.area_2f_Bedroom3 = 0.20 * self.area_of_floor
        self.area_2f_Bedroom4 = 0.15 * self.area_of_floor
        self.area_2f_Staircase = 0.075 * self.area_of_floor
        self.area_2f_Bathroom = 0.075 * self.area_of_floor
        self.area_2f_Hallway = 0.10 * self.area_of_floor

        self.area_3f_Atticroom1 = 0.50 * self.area_of_floor
        self.area_3f_Atticroom2 = 0.375 * self.area_of_floor
        self.area_3f_Hallway = 0.05 * self.area_of_floor
        self.area_3f_Staircase = 0.075 * self.area_of_floor

        # The extwall ratio (the length in y direction to the length in x direction) is [1, 1.5].
        # The length in y direction is always longer to ensure the reasonability of layout.
        self.length_extwall_x = [np.sqrt(self.area_of_floor / 1.5),
                                 np.sqrt(self.area_of_floor / 1.0)]
        self.length_extwall_y = [self.area_of_floor / self.length_extwall_x[1],
                                 self.area_of_floor / self.length_extwall_x[0]]

        # The room length ratio is set from 1 to 1.5, except for the Entrance are set at 1.5m.
        # Each room has a door to entrance, hallway or living room.
        self.length_intwall_b_Room1_x = [max(2.7, np.sqrt(self.area_b_Room1 / 1.5)),
                                         max(2.7, np.sqrt(self.area_b_Room1 / 1.0))]
        self.length_intwall_b_Room1_y = [self.area_b_Room1 / self.length_intwall_b_Room1_x[1],
                                         self.area_b_Room1 / self.length_intwall_b_Room1_x[0]]
        self.length_intwall_b_Room2_x = [max(2.7, np.sqrt(self.area_b_Room2 / 1.5)),
                                         max(2.7, np.sqrt(self.area_b_Room2 / 1.0))]
        self.length_intwall_b_Room2_y = [self.area_b_Room2 / self.length_intwall_b_Room2_x[1],
                                         self.area_b_Room2 / self.length_intwall_b_Room2_x[0]]
        self.length_intwall_b_Hallway_x = [1.1, 1.1]
        self.length_intwall_b_Hallway_y = [self.area_b_Hallway / 1.1, self.area_b_Hallway / 1.1]
        self.length_intwall_b_Staircase_x = [np.sqrt(self.area_b_Staircase / 1.5),
                                             np.sqrt(self.area_b_Staircase / 1.0)]
        self.length_intwall_b_Staircase_y = [self.area_b_Staircase / self.length_intwall_b_Staircase_x[1],
                                             self.area_b_Staircase / self.length_intwall_b_Staircase_x[0]]

        self.length_intwall_1f_Livingroom_x = [max(3.5, np.sqrt(self.area_1f_Livingroom / 1.5)),
                                               max(3.5, np.sqrt(self.area_1f_Livingroom / 1.0))]
        self.length_intwall_1f_Livingroom_y = [self.area_1f_Livingroom / self.length_intwall_1f_Livingroom_x[1],
                                               self.area_1f_Livingroom / self.length_intwall_1f_Livingroom_x[0]]
        self.length_intwall_1f_Kitchen_x = [max(1.8, np.sqrt(self.area_1f_Kitchen / 1.5)),
                                            max(1.8, np.sqrt(self.area_1f_Kitchen / 1.0))]
        self.length_intwall_1f_Kitchen_y = [self.area_1f_Kitchen / self.length_intwall_1f_Kitchen_x[1],
                                            self.area_1f_Kitchen / self.length_intwall_1f_Kitchen_x[0]]
        self.length_intwall_1f_GuestWC_x = [max(0.9, np.sqrt(self.area_1f_GuestWC / 1.5)),
                                            max(0.9, np.sqrt(self.area_1f_GuestWC / 1.0))]
        self.length_intwall_1f_GuestWC_y = [self.area_1f_GuestWC / self.length_intwall_1f_GuestWC_x[1],
                                            self.area_1f_GuestWC / self.length_intwall_1f_GuestWC_x[0]]
        self.length_intwall_1f_Guestroom_x = [max(2, np.sqrt(self.area_1f_Guestroom / 1.5)),
                                              max(2, np.sqrt(self.area_1f_Guestroom / 1.0))]
        self.length_intwall_1f_Guestroom_y = [self.area_1f_Guestroom / self.length_intwall_1f_Guestroom_x[1],
                                              self.area_1f_Guestroom / self.length_intwall_1f_Guestroom_x[0]]
        self.length_intwall_1f_Entrance_x = [1.5, 1.5]
        self.length_intwall_1f_Entrance_y = [self.area_1f_Entrance / 1.5, self.area_1f_Entrance / 1.5]
        self.length_intwall_1f_Staircase_x = [np.sqrt(self.area_1f_Staircase / 1.5),
                                              np.sqrt(self.area_1f_Staircase / 1.0)]
        self.length_intwall_1f_Staircase_y = [self.area_1f_Staircase / self.length_intwall_1f_Staircase_x[1],
                                              self.area_1f_Staircase / self.length_intwall_1f_Staircase_x[0]]

        self.length_intwall_2f_Bedroom1_x = [max(2.7, np.sqrt(self.area_2f_Bedroom1 / 1.5)),
                                             max(2.7, np.sqrt(self.area_2f_Bedroom1 / 1.0))]
        self.length_intwall_2f_Bedroom1_y = [self.area_2f_Bedroom1 / self.length_intwall_2f_Bedroom1_x[1],
                                             self.area_2f_Bedroom1 / self.length_intwall_2f_Bedroom1_x[0]]
        self.length_intwall_2f_Bedroom2_x = [max(2.7, np.sqrt(self.area_2f_Bedroom2 / 1.5)),
                                             max(2.7, np.sqrt(self.area_2f_Bedroom2 / 1.0))]
        self.length_intwall_2f_Bedroom2_y = [self.area_2f_Bedroom2 / self.length_intwall_2f_Bedroom2_x[1],
                                             self.area_2f_Bedroom2 / self.length_intwall_2f_Bedroom2_x[0]]
        self.length_intwall_2f_Bedroom3_x = [max(2.7, np.sqrt(self.area_2f_Bedroom3 / 1.5)),
                                             max(2.7, np.sqrt(self.area_2f_Bedroom3 / 1.0))]
        self.length_intwall_2f_Bedroom3_y = [self.area_2f_Bedroom3 / self.length_intwall_2f_Bedroom3_x[1],
                                             self.area_2f_Bedroom3 / self.length_intwall_2f_Bedroom3_x[0]]
        self.length_intwall_2f_Bedroom4_x = [max(2.7, np.sqrt(self.area_2f_Bedroom4 / 1.5)),
                                             max(2.7, np.sqrt(self.area_2f_Bedroom4 / 1.0))]
        self.length_intwall_2f_Bedroom4_y = [self.area_2f_Bedroom4 / self.length_intwall_2f_Bedroom4_x[1],
                                             self.area_2f_Bedroom4 / self.length_intwall_2f_Bedroom4_x[0]]
        self.length_intwall_2f_Bathroom_x = [max(1.65, np.sqrt(self.area_2f_Bathroom / 1.5)),
                                             max(1.65, np.sqrt(self.area_2f_Bathroom / 1.0))]
        self.length_intwall_2f_Bathroom_y = [self.area_2f_Bathroom / self.length_intwall_2f_Bathroom_x[1],
                                             self.area_2f_Bathroom / self.length_intwall_2f_Bathroom_x[0]]
        self.length_intwall_2f_Hallway_x = [1.1, 1.1]
        self.length_intwall_2f_Hallway_y = [self.area_2f_Hallway / 1.1, self.area_2f_Hallway / 1.1]
        self.length_intwall_2f_Staircase_x = [np.sqrt(self.area_2f_Staircase / 1.5),
                                              np.sqrt(self.area_2f_Staircase / 1.0)]
        self.length_intwall_2f_Staircase_y = [self.area_2f_Staircase / self.length_intwall_2f_Staircase_x[1],
                                              self.area_2f_Staircase / self.length_intwall_2f_Staircase_x[0]]

        self.length_intwall_3f_Atticroom1_x = [max(2.7, np.sqrt(self.area_3f_Atticroom1 / 1.5)),
                                               max(2.7, np.sqrt(self.area_3f_Atticroom1 / 1.0))]
        self.length_intwall_3f_Atticroom1_y = [self.area_3f_Atticroom1 / self.length_intwall_3f_Atticroom1_x[1],
                                               self.area_3f_Atticroom1 / self.length_intwall_3f_Atticroom1_x[0]]
        self.length_intwall_3f_Atticroom2_x = [max(2.7, np.sqrt(self.area_3f_Atticroom2 / 1.5)),
                                               max(2.7, np.sqrt(self.area_3f_Atticroom2 / 1.0))]
        self.length_intwall_3f_Atticroom2_y = [self.area_3f_Atticroom2 / self.length_intwall_3f_Atticroom2_x[1],
                                               self.area_3f_Atticroom2 / self.length_intwall_3f_Atticroom2_x[0]]
        self.length_intwall_3f_Hallway_x = [1.1, 1.1]
        self.length_intwall_3f_Hallway_y = [self.area_3f_Hallway / 1.1, self.area_3f_Hallway / 1.1]
        self.length_intwall_3f_Staircase_x = [np.sqrt(self.area_3f_Staircase / 1.5),
                                              np.sqrt(self.area_3f_Staircase / 1.0)]
        self.length_intwall_3f_Staircase_y = [self.area_3f_Staircase / self.length_intwall_3f_Staircase_x[1],
                                              self.area_3f_Staircase / self.length_intwall_3f_Staircase_x[0]]

        # Create list of all input variables to simplify LH sampling and rescaling depending on number of floors and (non-)available basement
        self.list_of_input_variables = [['length_extwall_x', self.length_extwall_x],
                                        ['length_extwall_y', self.length_extwall_y],
                                        ['length_intwall_base_Room1_x', self.length_intwall_b_Room1_x],
                                        ['length_intwall_base_Room1_y', self.length_intwall_b_Room1_y],
                                        ['length_intwall_base_Room2_x', self.length_intwall_b_Room2_x],
                                        ['length_intwall_base_Room2_y', self.length_intwall_b_Room2_y],
                                        ['length_intwall_base_Hallway_x', self.length_intwall_b_Hallway_x],
                                        ['length_intwall_base_Hallway_y', self.length_intwall_b_Hallway_y],
                                        ['length_intwall_base_Staircase_x', self.length_intwall_b_Staircase_x],
                                        ['length_intwall_base_Staircase_y', self.length_intwall_b_Staircase_y],
                                        ['length_intwall_1f_Livingroom_x', self.length_intwall_1f_Livingroom_x],
                                        ['length_intwall_1f_Livingroom_y', self.length_intwall_1f_Livingroom_y],
                                        ['length_intwall_1f_Kitchen_x', self.length_intwall_1f_Kitchen_x],
                                        ['length_intwall_1f_Kitchen_y', self.length_intwall_1f_Kitchen_y],
                                        ['length_intwall_1f_GuestWC_x', self.length_intwall_1f_GuestWC_x],
                                        ['length_intwall_1f_GuestWC_y', self.length_intwall_1f_GuestWC_y],
                                        ['length_intwall_1f_Guestroom_x', self.length_intwall_1f_Guestroom_x],
                                        ['length_intwall_1f_Guestroom_y', self.length_intwall_1f_Guestroom_y],
                                        ['length_intwall_1f_Entrance_x', self.length_intwall_1f_Entrance_x],
                                        ['length_intwall_1f_Entrance_y', self.length_intwall_1f_Entrance_y],
                                        ['length_intwall_1f_Staircase_x', self.length_intwall_1f_Staircase_x],
                                        ['length_intwall_1f_Staircase_y', self.length_intwall_1f_Staircase_y],
                                        ['length_intwall_2f_Bedroom1_x', self.length_intwall_2f_Bedroom1_x],
                                        ['length_intwall_2f_Bedroom1_y', self.length_intwall_2f_Bedroom1_y],
                                        ['length_intwall_2f_Bedroom2_x', self.length_intwall_2f_Bedroom2_x],
                                        ['length_intwall_2f_Bedroom2_y', self.length_intwall_2f_Bedroom2_y],
                                        ['length_intwall_2f_Bedroom3_x', self.length_intwall_2f_Bedroom3_x],
                                        ['length_intwall_2f_Bedroom3_y', self.length_intwall_2f_Bedroom3_y],
                                        ['length_intwall_2f_Bedroom4_x', self.length_intwall_2f_Bedroom4_x],
                                        ['length_intwall_2f_Bedroom4_y', self.length_intwall_2f_Bedroom4_y],
                                        ['length_intwall_2f_Bathroom_x', self.length_intwall_2f_Bathroom_x],
                                        ['length_intwall_2f_Bathroom_y', self.length_intwall_2f_Bathroom_y],
                                        ['length_intwall_2f_Hallway_x', self.length_intwall_2f_Hallway_x],
                                        ['length_intwall_2f_Hallway_y', self.length_intwall_2f_Hallway_y],
                                        ['length_intwall_2f_Staircase_x', self.length_intwall_2f_Staircase_x],
                                        ['length_intwall_2f_Staircase_y', self.length_intwall_2f_Staircase_y],
                                        ['length_intwall_3f_Atticroom1_x', self.length_intwall_3f_Atticroom1_x],
                                        ['length_intwall_3f_Atticroom1_y', self.length_intwall_3f_Atticroom1_y],
                                        ['length_intwall_3f_Atticroom2_x', self.length_intwall_3f_Atticroom2_x],
                                        ['length_intwall_3f_Atticroom2_y', self.length_intwall_3f_Atticroom2_y],
                                        ['length_intwall_3f_Hallway_x', self.length_intwall_3f_Hallway_x],
                                        ['length_intwall_3f_Hallway_y', self.length_intwall_3f_Hallway_y],
                                        ['length_intwall_3f_Staircase_x', self.length_intwall_3f_Staircase_x],
                                        ['length_intwall_3f_Staircase_y', self.length_intwall_3f_Staircase_y]]

    def lhs_areas_and_intwalls(self, n_samples):
        """
        Uses list of input variables to generate lhs samples for each input variable, and to find the
        total interior wall length, interior wall area, and total interior floor area.
        """

        def generate_lhs_sample():
            return lhs(1, samples=n_samples, criterion='center')

        # Generate samples belonging to [0, 1] for all variables in list
        dict_of_lhs_samples = {}

        #Adds keys,values for respective floor number if existent
        for variable in self.list_of_input_variables:
            if self.number_of_storeys == 2 and ('1f' in variable[0] or '2f' in variable[0] or 'extwall' in variable[0]):
                    dict_of_lhs_samples[variable[0]] = generate_lhs_sample()
            elif self.number_of_storeys == 3 and ('1f' in variable[0] or '2f' in variable[0] or '3f' in variable[0] or 'extwall' in variable[0]):
                    dict_of_lhs_samples[variable[0]] = generate_lhs_sample()
            elif self.number_of_storeys == 4 and ('base' in variable[0] or '1f' in variable[0] or '2f' in variable[0] or '3f' in variable[0] or 'extwall' in variable[0]):
                    dict_of_lhs_samples[variable[0]] = generate_lhs_sample()

        self.dict_of_lhs_samples = dict_of_lhs_samples

        self.list_of_rescaled_intwall_values = []
        self.list_of_rescaled_extwall_values = []
        self.list_of_rescaled_Staircase_x_values = []

        # Use the generated samples to generate possible lengths for variables with intwall and extwall.
        def rescale_lhs_sample(input_variables, lhs_samples, element_type, rescaled_values):
            for variable in input_variables:
                for key, sample in lhs_samples.items():
                    if (key == variable[0] and element_type in key):
                        rescaled_value = variable[1][0] + (variable[1][1] - variable[1][0]) * sample
                        rescaled_values.append(rescaled_value)

        rescale_lhs_sample(self.list_of_input_variables, self.dict_of_lhs_samples, 'intwall', self.list_of_rescaled_intwall_values)
        rescale_lhs_sample(self.list_of_input_variables, self.dict_of_lhs_samples, 'extwall', self.list_of_rescaled_extwall_values)
        rescale_lhs_sample(self.list_of_input_variables, self.dict_of_lhs_samples, 'Staircase_x', self.list_of_rescaled_Staircase_x_values)

        self.raw_input_values_intwall = np.hstack(self.list_of_rescaled_intwall_values)
        self.raw_input_values_extwall = np.hstack(self.list_of_rescaled_extwall_values)
        self.raw_input_values_Staircase_x = np.hstack(self.list_of_rescaled_Staircase_x_values)

        # Define output function. Find total, e.g. length of interior walls, for each rescaled, constrained sample set
        def find_total_of_variable_type(input, input_array):
            total_variable_type = 0
            for i in range(len(input)):
                total_variable_type += input_array[:, i]
            return total_variable_type

        self.interior_wall_lengths = find_total_of_variable_type(self.list_of_rescaled_intwall_values, self.raw_input_values_intwall)
        # the interior wall on different floor are listed. but the exterior wall is for the whole building. every foor is seen as an entirety, so it should multiple the number of storeys.
        self.exterior_wall_lengths = self.number_of_storeys * find_total_of_variable_type(self.list_of_rescaled_extwall_values,
                                                                 self.raw_input_values_extwall)
        self.Staircase_x_wall_lengths = find_total_of_variable_type(self.list_of_rescaled_Staircase_x_values,
                                                                    self.raw_input_values_Staircase_x)

        # Each rooms have a door to entrance, hallway or living room. If the floor are not considered, then the doors are also not exist.
        # the list_of_input_variables contains the 2 variables of exwall.
        if self.number_of_storeys == 2:
            # the list_of_input_variables includes 4-floor rooms, so the room on unrequired floors should be delated.
            num_rooms = (len(self.list_of_input_variables) - 2) / 2 - 4 - 4
            # On first floor: livingroom, entrance, staircase don't need doors.
            # On second floor: hallway and staicase don't need doors.
            num_doors = num_rooms - 3 - 2
        elif self.number_of_storeys == 3:
            num_rooms = (len(self.list_of_input_variables) - 2) / 2 - 4
            num_doors = num_rooms - 3 - 2 - 2
        else:
            num_rooms = (len(self.list_of_input_variables) - 2) / 2
            num_doors = num_rooms - 3 - 2 - 2 - 2
        # the staircase is open to entrance or hallway; the entrance is open to the living rooom.
        self.interior_wall_area = ((self.interior_wall_lengths * 2 - self.exterior_wall_lengths * 2) / 2 - self.Staircase_x_wall_lengths - num_doors * self.door_width - 1.5) * self.storey_height

        return self.interior_wall_area

    def intwall_list(self):

        if self.area_of_floor <= 52:
            self.small_SFH()
            total_intwall = self.lhs_areas_and_intwalls(self.n_sample)
        elif self.area_of_floor > 52 and self.area_of_floor <= 60:
            self.small_SFH()
            intwall_list1 = self.lhs_areas_and_intwalls(round(self.n_sample * (self.area_of_floor - 52) / (60 - 52)))
            self.normal_SFH()
            intwall_list2 = self.lhs_areas_and_intwalls(self.n_sample - round(self.n_sample * (self.area_of_floor - 52) / (60 - 52)))
            total_intwall = np.hstack((intwall_list1,intwall_list2))
        elif self.area_of_floor > 60 and self.area_of_floor <= 65:
            self.normal_SFH()
            total_intwall = self.lhs_areas_and_intwalls(self.n_sample)
        elif self.area_of_floor > 65 and self.area_of_floor <= 80:
            self.normal_SFH()
            intwall_list1 = self.lhs_areas_and_intwalls(round(self.n_sample * (self.area_of_floor - 65) / (80 - 65)))
            self.large_SFH()
            intwall_list2 = self.lhs_areas_and_intwalls(self.n_sample - round(self.n_sample * (self.area_of_floor - 65) / (80 - 65)))
            total_intwall = np.hstack((intwall_list1,intwall_list2))
        else:
            self.large_SFH()
            total_intwall = self.lhs_areas_and_intwalls(self.n_sample)

        return total_intwall



