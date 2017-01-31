#!/usr/bin/python

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

import sys, getopt, os

def usage(scriptname):
    print "\nUsage: "+scriptname+ " option\n"
    print "\nOptions:"
    print "------\n"
    print " -h, --help"
    print "   Show this help.\n"
    print " -s, --server"
    print "   Run the server process (used on the controlling computer).\n"
    print " -g, --gui"
    print "   Launch the gui.\n\n"

def main(allargs):
    try:
        opts, args = getopt.getopt(allargs[1:],"hsg",["help","server","gui"])
    except getopt.GetoptError:
        usage(allargs[0])
        sys.exit(2)
    if len(opts) == 0:
        usage(allargs[0])
        sys.exit(2)
    for opt, arg in opts:
        if opt in ["-h", "--help"]:
            usage(allargs[0])
            sys.exit(0)
        elif opt in ["-s","--server"]:
            print "Server start not yet implemented."
            sys.exit(0)
        elif opt in ["-g","--gui"]:
            sys.path.append(os.path.abspath('./pySICM/'))
            sys.path.append(os.path.abspath('./pySICMgui/'))
            from pySICM.pysicmcore import PySicmCore
            PySicmCore(PySicmCore.CLIENT)
        else:
            usage(allargs[0])
            sys.exit(2)
if __name__ == "__main__":
    main(sys.argv)

    
