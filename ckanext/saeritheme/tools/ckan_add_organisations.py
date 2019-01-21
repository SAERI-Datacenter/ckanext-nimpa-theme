#!/usr/bin/env python2
# 1.01 arb Mon Jan 21 13:58:21 GMT 2019 - update if already exists. Check logo file exists.

# Create all organisations from a CSV file.
# See https://docs.ckan.org/en/2.8/api/index.html#ckan.logic.action.patch.organization_patch
# See https://github.com/ckan/ckan/issues/3853

import urllib2
import urllib
import json
from pprint import pprint
import csv
import os # for os.path.isfile
from ckanapi import RemoteCKAN

# Configuration
csv_filename="grouped_organisations_ready_arb.csv"
ckan_ip = "172.16.92.142"
api_key = "0317c21c-7d04-48df-8f1b-9989edbd6165"
user_agent = 'ckanapiexample/1.0 (+http://example.com/my/website)'
logo_dir = "../public/logo"

# CSV fields are:
# organisation,organisation_name,organisation_logo,records_count

# -----------------------------------------------------------------------
# field names which can be set:
# name (lowercase, no spaces)
# id / title / description
# image_url
# eg.
#'description': u'Can be deleted',
#'image_url': u'',
#'name': u'testorg',
#'title': u'Test Organization',

# ---------------------------------------------------------------------
# Return a list of organisation names, eg. ['BAS', 'FIG']
def get_existing_organisations_dict():
	organisations_data = ckan.action.organization_list(all_fields=True)
	#pprint(organisations_data)
	return organisations_data

# ---------------------------------------------------------------------
# Return a list of organisation names, eg. ['BAS', 'FIG']
def get_existing_organisations_names(organisations_data):
	organisations_list = [x['name'] for x in organisations_data]
	return(organisations_list)


# ---------------------------------------------------------------------
# Add one organisation to CKAN from the CSV data given in row
# i.e. row['organisation'] and organisation_name and organisation_logo.
def add_organisation(row):
	# Sanitise the input
	name_lowercase = row['organisation'].lower()

	# For testing:
	#if name_lowercase != "caasm":
	#	return

	# Find the logo image
	if row['organisation_logo'] == '':
		image_with_path = ''
	else:
		if os.path.isfile("%s/%s" % (logo_dir, row['organisation_logo'])):
			image_with_path = "/logo/%s" % row['organisation_logo']
		else:
			print("WARNING: %s logo %s file not found" % (name_lowercase, row['organisation_logo']))
			image_with_path = ''

	fullname = row['organisation_name']
	print("Add %s %s = %s" % (name_lowercase, image_with_path, fullname))

	# Organisation to be added/updated
	org_dict = {}

	# First check that the organisation doesn't already exist
	create_or_update_action = 'organization_create'
	if name_lowercase in organisations_names:
		print("NOTE: %s already exists, will update" % name_lowercase)
		create_or_update_action = 'organization_patch' # not organization_update which cleans it all first
		# Find the id of the given organisation to update this exact one
		org_dict['id'] = [i for i in organisations_data if i['name']==name_lowercase][0]['id']
		org_dict['clear_upload'] = True # so that a change to image_url is forced

	# Create a dictionary with the info we need to add to CKAN
	org_dict['name'] = name_lowercase
	org_dict['title'] = row['organisation_name']
	org_dict['image_url'] = image_with_path
	#print("Using %s" % org_dict)

	result = ckan.call_action(create_or_update_action, org_dict)
	if result['approval_status'] == 'approved':
		print("Added %s" % name_lowercase)
		#pprint(result)
	else:
		print("ERROR adding %s :" % name_lowercase)
		pprint(result)
		exit(1)
	return


# -----------------------------------------------------------------------
# MAIN

# Read in the CSV file
fp = open(csv_filename)
reader = csv.DictReader(fp)

# Open the connection to the CKAN server
ckan = RemoteCKAN('http://%s' % ckan_ip, apikey=api_key, user_agent=user_agent)

organisations_data = get_existing_organisations_dict()
organisations_names = get_existing_organisations_names(organisations_data)

# Process each row
for row in reader:
	add_organisation(row)

# Close
RemoteCKAN.close(ckan)
fp.close()

exit(0)
