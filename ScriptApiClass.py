import json
import time


class ScriptApiClass:

    def __init__(self, input_args):
        self.timer = 0
        print('===============')
        print('Processing by ScriptApiClass')
        print('===============')
        print('Call this command for running this script independently for debugging purposes:')
        print(input_args[0] + ' \'' + input_args[1] + '\' \'' + input_args[2] + '\' \'' + input_args[3] + '\'')
        print('--------------')
        api_args = input_args[1].split('|')
        self.value_args = input_args[2].split('|')

        if len(self.value_args) < 1:
            raise ScriptApiClassException("Missing value arguments. At least one required")

        # api key fields
        if len(api_args) < 4:
            raise ScriptApiClassException("Missing API arguments. Require 4 found " + str(len(api_args)))
        else:
            self.field = api_args[0]
            self.field_format = api_args[1]
            self.distrib = api_args[2]
            self.record_count = int(api_args[3])
            if self.field_format == '':
                raise ScriptApiClassException("Please define the variable " + self.field + " in fields format file")

        if len(input_args) < 4:
            raise ScriptApiClassException("Missing flag arguments")

        flag_args = input_args[3].split('|')
        # flag fields
        if len(flag_args) < 1:
            raise ScriptApiClassException("At least one flag is required")
        else:
            if int(flag_args[0]) > 1:
                self.isRepeated = True
                self.num_repeat = int(flag_args[0])
            else:
                self.isRepeated = False

        self.isPlotted = False
        if len(flag_args) > 1:
            if int(flag_args[1]) == 1:
                self.isPlotted = True

        # output file name
        self.outfile = "temp/" + self.field + ".csv"
        print("DEBUG - ScriptApiClass: Received api keys field | field_format | distrib | record count ...... ")
        print(api_args)
        print("DEBUG - ScriptApiClass: Received distribution argument values .......")
        print(self.value_args)
        print("DEBUG - ScriptApiClass: Received flags .......")
        print(flag_args)

        # pandas can handle now on it's own, so don't need to convert for timeseries. For others, convert.
        # time series is a unique distribution with uniform increment, different from distrib.py
        if self.distrib != "timeseries":
            for i in range(0, len(self.value_args)-1):
                if self.value_args[i] == 'now':
                    import time
                    self.value_args[i] = int(time.time())
                    if self.field_format == 'millis' or self.field_format == 'micros':
                        self.value_args[i] = 1000000 * self.value_args[i]

    def start_timer(self):
        self.timer = time.time()

    def stop_timer(self, reason: str, restart_timer: bool = True) -> float:
        # TODO: other lmpeiris projects inherit this from custom logging library
        start_time = self.timer
        end_time = time.time()
        # time elapsed comes in seconds
        t_elapsed = end_time - start_time
        t_seconds = int(t_elapsed) // 60
        t_millis = int((t_elapsed - int(t_elapsed)) * 1000)
        t_minutes = int(t_elapsed/60) // 60
        print('Execution time for ' + reason + ' in minutes:seconds:millis '
              + str(t_minutes) + ':' + str(t_seconds) + ':' + str(t_millis))
        if restart_timer:
            self.start_timer()
        return t_elapsed

    def read_adv_conf(self) -> dict:
        adv_conf_filename = 'refer-csv/' + self.field + '.json'
        ad_conf = {}
        print('Opening json advanced field configuration: ' + adv_conf_filename)
        with open(adv_conf_filename, 'r') as f:
            ad_conf = json.load(f)
            if not ('elements' in ad_conf or 'csv_read' in ad_conf):
                raise ScriptApiClassException('elements or csv_read should be present in advanced config file')
        return ad_conf

    def list_bulk_write(self, ran_list: list[str], buffer_size_mb: int = 4):
        # TODO: find an efficient way of doing this
        # https://stackoverflow.com/questions/37732466/python-csv-optimizing-csv-read-and-write
        print('INFO: dumping ' + str(len(ran_list)) + ' records to output file: ' + self.outfile)
        with open(self.outfile, "w", 1024 * 1024 * buffer_size_mb) as fd:
            for i in ran_list:
                fd.write(i + '\n')
        fd.close()


class ScriptApiClassException(Exception):
    pass


class ScriptTransformApi(ScriptApiClass):

    @classmethod
    def unix2dos(cls, input_file, output_file):
        file_contents = open(input_file, "r").read()
        f = open(output_file, "w", newline="\r\n")
        f.write(file_contents)
        f.close()

    @classmethod
    def read_tlg_config(cls, config_name):
        import configparser
        config = configparser.ConfigParser()
        config.read('log_gen.properties')
        config_value = config['DEFAULT'][config_name]
        return config_value

    @classmethod
    def write_tlg_config(cls, config_name, new_value):
        import warnings
        import subprocess
        warnings.warn('Method write tlg config uses bash sed. No warranty :P')
        sed_regex = '/' + config_name + '/c\\' + config_name + '=' + new_value
        subprocess.check_call(['sed', '-i', sed_regex, 'log_gen.properties'])

    @classmethod
    def get_tlg_outfile(cls):
        import os
        expected_filename = "target/" + ScriptTransformApi.read_tlg_config('output_fileprefix') + "00" + ScriptTransformApi.read_tlg_config('output_filesuffix')
        if os.path.isfile(expected_filename):
            return expected_filename
        else:
            raise ScriptApiClassException("ERROR - cannot locate file generated by TLG")

    @classmethod
    def get_column_headers(cls):
        import csv

        column_header_list = []
        ref_format_file = 'temp/uncommented-fields.txt'
        print("DEBUG - reading column headers from " + ref_format_file)
        with open(ref_format_file) as ref_file_handle:
            data_reader = csv.reader(ref_file_handle, delimiter=',')
            for columns in data_reader:
                column_header_list.append(columns[1])
        return column_header_list
