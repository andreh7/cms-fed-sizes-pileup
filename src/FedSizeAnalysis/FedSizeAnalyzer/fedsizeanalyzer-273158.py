
# good_lumi_section_json_file is the list of 'good lumisections' to be
# used for filtering.
#
# set this to None if you don't want to apply any filtering
# (e.g. when running on the express stream)
#--------------------

# see https://hypernews.cern.ch/HyperNews/CMS/get/physics-validation/2648/1/1.html
#good_lumi_section_json_file = "/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions16/13TeV/Cert_271036-273450_13TeV_PromptReco_Collisions16_JSON_NoL1T.txt"

good_lumi_section_json_file = "Cert_271036-273450_13TeV_PromptReco_Collisions16_JSON_NoL1T.txt"

#--------------------

# set this to a positive number if you want
# to restrict running to less than the maximum
# number of events (useful for testing)
maxEvents = -1

# set this here to keep additional products
keepProducts = []

keepL1MenuInformation = True


# useRECO = False
