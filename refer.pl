#!/usr/bin/perl
use strict;
use warnings;
use Data::Dumper;
our %recordset;

#Passes the command line arguements to perl script. 
#This script is called by: perl refer.pl <refered_fieldname> <column_number> <analysed_field>  
#
chomp ($ARGV[0]);
my @value_args = split('\|',$ARGV[0]); 
my $arg1=$value_args[0];
my $arg2=$value_args[1];
print Dumper(@value_args);
my $field=$ARGV[1];


#open database text file
open REFERENCE, "refer-csv/$arg1.csv";

while(<REFERENCE>) {
#  	my ($col1, $col2) = /^\s*([^,]*?)\s*,\s*(.*?)\s*$/;
	chomp;
        my @csvline = split '\|';
	$recordset{$csvline[0]} = $csvline[$arg2];
#remove new lines, split and put to a hash table.
}
close REFERENCE;

#open generated list of primary keys in the previous steps.
open REFER_DATA, "temp/$arg1.csv";
#open temporary file for output. 
open(my $outfile, ">>", "temp/$field.csv") or die "Can't open out.txt: $!";

while(<REFER_DATA>) {
	chomp; 
        my $refervar = "$_";
	print $outfile "$recordset{$refervar}\n";
	#get data from hash table and print to temp file
}


close REFER_DATA;
close $outfile or die "$outfile: $!";

#print Dumper (\%recordset);

