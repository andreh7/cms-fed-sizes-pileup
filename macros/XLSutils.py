#!/usr/bin/env python
# some tools related to creating spreadsheets

import sys, os

externalTool = os.path.expanduser("~/bin/xlsutil.jar")
#----------------------------------------------------------------------

def runCmd(cmd):

    res = os.system(cmd)
    if res != 0:
        raise Exception("failed to run command '%s'" % cmd)

#----------------------------------------------------------------------
def xlsUtilExists():
    return os.path.exists(externalTool)

#----------------------------------------------------------------------

def countLinesInFile(fname):
    return len(open(fname).readlines())

#----------------------------------------------------------------------

def makeXLS(csvFname, xlsFname, avgNumVertices, numItems = None, triggerRateKHz = 100):
    """ makes a spread sheet of the overview csv files """

    # count the number of lines in the CSV file
    if numItems == None:
        # count the number of lines in the CSV file and subtract one for the header
        numItems = countLinesInFile(csvFname) - 1

    basicCmd = "java -jar " + externalTool
    #--------------------

    def setCellContent(cell, text, cellType = None):
        cmdParts = [
            basicCmd,
            "set",
            "-f " + xlsFname,
            "-c %s" % cell,
            "-v '%s'" % text,
        ]

        if cellType != None:
            cmdParts.append('-t %s' % cellType)
            
        runCmd(" ".join(cmdParts))
    #--------------------

    # create the spreadsheet
    cmdParts = [
        basicCmd,
        "create",
        "-f " + xlsFname,
        ]

    runCmd(" ".join(cmdParts))

    # import the existing CSV
    cmdParts = [
        basicCmd,
        "importcsv",
        "-f " + xlsFname,
        "-csv " + csvFname,
        "-c A5",
        ]

    runCmd(" ".join(cmdParts))

    setCellContent('A1','avg. number of vertices')
    setCellContent('B1',str(avgNumVertices))

    # title cells
    setCellContent('D3', 'sum data sizes [kByte/ev]')
    # setCellContent('F3', '=CONCATENATE("data size at ";CELL("contents";A2);" vertices") ')
    # setCellContent('F3', '=\"data size at \"\&A2\&\" vertices\"')

    # does not work with POI
    # setCellContent('F3', '="data size at "&A2&" vertices"')

    setCellContent('G2', 'data size [kByte/ev] at')
    setCellContent('G3', 'avg. #vertices')

    # data size at given number of vertices
    for i in range(numItems):
        row = 6+i
        # need absolute cell rows to allow sorting by the user
        setCellContent('G%d' % row, "=D%d+E%d*B$1" %(row,row) )
    # add additional cells with formulas

    #--------------------
    # data rate
    #--------------------
    setCellContent('H1', 'trigger rate [kHz]:')
    setCellContent('I1', str(triggerRateKHz))

    setCellContent('I3', "data rate [MByte/s]")
    setCellContent('I4', "at trigger rate")
    setCellContent('I5', "offset")
    setCellContent('J5', "slope")

    for i in range(numItems):
        row = 6+i
        setCellContent('I%d' % row, "=D%d*I$1" %row )
        setCellContent('J%d' % row, "=E%d*I$1" %row )

    #----------
    setCellContent('L3', "per FED data rate [MByte/s]")
    setCellContent('L4', "at trigger rate")
    setCellContent('L5', "offset")
    setCellContent('M5', "slope")

    for i in range(numItems):
        row = 6+i
        setCellContent('L%d' % row, "=I%d/B%d" %(row,row) )
        setCellContent('M%d' % row, "=J%d/B%d" %(row,row) )

    #----------
    # when do we reach 200 MByte/s per FED ?
    #----------
    setCellContent('O1', "per FED data rate limit [MByte/s]")
    setCellContent('P1', "200")
    setCellContent('O3', "# vertices for FED rate limit")

    for i in range(numItems):
        row = 6+i
        setCellContent('O%d' % row, "=(P$1-L%d)/M%d" %(row,row) )
    

    

