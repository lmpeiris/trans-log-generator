import time
import sys
from ScriptApiClass import ScriptTransformApi
from PostProcessor import TemplateBuilder

template_build_type = ScriptTransformApi.read_tlg_config('template_build_type')
sim_jobs = ScriptTransformApi.read_tlg_config('jobnum')
isFirstRecord = True

if template_build_type == 'json_single':
    divider_between_records = ','
    unique_first_record = 1
elif template_build_type == 'json_multi':
    divider_between_records = ''
    unique_first_record = 1
elif template_build_type == 'xml' or template_build_type == 'html':
    divider_between_records = ''
    unique_first_record = 0
else:
    divider_between_records = ScriptTransformApi.read_tlg_config('divider_between_records')
    unique_first_record = ScriptTransformApi.read_tlg_config('unique_first_record')

input_args = sys.argv[1]
print("DEBUG - received args: " + input_args)
if input_args == 'worker.00' and unique_first_record == 1:
    print("DEBUG: This is a unique first job, no record separator in front")
    unique_file = True
else:
    unique_file = False

print(time.asctime() + "INFO: entering template parser: ")
csv_in_file = 'simjobs/' + input_args

destination_file = csv_in_file + ".processed"
TemplateBuilder.parse_template(csv_in_file, ScriptTransformApi.read_tlg_config('template_file'),
                               destination_file, unique_file, divider_between_records)

print(time.asctime() + "INFO: exiting template parser: ")
