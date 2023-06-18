#!/usr/bin/python3

import sys
from ScriptApiClass import ScriptTransformApi

api = ScriptTransformApi(sys.argv)
static_label = api.value_args[0]

# format and write the array to the file
print("DEBUG - entered stringClass.py")

filename = "temp/" + str(api.field) + ".csv"
file_handle = open(filename, 'w')

if api.distrib == 'static' and api.field_format == 'string':
    print("INFO - printing " + str(static_label) + " again and again")
    if static_label == 'delimiter':
        for i in range(0, api.record_count, 1):
            file_handle.write('|')
    elif static_label == 'dos_line_endings':
        api.unix2dos(api.value_args[1], api.value_args[2])
    else:
        for i in range(0, api.record_count, 1):
            file_handle.write(static_label + '\n')


if api.distrib == 'fake' and api.field_format == 'string':
    from faker import Factory
    if len(api.value_args) > 1:
        locale = api.value_args[1]
        print("INFO - using " + str(locale) + " as locale for generating --> " + str(api.value_args[0]))
        fake = Factory.create(locale)
    else:
        fake = Factory.create()

    fake_method = api.value_args[0]
    print("INFO - generating values for " + str(fake_method))
    if fake_method == "name" or fake_method == "address":
        print("WARN - PLEASE CONSIDER USING shuffle_merge FOR FASTER DATA GENERATION FOR NAMES AND ADDRESSES")

    if api.isRepeated:
        print("DEBUG - field is repeated " + str(api.num_repeat) + " times")
        for i in range(0, api.record_count, 1):
            fake_out = getattr(fake, fake_method)()
            for x in range(1, api.num_repeat + 1, 1):
                file_handle.write(str(fake_out) + '\n')
    else:
        for i in range(0, api.record_count, 1):
            fake_out = getattr(fake, fake_method)()
            # calling method like this has about 20% performance hit
            # hard code usually required methods if necessary.
            file_handle.write(str(fake_out) + '\n')

if api.distrib == 'shuffle_merge' and api.field_format == 'string':
    import csv
    import numpy as np

    if len(api.value_args) > 2:
        shuffle_merge_operation = api.value_args[2]
    else:
        shuffle_merge_operation = "default"

    first_file = "refer-csv/dictionaries/" + api.value_args[0] + ".csv"
    second_file = "refer-csv/dictionaries/" + api.value_args[1] + ".csv"

    with open(first_file) as first_file_handle:
        first_file_list = list(csv.reader(first_file_handle))
    print("DEBUG - successfully read " + str(len(first_file_list)) + " values from " + first_file)

    with open(second_file) as second_file_handle:
        second_file_list = list(csv.reader(second_file_handle))
    print("DEBUG - successfully read " + str(len(second_file_list)) + " values from " + second_file)

    print("DEBUG - generating random number arrays")
    random_array_1 = np.random.random_integers(0, len(first_file_list) - 1, api.record_count)
    random_array_2 = np.random.random_integers(0, len(second_file_list) - 1, api.record_count)

    print("DEBUG - performing shuffle merge and writing to file")

    if shuffle_merge_operation == 'address':
        random_array_3 = np.random.random_integers(1, int(api.read_tlg_config('max_address_number')), api.record_count)
        for i in range(0, api.record_count, 1):
            file_handle.write("NO: " + str(random_array_3[i]) + ", " + "".join(first_file_list[random_array_1[i]]) + ", " + "".join(second_file_list[random_array_2[i]]) + '\n')
    else:
        for i in range(0, api.record_count, 1):
            file_handle.write("".join(first_file_list[random_array_1[i]]) + " " + "".join(second_file_list[random_array_2[i]]) + '\n')


file_handle.close()