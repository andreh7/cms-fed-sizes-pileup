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

    def __fillInputData(self, firstRow):
        # fills the fitted data per FED group on which almost
        # any other numbers are based on

        #----------
        # column headers
        #----------
        self[(firstRow, 4)] = 'sum data sizes [kByte/ev]' # D3
        # self.ws['F3'] = '=CONCATENATE("data size at ";CELL("contents";A2);" vertices") '
        # self.ws['F3'] = '=\"data size at \"\&A2\&\" vertices\"'

        # does not work with POI
        # self.ws['F3'] = '="data size at "&A2&" vertices"'

        self[(firstRow + 2, 1)] = 'FED group'               # A5                  
        self[(firstRow + 2, 2)] = 'number of feds'          # B5
        self[(firstRow + 2, 3)] = 'subsys' # do we still need this ? # C5
        self[(firstRow + 2, 4)] = 'offset'                  # D5
        self[(firstRow + 2, 5)] = 'slope'                   # E5

        self.ws.column_dimensions[_get_column_letter(2)].width = 14

        #----------
        # fill the evolution data
        #----------
        
        for rowOffset, data in enumerate(self.evolutionData):
            thisRow = rowOffset + firstRow + 3
            self[(thisRow, 1)] = data['subsystem']                          # A%d
            self[(thisRow, 2)] = data['numFeds']                            # B%d
            self.makeNumericCell((thisRow, 4), data['offset'], "#,##0.000") # D%d
            self.makeNumericCell((thisRow, 5), data['slope'], "#,##0.000")  # E%d


    #----------------------------------------

    def __fillDataSizeAtNumVertices(self, topLeft, topLeftInputData, numVtxCellName):
        # produces cells calculating the data size at a given number
        # of vertices
        #
        # @param topLeftInputData is (row,col) of the first data cell
        # (offset) of the input data

        firstRow, firstCol = topLeft

        firstRowInputData, inputCol = topLeftInputData

        #----------
        # title cells
        #----------

        self[(firstRow,     firstCol)] = 'data size [kByte/ev]'                                            # G3
        self[(firstRow + 1, firstCol)] = '=CONCATENATE("at ",TEXT(%s,"0.0")," vertices")' % numVtxCellName # G4

        #----------
        # fill the formulas
        #----------

        for i in range(len(self.evolutionData)):
            thisRow = firstRow + 3 + i
            # need absolute cell rows to allow sorting by the user

            inputRow = firstRowInputData + i 

            self.makeNumericCell((thisRow, firstCol), "=%s+%s*%s" %( # G%d =D%d+E%d*B$1
                    coordToName(inputRow, inputCol), # D%d
                    coordToName(inputRow, inputCol + 1), # E%d
                    numVtxCellName # B$1
                    ), "#,##0.000")


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
        row = self.__makeHeaderCells()

        # fill input data (fit results)
        self.__fillInputData(row)

        #----------
        # uncertainties fit
        #----------
        self[(row,     17)] = 'one sigma spread on data sizes [kByte/ev]' # Q3 
        self[(row + 2, 17)] = 'offset'                                    # Q5
        self[(row + 2, 18)] = 'slope'                                     # R5

        #----------
        # data size at given number of vertices
        #----------
        self.__fillDataSizeAtNumVertices(topLeft = (row, 7), 
                                         topLeftInputData = (row + 3, 4),
                                         numVtxCellName = self.avgNumVtxCellName)

        # add additional cells with formulas

        #--------------------
        # data rate
        #--------------------
        self[(row,     9)] = "data rate [MByte/s]" # I3
        self[(row + 1, 9)] = "at trigger rate"     # I4
        self[(row + 2, 9)] = "offset"              # I5
        self[(row + 2,10)] = "slope"               # J5

        for i in range(numItems):
            thisRow = row + 3 + i
            self.makeNumericCell((thisRow, 9),  "=%s*%s" % ( # I%d =D%d*I$1
                    coordToName(thisRow, 4), # D%d
                    self.triggerRateCellName),    # I$1
                                 "#,##0.000") 
            self.makeNumericCell((thisRow, 10), "=%s*%s" %( # J%d =E%d*I$1
                    coordToName(thisRow, 5), # D%d
                    self.triggerRateCellName),    # I$1
                                 "#,##0.000") 

        #----------
        # per FED data rate
        #----------
        self[(row,     12)] = "per FED data rate [MByte/s]" # L3
        self[(row + 1, 12)] = "at trigger rate"             # L4
        self[(row + 2, 12)] = "offset"                      # L5
        self[(row + 2, 13)] = "slope"                       # M5

        for i in range(numItems):
            thisRow = row + 3 + i
            self.makeNumericCell((thisRow, 12),  # L%d =I%d/B%d
                                 "=%s/%s" %(
                    coordToName(thisRow, 9),# I%d
                    coordToName(thisRow, 2) # B%d (number of FEDs in this group)
                    ), "#,##0.000")

            self.makeNumericCell((thisRow, 13),  # M%d =J%d/B%d
                                 "=%s/%s" %(
                    coordToName(thisRow, 10), # J%d
                    coordToName(thisRow, 2)  # B%d (number of FEDs in this group)
                    ), "#,##0.000")

        #----------
        # when do we reach 200 MByte/s per FED ?
        #----------
        limitColumn = 15  # column O


        self[(1, limitColumn)] = "per FED data rate limit [MByte/s]"
        self.ws.column_dimensions[_get_column_letter(limitColumn)].width = 27

        # maximum data rate per FED
        maxDataRateCell = (1, limitColumn + 1)
        maxDataRateCellName = coordToName(*maxDataRateCell, rowPrefix = "$")

        self[maxDataRateCell]  = "200" # P1
        self[(3, limitColumn)] = "# vertices for FED rate limit" # O3

        for i in range(numItems):
            thisRow = row + 3 + i
            self.makeNumericCell((thisRow, limitColumn), # O%d
                                 "=(%s-%s)/%s" %(  # =(P$1-L%d)/M%d
                                 maxDataRateCellName,      # P$1
                                 coordToName(thisRow, 12), # L%d
                                 coordToName(thisRow, 13), # M%d
                                 ),
                                 "0.0")
        #----------
        # offset and slope of uncertanties
        #----------
        for i, data in enumerate(self.evolutionData):
            thisRow = row + 3 + i 
            self.makeNumericCell((thisRow, 17), data['uncertOffset'], "#,##0.000") # Q%d
            self.makeNumericCell((thisRow, 18), data['uncertSlope'], "#,##0.000")  # R%d

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

