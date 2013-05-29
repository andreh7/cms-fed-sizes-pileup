#include "FedSizeAnalysis/FedSizeAnalysisData/interface/FedSizeAnalysisData.h"
#include "DataFormats/Common/interface/Wrapper.h"

#include <vector>

namespace
{
  struct dictionary
  {
    // APDSimData apd_sim_data;
    FedSizeAnalysisData data;
    edm::Wrapper<FedSizeAnalysisData> data_wrapper;
//    std::vector<APDSimData> apd_sim_data_vector;
//    edm::Wrapper<std::vector<APDSimData> > apd_sim_data_vector_wrapper;
//    edm::Ref<std::vector<PCaloHit> > v3;
//
//    PCaloHit v4;
//    std::vector<PCaloHit> v5;
//    edm::Wrapper<std::vector<PCaloHit> > v6;


  }; // struct
} // namespace
