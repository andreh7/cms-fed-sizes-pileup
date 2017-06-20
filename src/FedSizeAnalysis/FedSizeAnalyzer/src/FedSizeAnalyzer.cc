#include <memory>

#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/EDProducer.h"

#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"

#include "FWCore/ParameterSet/interface/ParameterSet.h"

#include <iostream>
#include <vector>


#include <DataFormats/FEDRawData/interface/FEDRawDataCollection.h>
#include <DataFormats/FEDRawData/interface/FEDNumbering.h>

#include <DataFormats/VertexReco/interface/Vertex.h>
#include <FedSizeAnalysis/FedSizeAnalysisData/interface/FedSizeAnalysisData.h>

#include <boost/foreach.hpp>

#include <iostream>

//----------------------------------------------------------------------


class FedSizeAnalyzer : public edm::EDProducer {
   public:
      explicit FedSizeAnalyzer(const edm::ParameterSet&);
      ~FedSizeAnalyzer();


   private:
      virtual void beginJob() ;
      virtual void produce(edm::Event&, const edm::EventSetup&);
      virtual void endJob() ;



  /** @return the list of 'good' primary vertices, as described in
      https://hypernews.cern.ch/HyperNews/CMS/get/recoTracking/1000/1.html
  */
  std::vector<const reco::Vertex *> findGoodPrimaryVertices(const std::vector<reco::Vertex> &primaryVertices);

  /** adds information about the given primary vertices */
  void addPrimaryVertices(edm::Event& iEvent, FedSizeAnalysisData &data, const std::vector<const reco::Vertex *> &primaryVertices);

  size_t maxNumVerticesSeen;
  
  /** token for the raw data */
  edm::EDGetTokenT<FEDRawDataCollection> rawDataSourceToken;

  edm::EDGetTokenT<reco::BeamSpot> beamSpotToken;

  edm::EDGetTokenT<std::vector<reco::Vertex> > primaryVerticesToken;

  bool useRECO;
};

//----------------------------------------------------------------------
FedSizeAnalyzer::FedSizeAnalyzer(const edm::ParameterSet& iConfig) : 
  maxNumVerticesSeen(0)
{
   produces<FedSizeAnalysisData>();

   rawDataSourceToken = consumes<FEDRawDataCollection>(iConfig.getParameter<edm::InputTag>("rawDataSource"));

   beamSpotToken = consumes<reco::BeamSpot>(edm::InputTag("offlineBeamSpot"));

   // see https://hypernews.cern.ch/HyperNews/CMS/get/recoTracking/1000/1.html
   
   // used to work for RECO files
   // primaryVerticesToken = consumes<std::vector<reco::Vertex> >(edm::InputTag("offlinePrimaryVertices"));
   // using this for MINIAOD
   primaryVerticesToken = consumes<std::vector<reco::Vertex> >(edm::InputTag("offlineSlimmedPrimaryVertices"));

   useRECO = iConfig.getUntrackedParameter<bool>("useRECO", true);

   

//   //if do put with a label
//   produces<ExampleData2>("label");o
}

//----------------------------------------------------------------------

FedSizeAnalyzer::~FedSizeAnalyzer()
{
 
   // do anything here that needs to be done at desctruction time
   // (e.g. close files, deallocate resources etc.)

}

//----------------------------------------------------------------------

std::vector<const reco::Vertex *>
FedSizeAnalyzer::findGoodPrimaryVertices(const std::vector<reco::Vertex> &primaryVertices)
{
  std::vector<const reco::Vertex *> retval;

  // see https://hypernews.cern.ch/HyperNews/CMS/get/recoTracking/1000/1.html
  // for how to count the number of vertices

  BOOST_FOREACH(const reco::Vertex &vtx, primaryVertices)
  {
    // 1)
    if (vtx.isFake())
      continue;

    // 2)
    if (vtx.ndof() <= 4.0001)
      continue;

    // 3)
    if (vtx.position().rho() >= 2 ||
	fabs(vtx.z()) >= 24)
	continue;
    
    retval.push_back(&vtx);

  } // loop over all vertices

  return retval;
}



//----------------------------------------------------------------------

// #include "DataFormats/GeometryVector/interface/GlobalPoint.h"
void 
FedSizeAnalyzer::addPrimaryVertices(edm::Event& iEvent, FedSizeAnalysisData &data, const std::vector<const reco::Vertex *> &primaryVertices)
{
  // get the beam spot 
  // (see https://twiki.cern.ch/twiki/bin/view/CMSPublic/SWGuideFindingBeamSpot#Access_to_the_beam_spot_data )
  reco::BeamSpot beamSpot;
  edm::Handle<reco::BeamSpot> beamSpotHandle;
  iEvent.getByToken(beamSpotToken, beamSpotHandle);
  
  if ( beamSpotHandle.isValid() )
    beamSpot = *beamSpotHandle;
  else
    // leave beamspot as it is (at 0,0,0 ?)
    edm::LogInfo("FedSizeAnalyzer") << "No beam spot available from EventSetup\n";
  
  // typically 20 um in both directions
  // std::cout << "beam width: x: " << beamSpot.BeamWidthX() << " y:" << beamSpot.BeamWidthY() << std::endl;

  //--------------------
  // subtract the beamspot from all given primary vertices
  // and calculate the distance in the plane transverse to 
  // the beam
  BOOST_FOREACH(const reco::Vertex *vtx, primaryVertices)
  {
    math::XYZVectorD dist = vtx->position() - beamSpot.position();

    data.primaryVerticesRho.push_back(dist.rho());
    data.primaryVerticesZ.push_back(dist.z());
  } // loop over all vertices

}


//----------------------------------------------------------------------

void
FedSizeAnalyzer::produce(edm::Event& iEvent, const edm::EventSetup& iSetup)
{
   using namespace edm;

  // std::cout << "event" << std::endl;

  // get FED raw data
  Handle< FEDRawDataCollection> fedRawData;
  // FEDRawDataCollection                  "rawDataCollector"          ""                "LHC"     

  iEvent.getByToken(rawDataSourceToken,fedRawData);

  // get primary vertex information
  Handle<std::vector<reco::Vertex> > primaryVertices;

  // see https://hypernews.cern.ch/HyperNews/CMS/get/recoTracking/1000/1.html
  iEvent.getByToken(primaryVerticesToken,primaryVertices);

  // create the output data
  FedSizeAnalysisData *data = new FedSizeAnalysisData();

  if (useRECO)
  {
    std::vector<const reco::Vertex *> goodPrimaryVertices = findGoodPrimaryVertices(*primaryVertices);
    data->setNumPrimaryVertices(goodPrimaryVertices.size());
    maxNumVerticesSeen = std::max(maxNumVerticesSeen, goodPrimaryVertices.size());

    addPrimaryVertices(iEvent,*data, goodPrimaryVertices);
  }
  else
    data->setNumPrimaryVertices(-1);

  //----------------------------------------
  // find the largest transverse distance from the beam spot 
  // of these primary vertices
  

  //----------------------------------------

  // set event time
  Timestamp ts = iEvent.eventAuxiliary().time();
  data->setEventTime(ts.unixTime());

  // get list of FEDs for this event
  // see also DataFormats/FEDRawData/test/DumpFEDRawDataProduct.cc

  for (int fedId = 0; fedId<=FEDNumbering::lastFEDId(); ++fedId)
  {
    const FEDRawData& fed_data = fedRawData->FEDData(fedId);
    size_t size=fed_data.size();
    if (size == 0)
      continue;

    data->addFedSize(fedId, size);

    // std::cout << "FED " << fedId << ": size=" << size << std::endl;

  } // loop over all possible fed numbers


  // std::cout << "number of primary vertices: " << primaryVertices->size() << std::endl;
  
  //--------------------
  // output product
  //--------------------

  std::auto_ptr<FedSizeAnalysisData> pOut(data);
  iEvent.put(pOut);

 
}

//----------------------------------------------------------------------
void 
FedSizeAnalyzer::beginJob()
{
}

//----------------------------------------------------------------------

void 
FedSizeAnalyzer::endJob() 
{
  // print the maximum number of reconstructed
  // vertices found (needed in the next step
  // of the analysis)
  std::cout << "maximum number of vertices seen: " << maxNumVerticesSeen << std::endl;
}

//----------------------------------------------------------------------

//define this as a plug-in
DEFINE_FWK_MODULE(FedSizeAnalyzer);
