import numpy as np
import time
import datetime
from typing import Literal

class DistributionClass:
    def __init__(self, distribution: Literal['normal', 'exponential', 'poisson', 'binomial', 'chi_square', 'random',
    'increment', 'static'], field_format: str, record_count: int, value_args: list):
        self.distribution = distribution
        self.value_args = value_args
        self.record_count = record_count
        self.field_format = field_format

    def get_numpy_array(self) -> np.ndarray:
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
                ran_array = np.arange(lower_bound, int(lower_bound + self.record_count * increment_value), increment_value)

            case 'static':
                static_label = float(self.value_args[0])
                if self.field_format == 'integer' or self.field_format == 'double':
                    ran_array = np.empty(self.record_count)
                    ran_array.fill(static_label)
            case _:
                print('ERROR: this distribution is not supported. Function will return an empty '
                      'numpy array which would cause a crash')

        return ran_array

    def get_list_array(self) -> list:
        ran_array = self.get_numpy_array()
        return ran_array.tolist()

    @classmethod
    def get_random_integers(cls, lower_bound, upper_bound, record_count):
        ran_array = np.random.random_integers(lower_bound, upper_bound, record_count)
        return ran_array.tolist()
