# Copyright (C) 2014 Patrick Happel <patrick.happel@rub.de>
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

# from piezo import 

from pySICM.error import PySICMError

class Controllable(object):
    '''Class for Devices that allow position control'''
    STAGE = 0
    PIPETTE = 1
    VOUT = 2
    OTHER = 3
    _axes = {}

    def __init__(self, name, typ):
        self.name = name
        self.type = typ
        
    def _is(self, typ):
        return  typ == self.type

    def isPipette(self):
        return self._is(self.PIPETTE)
    
    def isStage(self):
        return self._is(self.STAGE)

    def isVOut(self):
        return self._is(self.VOUT)
    def isOther(self):
        return self._is(self.OTHER)
    
    def axes(self, **kwargs):
        '''Specify the different axes for this control

        Params (optional):
        ------------------
        x: PiezoControl for x-axis
        y: PiezoControl for y-axis
        z: ZPiezoControl for z-axis
        '''

        if ('x' in kwargs):
            self._axes['x'] = kwargs['x']
        if ('y' in kwargs):
            self._axes['y'] = kwargs['y']
        if('z' in kwargs):
            try:
                kwargs['z'].approach
                self._axes['z'] = kwargs['z']
            except AttributeError:
                raise PySICMError("Z-Axis' PiezoControl does not implement method 'approach'")

        if('zcoarse' in kwargs):
            try:
                kwargs['zcoarse'].up
                kwargs['zcoarse'].down
                self._axes['zcoarse'] = kwargs['zcoarse']
            except AttributeError:
                raise PySICMError("coarse Z-Axis ' does not implement methods 'up' and 'down'")

        if('xcoarse' in kwargs):
            try:
                kwargs['xcoarse'].up
                kwargs['xcoarse'].down
                self._axes['xcoarse'] = kwargs['xcoarse']
            except AttributeError:
                raise PySICMError("coarse X-Axis ' does not implement methods 'up' and 'down'")

        if('ycoarse' in kwargs):
            try:
                kwargs['ycoarse'].up
                kwargs['ycoarse'].down
                self._axes['zcoarse'] = kwargs['ycoarse']
            except AttributeError:
                PySICMError("coarse Y-Axis ' does not implement methods 'up' and 'down'")

        if('zfine' in kwargs):
            self._axes['zfine'] = kwargs['zfine']


    def _get(self, what):
        if what in self._axes:
            return self._axes[what]
        else:
            return False
                
    def x(self):
        return self._get('x')


    def y(self):
        return self._get('y')

    def z(self):
        return self._get('z')

    def zfine(self):
        return self._get('zfine')

    def xcoarse(self):
        return self._get('xcoarse')
    
    def ycoarse(self):
        return self._get('ycoarse')
    
    def zcoarse(self):
        return self._get('zcoarse')
    
