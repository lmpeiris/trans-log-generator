#!/usr/bin/python3
import sys
from PostProcessor import TemplateBuilder
from ScriptApiClass import ScriptTransformApi
field_count = 0

out_template_file = sys.argv[1]
template_build_type = sys.argv[2]

print("DEBUG - creating " + out_template_file)
# out_file_handle = open(out_template_file, 'w')
template_builder = TemplateBuilder(out_template_file)

if template_build_type == 'json_multi' or template_build_type == 'json_single':
    template_builder.create_json()

if template_build_type == 'xml':
    template_builder.create_xml(sys.argv[3])

if template_build_type == 'html':
    template_builder.create_html_table_rows()
    header_file = 'templates/html-header.txt'
    footer_file = 'templates/html-footer.txt'
    ScriptTransformApi.write_tlg_config('template_file_header', header_file)
    ScriptTransformApi.write_tlg_config('template_file_footer', footer_file)

    html_header = open(header_file, 'w')
    html_header.write('''
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/bootstrap-table/1.8.1/bootstrap-table.min.css">
<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.5/css/bootstrap.min.css">
<table data-toggle = "table" data-pagination = "true">\n
\t<thead>\t\t<tr>\n
''')
    for columns in ScriptTransformApi.get_column_headers():
        html_header.write('\t\t\t<th data-sortable="true">' + columns + '</th>\n')

    html_header.write('''
\t\t</tr>\n\t</thead>\n
\t<tbody>\n
''')
    html_header.close()
    html_footer = open(footer_file, 'w')
    html_footer.write('''
\t</tbody>\n
</table>\n
<script src="https://ajax.googleapis.com/ajax/libs/jquery/2.1.0/jquery.min.js"></script>
<script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.5/js/bootstrap.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/bootstrap-table/1.8.1/bootstrap-table.min.js"></script>
''')
    html_footer.close()

if not template_builder.process_ok:
    print('ERROR - template building failed. Please check configuration parameters')


