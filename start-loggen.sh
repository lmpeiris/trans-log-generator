#!/usr/bin/env bash
start_time=`date '+%s'`
echo "INFO - starting translog generator (TLG)...."
#follow any symlinks and get actual script name with path
ppss_path=$(readlink -f "$0")
#strip script name to get path
ppss_path=$(dirname "$ppss_path")
cd $ppss_path

. log_gen.properties

#showing scripting versions
echo "INFO - used python version is "
$python3_command --version
#Remove temporary folders / else logs will be appended
echo "INFO - removing temporary files ....."
rm  temp/*.* temp/matching-fields/*.*
rm -r ppss_dir ppss_dir_phase_2 ppss_dir_phase_1

# meta data update
if [ $meta_data_enabled -eq 1 ]
then
	sh version_control.sh "translog_formats/$event_type_file"
fi

# clean builds
if [ $overwrite_target -eq 1 ]
then
	echo "INFO - removing conflicting target files"
	rm target/$output_fileprefix*
fi

echo "======================================================================"
echo "INFO - Started creating list data for  translog_formats/$event_type_file............."

#removing commented lines (if any) from field file
cat translog_formats/$event_type_file | grep -v "#" | grep -v "//" | grep '[^[:blank:]]'> temp/uncommented-fields.txt

field_count=`awk 'END{print NR}' temp/uncommented-fields.txt`
#fix for taking field count less than one
((field_count++))
#checking for record repetition enabled
cat temp/uncommented-fields.txt | grep REPEAT >/dev/null && repetition_enabled=1 || repetition_enabled=0

declare -a fields

while IFS= read -r record_blocks
do
{
	#Records in the field file can be swapped when parallel processing
	count=`echo $record_blocks | cut -d',' -f1`
	value_field=`echo $record_blocks | cut -d',' -f2`
  fields[$count]=$value_field
	field_distrib=`echo $record_blocks | cut -d',' -f3`

	#adding flags
	flags=""
	if [ $repetition_enabled -eq 1 ]
	then
		echo $record_blocks | grep REPEAT >/dev/null && echo "DEBUG - repetition is enabled for $value_field" || flags="NR"
	else
		flags="DR"
	fi

	#Dependent fields are processed in the 2nd ppss run to avoid concurrency issues
	if [ $field_distrib = "refer" ] || [ $field_distrib = "duplicate" ]
	then
		echo "DEBUG - field $count,$value_field having $field_distrib distribution added to 2nd phase"
		echo "$record_blocks,$flags" >> temp/delayed_fields.tmp
	#Checking for blank lines before adding to process
	elif [ $field_distrib != "" ]
	then
		echo "DEBUG - field $count,$value_field having $field_distrib distribution added to 1st phase"
		echo "$record_blocks,$flags" >> temp/taken_fields.tmp
	fi
}
done < `echo temp/uncommented-fields.txt`

echo -e "\033[36m"
echo -e "INFO - Starting PPSS server...............\nINFO - progress mentioned completed when a task was commisioned, not completed"
#running the PPSS in single node
#The trailing blank space in the command string is a must 
#ppss -f <input file> -c <command to run on each line of the file >

#fields are processed in a second run if they depend on other fields, in a multi process environment

if [ -f temp/delayed_fields.tmp ]
then
	echo "INFO - Process phase 1 ............."
	if [ $processes = "auto" ]
	then
		./ppss -f  temp/taken_fields.tmp -c './translog_gen.sh '
	else
		./ppss -p $processes -f  temp/taken_fields.tmp -c './translog_gen.sh '
	fi
	cp -r ppss_dir ppss_dir_phase_1
	rm -r ppss_dir

	echo -e "\nINFO - Process phase 2 .............\n"
	if [ $processes = "auto" ]
	then
		./ppss -f  temp/delayed_fields.tmp -c './translog_gen.sh '
	else
		./ppss -p $processes -f  temp/delayed_fields.tmp -c './translog_gen.sh '
	fi
	cp -r ppss_dir ppss_dir_phase_2
	rm -r ppss_dir
else
	if [ $processes = "auto" ]
	then
		./ppss -f  temp/taken_fields.tmp -c './translog_gen.sh '
	else
		./ppss -p $processes -f  temp/taken_fields.tmp -c './translog_gen.sh '
	fi
fi


echo "======================================================================"
echo "INFO - Stopping PPSS server ..........."
echo "DEBUG - verifying record count of generated files and adding them to chaining file"
echo -e "\033[0m"
[ $repetition_enabled -eq 1 ] && expected_records=$((record_count_per_file*number_of_files*num_repeat)) || expected_records=$((record_count_per_file*number_of_files))

# below syntax allows both key and value to be iterated
for i in "${!fields[@]}"
do
{
    if [ ${fields[i]} != "" ]
		then
		{
			if [ -f "temp/${fields[i]}.csv" ]
			then
			{
				echo "temp/${fields[i]}.csv" >> temp/paste_list.tmp
				if [ $validation_check -eq 1 ]
				then
				{
					actual_records=`awk 'END{print NR}' temp/${fields[i]}.csv`
					if [ $actual_records -eq $expected_records ]
					then
						echo -e "DEBUG - Record count in ${fields[i]}.csv is  $actual_records ......... \033[32m [ OK ] \033[0m"
						if [ $add_column_names -eq 1 ]
						then
						# TODO: this implementation writes files again, add the names before files are created and then add 1 to expected records when verifying
							echo "${fields[i]}"  > temp/${fields[i]}.csv.tmp1
							cat temp/${fields[i]}.csv.tmp1 temp/${fields[i]}.csv > temp/${fields[i]}.csv.tmp2
							rm temp/${fields[i]}.csv.tmp1 temp/${fields[i]}.csv
							mv temp/${fields[i]}.csv.tmp2 temp/${fields[i]}.csv
						fi

					else
						echo -e "ERROR - Record count for column $i in ${fields[i]}.csv is $actual_records expected $expected_records records ......... \033[31m [ FAILED ] \033[0m"
					fi
				}
				fi
			}
			else
			{
				echo -e "\033[31m ERROR - There was an issue when creating data for field ${fields[i]} \n Please check fields file (translog_formats/$event_type_file) and format file ($format_file) and the ppss_dir/job_log logs\n Exiting application\n \033[0m"
				echo -e "DEBUG - Below is the log of the failed script file"
				[ -f temp/delayed_fields.tmp ] && log_file=`find ppss_dir_phase_*/job*  -type f | grep ${fields[i]} | grep $i` || log_file=`find ppss_dir/job*  -type f | grep ${fields[i]} | grep $i`
				cat $log_file
				exit 1
			}
			fi
		}
		fi
}
done

#all generated files, and other after effects should be listed in a line in temp/paste_list.tmp
#adding delimiters at the end
if [ $delimiters_at_ends -eq 1 ]
then
{
	#ask string generating script to create a dummy file to paste
	$python3_command stringClass.py "delimiter|string|static|$expected_records" "delimiter" "0"

	cp temp/paste_list.tmp temp/paste_list.temp1
	echo "temp/delimiter.csv" > temp/paste_list.temp2
	cat temp/paste_list.temp2 temp/paste_list.temp1 temp/paste_list.temp2 > temp/paste_list.tmp
	rm temp/paste_list.temp2 temp/paste_list.temp1
 }
fi

#DOS line endings
if [ $dos_line_endings -eq 1 ]
then
{
	final_csv_file=`tail -n 1 temp/paste_list.tmp`
	#add \r for windows line endings to only the last column
	$python3_command stringClass.py "delimiter|string|static|$expected_records" "dos_line_endings|$final_csv_file|temp/dos_new_line.txt" "0"
	rm $final_csv_file
	mv temp/dos_new_line.txt $final_csv_file
 }
fi


io_start_time=`date '+%s'`
echo "INFO - Aggregating columns together"
#creating the paste command for all the columns, from the paste_list.tmp . This commands pastes columns horizontally between multiple files

cat temp/paste_list.tmp | while read paste_items
do
	echo -n " $paste_items" >> temp/paste_string.temp
done
paste_string=`cat temp/paste_string.temp`

echo "INFO - Adding final touches"
#cutting and shaping file names as user desires
if [ $number_of_files -eq 1 ]
then
{
	if [ $enable_compression -eq 1 ]
	then
		echo "INFO - using multi threaded compression"
		paste -d"$log_delimiter" $paste_string | "$compression_tech" -c > "$output_location"/"$output_fileprefix"00"$output_filesuffix".gz
	else
		paste -d"$log_delimiter" $paste_string > "$output_location"/"$output_fileprefix"00"$output_filesuffix"
	fi
}
else
{
	paste -d"$log_delimiter" $paste_string | split --additional-suffix="$output_filesuffix" -d -l $record_count_per_file - "$output_location"/"$output_fileprefix"
}
fi

end_time=`date '+%s'`
process_time=$((end_time-start_time))
io_time=$((end_time-io_start_time))
echo -e "\n======================================================\nINFO - Total Process took $process_time seconds\nINFO - IO rearrange operations took $io_time seconds of it \n "
echo "INFO - record creation speed $((expected_records/process_time)) records per second"

if [ $number_of_files -eq 1 ]
then
	gen_file_size=`ls -l --block-size=1k "$output_location"/"$output_fileprefix"* | awk '{print $5}'`
	[ $io_time -gt 0 ] && echo "INFO - data written log file $((gen_file_size/io_time)) kB/sec"
fi
echo -e "INFO - Check $output_location folder for the generated files\n"
if [ $benchmark_plot -eq 1 ]
then
	echo "Benchmark plot is enabled in configuration"
	$python3_command lib/benchMarking.py $event_type_file $expected_records
fi

if [ $post_template_enable -eq 1 ]
then
	echo "INFO - creating template file for $template_build_type writing to $template_file"
	$python3_command templateBuilder.py $template_file $template_build_type $repeating_tag_xml
fi
echo -e "\a"

if [ $start_ftp_after_process -eq 1 ]
then
	echo "INFO - starting FTP server on target folder, use port 2121 to access via network. Use ctrl + c to stop"
	$python3_command lib/ftpServer.py
fi
