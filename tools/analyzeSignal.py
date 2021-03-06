from pySICM.setup import pysicmsetup as SETUP
from twisted.internet import defer
import numpy, json

class AnalyzeSignal(object):

    mode = 'toolAnalyzeSignal'

    def __init__(self):
        for v in SETUP.instrument['inputsignals'].itervalues():
            self.signal = v
            

    def scan(self, settings, writeResponse):
        d = defer.succeed(self.measure())
        d.addCallback(writeResponse)
        
    def measure(self):
        
        data = self.signal.read_n(10000)
        res = {"mean" : float(numpy.average(data)),
               "max"  : int(numpy.max(data)),
               "min"  : int(numpy.min(data)),
               "std"  : float(numpy.std(data)),
               "c_max": self.signal.channel.range.max,
               "c_min": self.signal.channel.range.min}
        return json.dumps(res)
