#!/usr/bin/env bash

#follow any symlinks and get actual script name with path
ppss_path=$(readlink -f "$0")
#strip script name to get path
ppss_path=$(dirname "$ppss_path")

cd $ppss_path
. log_gen.properties

if [ -n "$1" ]
then
	operation=$1
else
{
	echo -e "Operator argument was not given\nex: ./http-client.sh <operation> \nPlease read README-http-client.txt on how to use \n========================================="
	echo -e "Please select an operation from below list\n-----------------------------------------"
	ls -1 simulators
	echo ""
	exit 1
}
fi

#ppss dir should be removed, otherwise logs will be appended 
rm -r ppss_dir
rm jobfilelist.tmp simjobs/*


if [ -n "$2" ]
then
        http_client_event_file="$2"
fi

#client event file splitting to number of jobs
record_count=`cat $http_client_event_file | wc -l`
lines_per_job=$((record_count/jobnum))
modulo_division=$((record_count%jobnum))

if [ $modulo_division -ne 0 ]
then
	jobnum2=$((jobnum-1))
	lines_per_job=$((record_count/jobnum2))
fi

split -d -l $lines_per_job $http_client_event_file simjobs/worker.

#Preparing job file list for workers
ls -1 simjobs > jobfilelist.tmp
echo -e "\nDividing the job to $jobnum sections and assigning to $processes workers\n"

if [ $operation = "templateParser.py" ]
 then
 	echo "Creating files out of template parser"
 	ppss_command="$python3_command templateParser.py"
 else
 	ppss_command="./simulators/$operation"
 fi

#simulator script. The trailing blank space in the command in the command is mandatory
echo "Invoking simulator script $ppss_command"

if [ $processes = "auto" ]
then
	./ppss -f jobfilelist.tmp -c "$ppss_command "
else
	./ppss -p $processes -f jobfilelist.tmp -c "$ppss_command "
fi

#kill any stray ppss processes
echo "Killing any stray ppss processes"
pkill -f ppss

if [ $operation = "templateParser.py" ]
then
	echo "INFO - concatanate created files using template in to $template_out_file"
	cat "$template_file_header" simjobs/*.processed "$template_file_footer" > $template_out_file
fi

#show event counts
if [ $http_success_counts -eq 1 ]
then
	total_count=`cat ppss_dir/job_log/worker_* | grep "job index" | wc -l`
	success_count=`cat ppss_dir/job_log/worker_* | grep "HTTP" | grep 200 | wc -l`
	echo -e "\nTotal events count: $total_count"
	echo "Success (HTTP 200) events count: $success_count"
fi

#if user has enabled log compression mode. Useful if client is automated
if [ $log_compress -eq 1 ]
then
	echo "compressing logs"
	tar -czf ppss-$operation-`date '+%Y-%m-%d-%H-%M-%S'`.tar.gz  ppss_dir/
	mv ppss-*.tar.gz $compressed_logs
fi

echo -e "\n========================================================="



