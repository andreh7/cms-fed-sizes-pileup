#include <FedSizeAnalysis/FedSizeAnalysisData/interface/FedSizeAnalysisData.h>


//----------------------------------------------------------------------
int 
FedSizeAnalysisData::getSumFedSizes(std::vector<int> fedids) const
{
  int sum = 0;

  for (std::vector<int>::const_iterator it = fedids.begin();
       it != fedids.end();
       ++it)
    {
      std::map<int, int>::const_iterator it2 = fedIdToSize.find(*it);
      if (it2 != fedIdToSize.end())
        sum += it2->second;

    } // loop over the given fedids

  return sum;

}

//----------------------------------------------------------------------

void 
FedSizeAnalysisData::setNumPrimaryVertices(int num_vertices)
{
  numPrimaryVertices = num_vertices;
}

//----------------------------------------------------------------------

int 
FedSizeAnalysisData::getNumPrimaryVertices() const
{
  return numPrimaryVertices;
}

//----------------------------------------------------------------------

void 
FedSizeAnalysisData::addFedSize(int fedid, int size)
{
  fedIdToSize[fedid] = size;
}

//----------------------------------------------------------------------

int 
FedSizeAnalysisData::getSumAllFedSizes() const
{
  std::vector<int> all_feds;

  for (std::map<int,int>::const_iterator it = fedIdToSize.begin();
       it != fedIdToSize.end();
       ++it)
    {
      all_feds.push_back(it->first);
    }

  return getSumFedSizes(all_feds);

}

//----------------------------------------------------------------------
int 
FedSizeAnalysisData::getSumSubsystemFedSizes(int subsystem) const
{
  return 0;
}
  
//----------------------------------------------------------------------
int 
FedSizeAnalysisData::getNumFeds() const
{
  return fedIdToSize.size();
}
  
//----------------------------------------------------------------------

void 
FedSizeAnalysisData::setEventTime(int time)
{
  eventTime = time;
}

//----------------------------------------------------------------------

int 
FedSizeAnalysisData::getEventTime() const
{
  return eventTime;
}

//----------------------------------------------------------------------

int 
FedSizeAnalysisData::getFedSize(int fed) const
{
  std::map<int, int>::const_iterator it = fedIdToSize.find(fed);
  
  if (it == fedIdToSize.end())
    return 0;
  else
    return it->second;
  


}

//----------------------------------------------------------------------
std::vector<int> 
FedSizeAnalysisData::getFedIds() const
{
  std::vector<int> retval;

  for (std::map<int, int>::const_iterator it = fedIdToSize.begin();
       it != fedIdToSize.end();
       ++it)
    retval.push_back(it->first);

  return retval;
}

//----------------------------------------------------------------------
