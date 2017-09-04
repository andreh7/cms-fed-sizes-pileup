#ifndef FedSizeAnalysis_FedSizeAnalyzer_BrilCalcReader_h
#define FedSizeAnalysis_FedSizeAnalyzer_BrilCalcReader_h

#include <string>
#include <unordered_map>

/** class to read the output of 

     brilcalc lumi -r 283171 --normtag pccLUM17001pre6(or5) --xing -u hz/ub --output-style csv

   and allowing to access the per BX instantaneous luminosity for each lumi section
*/
class BrilCalcReader {

 protected:
  /** first key is run, second key is lumi section, third key is bunch crossing */
  std::unordered_map<int,
    std::unordered_map<int, 
    std::unordered_map<int,
    double>>> data;

 public:
  /** adds the given file to the data */
  void addFile(const std::string &csvFname);

  /** @return the per bunch crossing luminosity in hz/ub = 10^30 cm^-2s^-1.
      Returns -1 if no entry for the given run, lumi section and bunch crossing was found 
  */
  inline double getLumi(int run, int lumiSection, int bx) {
    auto it1 = data.find(run);
    if (it1 != data.end()) {
      auto it2 = it1->second.find(lumiSection);
      if (it2 != it1->second.end()) {
        auto it3 = it2->second.find(bx);
        if (it3 != it2->second.end()) {
          return it3->second;
        }
      }
    }

    // not found
    return -1;
  }


};


#endif
