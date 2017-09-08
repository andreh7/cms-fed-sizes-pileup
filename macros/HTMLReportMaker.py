#!/usr/bin/env python

# produces a HTML report with the given tasks
from FedSizePerVertexLinearFit import FedSizePerVertexLinearFit

import utils

#----------------------------------------------------------------------

def encodeImage(imageFname):
    # returns a html fragment with image data URI encoded to the HTML output stream os

    # supported mime types
    if imageFname.endswith(".png"):
        mimeType = "image/png"
    else:
        raise Exception("don't know what mime type to use for file " + imageFname)

    data = open(imageFname).read().encode("base64").replace("\n","")

    return '<img src="data:' + mimeType + ';base64,' + data + '">'

#----------------------------------------------------------------------

def encodeDocument(data, linkText, mimeType):

    # returns a data URI encoded document 

    encodedData = data.encode("base64").replace("\n","")

    return '<a href="data:' + mimeType + ';base64,' + encodedData + '">%s</a>' % linkText
    

#----------------------------------------------------------------------

from makeEvolutionSpreadSheet import SpreadsheetCreator, getAverageNumVerticesFromTasks


class HTMLReportMaker:

    #----------------------------------------

    def __init__(self, tasks, run, dataset, xvar):
        # make a copy
        self.tasks = list(tasks)

        self.run = run
        self.dataset = dataset
        self.xvar = xvar

        # find maximum order of coefficients
        self.numCoeffs = -1
        for task in self.tasks:
            if not isinstance(task, FedSizePerVertexLinearFit):
                continue

            self.numCoeffs = max(self.numCoeffs, len(task.meanFitResult['coeffs']))

    #----------------------------------------
        
    def printSizeCalculatorJavascriptAndForm(self, numLines):

        if self.xvar == 'vtx':
            suffix = "number of reconstructed vertices"
        elif self.xvar == 'pu':
            suffix = "pileup"
        else:
            raise Exception("internal error")


        # code to extract coefficients
        coeffsCode = "var coeffs = [ " + ", ".join(
            [ "parseFloat(document.getElementById('coeff%d_subsys' + subsys).innerHTML)" % power
              for power in range(self.numCoeffs) ]) + "];"

        print >> self.os,"""
<script language="javascript">
//----------------------------------------------------------------------
function updateTable()
{
  var numVertices = document.getElementById('customNumVertices').value;

  // convert to integer
  numVertices = parseFloat(numVertices);
  if (isNaN(numVertices))
  {
    alert("malformed number of vertices");
    return;
  }

  document.getElementById('customNumVerticesField').innerHTML = numVertices;

  for (var subsys = 0; subsys < """ + str(numLines) + """; ++subsys)
  {
    """ + coeffsCode + """

    var value = 0;
    for (i = coeffs.length - 1; i >= 0; --i)
    {  
      value *= numVertices;
      value += coeffs[i];
    }

    document.getElementById('custom_size_subsys' + subsys).innerHTML = value.toFixed(3);

  }


}
//----------------------------------------------------------------------

</script>
<form>
Custom """ + suffix + """:
<input type='text' id='customNumVertices' />
<button type="button" onclick="updateTable();">update table</button>
</form>
<br/>
"""
    #----------------------------------------

    def __printEvolutionOverviewTable(self, subsystemEvolutionData):

        if self.xvar == 'vtx':
            suffix = "number of reconstructed vertices"
        elif self.xvar == 'pu':
            suffix = "pileup"
        else:
            raise Exception("internal error")

        print >> self.os, "<h2>Overview of FED size vs. " + suffix + " evolution (run %d %s)</h2><br/>" % (self.run, self.dataset)

        print >> self.os, encodeDocument(self.spreadSheetCreator.makeString(),
                                         "spreadsheet",
                                         "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        print >> self.os, "<br/>"
        print >> self.os, "<br/>"
        
        # print javascript for event size calculation
        self.printSizeCalculatorJavascriptAndForm(len(subsystemEvolutionData))


        # table with overview
        print >> self.os, "<table>"
        print >> self.os, "<tbody>"

        # table header

        colnames = [
            'grouping',
            'group',
            ]

        for power in range(self.numCoeffs):
            unit = 'kByte'
            if power == 1:
                unit += '/' + self.xvar
            elif power >= 2:
                unit += '/%s^%d' % (self.xvar, power)

            colnames.append(utils.getPowerName(power) + ' [%s]' % unit)

        if self.xvar == 'vtx':
            suffix = "vertices"
        elif self.xvar == 'pu':
            suffix = "pileup"
        else:
            raise Exception("internal error")

        colnames += [
            'number of feds',
            'event size at <div id="customNumVerticesField">?</div> ' + suffix + ' [kByte]',
            ]

        print >> self.os,"<tr>" + "".join([ "<th>" + x + "</th>" for x in colnames ]) + "</tr>"

        for line in subsystemEvolutionData:

            grouping = line['grouping']
            if grouping == None:
                grouping = "&nbsp;"

            def sizeToString(value):
                if value == None:
                    return "?"
                else:
                    return "%0.3f" % value

            # TODO: sort by what ? or print table multiple times with different sorting criteria ?
            print >> self.os,"<tr>"
            print >> self.os,"<td>" + grouping + "</td>"
            print >> self.os,"<td>" + '<a href="#subsys%04d">%s</a>' % (line['index'], line['subsystem']) + "</td>"

            for power in range(self.numCoeffs):
                print >> self.os,'<td id="coeff%d_subsys%d">' % (power, line['index']) + sizeToString(line['coeffs'][power]) + "</td>"

            if line['numFeds'] != None:
                numFedsStr = str(line['numFeds'])
            else:
                numFedsStr = "&nbsp;"

            print >> self.os,"<td>" + numFedsStr + "</td>"

            print >> self.os, '<td id="custom_size_subsys%d" style="text-align: right;">-</td>' % line['index']

            print >> self.os,"</tr>"

        print >> self.os, "</tbody>"
        print >> self.os, "</table>"

    #----------------------------------------

    # call this only after all tasks were completed
    def make(self):
        import cStringIO as StringIO
        self.os = StringIO.StringIO()
        #----------
        
        # collect the list of all fed size evolution plots
        # to summarize the evolution in a table

        subsystemEvolutionData = []

        groupedSubsystemEvolutionData = {}

        # index is used for linking within the document
        index = 0

        for task in self.tasks:
            if not isinstance(task, FedSizePerVertexLinearFit):
                continue

            thisData = {"subsystem":  task.subsys, 
                                           "grouping":   task.grouping,
                                           "coeffs":     task.meanFitResult['coeffs'], 

                                           "uncertCoeffs":     task.uncertFitResult['coeffs'], 

                                           "numFeds":    task.numFeds, 
                                           "index":      index}

            subsystemEvolutionData.append(thisData)

            groupedSubsystemEvolutionData.setdefault(task.grouping, []).append(thisData)

            index += 1


        self.spreadSheetCreator = SpreadsheetCreator(groupedSubsystemEvolutionData,
                                                     self.xvar,
                                                     getAverageNumVerticesFromTasks(self.tasks))



        #----------
        print >> self.os,"<html>"

        print >> self.os,"<head>"
        print >> self.os,"<title>Event sizes evolution run %d %s</title>" % (self.run, self.dataset)

        # see e.g. http://www.w3schools.com/css/css_table.asp for table CSS
        # attributes

        print >> self.os, "<style>"
        print >> self.os, "table, th, td {"
        print >> self.os, "  border: 1px solid black;"
        print >> self.os, "  border-collapse: collapse;"
        print >> self.os, "  padding: 5px;"
        print >> self.os, "}"
        print >> self.os, "tr:nth-child(even) {background-color: #f2f2f2}"
        print >> self.os, "tr:hover {background-color: #ffC0C0}"
        print >> self.os, "</style>"

        print >> self.os,"</head>"

        self.__printEvolutionOverviewTable(subsystemEvolutionData)

        #----------
        # add the plots for each task
        #----------

        sizeEvolutionIndex = 0

        for task in self.tasks:
            print >> self.os,"<hr/>"
            
            # print an anchor for FED size evolution w.r.t vertices
            if isinstance(task, FedSizePerVertexLinearFit):
                print >> self.os, '<a name="subsys%04d"/>' % sizeEvolutionIndex

                print >> self.os, "<h2>fed size evolution " + task.subsys + "</h2>"

                sizeEvolutionIndex += 1

            # append all plots among the output files
            for outputFile in task.outputFiles:
                if outputFile['fname'].endswith(".png"):
                    print >> self.os,encodeImage(outputFile['fname'])
                    print >> self.os,"<br/>"

        print >> self.os,"<body>"

        print >> self.os,"</body>"
        print >> self.os,"</html>"
        

        #----------
        retval = self.os.getvalue()
        del self.os
        return retval


