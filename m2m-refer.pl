#!/usr/bin/perl
use strict;
use warnings;
use Data::Dumper;
#use List::Util qw( shuffle );
our %recordset;
my @ran_array;

#Passes the command line arguements to perl script. 
my $field=$ARGV[1];
my @value_args = split('\|',$ARGV[0]);
my $key_field=$value_args[0];

#open the reference file for one to many mapping. 
open REFERENCE, "refer-csv/$field.m2m";
#read the file line by line
while(<REFERENCE>) {

	#chomp for removing new lines chars and other useless things
	chomp;
        my @csvline = split '\|';
	# @csvline got the values in current line as an array. $csvline[0] is the key. $csvline[1] contains number of enums we defined.
	# adding the array to hash array with element key $csvline[0]
	for (my $i=0; $i < $csvline[1]; $i++) 
	{
   	$recordset{$csvline[0]}[$i] = $csvline[$i+2];
	}

}
close REFERENCE;

print Dumper (\%recordset);

#open output file to write the resultant picked ups
open(my $outfile, ">", "temp/$field.csv") or die "Can't open temp/$field.csv: $!";

#opening the key distribuition file prepared by other process
open KEY_DISTRO, "temp/$key_field.csv";

	while(<KEY_DISTRO>) {
		chomp;
		my $cur_key="$_";
		# I hate perl. $recordset{$cur_key} is an array handle. $recordset{$cur_key}[0] is a array element handle. @{$recordset{$cur_key} is array handle for scalar.
		my $array_size = @{$recordset{$cur_key}};
		#rand - generates numbers between 0 to X.
		my $random_number = int(rand($array_size));

		print $outfile "$recordset{$cur_key}[$random_number]\n";
		}
close KEY_DISTRO;

close $outfile or die "$outfile: $!";


