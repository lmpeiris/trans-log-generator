# Pre-requisites
- Linux environment with bash
- Python 3.10 or later. Python 3.13 above is recommended

# Test run procedure (example run)
1. In log_gen.properties configure python3_command property to the python executable which is going to be used.
2. Install requirements in requirements.txt using pip
3. Run translog generator using './start-loggen.sh'
4. Find the generated data inside 'target' folder. Default number of records is 2000.

# Configuration
Above procedure used the trans log format stored in translog_formats/unitTest.csv by default.
We can also create our own configuration at the same location.

## Syntax of the trans log format file ##
Below is the syntax:
<column_number>,<field_name>,<distri_bution>,<value_args>,<flags>
ex: 1,datetime,increment,now|1,REPEAT

| Syntax item | purpose | example | allowed configurations |
|---|---|---|---|
| column_number | provide order of the column placed in csv | 1 | integer, >0 as increment. You can leave out numbers but cannot reuse same twice|
| field_name | name of column | datetime | any string |
| distribution | statistical distribution | increment | any distribution described in below dist table |
| value_args | values defining the distribution | 'now\|1' | values matching the required format as described in below dist table|
| flags | flags for turning on column specific features | REPEAT | REPEAT and/or PLOT, if multiple options separate by '\|' |
