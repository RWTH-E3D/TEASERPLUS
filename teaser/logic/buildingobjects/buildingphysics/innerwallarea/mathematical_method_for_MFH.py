import pandas as pd
import os
import random
import numpy as np
from pyDOE import lhs

class IntWallAreaMFH:
    def __init__(self, NLA, number_of_storeys, storey_height):

        self.NLA = NLA
        self.number_of_storeys = number_of_storeys
        self.storey_height = storey_height

        self.area_of_floor = self.NLA / self.number_of_storeys
        self.number_of_total_apartments = None
        self.door_width = 1.1
        self.area_of_apartment = None
        self.wall_ratio_minimum = 1.0
        self.wall_ratio_maximum = 1.5
        self.wall_ratio = [self.wall_ratio_minimum, self.wall_ratio_maximum]
        self.n_sample = 200

    def one_apartment(self):

        self.area_of_core = 12
        self.area_of_apartment = self.area_of_floor - self.area_of_core

        # Assume the length_y is always longer
        self.length_extwall_x = [np.sqrt(self.area_of_floor / 1.6),
                                 np.sqrt(self.area_of_floor / 1.0)]
        self.length_extwall_y = [np.sqrt(self.area_of_floor * 1.0),
                                 np.sqrt(self.area_of_floor * 1.6)]

        # The dimension of staircase is 2.4 m * 5 m.
        self.intwall_length_Core_Apartment_x = [2.4 - self.door_width, 2.4 - self.door_width]
        self.intwall_length_Core_Apartment_y = [5, 5]

        self.list_of_input_variables = [['intwall_length_Core_Apartment_x', self.intwall_length_Core_Apartment_x],
                                        ['intwall_length_Core_Apartment_y', self.intwall_length_Core_Apartment_y]]

        return self.list_of_input_variables

    def two_apartment(self):

        self.area_of_core = 15
        self.area_of_apartment1 = (self.area_of_floor - self.area_of_core) * 0.5
        self.area_of_apartment2 = (self.area_of_floor - self.area_of_core) * 0.5

        # The floor ratio is calculated from two apartments with ratio [1, 1.6]
        self.length_extwall_x = [np.sqrt(self.area_of_floor / 0.8),
                                 np.sqrt(self.area_of_floor / 0.3)]
        self.length_extwall_y = [np.sqrt(self.area_of_floor * 0.3),
                                 np.sqrt(self.area_of_floor * 0.8)]

        # The dimension of staircase is 3 m * 5 m.
        self.intwall_length_Core_Apartment1Apartment2_x = [3 - 2 * self.door_width, 3 - 2 * self.door_width]
        self.intwall_length_Core_Apartment1_y = [5, 5]
        self.intwall_length_Core_Apartment2_y = [5, 5]
        self.intwall_length_Apartment1_Apartment2_y = [self.length_extwall_y[0] - self.intwall_length_Core_Apartment1_y[1],
                                                       self.length_extwall_y[1] - self.intwall_length_Core_Apartment1_y[0]]

        self.list_of_input_variables = [['intwall_length_Core_Apartment1Apartment2_x', self.intwall_length_Core_Apartment1Apartment2_x],
                                        ['intwall_length_Core_Apartment1_y', self.intwall_length_Core_Apartment1_y],
                                        ['intwall_length_Core_Apartment2_y', self.intwall_length_Core_Apartment2_y],
                                        ['intwall_length_Apartment1_Apartment2_y', self.intwall_length_Apartment1_Apartment2_y]]

        return self.list_of_input_variables

    def three_apartment(self):

        self.area_of_core = 18
        self.area_of_apartment1 = (self.area_of_floor - self.area_of_core) * 0.38
        self.area_of_apartment2 = (self.area_of_floor - self.area_of_core) * 0.38
        self.area_of_apartment3 = (self.area_of_floor - self.area_of_core) * 0.24

        # The floor ratio is calculated from three apartments with ratio [1, 1.6]
        self.length_extwall_x = [np.sqrt(self.area_of_floor / 0.8),
                                 np.sqrt(self.area_of_floor / 0.3)]
        self.length_extwall_y = [np.sqrt(self.area_of_floor * 0.3),
                                 np.sqrt(self.area_of_floor * 0.8)]

        self.intwall_length_CoreApartment3_Apartment1_y = [self.length_extwall_y[0] - self.door_width,
                                                           self.length_extwall_y[1] - self.door_width]
        self.intwall_length_CoreApartment3_Apartment2_y = self.intwall_length_CoreApartment3_Apartment1_y
        self.intwall_length_Apartment1CoreApartment2_Apartment3_x = [np.sqrt(self.area_of_apartment3 / 1.6),
                                                                     np.sqrt(self.area_of_apartment3 / 1.0)]

        self.list_of_input_variables = [['intwall_length_CoreApartment3_Apartment1_y', self.intwall_length_CoreApartment3_Apartment1_y],
                                        ['intwall_length_CoreApartment3_Apartment2_y', self.intwall_length_CoreApartment3_Apartment2_y],
                                        ['intwall_length_Apartment1CoreApartment2_Apartment3_x', self.intwall_length_Apartment1CoreApartment2_Apartment3_x]]

        return self.list_of_input_variables

    def four_apartment(self):

        self.area_of_core = 21
        self.area_of_apartment1 = (self.area_of_floor - self.area_of_core) * 0.25
        self.area_of_apartment2 = (self.area_of_floor - self.area_of_core) * 0.25
        self.area_of_apartment3 = (self.area_of_floor - self.area_of_core) * 0.25
        self.area_of_apartment4 = (self.area_of_floor - self.area_of_core) * 0.25

        self.length_extwall_x = [np.sqrt(self.area_of_floor / 1.6),
                                 np.sqrt(self.area_of_floor / 1)]
        self.length_extwall_y = [np.sqrt(self.area_of_floor * 1.0),
                                 np.sqrt(self.area_of_floor * 1.6)]

        # The dimension of staircase is 4.5 m * 5 m.
        self.intwall_length_Core_Apartment1Apartment3_x = [4.2, 4.2]
        self.intwall_length_Core_Apartment2Apartment4_x = [4.2, 4.2]
        self.intwall_length_Core_Apartment1Apartment2_y = [5, 5]
        self.intwall_length_Core_Apartment3Apartment4_y = [5, 5]
        self.intwall_length_Apartment1Apartment3_Apartment2Apartment4_y = [self.length_extwall_y[0] - 5, self.length_extwall_y[1] - 5]
        self.intwall_length_Apartment1Apartment2_Apartment3Apartment4_x = [self.length_extwall_x[0] - 4.2, self.length_extwall_x[1] - 4.2]

        self.list_of_input_variables = [['intwall_length_Core_Apartment1Apartment3_x', self.intwall_length_Core_Apartment1Apartment3_x],
                                        ['intwall_length_Core_Apartment2Apartment4_x', self.intwall_length_Core_Apartment2Apartment4_x],
                                        ['intwall_length_Core_Apartment1Apartment2_y', self.intwall_length_Core_Apartment1Apartment2_y],
                                        ['intwall_length_Core_Apartment3Apartment4_y', self.intwall_length_Core_Apartment3Apartment4_y],
                                        ['intwall_length_Apartment1Apartment3_Apartment2Apartment4_y', self.intwall_length_Apartment1Apartment3_Apartment2Apartment4_y],
                                        ['intwall_length_Apartment1Apartment2_Apartment3Apartment4_x', self.intwall_length_Apartment1Apartment2_Apartment3Apartment4_x]]

        return self.list_of_input_variables

    def multi_apartment(self):

        self.area_of_corridor = self.area_of_floor * 0.12
        # The rooms on one floor include several studios and at least on vertial circulation unit. Assume the area of each vertical circualtion unit is the same with the area of one studio apartment.
        # The area of room is between 20 and 45 -> average area 32.5 m^2
        # The corridor is double-loaded. The room and vertical circulation are evenly distributed on both sides.
        self.number_of_apartments = max(5, 2*(round((self.area_of_floor * (1 - 0.12) / 32.5)/2)) - 1)
        # Get the number of apartments from average studio area. Get the exact studio area  from the number of apartments.
        self.area_of_studioapartment = self.area_of_floor * (1 - 0.12) / (self.number_of_apartments + 1)

        self.length_Studio_Corridor_x = [np.sqrt(self.area_of_studioapartment / 1.6),
                                         np.sqrt(self.area_of_studioapartment / 1.0)]
        self.length_Studio_Studio_y = [np.sqrt(self.area_of_studioapartment * 1.0),
                                       np.sqrt(self.area_of_studioapartment * 1.6)]

        # There must be a wall in x-direction between every room and corridor
        # There must be a wall between two rooms. And the corridor is double-loaded
        self.intwall_length_x = [self.number_of_apartments * (self.length_Studio_Corridor_x[0] - self.door_width),
                                 self.number_of_apartments * (self.length_Studio_Corridor_x[1] - self.door_width)]
        self.intwall_length_y = [(self.number_of_apartments - 2) * self.length_Studio_Studio_y[0],
                                 (self.number_of_apartments - 2) * self.length_Studio_Studio_y[1]]

        self.list_of_input_variables = [['intwall_length_x', self.intwall_length_x],
                                        ['intwall_length_y', self.intwall_length_y]]

        return self.list_of_input_variables

    def studio(self, area_of_apartment):

        self.area_of_apartment = area_of_apartment
        self.area_for_living = 0.85 * self.area_of_apartment
        self.area_of_bathroom = 0.15 * self.area_of_apartment

        self.wall_ratio = [self.wall_ratio_minimum, self.wall_ratio_maximum]

        self.length_extwall_x = [np.sqrt(self.area_of_apartment / 1.6),
                                 np.sqrt(self.area_of_apartment / 1.0)]
        self.length_extwall_y = [np.sqrt(self.area_of_apartment * 1.0),
                                 np.sqrt(self.area_of_apartment * 1.6)]

        self.intwall_length_living_x = [max(3.5, np.sqrt(self.area_for_living / self.wall_ratio[1])),
                                        max(3.5, np.sqrt(self.area_for_living / self.wall_ratio[0]))]
        self.intwall_length_living_y = [self.area_for_living / self.intwall_length_living_x[1],
                                        self.area_for_living / self.intwall_length_living_x[0]]
        self.intwall_length_bathroom_x = [max(1.6, np.sqrt(self.area_of_bathroom / self.wall_ratio[1])),
                                          max(1.6, np.sqrt(self.area_of_bathroom / self.wall_ratio[0]))]
        self.intwall_length_bathroom_y = [self.area_of_bathroom / self.intwall_length_bathroom_x[1],
                                          self.area_of_bathroom / self.intwall_length_bathroom_x[0]]

        self.list_of_input_variables = [['length_extwall_x', self.length_extwall_x],
                                        ['length_extwall_y', self.length_extwall_y],
                                        ['intwall_length_living_x', self.intwall_length_living_x],
                                        ['intwall_length_living_y', self.intwall_length_living_y],
                                        ['intwall_length_bathroom_x', self.intwall_length_bathroom_x],
                                        ['intwall_length_bathroom_y', self.intwall_length_bathroom_y]]

        return self.list_of_input_variables

    def one_bedroom(self, area_of_apartment):

        self.area_of_apartment = area_of_apartment
        self.length_extwall_x = [np.sqrt(self.area_of_apartment / 1.6),
                                 np.sqrt(self.area_of_apartment / 1.0)]
        self.length_extwall_y = [self.area_of_apartment / self.length_extwall_x[1],
                                 self.area_of_apartment / self.length_extwall_x[0]]

        if self.area_of_apartment < 51:
            self.area_of_livingroom = 0.55 * self.area_of_apartment
            self.area_of_bedroom = 0.30 * self.area_of_apartment
            self.area_of_bathroom = 0.15 * self.area_of_apartment

            self.intwall_length_livingroom_x = [max(3.5, np.sqrt(self.area_of_livingroom / self.wall_ratio[1])),
                                                max(3.5, np.sqrt(self.area_of_livingroom / self.wall_ratio[0]))]
            self.intwall_length_livingroom_y = [self.area_of_livingroom / self.intwall_length_livingroom_x[1],
                                                self.area_of_livingroom / self.intwall_length_livingroom_x[0]]
            self.intwall_length_bedroom_x = [max(2.7, np.sqrt(self.area_of_bedroom / self.wall_ratio[1])),
                                             max(2.7, np.sqrt(self.area_of_bedroom / self.wall_ratio[0]))]
            self.intwall_length_bedroom_y = [self.area_of_bedroom / self.intwall_length_bedroom_x[1],
                                             self.area_of_bedroom / self.intwall_length_bedroom_x[0]]
            self.intwall_length_bathroom_x = [max(1.6, np.sqrt(self.area_of_bathroom / self.wall_ratio[1])),
                                              max(1.6, np.sqrt(self.area_of_bathroom / self.wall_ratio[0]))]
            self.intwall_length_bathroom_y = [self.area_of_bathroom / self.intwall_length_bathroom_x[1],
                                              self.area_of_bathroom / self.intwall_length_bathroom_x[0]]

            self.list_of_input_variables = [['length_extwall_x', self.length_extwall_x],
                                            ['length_extwall_y', self.length_extwall_y],
                                            ['intwall_length_livingroom_x', self.intwall_length_livingroom_x],
                                            ['intwall_length_livingroom_y', self.intwall_length_livingroom_y],
                                            ['intwall_length_bedroom_x', self.intwall_length_bedroom_x],
                                            ['intwall_length_bedroom_y', self.intwall_length_bedroom_y],
                                            ['intwall_length_bathroom_x', self.intwall_length_bathroom_x],
                                            ['intwall_length_bathroom_y', self.intwall_length_bathroom_y]]
        else:
            self.area_of_livingroom = 0.40 * self.area_of_apartment
            self.area_of_bedroom = 0.30 * self.area_of_apartment
            self.area_of_bathroom = 0.15 * self.area_of_apartment
            self.area_of_kitchen = 0.15 * self.area_of_apartment

            self.intwall_length_livingroom_x = [max(3.5, np.sqrt(self.area_of_livingroom / self.wall_ratio[1])),
                                                max(3.5, np.sqrt(self.area_of_livingroom / self.wall_ratio[0]))]
            self.intwall_length_livingroom_y = [self.area_of_livingroom / self.intwall_length_livingroom_x[1],
                                                self.area_of_livingroom / self.intwall_length_livingroom_x[0]]
            self.intwall_length_bedroom_x = [max(2.7, np.sqrt(self.area_of_bedroom / self.wall_ratio[1])),
                                             max(2.7, np.sqrt(self.area_of_bedroom / self.wall_ratio[0]))]
            self.intwall_length_bedroom_y = [self.area_of_bedroom / self.intwall_length_bedroom_x[1],
                                             self.area_of_bedroom / self.intwall_length_bedroom_x[0]]
            self.intwall_length_bathroom_x = [max(1.6, np.sqrt(self.area_of_bathroom / self.wall_ratio[1])),
                                              max(1.6, np.sqrt(self.area_of_bathroom / self.wall_ratio[0]))]
            self.intwall_length_bathroom_y = [self.area_of_bathroom / self.intwall_length_bathroom_x[1],
                                              self.area_of_bathroom / self.intwall_length_bathroom_x[0]]
            self.intwall_length_kitchen_x = [max(1.8, np.sqrt(self.area_of_kitchen / self.wall_ratio[1])),
                                             max(1.8, np.sqrt(self.area_of_kitchen / self.wall_ratio[0]))]
            self.intwall_length_kitchen_y = [self.area_of_kitchen / self.intwall_length_kitchen_x[1],
                                             self.area_of_kitchen / self.intwall_length_kitchen_x[0]]

            self.list_of_input_variables = [['length_extwall_x', self.length_extwall_x],
                                            ['length_extwall_y', self.length_extwall_y],
                                            ['intwall_length_livingroom_x', self.intwall_length_livingroom_x],
                                            ['intwall_length_livingroom_y', self.intwall_length_livingroom_y],
                                            ['intwall_length_bedroom_x', self.intwall_length_bedroom_x],
                                            ['intwall_length_bedroom_y', self.intwall_length_bedroom_y],
                                            ['intwall_length_bathroom_x', self.intwall_length_bathroom_x],
                                            ['intwall_length_bathroom_y', self.intwall_length_bathroom_y],
                                            ['intwall_length_kitchen_x', self.intwall_length_kitchen_x],
                                            ['intwall_length_kitchen_y', self.intwall_length_kitchen_y]]

        return self.list_of_input_variables

    def two_bedroom(self, area_of_apartment):

        self.area_of_apartment = area_of_apartment
        self.area_of_entrance = 0.10 * self.area_of_apartment
        self.area_of_livingroom = 0.30 * self.area_of_apartment
        self.area_of_bedroom1 = 0.20 * self.area_of_apartment
        self.area_of_bedroom2 = 0.15 * self.area_of_apartment
        self.area_of_bathroom = 0.10 * self.area_of_apartment
        self.area_of_kitchen = 0.15 * self.area_of_apartment

        self.length_extwall_x = [np.sqrt(self.area_of_apartment / 1.6),
                                 np.sqrt(self.area_of_apartment / 1.0)]
        self.length_extwall_y = [np.sqrt(self.area_of_apartment * 1.0),
                                 np.sqrt(self.area_of_apartment * 1.6)]

        self.intwall_length_entrance_x = [max(1.5, np.sqrt(self.area_of_entrance / self.wall_ratio[1])),
                                          max(1.5, np.sqrt(self.area_of_entrance / self.wall_ratio[0]))]
        self.intwall_length_entrance_y = [self.area_of_entrance /  self.intwall_length_entrance_x[1],
                                          self.area_of_entrance /  self.intwall_length_entrance_x[0]]
        self.intwall_length_livingroom_x = [max(3.5, np.sqrt(self.area_of_livingroom / self.wall_ratio[1])),
                                            max(3.5, np.sqrt(self.area_of_livingroom / self.wall_ratio[0]))]
        self.intwall_length_livingroom_y = [self.area_of_livingroom / self.intwall_length_livingroom_x[1],
                                            self.area_of_livingroom / self.intwall_length_livingroom_x[0]]
        self.intwall_length_bedroom1_x = [max(2.7, np.sqrt(self.area_of_bedroom1 / self.wall_ratio[1])),
                                          max(2.7, np.sqrt(self.area_of_bedroom1 / self.wall_ratio[0]))]
        self.intwall_length_bedroom1_y = [self.area_of_bedroom1 / self.intwall_length_bedroom1_x[1],
                                          self.area_of_bedroom1 / self.intwall_length_bedroom1_x[0]]
        self.intwall_length_bedroom2_x = [max(2.7, np.sqrt(self.area_of_bedroom2 / self.wall_ratio[1])),
                                          max(2.7, np.sqrt(self.area_of_bedroom2 / self.wall_ratio[0]))]
        self.intwall_length_bedroom2_y = [self.area_of_bedroom2 / self.intwall_length_bedroom2_x[1],
                                          self.area_of_bedroom2 / self.intwall_length_bedroom2_x[0]]
        self.intwall_length_bathroom_x = [max(1.6, np.sqrt(self.area_of_bathroom / self.wall_ratio[1])),
                                          max(1.6, np.sqrt(self.area_of_bathroom / self.wall_ratio[0]))]
        self.intwall_length_bathroom_y = [self.area_of_bathroom / self.intwall_length_bathroom_x[1],
                                          self.area_of_bathroom / self.intwall_length_bathroom_x[0]]
        self.intwall_length_kitchen_x = [max(1.8, np.sqrt(self.area_of_kitchen / self.wall_ratio[1])),
                                         max(1.8, np.sqrt(self.area_of_kitchen / self.wall_ratio[0]))]
        self.intwall_length_kitchen_y = [self.area_of_kitchen / self.intwall_length_kitchen_x[1],
                                         self.area_of_kitchen / self.intwall_length_kitchen_x[0]]

        self.list_of_input_variables = [['length_extwall_x', self.length_extwall_x],
                                        ['length_extwall_y', self.length_extwall_y],
                                        ['intwall_length_entrance_x', self.intwall_length_entrance_x],
                                        ['intwall_length_entrance_y', self.intwall_length_entrance_y],
                                        ['intwall_length_livingroom_x', self.intwall_length_livingroom_x],
                                        ['intwall_length_livingroom_y', self.intwall_length_livingroom_y],
                                        ['intwall_length_bedroom1_x', self.intwall_length_bedroom1_x],
                                        ['intwall_length_bedroom1_y', self.intwall_length_bedroom1_y],
                                        ['intwall_length_bedroom2_x', self.intwall_length_bedroom2_x],
                                        ['intwall_length_bedroom2_y', self.intwall_length_bedroom2_y],
                                        ['intwall_length_bathroom_x', self.intwall_length_bathroom_x],
                                        ['intwall_length_bathroom_y', self.intwall_length_bathroom_y],
                                        ['intwall_length_kitchen_x', self.intwall_length_kitchen_x],
                                        ['intwall_length_kitchen_y', self.intwall_length_kitchen_y]]

        return self.list_of_input_variables

    def three_bedroom(self, area_of_apartment):

        self.area_of_apartment = area_of_apartment
        self.area_of_entrance = 0.04 * self.area_of_apartment
        self.area_of_livingroom = 0.28 * self.area_of_apartment
        self.area_of_bedroom1 = 0.18 * self.area_of_apartment
        self.area_of_bedroom2 = 0.12 * self.area_of_apartment
        self.area_of_bedroom3 = 0.12 * self.area_of_apartment
        self.area_of_bathroom = 0.08 * self.area_of_apartment
        self.area_of_guestWC = 0.05 * self.area_of_apartment
        self.area_of_kitchen = 0.08 * self.area_of_apartment
        self.area_of_hallway = 0.05 * self.area_of_apartment

        self.length_extwall_x = [np.sqrt(self.area_of_apartment / 1.6),
                                 np.sqrt(self.area_of_apartment / 1.0)]
        self.length_extwall_y = [np.sqrt(self.area_of_apartment * 1.0),
                                 np.sqrt(self.area_of_apartment * 1.6)]

        self.intwall_length_entrance_x = [max(1.5, np.sqrt(self.area_of_entrance / self.wall_ratio[1])),
                                          max(1.5, np.sqrt(self.area_of_entrance / self.wall_ratio[0]))]
        self.intwall_length_entrance_y = [self.area_of_entrance / self.intwall_length_entrance_x[1],
                                          self.area_of_entrance / self.intwall_length_entrance_x[0]]
        self.intwall_length_livingroom_x = [max(3.5, np.sqrt(self.area_of_livingroom / self.wall_ratio[1])),
                                            max(3.5, np.sqrt(self.area_of_livingroom / self.wall_ratio[0]))]
        self.intwall_length_livingroom_y = [self.area_of_livingroom / self.intwall_length_livingroom_x[1],
                                            self.area_of_livingroom / self.intwall_length_livingroom_x[0]]
        self.intwall_length_bedroom1_x = [max(2.7, np.sqrt(self.area_of_bedroom1 / self.wall_ratio[1])),
                                          max(2.7, np.sqrt(self.area_of_bedroom1 / self.wall_ratio[0]))]
        self.intwall_length_bedroom1_y = [self.area_of_bedroom1 / self.intwall_length_bedroom1_x[1],
                                          self.area_of_bedroom1 / self.intwall_length_bedroom1_x[0]]
        self.intwall_length_bedroom2_x = [max(2.7, np.sqrt(self.area_of_bedroom2 / self.wall_ratio[1])),
                                          max(2.7, np.sqrt(self.area_of_bedroom2 / self.wall_ratio[0]))]
        self.intwall_length_bedroom2_y = [self.area_of_bedroom2 / self.intwall_length_bedroom2_x[1],
                                          self.area_of_bedroom2 / self.intwall_length_bedroom2_x[0]]
        self.intwall_length_bedroom3_x = [max(2.7, np.sqrt(self.area_of_bedroom3 / self.wall_ratio[1])),
                                          max(2.7, np.sqrt(self.area_of_bedroom3 / self.wall_ratio[0]))]
        self.intwall_length_bedroom3_y = [self.area_of_bedroom3 / self.intwall_length_bedroom3_x[1],
                                          self.area_of_bedroom3 / self.intwall_length_bedroom3_x[0]]
        self.intwall_length_bathroom_x = [max(1.6, np.sqrt(self.area_of_bathroom / self.wall_ratio[1])),
                                          max(1.6, np.sqrt(self.area_of_bathroom / self.wall_ratio[0]))]
        self.intwall_length_bathroom_y = [self.area_of_bathroom / self.intwall_length_bathroom_x[1],
                                          self.area_of_bathroom / self.intwall_length_bathroom_x[0]]
        self.intwall_length_guestWC_x = [max(0.9, np.sqrt(self.area_of_guestWC / self.wall_ratio[1])),
                                         max(0.9, np.sqrt(self.area_of_guestWC / self.wall_ratio[0]))]
        self.intwall_length_guestWC_y = [self.area_of_guestWC / self.intwall_length_guestWC_x[1],
                                         self.area_of_guestWC / self.intwall_length_guestWC_x[0]]
        self.intwall_length_kitchen_x = [max(1.8, np.sqrt(self.area_of_kitchen / self.wall_ratio[1])),
                                         max(1.8, np.sqrt(self.area_of_kitchen / self.wall_ratio[0]))]
        self.intwall_length_kitchen_y = [self.area_of_kitchen / self.intwall_length_kitchen_x[1],
                                         self.area_of_kitchen / self.intwall_length_kitchen_x[0]]
        self.intwall_length_hallway_x = [max(1.8, np.sqrt(self.area_of_hallway / self.wall_ratio[1])),
                                         max(1.8, np.sqrt(self.area_of_hallway / self.wall_ratio[0]))]
        self.intwall_length_hallway_y = [self.area_of_hallway / self.intwall_length_hallway_x[1],
                                         self.area_of_hallway / self.intwall_length_hallway_x[0]]

        self.list_of_input_variables = [['length_extwall_x', self.length_extwall_x],
                                        ['length_extwall_y', self.length_extwall_y],
                                        ['intwall_length_entrance_x', self.intwall_length_entrance_x],
                                        ['intwall_length_entrance_y', self.intwall_length_entrance_y],
                                        ['intwall_length_livingroom_x', self.intwall_length_livingroom_x],
                                        ['intwall_length_livingroom_y', self.intwall_length_livingroom_y],
                                        ['intwall_length_bedroom1_x', self.intwall_length_bedroom1_x],
                                        ['intwall_length_bedroom1_y', self.intwall_length_bedroom1_y],
                                        ['intwall_length_bedroom2_x', self.intwall_length_bedroom2_x],
                                        ['intwall_length_bedroom2_y', self.intwall_length_bedroom2_y],
                                        ['intwall_length_bedroom3_x', self.intwall_length_bedroom3_x],
                                        ['intwall_length_bedroom3_y', self.intwall_length_bedroom3_y],
                                        ['intwall_length_bathroom_x', self.intwall_length_bathroom_x],
                                        ['intwall_length_bathroom_y', self.intwall_length_bathroom_y],
                                        ['intwall_length_guestWC_x', self.intwall_length_guestWC_x],
                                        ['intwall_length_guestWC_y', self.intwall_length_guestWC_y],
                                        ['intwall_length_kitchen_x', self.intwall_length_kitchen_x],
                                        ['intwall_length_kitchen_y', self.intwall_length_kitchen_y],
                                        ['intwall_length_hallway_x', self.intwall_length_hallway_x],
                                        ['intwall_length_hallway_y', self.intwall_length_hallway_y]]
        return self.list_of_input_variables

    def four_bedroom(self, area_of_apartment):
        self.area_of_apartment = area_of_apartment
        self.area_of_entrance = 0.03 * self.area_of_apartment
        self.area_of_livingroom = 0.26 * self.area_of_apartment
        self.area_of_bedroom1 = 0.15 * self.area_of_apartment
        self.area_of_bedroom2 = 0.11 * self.area_of_apartment
        self.area_of_bedroom3 = 0.11 * self.area_of_apartment
        self.area_of_bedroom4  = 0.11 * self.area_of_apartment
        self.area_of_bathroom = 0.06 * self.area_of_apartment
        self.area_of_guestWC = 0.05 * self.area_of_apartment
        self.area_of_kitchen = 0.07 * self.area_of_apartment
        self.area_of_hallway = 0.05 * self.area_of_apartment

        self.length_extwall_x = [np.sqrt(self.area_of_apartment / 1.6),
                                 np.sqrt(self.area_of_apartment / 1.0)]
        self.length_extwall_y = [np.sqrt(self.area_of_apartment * 1.0),
                                 np.sqrt(self.area_of_apartment * 1.6)]

        self.intwall_length_entrance_x = [max(1.5, np.sqrt(self.area_of_entrance / self.wall_ratio[1])),
                                          max(1.5, np.sqrt(self.area_of_entrance / self.wall_ratio[0]))]
        self.intwall_length_entrance_y = [self.area_of_entrance / self.intwall_length_entrance_x[1],
                                          self.area_of_entrance / self.intwall_length_entrance_x[0]]
        self.intwall_length_livingroom_x = [max(3.5, np.sqrt(self.area_of_livingroom / self.wall_ratio[1])),
                                            max(3.5, np.sqrt(self.area_of_livingroom / self.wall_ratio[0]))]
        self.intwall_length_livingroom_y = [self.area_of_livingroom / self.intwall_length_livingroom_x[1],
                                            self.area_of_livingroom / self.intwall_length_livingroom_x[0]]
        self.intwall_length_bedroom1_x = [max(2.7, np.sqrt(self.area_of_bedroom1 / self.wall_ratio[1])),
                                          max(2.7, np.sqrt(self.area_of_bedroom1 / self.wall_ratio[0]))]
        self.intwall_length_bedroom1_y = [self.area_of_bedroom1 / self.intwall_length_bedroom1_x[1],
                                          self.area_of_bedroom1 / self.intwall_length_bedroom1_x[0]]
        self.intwall_length_bedroom2_x = [max(2.7, np.sqrt(self.area_of_bedroom2 / self.wall_ratio[1])),
                                          max(2.7, np.sqrt(self.area_of_bedroom2 / self.wall_ratio[0]))]
        self.intwall_length_bedroom2_y = [self.area_of_bedroom2 / self.intwall_length_bedroom2_x[1],
                                          self.area_of_bedroom2 / self.intwall_length_bedroom2_x[0]]
        self.intwall_length_bedroom3_x = [max(2.7, np.sqrt(self.area_of_bedroom3 / self.wall_ratio[1])),
                                          max(2.7, np.sqrt(self.area_of_bedroom3 / self.wall_ratio[0]))]
        self.intwall_length_bedroom3_y = [self.area_of_bedroom3 / self.intwall_length_bedroom3_x[1],
                                          self.area_of_bedroom3 / self.intwall_length_bedroom3_x[0]]
        self.intwall_length_bedroom4_x = [max(2.7, np.sqrt(self.area_of_bedroom4 / self.wall_ratio[1])),
                                          max(2.7, np.sqrt(self.area_of_bedroom4 / self.wall_ratio[0]))]
        self.intwall_length_bedroom4_y = [self.area_of_bedroom4 / self.intwall_length_bedroom4_x[1],
                                          self.area_of_bedroom4 / self.intwall_length_bedroom4_x[0]]
        self.intwall_length_bathroom_x = [max(1.6, np.sqrt(self.area_of_bathroom / self.wall_ratio[1])),
                                          max(1.6, np.sqrt(self.area_of_bathroom / self.wall_ratio[0]))]
        self.intwall_length_bathroom_y = [self.area_of_bathroom / self.intwall_length_bathroom_x[1],
                                          self.area_of_bathroom / self.intwall_length_bathroom_x[0]]
        self.intwall_length_guestWC_x = [max(0.9, np.sqrt(self.area_of_guestWC / self.wall_ratio[1])),
                                         max(0.9, np.sqrt(self.area_of_guestWC / self.wall_ratio[0]))]
        self.intwall_length_guestWC_y = [self.area_of_guestWC / self.intwall_length_guestWC_x[1],
                                         self.area_of_guestWC / self.intwall_length_guestWC_x[0]]
        self.intwall_length_kitchen_x = [max(1.8, np.sqrt(self.area_of_kitchen / self.wall_ratio[1])),
                                         max(1.8, np.sqrt(self.area_of_kitchen / self.wall_ratio[0]))]
        self.intwall_length_kitchen_y = [self.area_of_kitchen / self.intwall_length_kitchen_x[1],
                                         self.area_of_kitchen / self.intwall_length_kitchen_x[0]]
        self.intwall_length_hallway_x = [max(1.8, np.sqrt(self.area_of_hallway / self.wall_ratio[1])),
                                         max(1.8, np.sqrt(self.area_of_hallway / self.wall_ratio[0]))]
        self.intwall_length_hallway_y = [self.area_of_hallway / self.intwall_length_hallway_x[1],
                                         self.area_of_hallway / self.intwall_length_hallway_x[0]]

        self.list_of_input_variables = [['length_extwall_x', self.length_extwall_x],
                                        ['length_extwall_y', self.length_extwall_y],
                                        ['intwall_length_entrance_x', self.intwall_length_entrance_x],
                                        ['intwall_length_entrance_y', self.intwall_length_entrance_y],
                                        ['intwall_length_livingroom_x', self.intwall_length_livingroom_x],
                                        ['intwall_length_livingroom_y', self.intwall_length_livingroom_y],
                                        ['intwall_length_bedroom1_x', self.intwall_length_bedroom1_x],
                                        ['intwall_length_bedroom1_y', self.intwall_length_bedroom1_y],
                                        ['intwall_length_bedroom2_x', self.intwall_length_bedroom2_x],
                                        ['intwall_length_bedroom2_y', self.intwall_length_bedroom2_y],
                                        ['intwall_length_bedroom3_x', self.intwall_length_bedroom3_x],
                                        ['intwall_length_bedroom3_y', self.intwall_length_bedroom3_y],
                                        ['intwall_length_bedroom4_x', self.intwall_length_bedroom4_x],
                                        ['intwall_length_bedroom4_y', self.intwall_length_bedroom4_y],
                                        ['intwall_length_bathroom_x', self.intwall_length_bathroom_x],
                                        ['intwall_length_bathroom_y', self.intwall_length_bathroom_y],
                                        ['intwall_length_guestWC_x', self.intwall_length_guestWC_x],
                                        ['intwall_length_guestWC_y', self.intwall_length_guestWC_y],
                                        ['intwall_length_kitchen_x', self.intwall_length_kitchen_x],
                                        ['intwall_length_kitchen_y', self.intwall_length_kitchen_y],
                                        ['intwall_length_hallway_x', self.intwall_length_hallway_x],
                                        ['intwall_length_hallway_y', self.intwall_length_hallway_y]]

        return self.list_of_input_variables

    def lhs_areas_and_intwalls(self, n_samples):

        def generate_lhs_sample():
            return lhs(1, samples=n_samples, criterion='center')

        # Generate samples belonging to [0, 1] for all variables in list
        dict_of_lhs_samples = {}
        for variable in self.list_of_input_variables:
            dict_of_lhs_samples[variable[0]] = generate_lhs_sample()

        self.dict_of_lhs_samples = dict_of_lhs_samples

        self.list_of_rescaled_intwall_values = []
        self.list_of_rescaled_extwall_values = []

        # Use the generated samples to generate possible lengths for variables with intwall and extwall.
        def rescale_lhs_sample(input_variables, lhs_samples, element_type, rescaled_values):
            for variable in input_variables:
                for key, sample in lhs_samples.items():
                    if (key == variable[0] and element_type in key):
                        rescaled_value = variable[1][0] + (variable[1][1] - variable[1][0]) * sample
                        rescaled_values.append(rescaled_value)

        rescale_lhs_sample(self.list_of_input_variables, self.dict_of_lhs_samples, 'intwall',
                           self.list_of_rescaled_intwall_values)
        rescale_lhs_sample(self.list_of_input_variables, self.dict_of_lhs_samples, 'extwall',
                           self.list_of_rescaled_extwall_values)

        self.raw_input_values_intwall = np.hstack(self.list_of_rescaled_intwall_values)

        # Initialize num_entrance and num_hallway to 0 outside the if-elif statements to ensure these variables have a value in all cases.
        # num_rooms = 0
        num_entrance = 0
        num_hallway = 0
        num_doors = 0
        # using the extwall to differentiate list_of_input_variables is for the wall between apartments (withou extwall) or in apartment (with extwall)
        if self.list_of_rescaled_extwall_values:
            self.raw_input_values_extwall = np.hstack(self.list_of_rescaled_extwall_values)

            def find_total_of_variable_type(input, input_array):
                total_variable_type = 0
                for i in range(len(input)):
                    total_variable_type += input_array[:, i]
                return total_variable_type

            self.interior_wall_lengths = find_total_of_variable_type(self.list_of_rescaled_intwall_values,
                                                                     self.raw_input_values_intwall)
            self.exterior_wall_lengths = find_total_of_variable_type(self.list_of_rescaled_extwall_values,
                                                                     self.raw_input_values_extwall)
            # Each rooms have a door to entrance, hallway or living room. If the floor are not considered, then the doors are also not exist.
            # the list_of_input_variables contains the 2 variables of exwall.
            num_rooms = (len(self.list_of_input_variables) - 2) / 2
            if num_rooms == 2:
                # according to the num_rooms, we can know what kind of rooms are in this apartment. When num_rooms is 2, this apartment is studio with living space and bathroom.
                num_entrance = 0
                num_hallway = 0
                num_doors = num_rooms - 1 - num_entrance - num_hallway
            elif num_rooms == 3:
                num_entrance = 0
                num_hallway = 0
                num_doors = num_rooms - 1 - num_entrance - num_hallway
            elif num_rooms == 4:
                num_entrance = 0
                num_hallway = 0
                num_doors = num_rooms - 1 - num_entrance - num_hallway
            elif num_rooms == 6:
                num_entrance = 1
                num_hallway = 0
                num_doors = num_rooms - 1 - num_entrance - num_hallway
            elif num_rooms == 9:
                num_entrance = 1
                num_hallway = 1
                num_doors = num_rooms - 1 - num_entrance - num_hallway
            elif num_rooms == 10:
                num_entrance = 1
                num_hallway = 1
                num_doors = num_rooms - 1 - num_entrance - num_hallway
            self.interior_wall_area = ((self.interior_wall_lengths * 2 - self.exterior_wall_lengths * 2) / 2 - num_entrance * 1.5 - num_hallway * 1.1 - num_doors * self.door_width) * self.storey_height
        else:
            def find_total_of_variable_type(input, input_array):
                total_variable_type = 0
                for i in range(len(input)):
                    total_variable_type += input_array[:, i]
                return total_variable_type

            self.interior_wall_lengths = find_total_of_variable_type(self.list_of_rescaled_intwall_values,
                                                                     self.raw_input_values_intwall)
            self.interior_wall_area = self.interior_wall_lengths * self.storey_height


        return self.interior_wall_area

    def floor_layout(self):

        self.intwall1 = []
        self.intwall2 = []
        self.intwall3 = []
        self.intwall4 = []
        self.intwall5 = []
        self.intwall_in_apartments1 = []
        self.intwall_in_apartments2 = []
        self.intwall_in_apartments3 = []
        self.intwall_in_apartments4 = []
        self.intwall_in_apartments5 = []
        if self.area_of_floor - 12  < 150:
            if self.area_of_floor - 12 > 38.5:
                self.one_apartment()
                self.intwall_input = self.lhs_areas_and_intwalls(self.n_sample)
                self.area_of_apartments = [self.area_of_apartment]
                self.intwall_between_apartments1 = [element * self.number_of_storeys for element in self.intwall_input]
                self.intwall_in_apartments1 = self.apartments_layout()
                self.intwall1 = [self.intwall_in_apartments1[a] + self.intwall_between_apartments1[a] for a in
                                 range(min(len(self.intwall_in_apartments1), len(self.intwall_between_apartments1)))]
            if (self.area_of_floor - 15) * 0.5 > 38.5:
                self.two_apartment()
                self.intwall_input = self.lhs_areas_and_intwalls(self.n_sample)
                self.area_of_apartments = [self.area_of_apartment1, self.area_of_apartment2]
                self.intwall_between_apartments2 = [element * self.number_of_storeys for element in self.intwall_input]
                self.intwall_in_apartments2 = self.apartments_layout()
                self.intwall2 = [self.intwall_in_apartments2[a] + self.intwall_between_apartments2[a] for a in
                                 range(min(len(self.intwall_in_apartments2), len(self.intwall_between_apartments2)))]
            if (self.area_of_floor - 18) * 0.24 > 38.5:
                self.three_apartment()
                self.intwall_input = self.lhs_areas_and_intwalls(self.n_sample)
                self.area_of_apartments = [self.area_of_apartment1, self.area_of_apartment2, self.area_of_apartment3]
                self.intwall_between_apartments3 = [element * self.number_of_storeys for element in self.intwall_input]
                self.intwall_in_apartments3 = self.apartments_layout()
                self.intwall3 = [self.intwall_in_apartments3[a] + self.intwall_between_apartments3[a] for a in
                                 range(min(len(self.intwall_in_apartments3), len(self.intwall_between_apartments3)))]
            if (self.area_of_floor - 21) * 0.25 > 38.5:
                self.four_apartment()
                self.intwall_input = self.lhs_areas_and_intwalls(self.n_sample)
                self.area_of_apartments = [self.area_of_apartment1, self.area_of_apartment2, self.area_of_apartment3,
                                           self.area_of_apartment4]
                self.intwall_between_apartments4 = [element * self.number_of_storeys for element in self.intwall_input]
                self.intwall_in_apartments4 = self.apartments_layout()
                self.intwall4 = [self.intwall_in_apartments4[a] + self.intwall_between_apartments4[a] for a in
                                 range(min(len(self.intwall_in_apartments4), len(self.intwall_between_apartments4)))]
            if self.area_of_floor * (1 - 0.12) > 32.5 * 6:
                self.multi_apartment()
                self.intwall_input = self.lhs_areas_and_intwalls(self.n_sample)
                self.area_of_apartments = [self.area_of_studioapartment]
                self.intwall_between_apartments5 = [element * self.number_of_storeys for element in self.intwall_input]
                self.intwall_in_apartments5 = self.apartments_layout()
                self.intwall5 = [self.intwall_in_apartments5[a] + self.intwall_between_apartments5[a] for a in
                                 range(min(len(self.intwall_in_apartments5), len(self.intwall_between_apartments5)))]
        elif self.area_of_floor - 15  < 150 / 0.5:
            if (self.area_of_floor - 15) * 0.5 > 38.5:
                self.two_apartment()
                self.intwall_input = self.lhs_areas_and_intwalls(self.n_sample)
                self.area_of_apartments = [self.area_of_apartment1, self.area_of_apartment2]
                self.intwall_between_apartments2 = [element * self.number_of_storeys for element in self.intwall_input]
                self.intwall_in_apartments2 = self.apartments_layout()
                self.intwall2 = [self.intwall_in_apartments2[a] + self.intwall_between_apartments2[a] for a in
                                 range(min(len(self.intwall_in_apartments2), len(self.intwall_between_apartments2)))]
            if (self.area_of_floor - 18) * 0.24 > 38.5:
                self.three_apartment()
                self.intwall_input = self.lhs_areas_and_intwalls(self.n_sample)
                self.area_of_apartments = [self.area_of_apartment1, self.area_of_apartment2, self.area_of_apartment3]
                self.intwall_between_apartments3 = [element * self.number_of_storeys for element in self.intwall_input]
                self.intwall_in_apartments3 = self.apartments_layout()
                self.intwall3 = [self.intwall_in_apartments3[a] + self.intwall_between_apartments3[a] for a in
                                 range(min(len(self.intwall_in_apartments3), len(self.intwall_between_apartments3)))]
            if (self.area_of_floor - 21) * 0.25 > 38.5:
                self.four_apartment()
                self.intwall_input = self.lhs_areas_and_intwalls(self.n_sample)
                self.area_of_apartments = [self.area_of_apartment1, self.area_of_apartment2, self.area_of_apartment3,
                                           self.area_of_apartment4]
                self.intwall_between_apartments4 = [element * self.number_of_storeys for element in self.intwall_input]
                self.intwall_in_apartments4 = self.apartments_layout()
                self.intwall4 = [self.intwall_in_apartments4[a] + self.intwall_between_apartments4[a] for a in
                                 range(min(len(self.intwall_in_apartments4), len(self.intwall_between_apartments4)))]
            if self.area_of_floor * (1 - 0.12) > 32.5 * 6:
                self.multi_apartment()
                self.intwall_input = self.lhs_areas_and_intwalls(self.n_sample)
                self.area_of_apartments = [self.area_of_studioapartment]
                self.intwall_between_apartments5 = [element * self.number_of_storeys for element in self.intwall_input]
                self.intwall_in_apartments5 = self.apartments_layout()
                self.intwall5 = [self.intwall_in_apartments5[a] + self.intwall_between_apartments5[a] for a in
                                 range(min(len(self.intwall_in_apartments5), len(self.intwall_between_apartments5)))]
        elif self.area_of_floor - 18 < 150 / 0.38:
            if (self.area_of_floor - 15) * 0.24 > 38.5:
                self.three_apartment()
                self.intwall_input = self.lhs_areas_and_intwalls(self.n_sample)
                self.area_of_apartments = [self.area_of_apartment1, self.area_of_apartment2, self.area_of_apartment3]
                self.intwall_between_apartments3 = [element * self.number_of_storeys for element in self.intwall_input]
                self.intwall_in_apartments3 = self.apartments_layout()
                self.intwall3 = [self.intwall_in_apartments3[a] + self.intwall_between_apartments3[a] for a in
                                 range(min(len(self.intwall_in_apartments3), len(self.intwall_between_apartments3)))]
            if (self.area_of_floor - 21) * 0.25 > 38.5:
                self.four_apartment()
                self.intwall_input = self.lhs_areas_and_intwalls(self.n_sample)
                self.area_of_apartments = [self.area_of_apartment1, self.area_of_apartment2, self.area_of_apartment3,
                                           self.area_of_apartment4]
                self.intwall_between_apartments4 = [element * self.number_of_storeys for element in self.intwall_input]
                self.intwall_in_apartments4 = self.apartments_layout()
                self.intwall4 = [self.intwall_in_apartments4[a] + self.intwall_between_apartments4[a] for a in
                                 range(min(len(self.intwall_in_apartments4), len(self.intwall_between_apartments4)))]
            if self.area_of_floor * (1 - 0.12) > 32.5 * 6:
                self.multi_apartment()
                self.intwall_input = self.lhs_areas_and_intwalls(self.n_sample)
                self.area_of_apartments = [self.area_of_studioapartment]
                self.intwall_between_apartments5 = [element * self.number_of_storeys for element in self.intwall_input]
                self.intwall_in_apartments5 = self.apartments_layout()
                self.intwall5 = [self.intwall_in_apartments5[a] + self.intwall_between_apartments5[a] for a in
                                 range(min(len(self.intwall_in_apartments5), len(self.intwall_between_apartments5)))]
        else:
            self.multi_apartment()
            self.intwall_input = self.lhs_areas_and_intwalls(self.n_sample)
            self.area_of_apartments = [self.area_of_studioapartment]
            self.intwall_between_apartments5 = [element * self.number_of_storeys for element in self.intwall_input]
            self.intwall_in_apartments5 = self.apartments_layout()
            self.intwall5 = [self.intwall_in_apartments5[a] + self.intwall_between_apartments5[a] for a in
                                 range(min(len(self.intwall_in_apartments5), len(self.intwall_between_apartments5)))]

        self.intwall_sample = np.hstack((self.intwall1, self.intwall2, self.intwall3, self.intwall4, self.intwall5))

        return self.intwall_sample

    def apartments_layout(self):

        self.intwall_in_apartments = []
        # make list of 'intwall_in_apartments' have the same number of samples as the following
        self.intwall_in_apartments.extend([0] * self.n_sample)

        for i in self.area_of_apartments:
            if i <= 38.5:
                self.studio(area_of_apartment=i)
                self.lhs_areas_and_intwalls(self.n_sample)
                self.intwall_output = [element * self.number_of_storeys for element in self.interior_wall_area]
                self.intwall_in_apartments = [self.intwall_output[x] + self.intwall_in_apartments[x] for x in range(min(len(self.intwall_output), len(self.intwall_in_apartments)))]
            elif i <= 69 and i > 38.5:
                self.one_bedroom(area_of_apartment=i)
                self.lhs_areas_and_intwalls(self.n_sample)
                self.intwall_output = [element * self.number_of_storeys for element in self.interior_wall_area]
                self.intwall_in_apartments = [self.intwall_output[x] + self.intwall_in_apartments[x] for x in
                                              range(min(len(self.intwall_output), len(self.intwall_in_apartments)))]
            elif i <= 76 and i > 69:
                self.one_bedroom(area_of_apartment=i)
                self.lhs_areas_and_intwalls(min(self.n_sample - 2, max(2, round(self.n_sample*(i-69)/(76-69)))))
                self.intwall_output_1 = [element * self.number_of_storeys for element in self.interior_wall_area]
                self.two_bedroom(area_of_apartment=i)
                self.lhs_areas_and_intwalls(self.n_sample-min(self.n_sample - 2, max(2, round(self.n_sample*(i-69)/(76-69)))))
                self.intwall_output_2 = [element * self.number_of_storeys for element in self.interior_wall_area]
                self.intwall_output = self.intwall_output_1 + self.intwall_output_2
                self.intwall_in_apartments = [self.intwall_output[x] + self.intwall_in_apartments[x] for x in
                                              range(min(len(self.intwall_output), len(self.intwall_in_apartments)))]
            elif i <= 84 and i > 76:
                self.two_bedroom(area_of_apartment=i)
                self.lhs_areas_and_intwalls(self.n_sample)
                self.intwall_output = [element * self.number_of_storeys for element in self.interior_wall_area]
                self.intwall_in_apartments = [self.intwall_output[x] + self.intwall_in_apartments[x] for x in
                                              range(min(len(self.intwall_output), len(self.intwall_in_apartments)))]
            elif i <= 88 and i > 84:
                self.two_bedroom(area_of_apartment=i)
                self.lhs_areas_and_intwalls(min(self.n_sample - 2, max(2, round(self.n_sample*(i-84)/(98-84)))))
                self.intwall_output_2 = [element * self.number_of_storeys for element in self.interior_wall_area]
                self.three_bedroom(area_of_apartment=i)
                self.lhs_areas_and_intwalls(self.n_sample-min(self.n_sample - 2, max(2, round(self.n_sample*(i-84)/(98-84)))))
                self.intwall_output_3 = [element * self.number_of_storeys for element in self.interior_wall_area]
                self.intwall_output = self.intwall_output_3 + self.intwall_output_2
                self.intwall_in_apartments = [self.intwall_output[x] + self.intwall_in_apartments[x] for x in
                                              range(min(len(self.intwall_output), len(self.intwall_in_apartments)))]
            elif i <= 97 and i > 88:
                self.three_bedroom(area_of_apartment=i)
                self.lhs_areas_and_intwalls(self.n_sample)
                self.intwall_output = [element * self.number_of_storeys for element in self.interior_wall_area]
                self.intwall_in_apartments = [self.intwall_output[x] + self.intwall_in_apartments[x] for x in
                                              range(min(len(self.intwall_output), len(self.intwall_in_apartments)))]
            elif i <= 129 and i > 97:
                self.three_bedroom(area_of_apartment=i)
                self.lhs_areas_and_intwalls(min(self.n_sample - 2, max(2, round(self.n_sample*(i-100)/(129-100)))))
                self.intwall_output_3 = [element * self.number_of_storeys for element in self.interior_wall_area]
                self.four_bedroom(area_of_apartment=i)
                self.lhs_areas_and_intwalls(self.n_sample-min(self.n_sample - 2, max(2, round(self.n_sample*(i-100)/(129-100)))))
                self.intwall_output_4 = [element * self.number_of_storeys for element in self.interior_wall_area]
                self.intwall_output = self.intwall_output_3 + self.intwall_output_4
                self.intwall_in_apartments = [self.intwall_output[x] + self.intwall_in_apartments[x] for x in
                                              range(min(len(self.intwall_output), len(self.intwall_in_apartments)))]
            elif i > 129:
                self.four_bedroom(area_of_apartment=i)
                self.lhs_areas_and_intwalls(self.n_sample)
                self.intwall_output = [element * self.number_of_storeys for element in self.interior_wall_area]
                self.intwall_in_apartments = [self.intwall_output[x] + self.intwall_in_apartments[x] for x in
                                              range(min(len(self.intwall_output), len(self.intwall_in_apartments)))]

        return self.intwall_in_apartments

    def total_intwall(self):

        self.total_intwall = self.floor_layout()

        return self.total_intwall



