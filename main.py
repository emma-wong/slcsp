# Emma Wong
# Spark Advisors Work Example
# Jan 18, 2024

# Given:
# slcsp.csv - csv of zipcodes
# plans.csv - all the health plans in the U.S. on the marketplace
# zips.csv - a mapping of ZIP code to county/counties & rate area(s)

# Output: print zipcodes and second lowest cost silver plans

# Rules:
# A ZIP code can potentially be in more than one county. If the county can not be determined definitively by the ZIP code, 
# it may still be possible to determine the rate area for that ZIP code. 
# A ZIP code can also be in more than one rate area. In that case, the answer should be left blank.

import csv
import pandas as pd

# Take in input files
slcsp_file = csv.reader(open('slcsp.csv', "r"), delimiter=",")
zips_file = pd.read_csv('zips.csv')
plans_file = pd.read_csv('plans.csv')

# Methods

# Given a zipcode, return the rate area list or empty list if there is no rate area
def zipcode_to_rate_area(zipcode_input):
	zipcode_int = int(zipcode_input)

	# Check if line exists in zips.csv
	zip_results = zips_file.query('zipcode == @zipcode_int')

	# Based on the zipcode, determine the rate area (state + number)
	# If there are no results, there is no rate area
	if (zip_results.empty): rate_area = []
	
	# If there is one result, create list var for that rate area
	elif (zip_results.shape[0] == 1): rate_area = [zip_results['state'].values[0], zip_results['rate_area'].values[0]]

	# If there are multiple results, check if they are unique
	else: 
		# If they are unique, return no rate area
		if (zip_results['state'].nunique() != 1 or zip_results['rate_area'].nunique() != 1): rate_area = []
		# If they are the same, they are the same rate area, create list 
		else:
			rate_area = [zip_results['state'].values[0], zip_results['rate_area'].values[0]]

	return rate_area

# Given a rate area list, return the the SLCSP or -1 if there is no SLCSP
def rate_area_to_slcsp(rate_area_input):
	if (type(rate_area_input) != list or not rate_area_input): rate = -1
	else:
		plan_results = plans_file.query('state == @rate_area_input[0] and rate_area == @rate_area_input[1] and metal_level == "Silver"')
		unique_rates = plan_results['rate'].drop_duplicates().nsmallest(2).tolist()

		# If there is no silver plan or only one silver plan, return nothing
		if (not unique_rates or len(unique_rates) == 1): rate = -1
		# Else if there are two or more, return second lowest silver plan (rounded to second decimal place)
		else : 
			# Set rate to second lowest and format to two decimal points
			rate = "{:.2f}".format(unique_rates[1])

	return rate


# Main function

# For loop through input file
for row in slcsp_file:
	# Skip header row
	if (row[0] == 'zipcode' or row[1] == 'rate'): 
		print(row[0] + ',' + row[1])
		continue
	
	# Find rate_area based on zipcode
	ra = (zipcode_to_rate_area(row[0]))

	# If there is a rate area, determine the list of silver plan rates
	if (len(ra) == 2): slcsp = rate_area_to_slcsp(ra)
	else: slcsp = -1

	# If there isn't a slcsp, don't print anything
	if (slcsp == -1): result_slcsp = ''
	else: result_slcsp = str(slcsp)

	# Print output line
	print(row[0] + ',' + result_slcsp)
