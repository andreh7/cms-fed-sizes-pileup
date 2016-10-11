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

from openpyxl.utils import _get_column_letter

def coordToName(row, col, rowPrefix = "", colPrefix = ""):
    # row and col are one-based

    return colPrefix + _get_column_letter(col) + rowPrefix + str(row)

#----------------------------------------------------------------------


class SingleGroupSheet:
    # fills a single spreadsheet for a given group

    #----------------------------------------
    
    def __init__(self, workbook, groupingName, evolutionData, avgNumVertices, 
                 triggerRateKHz):
        self.wb = workbook
        self.groupingName = groupingName
        self.evolutionData = evolutionData
        self.avgNumVertices = avgNumVertices
        self.triggerRateKHz = triggerRateKHz
    #----------------------------------------

    def __makeHeaderCells(self):
        # write average number of vertices
        # and trigger rate
        #
        # @return the next row index to be used

        self.avgNumVtxCell = (1,2)
        self.avgNumVtxCellName = coordToName(*self.avgNumVtxCell, rowPrefix = '$') # B$1

        self[(self.avgNumVtxCell[0], self.avgNumVtxCell[1] - 1)] = 'avg. number of vertices'
        if self.avgNumVertices == None:
            self[self.avgNumVtxCell] = "unknown"
        else:
            self.makeNumericCell(self.avgNumVtxCell, self.avgNumVertices, "0.0")

        self.ws.column_dimensions[_get_column_letter(self.avgNumVtxCell[1] - 1)].width = 20

        #----------
        # trigger rate
        #----------
        self.triggerRateCell = (1,9)
        self.triggerRateCellName = coordToName(*self.triggerRateCell, rowPrefix = "$")

        self[(self.triggerRateCell[0], self.triggerRateCell[1] - 1)] = 'trigger rate [kHz]:' # H1
        self.ws.column_dimensions[_get_column_letter(self.triggerRateCell[1] - 1)].width = 14
        self[self.triggerRateCell] = str(self.triggerRateKHz) # 'I1'

        return 3

    #----------------------------------------

    # helper function to assign to the current sheet
    # by row and column number
    def __setitem__(self, key, value):
        self.ws._get_cell(*key).value = value

    #----------------------------------------

    def fillSheet(self):
        
        numItems = len(self.evolutionData)

        # create a new worksheet
        self.ws = self.wb.create_sheet()
        
        if self.groupingName == "" or self.groupingName == None:
            self.ws.title = "-"
        else:
            self.ws.title = self.groupingName

        #----------
        # average number of vertices and
        # nominal trigger rate
        #----------
        self.__makeHeaderCells()

        #----------
        # title cells
        #----------

        self.ws['D3'] = 'sum data sizes [kByte/ev]'
        # self.ws['F3'] = '=CONCATENATE("data size at ";CELL("contents";A2);" vertices") '
        # self.ws['F3'] = '=\"data size at \"\&A2\&\" vertices\"'

        # does not work with POI
        # self.ws['F3'] = '="data size at "&A2&" vertices"'

        self.ws['G3'] = 'data size [kByte/ev] at'
        self.ws['G4'] = 'avg. #vertices'

        # column headers
        self.ws['A5'] = 'FED group'
        self.ws['B5'] = 'number of feds'
        self.ws['C5'] = 'subsys' # do we still need this ?
        self.ws['D5'] = 'offset'
        self.ws['E5'] = 'slope'

        self.ws.column_dimensions['B'].width = 14

        #----------
        # uncertainties fit
        #----------
        self.ws['Q3'] = 'one sigma spread on data sizes [kByte/ev]'
        self.ws['Q5'] = 'offset'
        self.ws['R5'] = 'slope'

        #----------
        # fill the evolution data
        #----------
        
        for row, data in enumerate(self.evolutionData):
            thisRow = row + 6
            self.ws['A%d' % thisRow] = data['subsystem']
            self.ws['B%d' % thisRow] = data['numFeds']
            self.makeNumericCell('D%d' % thisRow, data['offset'], "#,##0.000")
            self.makeNumericCell('E%d' % thisRow, data['slope'], "#,##0.000")

        #----------

        # data size at given number of vertices
        for i in range(numItems):
            row = 6+i
            # need absolute cell rows to allow sorting by the user
            self.makeNumericCell('G%d' % row, "=D%d+E%d*B$1" %(row,row), "#,##0.000")

        # add additional cells with formulas

        #--------------------
        # data rate
        #--------------------
        self.ws['I3'] = "data rate [MByte/s]"
        self.ws['I4'] = "at trigger rate"
        self.ws['I5'] = "offset"
        self.ws['J5'] = "slope"

        for i in range(numItems):
            row = 6+i
            self.makeNumericCell('I%d' % row, "=D%d*I$1" %row, "#,##0.000")
            self.makeNumericCell('J%d' % row, "=E%d*I$1" %row, "#,##0.000")

        #----------
        self.ws['L3'] = "per FED data rate [MByte/s]"
        self.ws.column_dimensions['O'].width = 27
        self.ws['L4'] = "at trigger rate"
        self.ws['L5'] = "offset"
        self.ws['M5'] = "slope"

        for i in range(numItems):
            row = 6+i
            self.makeNumericCell('L%d' % row, "=I%d/B%d" %(row,row), "#,##0.000")
            self.makeNumericCell('M%d' % row, "=J%d/B%d" %(row,row), "#,##0.000")

        #----------
        # when do we reach 200 MByte/s per FED ?
        #----------
        self.ws['O1'] = "per FED data rate limit [MByte/s]"
        self.ws['P1'] = "200"
        self.ws['O3'] = "# vertices for FED rate limit"

        for i in range(numItems):
            row = 6+i
            self.makeNumericCell('O%d' % row, "=(P$1-L%d)/M%d" %(row,row), "0.0")

        #----------
        # offset and slope of uncertanties
        #----------
        for row, data in enumerate(self.evolutionData):
            thisRow = row + 6
            self.makeNumericCell('Q%d' % thisRow, data['uncertOffset'], "#,##0.000")
            self.makeNumericCell('R%d' % thisRow, data['uncertSlope'], "#,##0.000")

    #----------------------------------------

    def makeNumericCell(self, cellName, value, format = None):
        # cellName can either be a string or a pair (row, col)
        if not isinstance(cellName, str):
            # convert from tuple to string
            cellName = coordToName(*cellName)

        self.ws[cellName] = value
        if format != None:
            self.ws.cell(cellName).number_format = format

    #----------------------------------------


#----------------------------------------------------------------------

class SpreadsheetCreator:


    #----------------------------------------

    def __init__(self, subsystemEvolutionData, avgNumVertices = None,
                 triggerRateKHz = 100, pileups = None):
        import openpyxl

        self.subsystemEvolutionData = subsystemEvolutionData
        self.triggerRateKHz = triggerRateKHz
        self.avgNumVertices = avgNumVertices

        # create a workbook
        self.wb = openpyxl.Workbook()

        # fill the workbook
        for groupingName, groupingData in self.subsystemEvolutionData.items():
            # make one sheet per grouping
            sheetFiller = SingleGroupSheet(self.wb, groupingName, groupingData, avgNumVertices, triggerRateKHz)
            sheetFiller.fillSheet()

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

