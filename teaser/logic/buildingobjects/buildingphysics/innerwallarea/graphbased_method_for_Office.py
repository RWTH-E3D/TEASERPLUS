import pandas as pd
import os
import random
import numpy as np
from pyDOE import lhs


class IntWallAreaOffice_graph_based:

    # set variables. variation_maximum and variation_minimum give more flexible space for the final results.
    def __init__(self, net_leased_area, number_of_storeys, storey_height):
        self.net_leased_area = net_leased_area
        self.number_of_storeys = number_of_storeys
        self.area_of_floor = self.net_leased_area / self.number_of_storeys
        self.grid_dimension = 1.35
        self.storey_height = storey_height
        self.variation_minimum = 0.9
        self.variation_maximum = 1.1
        self.n_samples = 500
        self.door_width = 1.1

    def double_loaded(self):

        # Assumption: the length of extwall y could be around 13 meter, and it varies between the variation range.
        self.grid = [int((self.area_of_floor / (13 * self.variation_maximum)) / self.grid_dimension),
                     int((self.area_of_floor / (13 * self.variation_minimum)) / self.grid_dimension)]
        self.length_extwall_x = [self.grid[0] * self.grid_dimension,
                                 self.grid[1] * self.grid_dimension]
        self.length_extwall_y = [self.area_of_floor / self.length_extwall_x[1],
                                 self.area_of_floor / self.length_extwall_x[0]]

        # assumption : The main staircase and elevator take always 4 * grid_dimension. The secondary staircase  take always 2 * grid_dimension.
        # One meeting room takes 5 * grid_dimension. For small buildings, there can be without meeting rooms.
        # The other rooms are neutral dimension, each with 2 grid.
        # According to the zone distribution and the lager room depth with 5.5 meter, the number of different room can be roughly calculated.
        self.stair_elevator_grid = 4
        self.stair_elevator_number = 1
        # "max" makes sure there is at least one room with specific function. "around" makes the area share of rooms more flexible
        self.meeting_grid = round(self.area_of_floor * 0.04 / (5.5 * self.grid_dimension))
        self.meeting_number = round(self.meeting_grid / 5)
        # neutral2 means 2-grid room.
        self.large_neutral2_grid = [max(2, self.grid[0] - self.stair_elevator_number * 4 - self.meeting_number * 5),
                                    max(2, self.grid[1] - self.stair_elevator_number * 4 - self.meeting_number * 5)]
        self.large_neutral2_number = [int(self.large_neutral2_grid[0] / 2), int(self.large_neutral2_grid[1] / 2)]
        self.large_room_number = [self.stair_elevator_number + self.meeting_number + self.large_neutral2_number[0],
                                  self.stair_elevator_number + self.meeting_number + self.large_neutral2_number[1]]

        # assumption : The neutral room are set with 2 or 2 grid. one of the 3-grid room is open as reception.
        # One group room takes 4 * grid. There must be one group office, because in small buildings, it can be used as meeting room.
        # According to the zone distribution and the lager room depth with 4.5 meter, the number of different room can be roughly calculated.
        self.group_grid = max(4, round(self.area_of_floor * 0.06 / (5.5 * self.grid_dimension)))
        self.group_number = round(self.group_grid / 4)
        self.small_neutral3_grid = [round((self.grid[0] - self.group_grid)/2), round((self.grid[1] - self.group_grid)/2)]
        self.small_neutral3_number = [round(self.small_neutral3_grid[0] / 3), round(self.small_neutral3_grid[1] / 3)]
        self.small_neutral2_grid = [self.grid[0] - self.small_neutral3_number[1] * 3 - self.group_grid,
                                    self.grid[1] - self.small_neutral3_number[0] * 3 - self.group_grid]
        self.small_neutral2_number = [int(self.small_neutral2_grid[0] / 2), int(self.small_neutral2_grid[1] / 2)]
        self.small_room_number = [self.small_neutral3_number[0] + self.small_neutral2_number[0] + self.group_number,
                                  self.small_neutral3_number[1] + self.small_neutral2_number[1] + self.group_number]

        # the intwall y is the walls between different rooms; the intwall x is the walls between the corridor and the rooms minus the door width.
        # the main vertical circulation (stair and elevator) and reception is open to the corridor.
        self.length_intwall_x = [2 * self.length_extwall_x[0] - self.door_width * (self.large_room_number[1] + self.small_room_number[1]) - (4 + 3) * self.grid_dimension,
                                 2 * self.length_extwall_x[1] - self.door_width * (self.large_room_number[0] + self.small_room_number[0]) - (4 + 3) * self.grid_dimension]
        self.length_intwall_y = [(5.5 * (self.large_room_number[0] - 1) + 4.5 * (self.small_room_number[0] - 1)) * self.variation_minimum,
                                 (5.5 * (self.large_room_number[1] - 1) + 4.5 * (self.small_room_number[1] - 1)) * self.variation_maximum]

        self.list_of_input_variables = [['length_extwall_x', self.length_extwall_x],
                                        ['length_extwall_y', self.length_extwall_y],
                                        ['length_intwall_x', self.length_intwall_x],
                                        ['length_intwall_x', self.length_intwall_x]]

        return self.list_of_input_variables

    def triple_loaded(self):

        # assumption: the length of extwall y could be around 15 meter, and it varies between the variation range.
        self.grid = [int((self.area_of_floor / (15 * self.variation_maximum)) / self.grid_dimension), int((self.area_of_floor / (15 * self.variation_minimum)) / self.grid_dimension)]
        self.length_extwall_x = [self.grid[0] * self.grid_dimension, self.grid[1] * self.grid_dimension]
        self.length_extwall_y = [self.area_of_floor / self.length_extwall_x[1], self.area_of_floor / self.length_extwall_x[0]]

        # assumption : The main staircase and elevator are set in the central open space. One meeting room takes 5 * grid_dimension. one group office takes 4 grid. The other rooms are neutral dimension, each with 2 grid.
        # According to the zone distribution and the lager room depth with 5 meter, the number of different room can be roughly calculated.
        self.meeting_grid = round(self.area_of_floor * 0.04 / (5 * self.grid_dimension))
        self.meeting_number = round(self.meeting_grid / 5)
        self.large_neutral2_grid = [max(2, self.grid[0] - self.meeting_number * 5),
                                    max(2, self.grid[1] - self.meeting_number * 5)]
        self.large_neutral2_number = [int(self.large_neutral2_grid[0] / 2), int(self.large_neutral2_grid[1] / 2)]
        self.large_room_number = [self.meeting_number + self.group_number + self.large_neutral2_number[0],
                                  self.meeting_number + self.group_number + self.large_neutral2_number[1]]

        # assumption : The neutral room are set with 2 or 2 grid.
        # According to the zone distribution and the lager room depth with 4 meter, the number of different room can be roughly calculated.
        self.group_grid = max(4, round(self.area_of_floor * 0.06 / (5 * self.grid_dimension)))
        self.group_number = round(self.group_grid / 4)
        self.small_neutral3_grid = [round((self.grid[0] - self.group_grid) / 2), round((self.grid[1] - self.group_grid) / 2)]
        self.small_neutral3_number = [round(self.small_neutral3_grid[0] / 3), round(self.small_neutral3_grid[1] / 3)]
        self.small_neutral2_grid = [self.grid[0] - self.small_neutral3_number[1] * 3 - self.group_grid,
                                    self.grid[1] - self.small_neutral3_number[0] * 3 - self.group_grid]
        self.small_neutral2_number = [int(self.small_neutral2_grid[0] / 2), int(self.small_neutral2_grid[1] / 2)]
        self.small_room_number = [self.small_neutral3_number[0] + self.small_neutral2_number[0] + self.group_number,
                                  self.small_neutral3_number[1] + self.small_neutral2_number[1] + self.group_number]

        # Assumption: the reception is set as open room.
        self.length_intwall_x = [2 * self.length_extwall_x[0] - self.door_width * (self.large_room_number[1] + self.small_room_number[1]) - 3 * self.grid_dimension,
                                 2 * self.length_extwall_x[1] - self.door_width * (self.large_room_number[0] + self.small_room_number[0]) - 3 * self.grid_dimension]
        self.length_intwall_y = [(5 * (self.large_room_number[0] - 1) + 4 * (self.small_room_number[0] - 1)) * self.variation_minimum,
                                 (5 * (self.large_room_number[1] - 1) + 4 * (self.small_room_number[1] - 1)) * self.variation_maximum]

        self.list_of_input_variables = [['length_extwall_x', self.length_extwall_x],
                                        ['length_extwall_y', self.length_extwall_y],
                                        ['length_intwall_x', self.length_intwall_x],
                                        ['length_intwall_x', self.length_intwall_x]]

    def lhs_areas_and_intwalls(self):

        # using Latin hypercube sampling method generates samples between [0, 1]
        def generate_lhs_sample():
            return lhs(1, samples=self.n_samples, criterion='center')

        dict_of_lhs_samples = {}
        dict_of_lhs_samples['length_extwall_y'] = generate_lhs_sample()
        dict_of_lhs_samples['length_extwall_x'] = generate_lhs_sample()
        dict_of_lhs_samples['length_intwall_y'] = generate_lhs_sample()
        dict_of_lhs_samples['length_intwall_x'] = generate_lhs_sample()

        self.dict_of_lhs_samples = dict_of_lhs_samples

        # with the help of lhs_samples, samples between the intervals of different wall lengths could be generated
        self.list_of_rescaled_extwall_values = []
        self.list_of_rescaled_intwall_values = []

        def rescale_lhs_sample(input_variables, lhs_samples, element_type, rescaled_values):
            for variable in input_variables:
                for key, sample in lhs_samples.items():
                    if (key == variable[0] and element_type in key):
                        rescaled_value = variable[1][0] + (variable[1][1] - variable[1][0]) * sample
                        rescaled_values.append(rescaled_value)

        rescale_lhs_sample(self.list_of_input_variables, self.dict_of_lhs_samples, 'extwall',
                           self.list_of_rescaled_extwall_values)
        rescale_lhs_sample(self.list_of_input_variables, self.dict_of_lhs_samples, 'intwall',
                           self.list_of_rescaled_intwall_values)

        self.raw_input_values_intwall = np.hstack(self.list_of_rescaled_intwall_values)

        # Add the lengths of intwall and calculate the area.
        def find_total_of_variable_type(input, input_array):
            total_variable_type = 0
            for i in range(len(input)):
                total_variable_type += input_array[:, i]
            return total_variable_type

        self.interior_wall_lengths = find_total_of_variable_type(self.list_of_rescaled_intwall_values, self.raw_input_values_intwall)
        self.interior_wall_area = self.interior_wall_lengths * self.storey_height
        return self.raw_input_values_intwall, self.interior_wall_lengths, self.interior_wall_area

    def floor_layout(self):

        self.double_loaded()
        self.intwall_input = self.lhs_areas_and_intwalls()
        self.intwall_output_1 = self.interior_wall_area

        self.triple_loaded()
        self.intwall_input = self.lhs_areas_and_intwalls()
        self.intwall_output_2 = self.interior_wall_area

        if self.area_of_floor < 15*15:
            self.total_intwall_average = self.intwall_output_1
        else:
            self.total_intwall_average = [(self.intwall_output_1[i] + self.intwall_output_2[i]) / 2 for i in
                                          range(min(len(self.intwall_output_1), len(self.intwall_output_2)))]

        return self.total_intwall_average





