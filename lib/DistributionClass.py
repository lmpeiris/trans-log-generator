import numpy as np
import time
import datetime
from typing import Literal
from typing import Union


class DistributionClass:
    def __init__(self, distribution: Literal['normal', 'exponential', 'poisson', 'binomial',
    'chi_square', 'random','increment', 'static'], field_format: str, record_count: int, value_args: list):
        self.distribution = distribution
        self.value_args = value_args
        self.record_count = record_count
        self.field_format = field_format
        self.is_numpy = False
        if self.distribution in ['normal', 'exponential', 'poisson', 'binomial', 'chi_square',
                                 'random', 'increment', 'static', 'percentage', 'roundrobin']:
            self.is_numpy = True

    def get_numpy_array(self) -> np.ndarray:
        """Generate distribution strictly as numbers, return in numpy form"""
        if self.is_numpy:
            ran_array = np.empty(0)
            # ------- distribution population of data -----------------
            # populating a numpy array according to our distribution, there's a lot more
            match self.distribution:
                case 'normal':
                    mean = float(self.value_args[0])
                    standard_deviation = float(self.value_args[1])
                    ran_array = np.random.normal(mean, standard_deviation, self.record_count)

                case 'exponential':
                    scale_parameter = float(self.value_args[0])
                    ran_array = np.random.exponential(scale_parameter, self.record_count)

                case 'poisson':
                    lamda_value = float(self.value_args[0])
                    ran_array = np.random.poisson(lamda_value, self.record_count)

                case 'binomial':
                    turns = float(self.value_args[0])
                    probability = float(self.value_args[1])
                    # ignore the PEP error
                    ran_array = np.random.binomial(turns, probability, self.record_count)

                case 'chi_square':
                    degrees_freedom = int(self.value_args[0])
                    ran_array = np.random.chisquare(degrees_freedom, self.record_count)

                case 'random':
                    lower_bound = int(self.value_args[0])
                    upper_bound = int(self.value_args[1])
                    if self.field_format == 'integer':
                        ran_array = np.random.random_integers(lower_bound, upper_bound, self.record_count)
                    else:
                        ran_array = (upper_bound - lower_bound) * np.random.random(self.record_count) + lower_bound

                # for increment we are using a standard list
                case 'increment':
                    lower_bound = int(self.value_args[0])
                    increment_value = int(self.value_args[1])
                    ran_array = np.arange(lower_bound, int(lower_bound + self.record_count * increment_value),
                                          increment_value)

                case 'static':
                    static_label = float(self.value_args[0])
                    if self.field_format == 'integer' or self.field_format == 'double':
                        ran_array = np.empty(self.record_count)
                        ran_array.fill(static_label)

                case 'percentage':
                    print('INFO: generating random integer for 100 elements')
                    ran_array = self.get_random_integers(0, 99, self.record_count)

                case 'roundrobin':
                    element_array = np.arange(int(self.value_args[0]), int(self.value_args[1])+1)
                    # find the min repeats required by modulo division
                    num_repeats = (self.record_count // len(element_array)) + 1
                    # repeat and splice to only get the record numbers we need
                    ran_array = np.tile(element_array, num_repeats)[:self.record_count]
                case _:
                    print('ERROR: this distribution is not supported. Function will return an empty '
                          'numpy array which would cause a crash')
        else:
            ran_list = self.get_list_array()
            ran_array = np.array(ran_list)
        return ran_array

    def get_list_array(self) -> list:
        """Generate distribution strictly as numbers, return in list form"""
        ran_list = []
        if self.is_numpy:
            ran_numpy = self.get_numpy_array()
            ran_list = ran_numpy.tolist()
        else:
            match self.distribution:
                # TODO: nothing here yet. This should only have distributions faster to generate
                #  using means other than numpy
                case _:
                    print('ERROR: this distribution is not supported. Function will return an empty '
                          'list which would cause a crash')
        return ran_list

    @classmethod
    def get_enum(cls, elements_list, ran_array: Union[list[int], np.ndarray]) -> list:
        """ returns a list of enumurated items based on elements defined in numpy array or list,
        according to index list given in ran_array"""
        enum_list = []
        max_index = max(ran_array)
        if (max_index+1) > len(ran_array):
            print('ERROR: max value of ran_array cannot be larger than number of items in element_list')
        else:
            print('INFO: generating enum entries: ' + str(len(ran_array)))
            print('INFO: unique enum records: ' + str(len(elements_list)))
            for i in ran_array:
                enum_list.append(elements_list[i])
        return enum_list

    @classmethod
    def get_random_integers(cls, lower_bound, upper_bound, record_count):
        ran_array = np.random.random_integers(lower_bound, upper_bound, record_count)
        return ran_array.tolist()
