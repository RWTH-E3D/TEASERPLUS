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

class IntWallAreaSFH:
    def __init__(self, net_leased_area, number_of_storeys, storey_height):

        """
        Constructor of IntWallArea class

        net_leased_area
        number_of_storeys: number of storeys in the building
        has_basement: Boolean
        storey_height: average height of storeys
        n_samples: No. of samples produced in Latin Hypercube Sampling for each variable

        The basic floor layout is assumed to consist of a basement, first floor, second floor, and third floor (attic).
        Each floor has a number of rooms of different usage types, assumed to be the common denominator of SFH in Germany.
        """

        self.net_leased_area = net_leased_area
        self.number_of_storeys = number_of_storeys
        self.storey_height = storey_height
        self.area_of_floor = self.net_leased_area / self.number_of_storeys

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

        # The meaning of variable name: Room1Room2_Room3 means that Room1 and Room2 are seemed as an entirety and the wall between the entirety and Room.
        # The Staircases stay open to the hallway or entrance for each floor.

        # The range of floor area is determined by second floor. So the calculation of wall lengths will also start from second floor.
        self.length_intwall_2f_Bedroom1_StaircaseHallwayBedroom2_x = [self.length_extwall_x[0] - self.door_width,
                                                                      self.length_extwall_x[1] - self.door_width]
        self.length_intwall_2f_HallwayBathroom_Bedroom2_y = [self.length_extwall_y[0] * ((self.area_of_floor - self.area_2f_Bedroom1) / self.area_of_floor) - self.door_width,
                                                             self.length_extwall_y[1] * ((self.area_of_floor - self.area_2f_Bedroom1) / self.area_of_floor) - self.door_width]
        self.length_intwall_2f_StaircaseHallway_Bathroom_x = [self.length_extwall_x[0] * (self.area_2f_Staircase + self.area_2f_Hallway + self.area_2f_Bathroom) / (self.area_of_floor - self.area_2f_Bedroom1) - self.door_width,
                                                              self.length_extwall_x[1] * (self.area_2f_Staircase + self.area_2f_Hallway + self.area_2f_Bathroom) / (self.area_of_floor - self.area_2f_Bedroom1) - self.door_width]

        # The wall length of 1f-GuestWC in y-direction is the same as the wall length of 2f-Bathroom in y-direction.
        # The minimal wall length of Bathroom is 1.65 m, which is larger than the GuestWC.
        self.length_intwall_1f_GuestWC_Entrance_y = [max(1.65 - self.door_width, self.area_2f_Bathroom / (self.length_intwall_2f_StaircaseHallway_Bathroom_x[1] + self.door_width) - self.door_width),
                                                     max(1.65 - self.door_width, self.area_2f_Bathroom / (self.length_intwall_2f_StaircaseHallway_Bathroom_x[0] + self.door_width) - self.door_width)]
        self.length_intwall_1f_Staircase_GuestWC_x = [self.area_1f_GuestWC / (self.length_intwall_1f_GuestWC_Entrance_y[1] + self.door_width),
                                                      self.area_1f_GuestWC / (self.length_intwall_1f_GuestWC_Entrance_y[0] + self.door_width)]
        self.length_intwall_1f_Livingroom_Staircase_x = self.length_intwall_1f_Staircase_GuestWC_x
        # The minimum width of entrance are set at 1.5 m. The entrance is open to Living room.
        self.length_intwall_1f_Livingroom_Kitchen_x = [max(1.8 - self.door_width, (self.length_extwall_x[0] - self.length_intwall_1f_Staircase_GuestWC_x[0]) * (self.area_1f_Kitchen) / (self.area_1f_Kitchen + self.area_1f_Entrance) - self.door_width),
                                                       max(1.8 - self.door_width, (self.length_extwall_x[1] - self.length_intwall_1f_Staircase_GuestWC_x[1]) * (self.area_1f_Kitchen) / (self.area_1f_Kitchen + self.area_1f_Entrance) - self.door_width)]
        self.length_intwall_1f_Entrance_Kitchen_y = [self.area_1f_Kitchen / (self.length_intwall_1f_Livingroom_Kitchen_x[1] + self.door_width),
                                                     self.area_1f_Kitchen / (self.length_intwall_1f_Livingroom_Kitchen_x[0] + self.door_width)]

        # The dimensions of Staircase and Hallway on different floors keep same.
        self.length_intwall_3f_Atticroom1_StaircaseHallwayAtticroom2_x = self.length_extwall_x
        self.length_intwall_3f_StaircaseHallway_Atticroom2_x = [self.length_intwall_2f_StaircaseHallway_Bathroom_x[0] + self.door_width,
                                                                self.length_intwall_2f_StaircaseHallway_Bathroom_x[1] + self.door_width]
        self.length_intwall_3f_Hallway_Atticroom1Atticroom2_y = [(self.area_3f_Hallway + self.area_3f_Staircase) / self.length_intwall_3f_StaircaseHallway_Atticroom2_x[1] - 2 * self.door_width,
                                                                 (self.area_3f_Hallway + self.area_3f_Staircase) / self.length_intwall_3f_StaircaseHallway_Atticroom2_x[0] - 2 * self.door_width]

        # The design of basement is the same as the design of attic.
        self.length_intwall_b_Room1_StaircaseHallwayRoom2_x = self.length_intwall_3f_Atticroom1_StaircaseHallwayAtticroom2_x
        self.length_intwall_b_StaircaseHallway_Room2_x = self.length_intwall_3f_StaircaseHallway_Atticroom2_x
        self.length_intwall_b_Hallway_Room1Room2_y = self.length_intwall_3f_Hallway_Atticroom1Atticroom2_y

        # Create list of all input variables to simplify LH sampling and rescaling depending on number of floors and (non-)available basement
        self.list_of_input_variables = [['length_intwall_2f_Bedroom1_StaircaseHallwayBedroom2_x', self.length_intwall_2f_Bedroom1_StaircaseHallwayBedroom2_x],
                                        ['length_intwall_2f_HallwayBathroom_Bedroom2_y', self.length_intwall_2f_HallwayBathroom_Bedroom2_y],
                                        ['length_intwall_2f_StaircaseHallway_Bathroom_x', self.length_intwall_2f_StaircaseHallway_Bathroom_x],
                                        ['length_intwall_1f_GuestWC_Entrance_y', self.length_intwall_1f_GuestWC_Entrance_y],
                                        ['length_intwall_1f_Staircase_GuestWC_x', self.length_intwall_1f_Staircase_GuestWC_x],
                                        ['length_intwall_1f_Livingroom_Staircase_x', self.length_intwall_1f_Livingroom_Staircase_x],
                                        ['length_intwall_1f_Livingroom_Kitchen_x', self.length_intwall_1f_Livingroom_Kitchen_x],
                                        ['length_intwall_1f_Entrance_Kitchen_y', self.length_intwall_1f_Entrance_Kitchen_y],
                                        ['length_intwall_3f_Atticroom1_StaircaseHallwayAtticroom2_x', self.length_intwall_3f_Atticroom1_StaircaseHallwayAtticroom2_x],
                                        ['length_intwall_3f_StaircaseHallway_Atticroom2_x', self.length_intwall_3f_StaircaseHallway_Atticroom2_x],
                                        ['length_intwall_3f_Hallway_Atticroom1Atticroom2_y', self.length_intwall_3f_Hallway_Atticroom1Atticroom2_y],
                                        ['length_intwall_base_Room1_StaircaseHallwayRoom2_x', self.length_intwall_b_Room1_StaircaseHallwayRoom2_x],
                                        ['length_intwall_base_StaircaseHallway_Room2_x', self.length_intwall_b_StaircaseHallway_Room2_x],
                                        ['length_intwall_base_Hallway_Room1Room2_y', self.length_intwall_b_Hallway_Room1Room2_y]]
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
        self.length_extwall_x = [max(6, np.sqrt(self.area_of_floor / 1.5)),
                                 max(6, np.sqrt(self.area_of_floor / 1.0))]
        self.length_extwall_y = [self.area_of_floor / self.length_extwall_x[1],
                                 self.area_of_floor / self.length_extwall_x[0]]

        # The meaning of variable name: Room1Room2_Room3 means that Room1 and Room2 are seemed as an entirety and the wall between the new entirety and Room3

        # The range of floor area is determined by second floor. So the calculation of wall lengths will also start from second floor.
        self.length_intwall_2f_Bedroom1HallwayBathroom_Bedroom2Bedroom3_y = [self.length_extwall_y[0] - 2 * self.door_width,
                                                                             self.length_extwall_y[1] - 2 * self.door_width]
        self.length_intwall_2f_Bedroom1Bedroom2_StaircaseHallwayBedroom3_x = self.length_extwall_x
        self.length_intwall_2f_StaircaseHallway_Bathroom_x = [self.length_extwall_x[0] * ((self.area_of_floor - self.area_2f_Bedroom2 - self.area_2f_Bedroom3) / self.area_of_floor) - self.door_width,
                                                              self.length_extwall_x[1] * ((self.area_of_floor - self.area_2f_Bedroom2 - self.area_2f_Bedroom3) / self.area_of_floor) - self.door_width]
        self.assistant_Hallway_x = [(self.length_intwall_2f_StaircaseHallway_Bathroom_x[0] + self.door_width) * (self.area_3f_Hallway / (self.area_3f_Hallway + self.area_3f_Staircase)),
                                    (self.length_intwall_2f_StaircaseHallway_Bathroom_x[1] + self.door_width) * (self.area_3f_Hallway / (self.area_3f_Hallway + self.area_3f_Staircase))]
        self.length_intwall_2f_Bedroom1_Hallway_y = [(self.area_2f_Hallway - self.area_3f_Hallway) / self.assistant_Hallway_x[1] - self.door_width,
                                                     (self.area_2f_Hallway - self.area_3f_Hallway) / self.assistant_Hallway_x[0] - self.door_width]

        self.length_intwall_1f_Livingroom_StaircaseEntranceKitchen_x = [self.length_extwall_x[0] - self.length_extwall_x[0] * self.area_1f_Entrance / (self.area_of_floor - self.area_1f_Livingroom) - self.door_width,
                                                                        self.length_extwall_x[1] - self.length_extwall_x[1] * self.area_1f_Entrance / (self.area_of_floor - self.area_1f_Livingroom) - self.door_width]
        self.length_intwall_1f_StaircaseKitchen_GuestWCGuestroom_x = [self.length_intwall_1f_Livingroom_StaircaseEntranceKitchen_x[0] + self.door_width,
                                                                      self.length_intwall_1f_Livingroom_StaircaseEntranceKitchen_x[1] + self.door_width]
        self.length_intwall_1f_Entrance_KitchenGuestroom_y = [self.length_extwall_y[0] * (self.area_of_floor - self.area_1f_Livingroom) / self.area_of_floor - self.door_width,
                                                              self.length_extwall_y[1] * (self.area_of_floor - self.area_1f_Livingroom) / self.area_of_floor - self.door_width]
        # The wall length of 1f-GuestWC in y-direction is the same as the wall length of 2f-Bathroom in y-direction.
        # The minimal wall length of Bathroom is 1.65 m, which is larger than the GuestWC.
        self.length_intwall_1f_GuestWC_Entrance_y = [max(1.65 - self.door_width, self.area_2f_Bathroom / (self.length_intwall_2f_StaircaseHallway_Bathroom_x[1] + self.door_width) - self.door_width),
                                                     max(1.65 - self.door_width, self.area_2f_Bathroom / (self.length_intwall_2f_StaircaseHallway_Bathroom_x[0] + self.door_width) - self.door_width)]

        self.length_intwall_3f_Atticroom1_StaircaseHallwayAtticroom2_x = self.length_extwall_x
        self.length_intwall_3f_StaircaseHallway_Atticroom2_x = [self.length_intwall_2f_StaircaseHallway_Bathroom_x[0] + self.door_width,
                                                                self.length_intwall_2f_StaircaseHallway_Bathroom_x[1] + self.door_width]
        self.length_intwall_3f_Hallway_Atticroom1Atticroom2_y = [(self.area_3f_Hallway + self.area_3f_Staircase) / self.length_intwall_3f_StaircaseHallway_Atticroom2_x[1] - 2 * self.door_width,
                                                                 (self.area_3f_Hallway + self.area_3f_Staircase) / self.length_intwall_3f_StaircaseHallway_Atticroom2_x[0] - 2 * self.door_width]

        # The design of basement is the same as the design of attic.
        self.length_intwall_b_Room1_StaircaseHallwayRoom2_x = self.length_intwall_3f_Atticroom1_StaircaseHallwayAtticroom2_x
        self.length_intwall_b_StaircaseHallway_Room2_x = self.length_intwall_3f_StaircaseHallway_Atticroom2_x
        self.length_intwall_b_Hallway_Room1Room2_y = self.length_intwall_3f_Hallway_Atticroom1Atticroom2_y

        # Create list of all input variables to simplify LH sampling and rescaling depending on number of floors and (non-)available basement
        self.list_of_input_variables = [
            ['length_intwall_2f_Bedroom1HallwayBathroom_Bedroom2Bedroom3_y', self.length_intwall_2f_Bedroom1HallwayBathroom_Bedroom2Bedroom3_y],
            ['length_intwall_2f_Bedroom1Bedroom2_StaircaseHallwayBedroom3_x', self.length_intwall_2f_Bedroom1Bedroom2_StaircaseHallwayBedroom3_x],
            ['length_intwall_2f_StaircaseHallway_Bathroom_x', self.length_intwall_2f_StaircaseHallway_Bathroom_x],
            ['length_intwall_2f_Bedroom1_Hallway_y', self.length_intwall_2f_Bedroom1_Hallway_y],
            ['length_intwall_1f_Livingroom_StaircaseEntranceKitchen_x', self.length_intwall_1f_Livingroom_StaircaseEntranceKitchen_x],
            ['length_intwall_1f_StaircaseKitchen_GuestWCGuestroom_x', self.length_intwall_1f_StaircaseKitchen_GuestWCGuestroom_x],
            ['length_intwall_1f_Entrance_KitchenGuestroom_y',self.length_intwall_1f_Entrance_KitchenGuestroom_y],
            ['length_intwall_1f_GuestWC_Entrance_y', self.length_intwall_1f_GuestWC_Entrance_y],
            ['length_intwall_3f_Atticroom1_StaircaseHallwayAtticroom2_x', self.length_intwall_3f_Atticroom1_StaircaseHallwayAtticroom2_x],
            ['length_intwall_3f_StaircaseHallway_Atticroom2_x', self.length_intwall_3f_StaircaseHallway_Atticroom2_x],
            ['length_intwall_3f_Hallway_Atticroom1Atticroom2_y', self.length_intwall_3f_Hallway_Atticroom1Atticroom2_y],
            ['length_intwall_base_Room1_StaircaseHallwayRoom2_x', self.length_intwall_b_Room1_StaircaseHallwayRoom2_x],
            ['length_intwall_base_StaircaseHallway_Room2_x', self.length_intwall_b_StaircaseHallway_Room2_x],
            ['length_intwall_base_Hallway_Room1Room2_y', self.length_intwall_b_Hallway_Room1Room2_y]]

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

        # The meaning of variable name: Room1Room2_Room3 means that Room1 and Room2 are seemed as an entirety and the wall between the new entirety and Room3

        # The range of floor area is determined by second floor. So the calculation of wall lengths will also start from second floor.
        # The Hallway width is set at 1.1 m.
        self.length_intwall_2f_Bedroom4Bedroom1_StaircaseHallwayBedroom2_x = self.length_extwall_x
        self.length_intwall_2f_StaircaseHallwayBedroom2_BathroomBedroom3_x = [self.length_extwall_x[0] - self.door_width,
                                                                              self.length_extwall_x[1] - self.door_width]
        self.length_intwall_2f_Bedroom4HallwayBathroom_Bedroom1Bedroom2Bedroom3_y = [self.length_extwall_y[0] - 3 * self.door_width,
                                                                                   self.length_extwall_y[1] - 3 * self.door_width]
        self.assistant_2f_StaircaseHallway_Bathroom_x = [self.length_extwall_x[0] * ((self.area_of_floor - self.area_2f_Bedroom1 - self.area_2f_Bedroom2 - self.area_2f_Bedroom3) / self.area_of_floor) - self.door_width,
                                                         self.length_extwall_x[1] * ((self.area_of_floor - self.area_2f_Bedroom1 - self.area_2f_Bedroom2 - self.area_2f_Bedroom3) / self.area_of_floor) - self.door_width]
        self.assistant_2f_Hallway_width = [(self.assistant_2f_StaircaseHallway_Bathroom_x[0] + self.door_width) * (self.area_3f_Hallway / (self.area_3f_Hallway + self.area_3f_Staircase)),
                                           (self.assistant_2f_StaircaseHallway_Bathroom_x[1] + self.door_width) * (self.area_3f_Hallway / (self.area_3f_Hallway + self.area_3f_Staircase))]
        self.length_intwall_2f_Bedroom4_Hallway_y = [(self.area_2f_Hallway - self.area_3f_Hallway) / self.assistant_2f_Hallway_width[1] - self.door_width,
                                                     (self.area_2f_Hallway - self.area_3f_Hallway) / self.assistant_2f_Hallway_width[0] - self.door_width]

        # The wall length of 1f-GuestWC in y-direction is the same as the wall length of 2f-Bathroom in y-direction.
        # The minimal wall length of Bathroom is 1.65 m, which is larger than the GuestWC.
        self.length_intwall_1f_GuestWC_Entrance_y = [max(1.65 - self.door_width, self.area_2f_Bathroom / (self.assistant_2f_StaircaseHallway_Bathroom_x[1] + self.door_width) - self.door_width),
                                                     max(1.65 - self.door_width, self.area_2f_Bathroom / (self.assistant_2f_StaircaseHallway_Bathroom_x[0] + self.door_width) - self.door_width)]
        self.length_intwall_1f_Staircase_GuestWC_x = [self.area_1f_GuestWC / (self.length_intwall_1f_GuestWC_Entrance_y[1] + self.door_width),
                                                      self.area_1f_GuestWC / (self.length_intwall_1f_GuestWC_Entrance_y[0] + self.door_width)]
        self.length_intwall_1f_Kitchen_Guestroom_x = [self.length_extwall_x[0] - (1 + (self.area_1f_Entrance / (self.area_1f_Staircase + self.area_1f_GuestWC))) * self.length_intwall_1f_Staircase_GuestWC_x[0],
                                                      self.length_extwall_x[1] - (1 + (self.area_1f_Entrance / (self.area_1f_Staircase + self.area_1f_GuestWC))) * self.length_intwall_1f_Staircase_GuestWC_x[1]]
        self.length_intwall_1f_Livingroom_Staircase_x = self.length_intwall_1f_Staircase_GuestWC_x
        self.length_intwall_1f_Livingroom_Kitchen_x = [self.length_intwall_1f_Kitchen_Guestroom_x[0] - self.door_width,
                                                       self.length_intwall_1f_Kitchen_Guestroom_x[1] - self.door_width]
        self.length_intwall_1f_Entrance_KitchenGuestroom_y = [(self.area_1f_Kitchen + self.area_1f_Guestroom) / self.length_intwall_1f_Kitchen_Guestroom_x[1] - self.door_width,
                                                              (self.area_1f_Kitchen + self.area_1f_Guestroom) / self.length_intwall_1f_Kitchen_Guestroom_x[0] - self.door_width]

        self.length_intwall_3f_Atticroom1_StaircaseHallwayAtticroom2_x = self.length_extwall_x
        self.length_intwall_3f_StaircaseHallway_Atticroom2_x = [(self.length_extwall_x[0] * (self.area_2f_Bathroom + self.area_2f_Hallway + self.area_2f_Staircase + self.area_2f_Bedroom4) / self.area_of_floor),
                                                                (self.length_extwall_x[1] * (self.area_2f_Bathroom + self.area_2f_Hallway + self.area_2f_Staircase + self.area_2f_Bedroom4) / self.area_of_floor)]
        self.length_intwall_3f_Hallway_Atticroom1Atticroom2_y = [(self.area_3f_Hallway + self.area_3f_Staircase) / self.length_intwall_3f_StaircaseHallway_Atticroom2_x[1] - 2 * self.door_width,
                                                                 (self.area_3f_Hallway + self.area_3f_Staircase) / self.length_intwall_3f_StaircaseHallway_Atticroom2_x[0] - 2 * self.door_width]

        # The design of basement is the same as the design of attic.
        self.length_intwall_b_Room1_StaircaseHallwayRoom2_x = self.length_intwall_3f_Atticroom1_StaircaseHallwayAtticroom2_x
        self.length_intwall_b_StaircaseHallway_Room2_x = self.length_intwall_3f_StaircaseHallway_Atticroom2_x
        self.length_intwall_b_Hallway_Room1Room2_y = self.length_intwall_3f_Hallway_Atticroom1Atticroom2_y

        # Create list of all input variables to simplify LH sampling and rescaling depending on number of floors and (non-)available basement
        self.list_of_input_variables = [
            ['length_intwall_2f_Bedroom4Bedroom1_StaircaseHallwayBedroom2_x', self.length_intwall_2f_Bedroom4Bedroom1_StaircaseHallwayBedroom2_x],
            ['length_intwall_2f_StaircaseHallwayBedroom2_BathroomBedroom3_x', self.length_intwall_2f_StaircaseHallwayBedroom2_BathroomBedroom3_x],
            ['length_intwall_2f_Bedroom4HallwayBathroom_Bedroom1Bedroom2Bedroom3_y', self.length_intwall_2f_Bedroom4HallwayBathroom_Bedroom1Bedroom2Bedroom3_y],
            ['length_intwall_2f_Bedroom4_Hallway_y', self.length_intwall_2f_Bedroom4_Hallway_y],
            ['length_intwall_1f_GuestWC_Entrance_y', self.length_intwall_1f_GuestWC_Entrance_y],
            ['length_intwall_1f_Staircase_GuestWC_x', self.length_intwall_1f_Staircase_GuestWC_x],
            ['length_intwall_1f_Kitchen_Guestroom_x',self.length_intwall_1f_Kitchen_Guestroom_x],
            ['length_intwall_1f_Livingroom_Staircase_x', self.length_intwall_1f_Livingroom_Staircase_x],
            ['length_intwall_1f_Livingroom_Kitchen_x', self.length_intwall_1f_Livingroom_Kitchen_x],
            ['length_intwall_1f_Entrance_KitchenGuestroom_y', self.length_intwall_1f_Entrance_KitchenGuestroom_y],
            ['length_intwall_3f_Atticroom1_StaircaseHallwayAtticroom2_x', self.length_intwall_3f_Atticroom1_StaircaseHallwayAtticroom2_x],
            ['length_intwall_3f_StaircaseHallway_Atticroom2_x', self.length_intwall_3f_StaircaseHallway_Atticroom2_x],
            ['length_intwall_3f_Hallway_Atticroom1Atticroom2_y', self.length_intwall_3f_Hallway_Atticroom1Atticroom2_y],
            ['length_intwall_base_Room1_StaircaseHallwayRoom2_x', self.length_intwall_b_Room1_StaircaseHallwayRoom2_x],
            ['length_intwall_base_StaircaseHallway_Room2_x', self.length_intwall_b_StaircaseHallway_Room2_x],
            ['length_intwall_base_Hallway_Room1Room2_y', self.length_intwall_b_Hallway_Room1Room2_y]]

    def lhs_areas_and_intwalls(self, n_samples):
        """
        Uses list of input variables to generate lhs samples for each input variable, and to find the
        total interior wall length, interior wall area, and total interior floor area.
        """

        def generate_lhs_sample():
            return lhs(1, samples=n_samples, criterion='center')

        dict_of_lhs_samples = {}

        #Adds keys,values for respective floor number if existent
        for variable in self.list_of_input_variables:
            if self.number_of_storeys == 2 and ('1f' in variable[0] or '2f' in variable[0]):
                    dict_of_lhs_samples[variable[0]] = generate_lhs_sample()
            elif self.number_of_storeys == 3 and ('1f' in variable[0] or '2f' in variable[0] or '3f' in variable[0]):
                    dict_of_lhs_samples[variable[0]] = generate_lhs_sample()
            elif self.number_of_storeys == 4 and ('base' in variable[0] or '1f' in variable[0] or '2f' in variable[0] or '3f' in variable[0]):
                    dict_of_lhs_samples[variable[0]] = generate_lhs_sample()

        self.dict_of_lhs_samples = dict_of_lhs_samples

        self.list_of_rescaled_intwall_values = []

        def rescale_lhs_sample(input_variables, lhs_samples, element_type, rescaled_values):
            for variable in input_variables:
                for key, sample in lhs_samples.items():
                    if (key == variable[0] and element_type in key):
                        rescaled_value = variable[1][0] + (variable[1][1] - variable[1][0]) * sample
                        rescaled_values.append(rescaled_value)

        rescale_lhs_sample(self.list_of_input_variables, self.dict_of_lhs_samples, 'intwall', self.list_of_rescaled_intwall_values)

        self.raw_input_values_intwall = np.hstack(self.list_of_rescaled_intwall_values)

        # Define output function. Find total, e.g. length of interior walls, for each rescaled, constrained sample set
        def find_total_of_variable_type(input, input_array):
            total_variable_type = 0
            for i in range(len(input)):
                total_variable_type += input_array[:, i]
            return total_variable_type

        self.interior_wall_lengths = find_total_of_variable_type(self.list_of_rescaled_intwall_values, self.raw_input_values_intwall)
        self.interior_wall_area = self.interior_wall_lengths * self.storey_height

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



