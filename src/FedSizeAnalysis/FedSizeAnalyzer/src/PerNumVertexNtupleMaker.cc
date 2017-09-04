#include <memory>

#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/EDAnalyzer.h"

#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"

#include "FWCore/ParameterSet/interface/ParameterSet.h"

#include <iostream>
#include <vector>
#include <map>


#include <DataFormats/FEDRawData/interface/FEDRawDataCollection.h>
#include <DataFormats/FEDRawData/interface/FEDNumbering.h>

#include <DataFormats/VertexReco/interface/Vertex.h>
#include <FedSizeAnalysis/FedSizeAnalysisData/interface/FedSizeAnalysisData.h>

#include "FWCore/Framework/interface/LuminosityBlock.h"
#include "DataFormats/Luminosity/interface/LumiDetails.h"

#include "FedSizeAnalysis/FedSizeAnalyzer/interface/BrilCalcReader.h"

//--------------------
// for TFileService 

#include "FWCore/ServiceRegistry/interface/Service.h"
#include "CommonTools/UtilAlgos/interface/TFileService.h"

//--------------------
// ROOT
//--------------------
#include <TNtuple.h>
#include <TTree.h>
#include <TObjString.h>

//--------------------

#include <boost/foreach.hpp>
#include <boost/format.hpp>
#include <boost/algorithm/string.hpp>
#include <boost/algorithm/string/join.hpp>
#include <boost/lexical_cast.hpp>
//----------------------------------------------------------------------

/** takes FedSizeAnalysisData objects and produces 
    ntuples (one per number of vertices) with detailed 
    information about the size of the fragments in each fed */
class PerNumVertexNtupleMaker : public edm::EDAnalyzer 
{
   public:
      explicit PerNumVertexNtupleMaker(const edm::ParameterSet&);
      ~PerNumVertexNtupleMaker();

   private:
      virtual void beginJob();
      virtual void analyze(const edm::Event&, const edm::EventSetup&);
      virtual void endJob();

      virtual void beginLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&);


  /** currently, running over more than one run is not really
      supported. In the future we could at least check that
      the set of FEDs of subsequent runs is the same as for the
      first run. */
  virtual void beginRun(const edm::Run &run, const edm::EventSetup &es);

  void initializeFedIDranges();

  /** given a FEDid, returns the FED group names (e.g. subsystem) this FEDid 
      belongs to */
  std::vector<std::string> fedToFedGroupNames(unsigned fedID);

  //--------------------
  // config parameters
  //--------------------

  /** the input tag where the FedSizeAnalysisData objects should be taken from */
  edm::EDGetTokenT<FedSizeAnalysisData> sourceToken;

  edm::EDGetTokenT<LumiDetails> lumiDetailsToken;

  // see https://twiki.cern.ch/twiki/bin/view/CMS/LumiCalc#LumiDetails
  edm::Handle<LumiDetails> lumiDetails;


  /** all FedIDs to look at
      TODO: do we actually need this ? If we used a TTree instead, we could
      declare the fields in the first event.
 */
  std::vector<unsigned int> fedIDs;

  unsigned maxNumVertices;

  //--------------------

  bool isFirstRun;

  bool isFirstEventInRun;

  // (optional) name of .csv file containing detailed ber bunch crossing
  // and lumi section instantaneous luminosity. If this is the empty
  // string (defualt if parameter not given in the configuration file)
  // the instantaneous luminosity will be returned as -1 by getLumi().
  const std::string lumiFname;
  
  BrilCalcReader brilCalcReader;

  //----------

  /** index of the 'number of vertices' variable inside outputBuffer */
  unsigned numVerticesVarPosInNtuple;

  unsigned varPosBunchCrossing;
  unsigned varPosPerBXLumi;

  //----------

  /** maps from the FEDid to the position of the corresponding
      variable in the output tuple. */
  int fedIDsSubstemVariablePosInNtuple[FEDNumbering::MAXFEDID+1];

  /** to how many subsystems sums a FED can contribute to.
      An example is: a fed can belong to Pixel and BPIX at the same time. */
  static const size_t MAX_NUM_SUBSYSTEMS_PER_FED = 3;

  /** the position of the variable containing the SUM
      of the subsystem given the nth fed (index
      in fedIDs).

      Note that this implicitly assumes that each fed is only
      part of one group (e.g. we can't have a group 
      Pixel and groups BPIX and FPIX in parallel)

      To get the position in the output ntuple,
      add the value of firstSubsystemSumVariablePos.

      The second index is a index for allowing a FED to contribute
      to multiple subsystems/groups (e.g. Pixel and BPIX). 
  */
  int fedIDsSubstemSumVariableIndex[FEDNumbering::MAXFEDID+1][MAX_NUM_SUBSYSTEMS_PER_FED];

  /** position of the first 'sum of subsystems' variable
      in the output ntuple */
  unsigned firstSubsystemSumVariablePos;

  /** information about a range of FEDids */
  class FedIdRangeData
  {
  public:
    unsigned first, last;
    std::string subsysLabel;

    FedIdRangeData(unsigned first_, unsigned last_, const std::string &subsysLabel_) :
      first(first_),
      last(last_),
      subsysLabel(subsysLabel_)
    {
    }
  };

  /** ranges of FedIDs */
  std::vector<FedIdRangeData> fedIDRanges;

  /** maps from number of reconstructed vertices to
      the corresponding TNtuple.
  */
  std::vector<TNtuple *> outputTuples;

  /** maps from number of reconstructed vertices ( = index
      of output tuple) to the buffer containing the data
      to be written out. */
  std::vector<Float_t *> outputTupleBuffers;

  /** number of variables in each output buffer */
  unsigned numVars;

  /** subsystem sums as integers */
  unsigned *subsystemIntegerSums;
  
  /** number of distinct subsystems found */
  unsigned numSubsytems;

  /** variable position in the output buffer of the 'total event size' 
      variable */
  unsigned totalSizeVarPos;

  /** variable position in the output buffer of the 'minimum/maximum fragment size' 
      variable */
  unsigned minSizeVarPos;
  unsigned maxSizeVarPos;

  //--------------------
  // stuff for the 'small tuple'
  //--------------------
  TNtuple *smallTuple;

  Float_t smallTupleBuffer[6];

  //--------------------
  // number of FEDs per subsystem tree
  //--------------------
  /** maps from a named group of FEDs (typcially a subsystem but can be overlapping with
      other groups) to the number of FEDs found for this subsystem. This is determined
      on the first event, assuming that there are no FEDs taken out or brought
      in during the run (which is true by convention as far as I understood).

      At the end of the job, this is written to a special tuple in the output file.
  */
  std::map<std::string, unsigned> fedGroupToNumFeds;

  //--------------------
  // variables for number of feds per fed group / subsystem
  //
  // we actually could declare these buffers just inside endJob(..)
  // (where the tree is filled) but then we would have to make
  // sure that they are not on the stack, otherwise we might risk
  // that something could crash..
  //--------------------
  TTree *fedGroupSizeTree;

  TObjString *fedGroupSizeTreeName;
  Int_t fedGroupSizeTreeGroupSize;

protected:
  void fillBx(const edm::Event& iEvent, Float_t *outputBuffer);

  void fillLumi(const edm::Event& iEvent, Float_t *outputBuffer);

  /** returns the per-bunch crossing lumiosity for the given event's bunch crossing */
  double getLumi(const edm::Event& iEvent);
};

//----------------------------------------------------------------------
PerNumVertexNtupleMaker::PerNumVertexNtupleMaker(const edm::ParameterSet& iConfig) : 
  isFirstRun(true),

  // we could use edm::FileInPath but we do not want to restrict the
  // file location to within the CMSSW area
  lumiFname(iConfig.getUntrackedParameter<std::string>("lumiFile"))
{
  maxNumVertices = iConfig.getUntrackedParameter<unsigned>("maxNumVertices");
  sourceToken = consumes<FedSizeAnalysisData>(iConfig.getUntrackedParameter<edm::InputTag>("src"));
  lumiDetailsToken = consumes<LumiDetails, edm::InLumi>(edm::InputTag("lumiProducer"));

  if (! lumiFname.empty()) {
    brilCalcReader.addFile(lumiFname);
  }

  for (unsigned i = 0; i <= FEDNumbering::MAXFEDID; ++i)
  {
    fedIDsSubstemVariablePosInNtuple[i] = -1;

    for (unsigned j = 0; j < MAX_NUM_SUBSYSTEMS_PER_FED; ++j)
      fedIDsSubstemSumVariableIndex[i][j] = -1;
  }

  // produce the names of the output variables
  // note that -- contrary to doing this in the python
  // script before this analyzer -- we can NOT look at the
  // first event to get the ids of the FEDs, we need an additional
  // step to determine this
  fedIDs = iConfig.getUntrackedParameter<std::vector<unsigned int> >("fedIDs");  

  // create the names of the variables in the output ntuples
  std::vector<std::string> varnames;

  // number of reconstructed vertices (after some quality cuts)
  // in the event
  numVerticesVarPosInNtuple = varnames.size();
  varnames.push_back("num_vertices");

  // bunch crossing number
  varPosBunchCrossing = varnames.size();
  varnames.push_back("bx");

  // per bunch crossing delivered instantaneous luminosity
  varPosPerBXLumi = varnames.size();
  varnames.push_back("per_bx_lumi");

  unsigned var_pos = varnames.size();

  BOOST_FOREACH(unsigned fedid, fedIDs)
  {
    if (fedid >= FEDNumbering::MAXFEDID + 1)
      throw cms::Exception(boost::str(boost::format("fedid %d is out of range") % fedid));

    varnames.push_back(boost::str(boost::format("size%03d") % fedid));
    fedIDsSubstemVariablePosInNtuple[fedid] = var_pos;

    ++var_pos;
  } // loop over fedids

  //--------------------
  // add per subdetector sums
  //--------------------

  initializeFedIDranges();

  firstSubsystemSumVariablePos = varnames.size();

  // for the moment, we just create ntuples for
  // ALL fed id ranges, even if in the list
  // of feds given to analyze there aren't
  // any feds in some ranges

  // maps from subsystem name to index of the
  // subsystem
  std::map<std::string, unsigned> subsysToSumVariableIndex;

  BOOST_FOREACH(FedIdRangeData range, fedIDRanges)
  {
    std::string label = boost::to_lower_copy(range.subsysLabel);

    // we could actually use lower_bound here instead of find, see http://stackoverflow.com/questions/97050
    std::map<std::string, unsigned>::const_iterator it = subsysToSumVariableIndex.find(label);
    
    // fill a map fedId -> position of the variable for the sum of this subsystem
    unsigned subsysIndex;

    if (it == subsysToSumVariableIndex.end())
      // subsystem not yet encountered before
      {
	subsysIndex = subsysToSumVariableIndex.size();

	subsysToSumVariableIndex[label] = subsysIndex;
	varnames.push_back("size_" + label);
      }
    else
      // subsystem with this name (but a different range)
      // seen before
      subsysIndex = it->second;

    for (unsigned fed = range.first; fed <= range.last; ++fed)
      {      
	// find the first unused index
	unsigned k;
	for (k = 0; k < MAX_NUM_SUBSYSTEMS_PER_FED; ++k)
	  {
	    if (fedIDsSubstemSumVariableIndex[fed][k] == -1) 
	      {
		fedIDsSubstemSumVariableIndex[fed][k] = subsysIndex;
		break;
	      }
	  }

	if (k == MAX_NUM_SUBSYSTEMS_PER_FED)
	  throw std::runtime_error("too many groups (more than " + boost::lexical_cast<std::string>(MAX_NUM_SUBSYSTEMS_PER_FED) + 
				   " for fed " + boost::lexical_cast<std::string>(fed));

      } // loop over all Feds in the range
  } // loop over all FED id ranges

  numSubsytems = subsysToSumVariableIndex.size();
  subsystemIntegerSums = new unsigned[numSubsytems];

  //--------------------
  // add total size of event
  // (sum of all FEDs)
  //--------------------
  
  totalSizeVarPos = varnames.size();
  varnames.push_back("size_total");

  // minimum and maximum size fed
  minSizeVarPos = varnames.size(); varnames.push_back("size_min");
  maxSizeVarPos = varnames.size(); varnames.push_back("size_max");

  //--------------------
  // see https://twiki.cern.ch/twiki/bin/view/CMSPublic/SWGuideTFileService
  // for instructions how to use the TFileService.
  // It looks like we can only have one output file so
  // we store multiple ntuples in one output file
  // (maybe one could have multiple TFileService instances
  // with different labels ? but it is not obvious how to
  // do this from the above twiki page and we would need
  // to know the maximum number of vertices before running
  // cmsRun).
  edm::Service<TFileService> fs;

  // book the output ntuples
  numVars = varnames.size();
  for (unsigned numVertices = 0; numVertices <= maxNumVertices; ++numVertices)
    {
      std::string tupleName = boost::str(boost::format("all_sizes_%dvtx") % numVertices);
      
      outputTuples.push_back(fs->make<TNtuple>(tupleName.c_str()  , tupleName.c_str(), 
					       boost::algorithm::join(varnames, ":").c_str()));

      // allocate the output buffer for this tuple
      outputTupleBuffers.push_back(new Float_t[numVars]);
    }

  //--------------------
  // 'small tuple'
  //--------------------

  smallTuple = fs->make<TNtuple>("small_tuple", "small_tuple",
				 "num_vertices:"
				 "total_event_size:"
				 "lumisection:"
				 "event:"
				 "bx:"
				 "per_bx_lumi"
				 );


  //--------------------
  // number of FEDs per subsystem tree
  //--------------------
  fedGroupSizeTree = fs->make<TTree>("fedGroupSize","fedGroupSize");

  // fedGroupSizeTreeGroupNames = new TClonesArray("TObjString",fedIDRanges.size());
  // fedGroupSizeTree->Branch("groupName", "TClonesArray", &fedGroupSizeTreeGroupNames);

  fedGroupSizeTreeName = new TObjString();
  fedGroupSizeTree->Branch("groupName", "TObjString", &fedGroupSizeTreeName);

  fedGroupSizeTree->Branch("groupSize", &fedGroupSizeTreeGroupSize, "groupSize/I");
}

//----------------------------------------------------------------------

PerNumVertexNtupleMaker::~PerNumVertexNtupleMaker()
{

}

//----------------------------------------------------------------------
#include "FWCore/Framework/interface/Run.h"

void 
PerNumVertexNtupleMaker::beginRun(const edm::Run &run, const edm::EventSetup &es)
{
  if (! isFirstRun)
    throw std::runtime_error("currently, running over more than one run is not supported");

  isFirstRun = false;

  isFirstEventInRun = true;
}

//----------------------------------------------------------------------

/** basically relying on DataFormats/FEDRawData/interface/FEDNumbering.h */
void PerNumVertexNtupleMaker::initializeFedIDranges()
{
  assert(fedIDRanges.size() == 0);

  fedIDRanges.push_back(FedIdRangeData(FEDNumbering::MINSiPixelFEDID                        ,  FEDNumbering::MAXSiPixelFEDID 		        , "Pixel"));

  // distinguish between BPIX and FPIX (requested on 2011-06-07)
  // determined on 2011-07-07 by looking at http://cmsdaqweb.cms/local/daqview/cdaq/DAQ_ru.html
  // and verified with the runsummary page of run 166161 that the number of BPIX and FPIX
  // FEDs is 32 and 8 respectively.
  fedIDRanges.push_back(FedIdRangeData(0                                                    ,  31                                               , "BPIX"));
  fedIDRanges.push_back(FedIdRangeData(32                                                   ,  39                                               , "FPIX"));

  // special group: HF only (718, 719, 720, 721, 722, 723), taken from DAQ_ru.html
  fedIDRanges.push_back(FedIdRangeData(718                                                  ,  723                                              , "HF"));

  // added 2013-05: HBHE (700..717) and HO (724..731)
  fedIDRanges.push_back(FedIdRangeData(700                                                  ,  717                                              , "HBHE"));
  fedIDRanges.push_back(FedIdRangeData(724                                                  ,  731                                              , "HO"));


  fedIDRanges.push_back(FedIdRangeData(FEDNumbering::MINSiStripFEDID 		            ,  FEDNumbering::MAXSiStripFEDID 		  	, "Tracker"));
  fedIDRanges.push_back(FedIdRangeData(FEDNumbering::MINPreShowerFEDID                      ,  FEDNumbering::MAXPreShowerFEDID 		        , "Preshower"));  
  fedIDRanges.push_back(FedIdRangeData(FEDNumbering::MINECALFEDID 			    ,  FEDNumbering::MAXECALFEDID 			, "ECAL"));  
  fedIDRanges.push_back(FedIdRangeData(FEDNumbering::MINCASTORFEDID 			    ,  FEDNumbering::MAXCASTORFEDID 			, "CASTOR"));  
  fedIDRanges.push_back(FedIdRangeData(FEDNumbering::MINHCALFEDID 			    ,  FEDNumbering::MAXHCALFEDID 			, "HCAL"));  
  fedIDRanges.push_back(FedIdRangeData(FEDNumbering::MINLUMISCALERSFEDID 		    ,  FEDNumbering::MAXLUMISCALERSFEDID 		, "LumiScalers"));  
  fedIDRanges.push_back(FedIdRangeData(FEDNumbering::MINCSCFEDID 			    ,  FEDNumbering::MAXCSCFEDID 			, "CSC"));  
  fedIDRanges.push_back(FedIdRangeData(FEDNumbering::MINCSCTFFEDID 			    ,  FEDNumbering::MAXCSCTFFEDID 			, "CSCTF"));  
  fedIDRanges.push_back(FedIdRangeData(FEDNumbering::MINDTFEDID 			    ,  FEDNumbering::MAXDTFEDID 			, "DT"));  
  fedIDRanges.push_back(FedIdRangeData(FEDNumbering::MINDTTFFEDID 			    ,  FEDNumbering::MAXDTTFFEDID 			, "DTTF"));  
  fedIDRanges.push_back(FedIdRangeData(FEDNumbering::MINRPCFEDID 			    ,  FEDNumbering::MAXRPCFEDID 			, "RPC"));  
  fedIDRanges.push_back(FedIdRangeData(FEDNumbering::MINTriggerGTPFEDID 		    ,  FEDNumbering::MAXTriggerGTPFEDID 		, "GlobalTrigger"));  
  fedIDRanges.push_back(FedIdRangeData(FEDNumbering::MINTriggerEGTPFEDID 		    ,  FEDNumbering::MAXTriggerEGTPFEDID 		, "GlobalTrigger"));  
  fedIDRanges.push_back(FedIdRangeData(FEDNumbering::MINTriggerGCTFEDID 		    ,  FEDNumbering::MAXTriggerGCTFEDID 		, "GCT"));  
  
  // Ignore LTCs (there shouldn't be any). Note also that 
  //  MAXTriggerEGTPFEDID ==  MINTriggerLTCmtccFEDID (i.e. the ranges overlap)
  // which could cause problems
  //fedIDRanges.push_back(FedIdRangeData(MINTriggerLTCFEDID 		    ,  MAXTriggerLTCFEDID 		, ""));  
  //fedIDRanges.push_back(FedIdRangeData(MINTriggerLTCmtccFEDID 		    ,  MAXTriggerLTCmtccFEDID 		, ""));  
  //fedIDRanges.push_back(FedIdRangeData(MINTriggerLTCTriggerFEDID            ,  MAXTriggerLTCTriggerFEDID 	, ""));  
  //fedIDRanges.push_back(FedIdRangeData(MINTriggerLTCHCALFEDID 		    ,  MAXTriggerLTCHCALFEDID 		, ""));  
  //fedIDRanges.push_back(FedIdRangeData(MINTriggerLTCSiStripFEDID 	    ,  MAXTriggerLTCSiStripFEDID 	, ""));  
  //fedIDRanges.push_back(FedIdRangeData(MINTriggerLTCECALFEDID 		    ,  MAXTriggerLTCECALFEDID 		, ""));  
  //fedIDRanges.push_back(FedIdRangeData(MINTriggerLTCTotemCastorFEDID 	    ,  MAXTriggerLTCTotemCastorFEDID 	, ""));  
  //fedIDRanges.push_back(FedIdRangeData(MINTriggerLTCRPCFEDID 		    ,  MAXTriggerLTCRPCFEDID 		, ""));  
  //fedIDRanges.push_back(FedIdRangeData(MINTriggerLTCCSCFEDID 		    ,  MAXTriggerLTCCSCFEDID 		, ""));  
  //fedIDRanges.push_back(FedIdRangeData(MINTriggerLTCDTFEDID 		    ,  MAXTriggerLTCDTFEDID 		, ""));  
  //fedIDRanges.push_back(FedIdRangeData(MINTriggerLTCSiPixelFEDID            ,  MAXTriggerLTCSiPixelFEDID 	, ""));  
  fedIDRanges.push_back(FedIdRangeData(FEDNumbering::MINCSCDDUFEDID 			    ,  FEDNumbering::MAXCSCDDUFEDID 			, "CSC"));  
  fedIDRanges.push_back(FedIdRangeData(FEDNumbering::MINCSCContingencyFEDID 		    ,  FEDNumbering::MAXCSCContingencyFEDID 		, "CSC"));  
  fedIDRanges.push_back(FedIdRangeData(FEDNumbering::MINCSCTFSPFEDID 		            ,  FEDNumbering::MAXCSCTFSPFEDID 		  	, "CSCTF"));
  fedIDRanges.push_back(FedIdRangeData(FEDNumbering::MINDAQeFEDFEDID 		            ,  FEDNumbering::MAXDAQeFEDFEDID 		  	, "DAQ"));
  fedIDRanges.push_back(FedIdRangeData(FEDNumbering::MINDAQmFEDFEDID 		            ,  FEDNumbering::MAXDAQmFEDFEDID                  , "DAQ"));
}

//----------------------------------------------------------------------

void
PerNumVertexNtupleMaker::analyze(const edm::Event& iEvent, const edm::EventSetup& iSetup)
{
  using namespace edm;

  // std::cout << "event" << std::endl;

  // get the input data
  Handle<FedSizeAnalysisData> sizeData;
  iEvent.getByToken(sourceToken,sizeData);
  
  // find out how many vertices there were
  int numVertices = sizeData->getNumPrimaryVertices();
  assert(numVertices >= 0);
  
  if ((unsigned)numVertices > maxNumVertices)
    {
      edm::LogWarning("PerNumVertexNtupleMaker") << "event found with " << numVertices << " vertices which exceeds the maximum number of vertices " << maxNumVertices << ". Assigning to " << maxNumVertices << ".";
      numVertices = maxNumVertices;
    }
  else if ((unsigned)numVertices == maxNumVertices)
    {
      // print run/ls/event number for events with highest 
      // number of vertices
      std::cout << "found event with maximum number of vertices (" << numVertices << "): run/ls/event=" 
                << iEvent.run() << "/" 
                << iEvent.luminosityBlock() << "/" 
                << iEvent.id().event() << std::endl;
    }
  // get the corresponding output buffer
  Float_t *outputBuffer = outputTupleBuffers[(unsigned) numVertices];

  // clear it (see http://stackoverflow.com/questions/877385)
  std::fill_n(outputBuffer, numVars, 0);
  // potentially faster:
  // memset(outputBuffer, 0, sizeof(float) * numVars);

  //--------------------

  fillBx(iEvent, outputBuffer);
  fillLumi(iEvent, outputBuffer);

  // first variable is the number of vertices
  // (note that we use the actual number here even
  // if there was an overflow, i.e. the current
  // event has a number of vertices higher than
  // the maximum we were given)
  outputBuffer[numVerticesVarPosInNtuple] = sizeData->getNumPrimaryVertices();

  // fill individual feds and sums
  unsigned totalSize = 0;

  // minimum and maximum fed size in the event
  int minSize = 0;
  int maxSize = 0;

  // clear integer buffer for sums of subsystems
  std::fill_n(subsystemIntegerSums, numSubsytems, 0);

  //--------------------
  // sanity check: did we forget to include a FEDid in the configuration ?
  if (isFirstEventInRun)
  {
    std::vector<int> allFedsInThisEvent = sizeData->getFedIds();
    
    // bool isFirst = true;
    // std::ostringstream buf;
    // BOOST_FOREACH(int fed, allFedsInThisEvent)
    // {
    //   if (isFirst)
    //     isFirst = false;
    //   else
    //     buf << ", ";
    // 
    //   buf << fed;
    // }
    // 
    // edm::LogWarning("PerNumVertexNtupleMaker") << "found the following " << allFedsInThisEvent.size() << " FEDS in the first event:" << buf.str();
    
    BOOST_FOREACH(int fed, allFedsInThisEvent)
    {
      if (std::find(fedIDs.begin(), fedIDs.end(), fed) == fedIDs.end())
	edm::LogWarning("PerNumVertexNtupleMaker") << "fed " << fed << " found in event but excluded by configuration";
    }
  }

  //--------------------


  bool isFirst = true;

  // loop over all feds
  BOOST_FOREACH(unsigned fedid, fedIDs)
  {
    // store the size of this fed in the output tuple  
    int thisSize = sizeData->getFedSize(fedid);
    outputBuffer[fedIDsSubstemVariablePosInNtuple[fedid]] = thisSize;

    // add to the total sum
    totalSize += thisSize;

    if (isFirst)
      {
	minSize = thisSize;
	maxSize = thisSize;

	isFirst = false;
      }
    else
      {
	minSize = std::min(minSize, thisSize);
	maxSize = std::max(maxSize, thisSize);
      }

    // first add the subsystem sizes as integers
    // convert to float later
    for (unsigned k = 0; k < MAX_NUM_SUBSYSTEMS_PER_FED; ++k)
      {
	int index = fedIDsSubstemSumVariableIndex[fedid][k];
	if (index != -1)
	  subsystemIntegerSums[(unsigned) index] += thisSize;
      }

    // count number of feds per subsystem on first event
    if (isFirstEventInRun)
      {
	std::vector<std::string> fedGroupNames = fedToFedGroupNames(fedid);

	// increase the number of members for each of the fed gorups/subsystems
	// this FED is member of
	BOOST_FOREACH(const std::string &groupName, fedGroupNames)
        {
	  std::map<std::string, unsigned>::iterator it = fedGroupToNumFeds.find(groupName);
	  if (it == fedGroupToNumFeds.end())
	    // first FED for this group
	    fedGroupToNumFeds[groupName] = 1;
	  else  
	    ++(it->second);
	}
      } // if this is the first event in the run

  } // loop over all FEDids

  // copy the integer subsystem sums to the output buffer
  for (unsigned i = 0; i < numSubsytems; ++i)
    outputBuffer[firstSubsystemSumVariablePos + i] = subsystemIntegerSums[i];

  // store the total event size
  outputBuffer[totalSizeVarPos] = totalSize;

  // store the minimum and maximum fragment size
  outputBuffer[minSizeVarPos] = minSize;
  outputBuffer[maxSizeVarPos] = maxSize;

  // add the event to the corresponding output tuple  
  outputTuples[numVertices]->Fill(outputBuffer);

  //----------------------------------------
  // fill the 'small tuple'
  //----------------------------------------

  smallTupleBuffer[0] = sizeData->getNumPrimaryVertices();
  smallTupleBuffer[1] = sizeData->getSumAllFedSizes();
  smallTupleBuffer[2] = iEvent.eventAuxiliary().luminosityBlock();
  smallTupleBuffer[3] = iEvent.eventAuxiliary().event();
  smallTupleBuffer[4] = iEvent.bunchCrossing();
  smallTupleBuffer[5] = getLumi(iEvent);


  smallTuple->Fill(smallTupleBuffer);

  isFirstEventInRun = false;
}

//----------------------------------------------------------------------
void 
PerNumVertexNtupleMaker::beginJob()
{
}

//----------------------------------------------------------------------

void 
PerNumVertexNtupleMaker::endJob() 
{
  for (std::map<std::string, unsigned>::const_iterator it = fedGroupToNumFeds.begin();
       it != fedGroupToNumFeds.end();
       ++it)
    {
      fedGroupSizeTreeName->SetString(it->first.c_str());
      fedGroupSizeTreeGroupSize = it->second;
      fedGroupSizeTree->Fill();
    }
}

//----------------------------------------------------------------------

std::vector<std::string> 
PerNumVertexNtupleMaker::fedToFedGroupNames(unsigned fedID)
{
  std::vector<std::string> retval;

  BOOST_FOREACH(FedIdRangeData range, fedIDRanges)
  {
    if (fedID >= range.first && fedID <= range.last)
      retval.push_back(range.subsysLabel);
  } // loop over all ranges

  return retval;
}

//----------------------------------------------------------------------

void 
PerNumVertexNtupleMaker::fillBx(const edm::Event& iEvent, Float_t *outputBuffer)
{
  outputBuffer[varPosBunchCrossing] = iEvent.bunchCrossing();
}

//----------------------------------------------------------------------

void 
PerNumVertexNtupleMaker::fillLumi(const edm::Event& iEvent, Float_t *outputBuffer)
{
  // std::cout << "GOT LUMI " << outputBuffer[varPosPerBXLumi] << " FOR BX=" << iEvent.bunchCrossing() << std::endl;
  outputBuffer[varPosPerBXLumi] = getLumi(iEvent);
}

//----------------------------------------------------------------------

double 
PerNumVertexNtupleMaker::getLumi(const edm::Event& iEvent)
{
  // use the brilcalc reader instead for LHC Run II
  return brilCalcReader.getLumi(iEvent.run(), 
                                iEvent.luminosityBlock(),
                                iEvent.bunchCrossing());


  iEvent.getLuminosityBlock().getByToken(lumiDetailsToken, lumiDetails); 
  // lb.getByToken(lumiDetailsToken, lumiDetails); 

  // this luminosity should be in Hz/ubarn (i.e. 10^30 s^-1 cm^-2)
  if (! lumiDetails.isValid())  
    // object not available for some reason
    return -1;
  else
    {
      // this is what we used for LHC Run I
      // double value = lumiDetails->lumiValue(LumiDetails::kOCC1,iEvent.bunchCrossing()) * 6.37;

      // neither kOCC1, kOCC2 nor kPLT seem to work for LHC Run II (CMS run 273158)
      // double value = lumiDetails->lumiValue(LumiDetails::kPLT,iEvent.bunchCrossing()) * 6.37;
      // std::cout << "here2" << std::endl;
      // return value;
      return -1;
    }
}

//----------------------------------------------------------------------

void 
PerNumVertexNtupleMaker::beginLuminosityBlock(edm::LuminosityBlock const&lb, edm::EventSetup const&)
{
}

//----------------------------------------------------------------------
//define this as a plug-in
DEFINE_FWK_MODULE(PerNumVertexNtupleMaker);
