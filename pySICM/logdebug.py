# (C) 2017 Patrick Happel <patrick.happel@rub.de>
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

"Enabling logging and debugging messages. Allows changing the log-level." 

import datetime

class Logger( object ):
    '''The Logger class is used to log debug messages'''
    
    # Default log file
    logfile      = '/var/log/pySICM/pySICM.log'

    # Other default settings
    save_old_log = True
    log_level    = 1
    file_object  = None
    log_info     = ['info', 'log', 'debug']
    to_console   = False

    def __init__( self, logfile = None ):
        '''Optionally initialize with a new logfile'''
        if logfile is not None:
            self.logfile = logfile
    
    def save_old_log( self ):
        '''Should the old log file (if available) be saved?'''
        self.save_old_log = True

    def delete_old_log( self ):
        '''Should the old log file (if available) be deleted?'''
        self.save_old_log = False
        
    def _open( self ):
        '''Internal: Opens the file for writing'''
        self.file_object = open( self.logfile, 'w' )

    def _close( self ):
        '''Internal: Closes the file.'''
        close( self.file_object )

    def _write_log ( self, msg , mode ):
        '''Internal: Writes data to the log file'''
        if self.file_object is None:
            self._open()
            self.log("Started logging.")

        if mode <= self.log_level:
            s = '{time}|{level}: {msg}'.format(
                time  = datetime.datetime.now( ), 
                level = self.log_info[ mode ], 
                msg   = msg
            )
            file_object.write(s)
            if self.to_console:
                print(s)

    def log( self, msg ):
        '''Logs a message at log-level 1 (log):
           param: msg     (string) the message to log'''
        self._write_log( msg, 1 )

    def info( self, msg ):
        '''Logs a message at log-level 2 (info):
           param: msg     (string) the message to log'''
        self._write_log( msg, 2 )
                              
    def debug( self, msg ): 
        '''Logs a message at log-level 3 (debug):
           param: msg     (string) the message to log'''
        self._write_log( msg, 3 )
    

    def log_level_log( self ):
        '''Sets log-level to log'''
        self.log_level = 1

    def log_level_info( self ):
        '''Sets log-level to log'''
        self.log_level = 2

    def log_level_debug( self ):
        '''Sets log-level to log'''
        self.log_level = 3
    
    




