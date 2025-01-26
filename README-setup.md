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

## field formats ##
Field format for any field_name is also need to be defined in field_formats.csv. This is a common file and any translog format file can reuse.
supported field formats: 
- enum (string, but limited choices)
- string (any string)
- integer
- double (number with decimals)
- time field formats: datetime (up to second), date, time (up to second), millis (miliseconds)

Assume we selected enum as field format, and used normal as the distribution. Then we get a dataset where you get a normal distribution of enum values.

## Distribution definition ##

| Distribution | Definition | value arg1 | value arg2 | value arg3 | field_format support|
|---|---|---|---|---|---|
| normal | normal distribution | mean | standard deviation || all except string|
| exponential | exponential distribution | scale | N/A || all except string|
| poisson | poisson distribution | lambda | N/A || all except string|
| binomial | binomial distribution | number of turns | probability || all except string|
| chi_square | chi_square dist| degrees of freedom | N/A || all except string|
| random | random distribution | lower bound | upper bound|| all except string|
| increment | incrementing integer | lower bound | increment || integer|
| static | same value repeated | repeated value ||| string, integer, double|
| percentage | enum percentage | N/A | N/A || enum|
| roundrobin | RR repeated distribution | lower bound | upper bound||all except string|
| timeseries | incremental timeseries | start_time | interval string | datetime format| time field formats|
| fake | data generated using fake method | fake_method | fake_locale || string, enum|
| regex | data generated matching regex | regex string ||| string, enum|
| shuffle merge | use multiple csv as input to create new strings | file1 | file2 | sm operation| string|
| refer | random choice from selected set of values depending on another field | other field||| string|
| duplicate | exact duplicate of another field| other field|N/A|| string|

## advanced field configuration ##
enum and refer fields also require advanced configurations to be placed as json and csv inside refer-csv/<field_name>.json to work

below are examples:

### enum ###
```json
{
  "type": "enum",
  "source": "elements",
  "elements": [
    {
      "enum": "agree",
      "count": 45
    },
    {
      "enum": "deny",
      "count": 30
    },
    {
      "enum": "none",
      "count": 25
    }
  ]
}
```

### refer ###
refer uses first column as the value from the 'other field'. Next column shows allowed values in '\|' delimited values.

```csv
SPP_000001,APP_000001|APP_000002|APP_000003
SPP_000002,APP_000004
SPP_000003,APP_000005|APP_000006
SPP_000021,APP_000041|APP_000042|APP_000043|APP_000031|APP_000032|APP_000033|APP_000021|APP_000022|APP_000023
```
