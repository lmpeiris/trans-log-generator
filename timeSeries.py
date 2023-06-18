#!/usr/bin/python3
import pandas as pd
import sys
from ScriptApiClass import ScriptApiClass

api = ScriptApiClass(sys.argv)
start_time = api.value_args[0]
interval_string = api.value_args[1]
dt_format = api.value_args[2]

# format and write the array to the file
filename = "temp/" + api.field + ".csv"

panda_array = pd.date_range(start_time, periods=api.record_count, freq=interval_string)

if api.isRepeated:
    print("DEBUG - time series generation; repeating is enabled, repeat " + str(api.num_repeat) + " times")
    pd.Series.to_csv(panda_array.repeat(api.num_repeat), filename, False, '.', '', None, False, None, 'w', None, None, dt_format)
else:
    print("DEBUG - time series generation; repeating is disabled")
    pd.Series.to_csv(panda_array, filename, False, '.', '', None, False, None, 'w', None, None, dt_format)

