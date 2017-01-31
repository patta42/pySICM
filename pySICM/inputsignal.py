

class InputSignal(object):
    channel = None
    name = None
    converter = None
    def __init__(self, name, channel):
        self.channel = channel
        self.name = name
        self.converter = self.channel.get_converter()
    def read(self):
        return self.channel.data_read()

    def read_n(self, n):
        return self.channel.data_read_n(n)
    
    def toPhysical(self, value):
#        conv = self.channel.get_converter()
#        print "Value is: "+str(value)+". I will return: "+str(self.converter.to_physical(value))
        
#        return self.converter.to_physical(value)
        print "Converting to volts with uncalibrated settings"
        mi = self.channel.range.min
        ma = self.channel.range.max
        frac = float(value) / float(2**16)
        ra = float(ma - mi)
        print "frac: "+str(frac)+", ra: "+str(ra)
        ret = (frac * ra) + mi
        print "Returning "+str(ret)
        return ret
    
    def toBits(self, value):
        print "\n\n\n"
        print "============================="
        print "Value is: "+str(value)
        ret = None
#        try:
#            ret =  self.converter.from_physical(value)
#        except:
        print "Using simple non-calibrated conversion"

        if ret is None:

            mi = self.channel.range.min
            ma = self.channel.range.max
            frac = (value - mi)/(ma - mi)
            ra = 2**16
            ret = (frac * ra)
        print "============================="            
        return int(round(ret))

