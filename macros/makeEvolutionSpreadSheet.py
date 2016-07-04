#!/usr/bin/env python

# given a plot output directory, produces a spreadsheet with the fit parameters

import sys, os
import GrandUnificationPlot

#----------------------------------------------------------------------

def getAverageNumVerticesFromTasks(tasks):
    from NumVertices import NumVertices

    for task in tasks:
        if isinstance(task, NumVertices):
            return task.avg_num_vertices

    # not found
    return None

#----------------------------------------------------------------------

class SpreadsheetCreator:


    #----------------------------------------

    def __init__(self, subsystemEvolutionData, avgNumVertices = None,
                 triggerRateKHz = 100):
        import openpyxl

        self.subsystemEvolutionData = subsystemEvolutionData
        self.triggerRateKHz = triggerRateKHz
        self.avgNumVertices = avgNumVertices

        # create a workbook
        self.wb = openpyxl.Workbook()

        # fill the workbook
        for groupingName, groupingData in self.subsystemEvolutionData.items():
            # make one sheet per grouping
            self.makeSheet(groupingName, groupingData)

    #----------------------------------------
    def writeToFile(self, outputFname):

        fout = open(outputFname, "w")
        fout.write(self.makeString())
        fout.close()

    #----------------------------------------

    def makeString(self):
        # returns the binary notebook as a string
        # (which could be written to a file etc.)

        import openpyxl

        # see http://stackoverflow.com/a/8714342/288875
        return openpyxl.writer.excel.save_virtual_workbook(self.wb)

    #----------------------------------------

    def makeSheet(self, groupingName, evolutionData):
        
        numItems = len(evolutionData)

        # create a new worksheet
        ws = self.wb.create_sheet()
        
        if groupingName == "" or groupingName == None:
            ws.title = "-"
        else:
            ws.title = groupingName


        #----------
        # make titles
        #----------
        ws['A1'] = 'avg. number of vertices'
        if self.avgNumVertices == None:
            ws['B1'] = "unknown"
        else:
            ws['B1'] = str(self.avgNumVertices)

        #----------
        # title cells
        #----------

        ws['D3'] = 'sum data sizes [kByte/ev]'
        # ws['F3'] = '=CONCATENATE("data size at ";CELL("contents";A2);" vertices") '
        # ws['F3'] = '=\"data size at \"\&A2\&\" vertices\"'

        # does not work with POI
        # ws['F3'] = '="data size at "&A2&" vertices"'

        ws['G2'] = 'data size [kByte/ev] at'
        ws['G3'] = 'avg. #vertices'

        # column headers
        ws['A5'] = 'FED group'
        ws['B5'] = 'number of feds'
        ws['C5'] = 'subsys' # do we still need this ?
        ws['D5'] = 'offset'
        ws['E5'] = 'slope'

        #----------
        # fill the evolution data
        #----------
        
        for row, data in enumerate(evolutionData):
            thisRow = row + 6
            ws['A%d' % thisRow] = data['subsystem']
            ws['B%d' % thisRow] = data['numFeds']
            ws['D%d' % thisRow] = data['offset']
            ws['E%d' % thisRow] = data['slope']

        #----------

        # data size at given number of vertices
        for i in range(numItems):
            row = 6+i
            # need absolute cell rows to allow sorting by the user
            ws['G%d' % row] = "=D%d+E%d*B$1" %(row,row)

        # add additional cells with formulas

        #--------------------
        # data rate
        #--------------------
        ws['H1'] = 'trigger rate [kHz]:'
        ws['I1'] = str(self.triggerRateKHz)

        ws['I3'] = "data rate [MByte/s]"
        ws['I4'] = "at trigger rate"
        ws['I5'] = "offset"
        ws['J5'] = "slope"

        for i in range(numItems):
            row = 6+i
            ws['I%d' % row ] = "=D%d*I$1" %row 
            ws['J%d' % row ] = "=E%d*I$1" %row 

        #----------
        ws['L3'] = "per FED data rate [MByte/s]"
        ws['L4'] = "at trigger rate"
        ws['L5'] = "offset"
        ws['M5'] = "slope"

        for i in range(numItems):
            row = 6+i
            ws['L%d' % row] = "=I%d/B%d" %(row,row)
            ws['M%d' % row] = "=J%d/B%d" %(row,row)

        #----------
        # when do we reach 200 MByte/s per FED ?
        #----------
        ws['O1'] = "per FED data rate limit [MByte/s]"
        ws['P1'] = "200"
        ws['O3'] = "# vertices for FED rate limit"

        for i in range(numItems):
            row = 6+i
            ws['O%d' % row] = "=(P$1-L%d)/M%d" %(row,row)

#----------------------------------------------------------------------
# main
#----------------------------------------------------------------------
if __name__ == "__main__":


    ARGV = sys.argv[1:]

    assert len(ARGV) == 1

    tasksFile = ARGV.pop(0)

    import pickle

    tasks = pickle.load(open(tasksFile))

    plotDir = os.path.dirname(tasksFile)

    subsystemEvolutionData = GrandUnificationPlot.makeSubsystemEvolutionData(tasks)
    sc = SpreadsheetCreator(subsystemEvolutionData,
                            getAverageNumVerticesFromTasks(tasks))

    outputFname = os.path.join(plotDir, "evolution.xlsx")

    sc.writeToFile(outputFname)

    print >> sys.stderr,"wrote report to", outputFname

