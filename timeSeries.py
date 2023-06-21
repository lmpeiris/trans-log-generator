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

time_series = pd.date_range(start_time, periods=api.record_count, freq=interval_string)

if api.isRepeated:
    print("DEBUG - time series generation; repeating is enabled, repeat " + str(api.num_repeat) + " times")
    time_series = time_series.repeat(api.num_repeat)

else:
    print("DEBUG - time series generation; repeating is disabled")

# convert to dataframe
writing_df = time_series.to_frame(index=False)
print("INFO - writing time series to file")
writing_df.to_csv(path_or_buf=filename, index=False, header=False, date_format=dt_format)

