import pyAPT.pt1 as PT1 
from pySICM.setup import pysicmsetup as SETUP

class StagePT1(object):

    mode='toolStagePT1'

    def __init__(self):
        print str(SETUP.instrument['controllables'])
        for k,v in SETUP.instrument['controllables'].iteritems():
            print str(k)+" ("+str(v.name)+"): " +str(v._axes)
            if v.zcoarse():
                if v.name == "Thorlabs Stage PT1":
                    self.stage = v.zcoarse()
        

    def scan(self, settings, writeResponse):
        print str(settings)
        if 'command' in settings['toolStagePT1']:
            command = settings['toolStagePT1']['command']

            if command == 'home':
                self.stage.home()
            elif command == 'up':
                self.stage.move(-1*float(settings['toolStagePT1']['param']))
            elif command == 'down':
                self.stage.move(float(settings['toolStagePT1']['param']))
            elif command == 'goto':
                self.stage.goto(float(settings['toolStagePT1']['param']))
            del self.stage
    
