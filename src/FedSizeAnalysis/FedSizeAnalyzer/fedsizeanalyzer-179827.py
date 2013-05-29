
# good_lumi_section_json_file is the list of 'good lumisections' to be
# used for filtering.
#
# set this to None if you don't want to apply any filtering
# (e.g. when running on the express stream)
#--------------------

# good_lumi_section_json_file = '/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions11/7TeV/Prompt/Cert_160404-167913_7TeV_PromptReco_Collisions11_JSON.txt'

# newest DCS only file (should be updated on a daily basis)

good_lumi_section_json_file = "/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions11/7TeV/DCSOnly/json_DCSONLY.txt"

# note that this does NOT contain e.g. run 179823 (high pileup fill 2)
# good_lumi_section_json_file = "/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions11/7TeV/Prompt/Cert_160404-180252_7TeV_PromptReco_Collisions11_JSON.txt"

# good_lumi_section_json_file = None

#--------------------

# set this to a positive number if you want
# to restrict running to less than the maximum
# number of events (useful for testing)
maxEvents = -1

# set this here to keep additional products
keepProducts = []

keepL1MenuInformation = True

