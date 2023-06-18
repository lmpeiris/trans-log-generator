class PostProcessor:
    def __init__(self, output_file):
        self.output_file = output_file
        self.csv_content = []
        self.process_ok = False

    def set_input_as_list(self, input_2d_list):
        if not isinstance(input_2d_list[0], list):
            raise PostProcessorException("Input should be two dimentional python array")
        else:
            self.csv_content = input_2d_list

    def set_input_as_csv(self, csv_file, delimiter):
        import csv
        with open(csv_file, 'r') as csv_handler:
            row_handler = csv.reader(csv_handler, delimiter=delimiter)
            self.csv_content = list(row_handler)


class PostProcessorException(Exception):
    pass


class ExcelProcessor(PostProcessor):

    def convert_to_xlsx(self):
        from pyexcelerate import Workbook

        if len(self.csv_content) > 65534:
            raise PostProcessorException("Cannot create file larger than 65564 rows")

        excel = Workbook()
        excel.new_sheet('default', data=self.csv_content)
        excel.save(self.output_file)
        self.process_ok = True


class TemplateBuilder(PostProcessor):
    def __init__(self, output_file):
        PostProcessor.__init__(self, output_file)
        from ScriptApiClass import ScriptTransformApi
        self.out_file_handle = open(self.output_file, 'w')
        self.column_list = ScriptTransformApi.get_column_headers()

    def close_builder(self):
        self.out_file_handle.close()
        print("DEBUG - post processing operation completed")
        self.process_ok = True

    def create_json(self):
        field_count = 0
        print("DEBUG - writing json template to " + self.output_file)
        self.out_file_handle.write('{')
        for columns in self.column_list:
            if field_count >= 0:
                if field_count >= 1:
                    self.out_file_handle.write(',')
            self.out_file_handle.write('\"' + columns + '\"' + ' : \"$d[' + str(field_count) + ']\"')
            field_count += 1
        self.out_file_handle.write('}')
        self.close_builder()

    def create_xml(self, repeating_tag_xml):
        field_count = 0
        print("DEBUG - writing xml template to " + self.output_file)
        self.out_file_handle.write('<' + repeating_tag_xml + '>')
        for columns in self.column_list:
            self.out_file_handle.write('<' + columns + '>' + '$d[' + str(field_count) + ']</' + columns + '>')
            field_count += 1
        self.out_file_handle.write('</' + repeating_tag_xml + '>')
        self.close_builder()

    def create_html_table_rows(self):
        field_count = 0
        print("DEBUG - writing XML template to " + self.output_file)
        self.out_file_handle.write('\t\t<tr>\n')
        for columns in self.column_list:
            self.out_file_handle.write('\t\t\t<td>' + '$d[' + str(field_count) + ']' + '</td>\n')
            field_count += 1
        self.out_file_handle.write('\t\t</tr>\n')
        self.close_builder()

    @classmethod
    def parse_template(cls, data_csv, template_file, dest_file,
                       unique_file=False, divider_between_records=',', input_divider='|'):
        import airspeed
        import csv
        is_first_record = True

        with open(template_file, 'r') as tf_handler:
            t = airspeed.Template(tf_handler.read())

        df_handle = open(dest_file, 'w')
        print("INFO: Processing " + data_csv + " and writing in to " + dest_file)
        with open(data_csv, 'r') as data_handle:
            data_reader = csv.reader(data_handle, delimiter=input_divider)
            for d in data_reader:
                if unique_file and is_first_record:
                    print("DEBUG: first record of a unique file will skip the separator")
                    is_first_record = False
                else:
                    df_handle.write(divider_between_records)

                df_handle.write(t.merge(locals()) + '\n')
        df_handle.close()
        data_handle.close()

    @classmethod
    def random_parser(cls, data_csv, template_array, dest_file, number_of_records, input_divider='|'):
        import airspeed
        import csv
        import numpy as np

        airspeed_templates = [airspeed.Template(pattern) for pattern in template_array]

        df_handle = open(dest_file, 'w')
        print("INFO: Processing " + data_csv + " and writing in to " + dest_file)
        with open(data_csv, 'r') as data_handle:
            data_reader = csv.reader(data_handle, delimiter=input_divider)
            random_array = np.random.random_integers(0, len(template_array) - 1, number_of_records)
            for i in range(0, number_of_records, 1):
                df_handle.write(airspeed_templates[random_array[i]].merge(locals()) + '\n')





