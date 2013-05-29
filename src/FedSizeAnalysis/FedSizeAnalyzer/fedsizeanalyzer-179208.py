
# good_lumi_section_json_file is the list of 'good lumisections' to be
# used for filtering.
#
# set this to None if you don't want to apply any filtering
# (e.g. when running on the express stream)
#--------------------

# run 179208 is not in the 'golden' JSON file
good_lumi_section_json_file = "/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions11/7TeV/DCSOnly/json_DCSONLY.txt"

#--------------------

# set this to a positive number if you want
# to restrict running to less than the maximum
# number of events (useful for testing)
maxEvents = -1

# set this here to keep additional products
keepProducts = []

keepL1MenuInformation = True

