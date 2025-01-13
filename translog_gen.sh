#!/usr/bin/env bash
start_time=$(($(date +%s%N)/1000000))
echo "DEBUG - started sourcing property file"
. log_gen.properties

#memory limit per child process
if [ $max_memory_child -gt 0 ]
then
    echo "current free memory in system: `free | grep 'buffers/cache' | awk {'print $4'}`"
    echo "Current memory limit: `ulimit -Sv`"
    ulimit -Sv $max_memory_child
    echo "Memory after applying max memory per child process limitation: `ulimit -Sv`"
fi

field_format=""
format_line=""
#The script receives a single line of spec to generate a column from ppss
#line format: number,field,distrib,value_args_separated_by |,flags
	echo "INFO - `date` - Entered the translog field allocator" 
	lines=$1
       field=`echo $lines | cut -d',' -f2`
       distrib=`echo $lines | cut -d',' -f3`
	value_args=`echo $lines| cut -d',' -f4`

	#flag checking
	echo $lines | grep REPEAT >/dev/null && repeat_enabled=1 && record_count=$((record_count_per_file*number_of_files)) && echo "DEBUG - $field is to be REPEATED"
	echo $lines | grep NR >/dev/null && repeat_enabled=0 && record_count=$((record_count_per_file*number_of_files*num_repeat)) && num_repeat=0 && echo "DEBUG - $field is NOT REPEATED"
	echo $lines | grep DR >/dev/null && repeat_enabled=0 && record_count=$((record_count_per_file*number_of_files)) && num_repeat=0 && echo "DEBUG - REPEAT is not defined for this translog"
	echo $lines | grep PLOT >/dev/null && plot_enabled=1 && echo "Plotting is enabled for $field" || plot_enabled=0

#A wierd bug causing format_file variable not  being able to be used in the code. So use as field_formats.csv directly.
echo "INFO - started to create matching fields"
#Checking for duplicate entries, and partial matches in field formats file. We can't just grep and match. It could match anything.
	cat field_formats.csv | grep $field > temp/matching-fields/$field.txt
#use IFS as normal while cannot retain variables
while IFS= read -r format_lines
       do
	{
       		tempfield=`echo $format_lines| cut -d',' -f1`
       		if [ $tempfield = $field ]
		then
			field_format=`echo $format_lines| cut -d',' -f2`
			format_line=$format_lines
		fi
	}
	done < temp/matching-fields/$field.txt

      echo "INFO - matching fields compilation complete"
       echo "DEBUG - Fields received for processing"
	echo "DEBUG - fieldname|distribution|formatfile used|received format type"
       echo "DEBUG - $field|$distrib|$format_file|$field_format"

#duplicate check logic ends here.

#rewrite third arguement for date,time,datetime entries for compatibility, if not use custom datetime "customDT"
if [ $field_format = "datetime" ]
then
	value_args="$value_args|$datetime_format"
elif [ $field_format = "date" ]
then
	value_args="$value_args|$date_format"
elif [ $field_format = "time" ]
then
	value_args="$value_args|$time_format"
elif [ $field_format = "millis" ] || [ $field_format = "micros" ]
then
	value_args="$value_args|$microtime_format"
elif [ $field_format = "customDT" ]
then
	echo "DEBUG - using custom date time format"
fi

#read arguement 4 for following fields
if [ $field_format = "equation" ]
then
	arg4=`echo $lines| cut -d',' -f7`
else
	arg4='NULL'
fi

#decide logic on numerical distribution
case $distrib in
#=======================================

#Logic for importing data from a csv, not generating.
"import")
echo "INFO - Entered csv import sub routine at allocator"
file_lines=`cat $import_data_location/$field.csv | wc -l`

#if the imported file has more records than we need, just get the amount we need from the top
if [ $file_lines -ge $record_count ]
then
	echo "DEBUG - file with $file_lines lines imported directly"
	head -n $record_count $import_data_location/$field.csv > temp/$field.csv
else
#repeat the file' records to match the amount we need.
	mod_div=$((record_count%file_lines))
	cat_iterations=$((record_count-mod_div))
	cat_iterations=$((cat_iterations/file_lines))

	echo "DEBUG - repeating file of $file_lines lines to be inserted"
	for (( i=0; i<$cat_iterations; i++ ))
	do
		cat $import_data_location/$field.csv  >> temp/$field.csv
	done
	head -n $mod_div $import_data_location/$field.csv >> temp/$field.csv
fi
;;
#============================================
"static")
echo "INFO - Generating a static field file of $record_count records"
if [ $field_format = "integer" ] || [ $field_format = "double" ]
then
	$python3_command distrib.py "$field|$field_format|$distrib|$record_count" "$value_args" "$num_repeat|$plot_enabled"
else
	#no need to define in field format file if you define static string
	$python3_command stringClass.py "$field|string|$distrib|$record_count" "$value_args" "$num_repeat"
fi
;;

#========================================
"shuffle_merge"|"fake"|"regex")
echo "DEBUG - redirecting to strinClass.py for string operation"
$python3_command stringClass.py "$field|$field_format|$distrib|$record_count" "$value_args" "$num_repeat"
;;

#========================================
"duplicate")
copied_field=`echo $value_args | cut -d'|' -f1`
# no need to define field format in field format file
echo "INFO - copying $copied_field as $field"
cp temp/$copied_field.csv temp/$field.csv
;;

#========================================
"random"|"roundrobin"|"increment"|"normal"|"poisson"|"exponential"|"binomial"|"chi_square")
echo "DEBUG - in common numeric distro block. format: $field_format, distrib: $distrib"
#perl distrib.pl $field $field_format $distrib $record_count "$arg1" "$arg2" "$arg3"
$python3_command distrib.py "$field|$field_format|$distrib|$record_count" "$value_args" "$num_repeat|$plot_enabled"
;;

#=============================================
"refer")
#logic for dependent fields on another field. A field can only depend on one field.
#perl refer.pl <refered_fieldname> <column_number> <analysed_field>
echo "INFO - entered refer block. field format: $field_format"
if [ $field_format = "m2m" ]
then
{
	perl m2m-refer.pl $value_args $field
}
else
{
	perl refer.pl $value_args $field
}
fi
;;

#=========================
"timeseries")
echo "INFO - enetered time series block"
$python3_command timeSeries.py "$field|$field_format|$distrib|$record_count" "$value_args" "$num_repeat"

;;

#===============================================
#unknown distribution
*) echo "ERROR - Unsupported stastical distribution. Please check $field";;

esac

end_time=$(($(date +%s%N)/1000000))
process_time=$((end_time-start_time))
echo "$field,$distrib,$process_time" >> temp/process_times.csv
echo -e "\n======================================================\nINFO - Process took $process_time miliseconds\n"
echo -e "\nINFO - `date` - exited the translog field allocator\n" 


