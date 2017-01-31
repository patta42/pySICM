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


from pySICM.error import PySICMError

import imp, os

#f '__PYSICM' not in globals() and ('__isFirstCall' in globals() and __isFirstCall == TRUE):
#   raise PySICMError('The file '+__file__+' should be only imported after the global __PYSICM variabl# has been defined')



class Helpers(object):
    @staticmethod
    def makeDictKeysInt(d):
        '''Changes the keys of the dictionary to integers if they are convertable.
        Used for object representation by json.dumps

        Input argument: a dictionary

        Return value: The dictionary with new keys'''
        
        if not isinstance(d, dict):
            raise TypeError('makeDictKeysInt expects a dict as input argument')
        retd = {}
        try:
            for k,v in d.iteritems():
                try:
                    if str(int(k)) == k:
                        if isinstance(v, dict):
                            retd[int(k)] = Helpers.makeDictKeysInt(v)
                        else:
                            retd[k] = v
                    else:
                        retd[k] = v
                except:
                    retd[k] = v
        except:
            pass
            
                
        
