import pySICM.error as PySICMError
import numpy

class UNIT:
    bits = 0
    volts = 1
    nm = 2
    names = ['bits','volts','nanometer']



class CHANNEL:
    inp = 0
    outp = 1


class NumberConverter:
    input_range = None
    output_range = None
    distance = None
    out2in_bits_poly = None
    in2out_bits_poly = None
    out_volts2bits_poly = None
    nm2outvolts_poly = None

    def __init__(self, input_range,
                 output_range, distance,
                 calib):
        self.input_range = input_range
        self.output_range = output_range
        self.distance = distance
        self.out2in_bits_poly = numpy.polyfit(calib[8000:,0], calib[8000:,1], 1)
        x = numpy.linspace(
            min(self.output_range), max(self.output_range),
            num = len(calib[:,0]))
        self.out_volts2bits_poly = numpy.polyfit(x, calib[:,0], 1)
        
        x2 = numpy.linspace(0, self.distance, len(x))
        self.nm2outvolts_poly = numpy.polyfit(x2, x, 1)
        self.in2out_bits_poly = [
            1/self.out2in_bits_poly[0],
            -1*self.out2in_bits_poly[1]/self.out2in_bits_poly[0]]

        
    def getConvertedNumber(self, value = None, unit = None, channel = None):
        return ConvertedNumber(self, value, unit, channel)

    def checkNM(self, nm):
        if nm > self.distance:
            return self.distance
        if nm < 0:
            return 0
        return nm

    # Convert from nm

    def nm2volts_out(self, nm):
        if nm < 0:
            nm = 0
        if nm > self.distance:
            nm = self.distance

        return numpy.polyval(self.nm2outvolts_poly, nm)
    
    def nm2volts_in(self, nm):
        pass
    
    def nm2bits_in(self, nm):
        return numpy.polyval(
            self.out2in_bits_poly,
            self.nm2bits_out(nm))
    
    def nm2bits_out(self, nm):
        return numpy.polyval(
            self.out_volts2bits_poly,
            self.nm2volts_out(nm))
    
    # Convert to nm
    
    def out_bits2nm(self, obits):
        ovolts = numpy.polyval([
            1/self.out_volts2bits_poly[0],
            -1*self.out_volts2bits_poly[1]/self.out_volts2bits_poly[0]
            ], obits)
        return self.out_volts2nm(ovolts)


    def out_volts2nm(self, ovolts):
        return numpy.polyval([
            1/self.nm2outvolts_poly[0],    
            -1*self.nm2outvolts_poly[1]/self.nm2outvolts_poly[0]
            ], ovolts)


    def in_bits2nm(self, ibits):
        return self.out_bits2nm(
            numpy.polyval(self.in2out_bits_poly, ibits))

    def in_volts2nm(self, ivolts):
        pass



class ConvertedNumber:
    
    def __init__(self, converter, val = None, unit = None, channel = None):
        self.converter = converter
        self.nm=None
        self.inp= {'bits':None, 'volts': None}
        self.outp= {'bits': None, 'volts': None}
        
        if val is not None:
            if hasattr(val, 'unit') and hasattr(val, 'val'):
                self.setValue(val.val, val.unit, channel)
            else:
                self.setValue(val, unit, channel)

    def __str__(self):
        lines = []
        lines.append('Nanometer: %s' % self.nm)
        lines.append('Input:')
        lines.append('  Bits: %s' % self.inp['bits'])
        lines.append('  Volts: %s' % self.inp['volts'])
        lines.append('Output:')
        lines.append('  Bits: %s' % self.outp['bits'])
        lines.append('  Volts: %s' % self.outp['volts'])
        return '\n'.join(lines)
    
    def getValue(self, unit, channel=None):
        if channel is None and unit != UNIT.nm:
            raise PySICMError()
        elif unit == UNIT.nm:
            return self.nm
        elif unit == UNIT.volts:
            if channel == CHANNEL.inp:
                return self.inp['volts']
            else:
                return self.outp['volts']
        else:
            if channel == CHANNEL.inp:
                return self.inp['bits']
            else:
                return self.outp['bits']
            
    def setValue(self, val, unit, channel = None):
        if channel is None and unit != UNIT.nm:
            raise PySICMError()
        elif unit == UNIT.nm:
            self.nm = self.converter.checkNM(val);
            self.updateFromNm()
        elif unit == UNIT.volts:
            if channel == CHANNEL.inp:
                self.inp['volts'] = val
                self.updateFromInputVolts()
            else:
                self.outp['volts'] = val
                self.updateFromOutputVolts()
        else:
            if channel == CHANNEL.inp:
                self.inp['bits'] = val
                self.updateFromInputBits()
            else:
                self.outp['bits'] = val
                self.updateFromOutputBits()

    def updateFromNm(self):
        self.nm = self.converter.checkNM(self.nm)
        self.outp['volts'] = self.converter.nm2volts_out(self.nm)
        self.outp['bits'] = self.converter.nm2bits_out(self.nm)
        self.inp['bits'] = self.converter.nm2bits_in(self.nm)

    def updateFromInputVolts(self):
        pass

    def updateFromInputBits(self):
        self.nm = self.converter.in_bits2nm(self.inp['bits'])
        self.updateFromNm()
        
    def updateFromOutputBits(self):
        self.nm = self.converter.out_bits2nm(self.outp['bits'])
        self.updateFromNm()

    def updateFromOutputVolts(self):
        self.nm = self.converter.out_volts2nm(self.outp['volts'])
        self.updateFromNm()

    def __add__(self, other):
      
        tmp = self.converter.getConvertedNumber()
        try:
            tmp.setValue(self.nm + other.nm, UNIT.nm)
        except:
            try:
                tmp.setValue(self.nm + other.val, UNIT.nm)
            except:
                tmp.setValue(self.nm + other, UNIT.nm)
        return tmp

    def __iadd__(self, other):
        try:
            self.nm += other.nm
        except:
            try:
                self.nm += other.val
            except:
                self.nm += other
        self.updateFromNm()
        return self

    def __sub__(self, other):
        tmp = self.converter.getConvertedNumber()
        tmp.setValue(self.nm - other.nm, UNIT.nm)
        return tmp

    def __lt__(self, other):
        try:
            return self.nm < other.nm
        except:
            return self.nm < other
    def __le__(self, other):
        try:
            return self.nm <= other.nm
        except:
            return self.nm <= other
        
    def __eq__(self, other):
        try:
            return self.nm == other.nm
        except:
            return self.nm == other
    def __ne__(self, other):
        try:
            return self.nm != other.nm
        except:
            return self.nm != other

    def __ge__(self, other):
        try:
            return self.nm >= other.nm
        except:
            return self.nm >= other
    def __gt__(self, other):
        try:
            return self.nm > other.nm
        except:
            return self.nm > other
    
    
    def add(self, val, unit, channel=None):
        if channel is None and unit != UNIT.nm:
            raise PySICMError()
        elif unit == UNIT.nm:
            self.nm += val;
            self.updateFromNm()
        elif unit == UNIT.volts:
            if channel == CHANNEL.inp:
                self.inp['volts'] += val
                self.updateFromInputVolts()
            else:
                self.outp['volts'] += val
                self.updateFromOutputVolts()
        else:
            if channel == CHANNEL.inp:
                self.inp['bits'] += val
                self.updateFromInputBits()
            else:
                self.outp['bits'] += val
                self.updateFromOutputBits()

    def get_oBits(self):
        return UNumber(self.outp['bits'], UNIT.bits)
    def get_iBits(self):
        return UNumber(self.inp['bits'], UNIT.bits)
    def get_oVolts(self):
        return UNumber(self.inp['volts'], UNIT.volts)
    def get_nm(self):
        return UNumber(self.nm, UNIT.nm)

class UNumber:
    val = None
    unit= None

    def __init__(self, val, unit):
        self.val = val
        self.unit = unit

    def __int__ (self):
        return int(round(self.val))

    def __str__(self):
        return str(self.val) + ' ' + UNIT.names[self.unit]

    def _get_val_from_other(self, other):
        try:
            if other.unit != self.unit:
                raise PySICMError()
            else:
                val = other.val
        except:
            val = other
        return val

    def __add__(self, other):
        return UNumber(self._get_val_from_other(other) + self.val, self.unit)

    def __sub__(self, other):
        return UNumber(self.val - self._get_val_from_other(other), self.unit)

    def __iadd__(self, other):
        self.val = self.val + self._get_val_from_other(other)
        return self

    def __isub__(self, other):
        self.val = self.val - self._get_val_from_other(other)
        return self
    def __mul__(self, other):
        return UNumber(self.val * self._get_val_from_other(other), self.unit)

    def __div__(self, other):
        return UNumber(self.val * self._get_val_from_other(other), self.unit)
        
    def __idiv__(self, other):
        self.val /= self._get_val_from_other(other)
        return self

    def __imul__(self, other):
        self.val *= self._get_val_from_other(other)
        return self

    def __float__(self):
        return float(self.val)
