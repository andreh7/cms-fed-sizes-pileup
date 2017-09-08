#include "FedSizeAnalysis/FedSizeAnalyzer/interface/BrilCalcReader.h"

#include <fstream>
#include <vector>

#include <boost/algorithm/string.hpp>
#include <boost/lexical_cast.hpp>

#include <iostream>

using namespace std;

void BrilCalcReader::addFile(const std::string &csvFname) {

  std::string line;
  ifstream infile(csvFname);
  unsigned lineNo = 0;

  while (getline(infile, line)) {
    lineNo++;


    if (lineNo == 1) {
      // ignore first line
      continue;
    }

    // note that some of the lines (but not all !) have a \r at the end...
    boost::trim(line);

    // second line is header: just insist that the format is as expected
    if (lineNo == 2) {
      assert(line == "#run:fill,ls,time,beamstatus,E(GeV),delivered(hz/ub),recorded(hz/ub),avgpu,source,[bxidx bxdelivered(hz/ub) bxrecorded(hz/ub)]");
      continue;
    }

    // third line or greater
    if (line == "") {
      // ignore empty lines
      continue;
    }

    if (line[0] == '#') {
      // commented line
      continue;
    }

    // ordinary line
    // expect the following columns:
    //   run:fill
    //   ls
    //   time
    //   beamstatus
    //   E(GeV)
    //   delivered(hz/ub)
    //   recorded(hz/ub)
    //   avgpu
    //   source
    //   [bxidx bxdelivered(hz/ub) bxrecorded(hz/ub)]
    vector<string> fields;
    boost::split(fields, line, boost::is_any_of(","));

    // split first column to get the run number
    vector<string> parts;
    boost::split(parts, fields[0], boost::is_any_of(":"));

    int run = boost::lexical_cast<int>(parts[0]);

    // fields[1] is typically ls:ls. We just take the number before
    // the colon
    boost::split(parts, fields[1], boost::is_any_of(":"));
    int ls  = boost::lexical_cast<int>(parts[0]);

    // split the last field (which contains information about each bunch crossing)
    // note that the last field has [ as first and ] as last character
    string tmp = fields[9].substr(1, fields[9].length() - 2);
    boost::split(parts, tmp, boost::is_any_of(" "));
    
    // parts has now (string) triplets of (bxid, delivered, recorded instantaneous luminosity)
    assert(parts.size() % 3 == 0);

    for (unsigned i = 0; i < parts.size(); i += 3) {
      
      int bxid = boost::lexical_cast<int>(parts[i]);
      double lumi = boost::lexical_cast<double>(parts[i+1]);

      // TODO: should we insist that we do not have the information for the same
      //       run/ls/bx more than once ?
      data[run][ls][bxid] = lumi;

    } // loop over triplets of the last column

  } // loop over lines


}
