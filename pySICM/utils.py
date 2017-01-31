import struct

def mkByte(self, number, r = 16):
    # little endian
    if r == 16:
        a = int(number / 256)
        b = int(number % 256)
        try:
            return struct.pack('B',b)+struct.pack('B',a)
        except:
            print "b: "+str(b)
            print "a: "+str(a)
            
    elif r == 24:
        a = int(number/(2**16))
        return struct.pack('b',a) + mkByte(int(a%2^16), r=16)
