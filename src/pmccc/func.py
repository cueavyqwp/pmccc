import subprocess
import platform
import sys
import os
import re

__all__ = [ "osname" , "osarch" ]

osname = str( { "win32" : "windows" , "linux" : "linux" , "cygwin" : "linux" , "darwin" : "osx" }.get( sys.platform ) ).replace( "None" , "" )
osarch = str( { "64bit" : "x64" , "32bit" : "x86" }.get( platform.architecture()[ 0 ] ) ).replace( "None" , "" )
osversion = platform.version()

def check_rules( rules : dict | list , osname : str = osname , osarch : str = osarch , osversion : str = osversion ) -> bool :
    rules = rules[ "rules" ] if isinstance( rules , dict ) else rules
    action = "disallow"
    for value in rules :
        if "os" in value :
            if "arch" in value[ "os" ] and osarch != value[ "os" ][ "arch" ] : continue
            if "name" in value[ "os" ] and osname != value[ "os" ][ "name" ] : continue
            if "version" in value[ "os" ] and not re.search( value[ "os" ][ "version" ] , osversion ) : continue
        action = value[ "action" ]
    return action == "allow"
