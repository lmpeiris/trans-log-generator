#!/usr/bin/env bash
#Installing necessary stuff

#checking whether you have root access
touch /test.txt
[ $? -ne 0 ] && echo "You do not have root access. Please run as root" && exit 1

#checking whether you have commands

cpan -v
[ $? -ne 0 ] && echo -e "You do not have CPAN installed. Use your package manager to install; ex: ubuntu - sudo apt-get install cpan\n" && exit 1

echo "Please insert path / command to python3 executable (default: python3, press enter for default):"
read python3_executable
[ "$python3_executable" = "" ] && python3_executable="python3"
$python3_executable --version
if [ $? -ne 0 ] 
then
	echo -e "Python 3 executable not found. Aborting script\n" && exit 1
else
	sed -i "/python3_command/c\python3_command=$python3_executable" log_gen.properties
fi

echo "Please insert path / command to pip for python3 (default: pip3, press enter for default):"
read pip3_executable
[ "$pip3_executable" = "" ] && pip3_executable="pip3"
$pip3_executable --version
[ $? -ne 0 ] && echo -e "Pip 3 executable not found. Aborting script\n" && exit 1


cat refer-csv/dependencies.csv | while read dependency
do
{
library_name=`echo $dependency | cut -d'|' -f1`
language=`echo $dependency | cut -d'|' -f2`
critical=`echo $dependency | cut -d'|' -f3`
task_role=`echo $dependency | cut -d'|' -f4`
man_inst=`echo $dependency | cut -d'|' -f5`


echo "Searching for $language $library_name library availability......"

if [ "$language" = "perl" ]
then
	perl -e "use $library_name"
	search_result=$?
fi
if [ "$language" = "python" ]
then
	$pip3_executable show $library_name
	search_result=$?
fi

if [ $search_result -eq 0 ]
then
{
	echo "Found $library_name. ok to go..."
}
else
{
	echo "$library_name not found. This enables $task_role. Do you want to try install it via installer? (y/n)"
	read whatever_entered < /dev/tty
	if [ "$whatever_entered" = "y" ]
	then
		if [ "$language" = "perl" ]
		then
			cpan $library_name
			install_result=$?
		fi
		if [ "$language" = "python" ]
		then
			$pip3_executable install $library_name
			install_result=$?
		fi

		if [ $install_result -ne 0 ]
		then
			echo -e "Installing $language $library_name failed. \n You can try to install it manually using - $man_inst"
			[ $critical -eq 1 ] && echo -e "FATAL - aborting script\n" && exit 1
		else
			echo -e "TLG install script - Installing $language $library_name success" 
		fi
	fi
}
fi
echo "========================================================"
echo "========================================================"
}
done

echo "extracting dictionaries....."
tar -xvf refer-csv/dictionaries.tar.xz

