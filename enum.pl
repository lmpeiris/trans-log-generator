#!/usr/bin/perl
use strict;
use warnings;
use Math::Random qw(:all);
use Data::Dumper;

my @enum_array;
my @ran_array;
my @seed;
my $isPercent;
my $total_count = 0;
#to call this perl script use: perl enum.pl <record_count> <field format line> <enum from|enum to> <distribution>
my $record_count=$ARGV[0];
my $enum_line=$ARGV[1];

#reading values from new api format
chomp ($ARGV[2]);
my @value_args = split('\|',$ARGV[2]); 
my $enum_from=$value_args[0];
my $enum_to=$value_args[1];
my $distribution=$ARGV[3];
print Dumper(@value_args);

#random seeder
$seed[0]=int(rand(2047483562));
$seed[1]=int(rand(2047483562));
random_set_seed(@seed);

#put the enums to an array
chomp ($enum_line);
my @values = split(',', $enum_line);
print "DEBUG - read values from field format file\n";
print Dumper(@values);

# checking whether values have | in them, in other words, are we using percentages
if (index($values[3], '|') != -1)
{
	$isPercent=1;
	for (my $i=$enum_from; $i <= $enum_to; $i++) 
	{
   		#enum values start at 3, in following format: malshan|15 for 15%
   		chomp ($values[$i+2]);
   		my @percent_kv = split('\|',$values[$i+2]);
   		print "DEBUG - values for element $i\n";
		print Dumper(@percent_kv);
		#populate the array up to 100 with biased filling using array multiplication
		my $key_name = $percent_kv[0];
		my $key_percentage = int($percent_kv[1]);
		@enum_array = (@enum_array, ($key_name) x $key_percentage);
		$total_count = $total_count + $key_percentage;
	}
	print "ERROR - The sum of percentages are not 100. Aborting script\n"; exit 1 if $total_count ne 100;
	#create a random integer array
	@ran_array=random_uniform_integer($record_count,0,99);
}
else
{
	$isPercent=0;
	#if no percentages, use the given enum with equal bias
	#values is the array of values from field format line. 0th --> fieldname, 2nd --> total number of enum records, 3rd onwards --> enum values
	#enum array starts from 0, values start from 3, and enum from value starts from 1
	for (my $i=$enum_from; $i <= $enum_to; $i++)
	{
   		$enum_array[$i-1]=$values[$i+2];
	}
	if ($distribution eq 'random')
	{
		@ran_array = random_uniform_integer($record_count,$enum_from-1,$enum_to-1);
		# we keep enum indexes starting from 0 in rand array
	}

	if ($distribution eq 'Robin')
	{
	    #find number of iterations and remaining numbers for us to do round robin
	    my $enum_count = $#enum_array + 1;
		my $iterations = int(int($record_count)/$enum_count);
		my $remaining = int($record_count)%$enum_count;
		print "DEBUG - iterating enum array of $enum_count records $iterations times\n";
		my @enum_numbers = (0..$enum_count-1);
		#adding index of the enum in to ran_array, not values
		for (my $i=0; $i < $iterations; $i++)
		{
			push(@ran_array,@enum_numbers);
		}
		if ($remaining > 0)
		{
            print "DEBUG - adding modulo divided $remaining values to array\n";
            my @remaining_numbers = [];
            for (my $i=0; $i < $remaining; $i++)
            {
                $remaining_numbers[$i] = $i;
            }
            push(@ran_array,@remaining_numbers);
        }
	}
}

print "DEBUG - considered enum array\n";
print Dumper(@enum_array);
print "\nDEBUG - random uniform array created\n";

#populate a file according to random array picking values from enum values array
open(my $outfile, ">>", "temp/$values[0].csv") or die "Can't open temp/$values[0].csv: $!";

foreach (@ran_array)
{
    #TODO: find an efficient array to file writer
    print $outfile "$enum_array[$_]\n";
#    print $outfile "$_\n" ; # Print each entry in our array to the file
}
close $outfile or die "$outfile: $!";

print "\nDEBUG - writing to file completed. redirecting to allocator";

