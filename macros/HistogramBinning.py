
class HistogramBinning:
    """ contains utilities related to binning """

    #----------------------------------------

    def __init__(self, nbins, xlow, xhigh):

        self.nbins = nbins
        self.xlow = xlow
        self.xhigh = xhigh

        self.binWidth = (self.xhigh - self.xlow) / float(self.nbins)

    #----------------------------------------

    def getBinNumber(self, x):
        """ returns a ROOT style bin number for the value x:
            0 for the underflow bin
            nbins + 1 for the overflow bin
            1..nbins for bins in between
            """

        if x < self.xlow:
            return 0

        if x >= self.xhigh:
            return self.nbins + 1

        import math

        retval = int((x - self.xlow) / self.binWidth)

        if retval < 0:
            retval = 0
        if retval >= self.nbins:
            retval = self.nbins - 1

        return retval + 1

    #----------------------------------------

    def getBinIndexGenerator(self, includeUnderOverFlow = False):

        if includeUnderOverFlow:
            return xrange(0, self.nbins + 2)
        else:
            return xrange(1, self.nbins + 1)

    #----------------------------------------

    def getBinCenter(self, binNumber):

        assert(binNumber >= 1)
        assert(binNumber <= self.nbins)

        return self.xlow + (binNumber - 1 + 0.5) * self.binWidth

    #----------------------------------------

    def isInRange(self, value):
        return value >= self.xlow and values < self.xhigh
