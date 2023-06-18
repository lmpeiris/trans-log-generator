#!/usr/bin/python3

import sys
import numpy as np
import time
import datetime
from ScriptApiClass import ScriptTransformApi

# TODO: update random generator for new versions of numpy, see https://numpy.org/doc/stable/reference/random/index.html

api = ScriptTransformApi(sys.argv)
# following decides whether to use numpy write or not
numpy_write = True

# ------- distribution population of data -----------------
# populating a numpy array according to our distribution, there's a lot more
if api.distrib == 'normal':
    mean = float(api.value_args[0])
    standard_deviation = float(api.value_args[1])
    ran_array = np.random.normal(mean, standard_deviation, api.record_count)

if api.distrib == 'exponential':
    scale_parameter = float(api.value_args[0])
    ran_array = np.random.exponential(scale_parameter, api.record_count)

if api.distrib == 'poisson':
    lamda_value = float(api.value_args[0])
    ran_array = np.random.poisson(lamda_value, api.record_count)

if api.distrib == 'binomial':
    turns = float(api.value_args[0])
    probability = float(api.value_args[1])
    ran_array = np.random.binomial(turns, probability, api.record_count)

if api.distrib == 'chi_square':
    degrees_freedom = int(api.value_args[0])
    ran_array = np.random.chisquare(degrees_freedom, api.record_count)

if api.distrib == 'random':
    lower_bound = int(api.value_args[0])
    upper_bound = int(api.value_args[1])
    if api.field_format == 'integer':
        ran_array = np.random.random_integers(lower_bound, upper_bound, api.record_count)
    else:
        ran_array = (upper_bound - lower_bound) * np.random.random(api.record_count) + lower_bound

# for increment we are using a standard list
if api.distrib == 'increment':
    lower_bound = int(api.value_args[0])
    increment_value = int(api.value_args[1])
    ran_array = np.arange(lower_bound, int(lower_bound + api.record_count * increment_value), increment_value)

if api.distrib == 'static':
    static_label = float(api.value_args[0])
    if api.field_format == 'integer' or api.field_format == 'double':
        ran_array = np.empty(api.record_count)
        ran_array.fill(static_label)

# -------- conversions and writing to files ------------------------------------
#format and write the array to the file
filename = "temp/" + api.field + ".csv"

if api.field_format == 'equation':
    from sympy.abc import x
    from sympy.parsing.sympy_parser import parse_expr
    math_expression = api.value_args[3]
    parsed_expression = parse_expr(math_expression)
    print(ran_array)
    count = 0
    for i in ran_array:
        ran_array[count] = parsed_expression.evalf(subs={x: i})
        count += 1


# cannot use numpy text save for this, using standard file write
if api.field_format == 'datetime' or api.field_format == 'time' or api.field_format == 'date' or api.field_format == 'customDT':
    numpy_write = False
    date_time_format = api.value_args[2]
    file_handle = open(filename, 'w')
    if api.isRepeated:
        print("DEBUG - time conversion; repeating is enabled, repeat " + str(api.num_repeat) + " times")
        for i in ran_array:
            converted_string = time.strftime(date_time_format, time.localtime(i))
            for x in range(1, api.num_repeat + 1, 1):
                file_handle.write(converted_string + '\n')
    else:
        print("DEBUG - time conversion; repeating is disabled")
        for i in ran_array:
            file_handle.write(time.strftime(date_time_format, time.localtime(i)) + '\n')
    file_handle.close()
    if api.isPlotted:
        print("DEBUG - PLOT is not supported for this distribution")
        api.isPlotted = False

if api.field_format == 'millis' or api.field_format == 'micros':
    # special writer for timestamp (millis and micros)
    print("DEBUG - using micros time conversion")
    numpy_write = False
    micros_format = api.value_args[2]
    file_handle = open(filename, 'w')
    if api.isRepeated:
        print("DEBUG - repeating is enabled, repeat " + str(api.num_repeat) + " times")
    if api.field_format == 'millis':
        millis = True
        print("DEBUG - cropping to millis")
    else:
        millis = False
    print("DEBUG - time conversion on " + api.field)
    for i in ran_array:
        if millis:
            converted_string = datetime.datetime.fromtimestamp(i/1000000).strftime(micros_format)[:-3]
        else:
            converted_string = datetime.datetime.fromtimestamp(i/1000000).strftime(micros_format)
        if api.isRepeated:
            for x in range(1, api.num_repeat + 1, 1):
                file_handle.write(converted_string + '\n')
        else:
            file_handle.write(converted_string + '\n')
    file_handle.close()
    if api.isPlotted:
        print("DEBUG - PLOT is not supported for this distribution")
        api.isPlotted = False


# plot fields which is still plotting true
if api.isPlotted:
    t1 = time.time()
    import matplotlib.pyplot as plt
    plot_type = api.read_tlg_config('plot_type')
    print("DEBUG - " + str(plot_type) + " plotting is enabled for this column")
    plt.title(api.field + " distribution")

    if plot_type == 'scatter':
        plt.xlabel('array index')
        x_axis = np.arange(1, api.record_count + 1, 1)
        plt.plot(x_axis, ran_array, ScriptTransformApi.read_tlg_config('plotting_format'))

    if plot_type == 'histogram':
        plt.ylabel('Frequency')
        plt.xlabel(api.field + ' value')
        plt.hist(ran_array, bins=int(api.read_tlg_config('plot_bars')))

    plt.savefig(ScriptTransformApi.read_tlg_config('output_location') + "/" + api.field + ".png", bbox_inches="tight")
    t2 = time.time()
    print("DEBUG - plotting " + plot_type + " took " + str(t2-t1) + " seconds")

# if numpy write is still true, write them using numpy which is extremely fast
if numpy_write:
    if api.field_format == 'integer':
        formatting = '%.' + '0f'
    else:
        number_of_decimals = api.value_args[2]
        formatting = '%.' + number_of_decimals + 'f'

    if api.isRepeated:
        print("DEBUG - numpy write section: repeating is enabled, repeat " + str(api.num_repeat) + " times")
        np.savetxt(filename, np.repeat(ran_array, api.num_repeat), formatting)
    else:
        print("DEBUG - numpy write section: repeating is disabled")
        np.savetxt(filename, ran_array, formatting)

print("INFO - exiting distrib.py")
