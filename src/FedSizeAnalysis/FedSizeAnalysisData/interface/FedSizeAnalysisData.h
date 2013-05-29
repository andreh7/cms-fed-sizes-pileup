#ifndef FedSizeAnalysisData_h
#define FedSizeAnalysisData_h

#include <vector>
#include <map>

class FedSizeAnalysisData
{
protected:
  int numPrimaryVertices;

  /** maps from FED id to size */
  std::map<int, int> fedIdToSize;

  int getSumFedSizes(std::vector<int> fedids) const;

  int eventTime;

  /** selected primary vertices with beam spot position
      subtracted */
public:
  /** for the moment, just store the distance in the plane
      transverse to the beam for each accpeted vertex */
  std::vector<double> primaryVerticesRho;

  /** same as primaryVerticesRho but for the z component */
  std::vector<double> primaryVerticesZ;

public:

  void setNumPrimaryVertices(int num_vertices);

  int getNumPrimaryVertices() const;

  void addFedSize(int fedid, int size);

  int getSumAllFedSizes() const;

  /** return the number of FEDs found in this event */
  int getNumFeds() const;

//  /** returns the ith fed in the list where index must be
//      in the range 0..getNumFeds()-1. This is useful
//      for looping over all FEDs in the current event */
//  int getFedIdByIndex(int index);

  /** returns a list of all FEDids */
  std::vector<int> getFedIds() const;

  /** meant for interactive analysis */
  int getSumSubsystemFedSizes(int subsystem) const;
  
  /** size of an individual FED */
  int getFedSize(int fed) const;

  void setEventTime(int time);

  int getEventTime() const;

};


#endif
