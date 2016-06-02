#!/usr/bin/env python

# produces a HTML report with the given tasks
from FedSizePerVertexLinearFit import FedSizePerVertexLinearFit


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

class HTMLReportMaker:

    #----------------------------------------

    def __init__(self, tasks):
        # make a copy
        self.tasks = list(tasks)

    #----------------------------------------

    def __printEvolutionOverviewTable(self, subsystemEvolutionData):

        print >> self.os, "<h2>Overview of FED size vs. number of reconstructed vertices evolution</h2><br/>"
        print >> self.os, "<table>"
        print >> self.os, "<tbody>"
        
        print >> self.os,"<tr>" + "".join([ "<th>" + x + "</th>" for x in [
                    'grouping',
                    'group',
                    'offset [kByte]',
                    'slope [kByte/vtx]',
                    'number of feds']]) + "</tr>"

        for line in subsystemEvolutionData:

            grouping = line['grouping']
            if grouping == None:
                grouping = "&nbsp;"

            # TODO: sort by what ? or print table multiple times with different sorting criteria ?
            print >> self.os,"<tr>"
            print >> self.os,"<td>" + grouping + "</td>"
            print >> self.os,"<td>" + '<a href="#subsys%04d">%s</a>' % (line['index'], line['subsystem']) + "</td>"
            print >> self.os,"<td>" + "%0.3f" % line['offset'] + "</td>"
            print >> self.os,"<td>" + "%0.3f" % line['slope'] + "</td>"

            if line['numFeds'] != None:
                numFedsStr = str(line['numFeds'])
            else:
                numFedsStr = "&nbsp;"

            print >> self.os,"<td>" + numFedsStr + "</td>"
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

        # index is used for linking within the document
        index = 0

        for task in self.tasks:
            if not isinstance(task, FedSizePerVertexLinearFit):
                continue

            subsystemEvolutionData.append({"subsystem":  task.subsys, 
                                           "grouping":   task.grouping,
                                           "offset":     task.alpha, 
                                           "slope":      task.beta, 
                                           "numFeds":    task.numFeds, 
                                           "index":      index})

            if task.subsys == 'total':
                # convert from MB to kB
                subsystemEvolutionData[-1]['offset'] *= 1000.0
                subsystemEvolutionData[-1]['slope'] *= 1000.0

            index += 1

        #----------
        print >> self.os,"<html>"

        print >> self.os,"<head>"
        print >> self.os,"<title>Event sizes evolution</title>"

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


