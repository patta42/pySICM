# Copyright (C) 2015 Patrick Happel <patrick.happel@rub.de>
#
# This file is part of pySICM.
#
# pySICM is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation, either version 2 of the License, or (at your option) any later
# version.
#
# pySICM is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# pySICM. If not, see <http://www.gnu.org/licenses/>.
'''pySICM.helpers is a module that contains several helper functions.'''

from pySICM.error import PySICMError

import imp, os, struct
import numpy as np

SCANMODESDIR = '/home/happel/coding/python/sicm/scanmodes/'
TOOLSDIR = '/home/happel/coding/python/sicm/tools/'
SETUPFILE = '/etc/pySICM/setup.ini'
BOARDINFO = '/usr/local/bin/comedi_board_info'

#class Helpers(object):
#@staticmethod
def makeDictKeysInt(d):
    '''Changes the keys of the dictionary to integers if they are convertable.
    Used for object representation by json.dumps. If dictionary has an 
    integer-key and a corresponding string-key, the string-key will not be 
    changed. Works recursively.
    
    Input argument: a dictionary
    
    Return value: The dictionary with new keys'''
    
    if not isinstance(d, dict):
        raise TypeError('makeDictKeysInt expects a dict as input argument')
    retd = {}
    try:
        for k,v in d.iteritems():
            try:
                if str(int(k)) == k:
                    if int(k) in d:
                        key = k
                    else:
                        key = int(k)
                        
                    if isinstance(v, dict):
                        retd[key] = Helpers.makeDictKeysInt(v)
                    else:
                        retd[key] = v
                else:
                    retd[k] = v
            except:
                retd[k] = v
    except:
        pass
    return retd
                
def mkByteFromInt(i):
    a = i / 256
    b = i % 256
    return struct.pack('B', b)+struct.pack('B', a)

def mkIntFromByte(s):
    a = struct.unpack('B', s[1])[0]
    b = struct.unpack('B', s[0])[0]
    return a * 256 + b

def mkFloatFromInt(i, rang):
    diff = (max(rang) - min(rang))/float(np.iinfo(np.uint16).max)
    return float(min(rang)) + float(i) * diff

def mkIntFromFloat(f, rang):
    diff = (max(rang) - min(rang))/float(np.iinfo(np.uint16).max)
    return int(round((f-min(rang))/diff))

def mkFloatFromByte(b, rang):
    return mkFloatFromInt(mkIntFromByte(b),rang)

def getScanmodeObject(mode, tool = False):
    if tool == False:
        print 'Trying to load from %s' % os.path.join(SCANMODESDIR, mode+'.py')
        pymod = imp.load_source(mode, os.path.join(SCANMODESDIR, mode+'.py'))
    else:
        mode = mode[4].lower()+mode[5:]
        print 'Trying to load from %s' % os.path.join(TOOLSDIR, mode+'.py')
        pymod = imp.load_source(mode, os.path.join(TOOLSDIR, mode+'.py'))
    inst = getattr(pymod, mode[0].capitalize()+mode[1:])
    return inst

def getObject(module, cls, path=None):
    tmp = module.split('.',1)
    sub = None
    if len(tmp) > 1:
        sub = tmp[1]

    mod = tmp[0]
    if path is None:
        res = imp.find_module(mod)
    else:
        res = imp.find_module(mod, [path])
    if sub is not None:
        res = imp.find_module(sub, [res[1]])
    mod = imp.load_source(sub, res[1])
    inst = getattr(mod, cls)
    return inst
    
    

