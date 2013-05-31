#----------------------------------------------------------------------
# note that this file was NOT used to make the presentations
# in September 2011
#
# note also that the presentation in September 2011 used the
# dataset
#
#    /MinimumBias/Run2011B-PromptReco-v1/RECO
#
# while now this dataset does not exist any more and we use
#
#    /MinimumBias/Run2011B-PromptReco-v1/AOD (should not make a difference)
#
#----------------------------------------------------------------------

# good_lumi_section_json_file is the list of 'good lumisections' to be
# used for filtering.
#
# set this to None if you don't want to apply any filtering
# (e.g. when running on the express stream)
#--------------------

good_lumi_section_json_file = "/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions11/7TeV/Prompt/Cert_160404-180252_7TeV_PromptReco_Collisions11_JSON.txt"

#--------------------

# set this to a positive number if you want
# to restrict running to less than the maximum
# number of events (useful for testing)
maxEvents = -1

# set this here to keep additional products
keepProducts = []

keepL1MenuInformation = True


# useRECO = False

FEDRawDataCollectionModule = "source"
