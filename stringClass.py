#!/usr/bin/python3

import sys
from ScriptApiClass import ScriptTransformApi
sys.path.insert(0, 'lib')
from DistributionClass import DistributionClass

api = ScriptTransformApi(sys.argv)
static_label = api.value_args[0]

print("DEBUG - entered stringClass.py")
api.start_timer()

filename = "temp/" + str(api.field) + ".csv"
file_handle = open(filename, 'w', 1024 * 1024 * 4)

if api.distrib == 'static':
    print("INFO - printing " + str(static_label) + " again and again")
    if static_label == 'delimiter':
        for i in range(0, api.record_count, 1):
            file_handle.write('|')
    elif static_label == 'dos_line_endings':
        api.unix2dos(api.value_args[1], api.value_args[2])
    else:
        for i in range(0, api.record_count, 1):
            file_handle.write(static_label + '\n')
    api.stop_timer('Static file write')

if api.distrib in ['fake', 'regex']:
    elements_list = []
    # determine number of records which needs to be generated.
    # generating all records as unique is not feasible.
    fake_proportion = float(api.read_tlg_config('fake_proportion'))
    gen_count = int(api.record_count * fake_proportion)
    if gen_count < 100:
        gen_count = 100
    print('Number of unique values to be generated: ' + str(gen_count))
    print("INFO - generating values for " + str(api.value_args[0]))
    match api.distrib:
        case 'fake':
            fake_method = api.value_args[0]
            locale = ''
            if len(api.value_args) > 1:
                locale = api.value_args[1]
                print("INFO - using " + str(locale) + " as locale for generating --> " + str(api.value_args[0]))
            elements_list = DistributionClass.gen_fake_list(fake_method, gen_count, locale)
        case 'regex':
            regex = api.value_args[0]
            elements_list = DistributionClass.gen_regex_list(regex, gen_count)

        case _:
            print('ERROR: this distribution is not supported.')
    api.stop_timer('String generation')
    record_count = api.record_count
    if api.isRepeated:
        print('WARN: repeat has no meaning for fake or regex methods. Only record count would be synced')
        record_count = api.record_count * api.num_repeat
    # generate random uniform integers
    api.start_timer()
    ran_array = DistributionClass.get_random_integers(0, gen_count-1, record_count)
    api.stop_timer('Distribution')
    # get enum for them
    api.start_timer()
    enum_list = DistributionClass.get_enum(elements_list, ran_array)
    # write to file - need to close previously opened file
    file_handle.close()
    api.list_bulk_write(enum_list)
    api.stop_timer('Enum mapping and write')

if api.distrib == 'shuffle_merge':
    import csv

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
    random_array_1 = DistributionClass.get_random_integers(0, len(first_file_list) - 1, api.record_count)
    random_array_2 = DistributionClass.get_random_integers(0, len(second_file_list) - 1, api.record_count)
    api.stop_timer('Distribution')

    print("DEBUG - performing shuffle merge and writing to file")
    api.start_timer()
    if shuffle_merge_operation == 'address':
        random_array_3 = DistributionClass.get_random_integers(
            1, int(api.read_tlg_config('max_address_number')), api.record_count)
        for i in range(0, api.record_count, 1):
            file_handle.write("NO: " + str(random_array_3[i]) + ", " + "".join(first_file_list[random_array_1[i]])
                              + ", " + "".join(second_file_list[random_array_2[i]]) + '\n')
    else:
        for i in range(0, api.record_count, 1):
            file_handle.write("".join(first_file_list[random_array_1[i]]) + " "
                              + "".join(second_file_list[random_array_2[i]]) + '\n')
    api.stop_timer('Merge and write')

file_handle.close()