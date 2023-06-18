#!/usr/bin/perl

use strict;
use warnings;
use String::Random;

my $field=$ARGV[0];
my $distrib=$ARGV[2];
my $field_format=$ARGV[1];
my $record_count=$ARGV[3];
my $regex=$ARGV[4];

my $ran_string = String::Random->new;

print "DEBUG - perl $field_format $distrib is $regex";

open(my $outfile, ">>", "temp/$field.csv") or die "Can't open temp/$field.csv: $!";

if ( $distrib eq "regex" )
{
	for (my $i=1; $i <= $record_count; $i++)
	{		
	print $outfile $ran_string->randregex($regex), "\n";	
	}
}

if ( $distrib eq "pattern" )
{
	for (my $i=1; $i <= $record_count; $i++)
	{		
	print $outfile $ran_string->randpattern($regex), "\n";	
	}
}

close $outfile or die "$outfile: $!";


#fedora package - perl-String-Random, ubuntu package - libstring-random-perl
#http://search.cpan.org/~steve/String-Random-0.20/Random.pm
