import urllib.parse
import subprocess
import threading
import traceback
import platform
import hashlib
import sys
import os
import re

__all__ = [ "osname" , "osarch" , "osversion" , "chdir" , "check_rules" , "check_path" , "check_file" , "get_filename" , "get_download" ]

osname = str( { "win32" : "windows" , "linux" : "linux" , "cygwin" : "linux" , "darwin" : "osx" }.get( sys.platform ) ).replace( "None" , "" )
osarch = str( { "64bit" : "x64" , "32bit" : "x86" }.get( platform.architecture()[ 0 ] ) ).replace( "None" , "" )
osversion = platform.version()

chdir = lambda : os.chdir( os.path.dirname( traceback.extract_stack()[ -2 ].filename ) )

def check_rules( rules : dict | list , osname : str = osname , osarch : str = osarch , osversion : str = osversion ) -> bool :
    if isinstance( rules , dict ) :
        if "rules" in rules : rules = rules[ "rules" ]
        else : return True
    action = "disallow"
    for value in rules :
        if "os" in value :
            v = value[ "os" ]
            if "arch" in v and osarch != v[ "arch" ] : continue
            if "name" in v and osname != v[ "name" ] : continue
            if "version" in v and not re.search( v[ "version" ] , osversion ) : continue
        action = value[ "action" ]
    return action == "allow"

def check_path( path : str ) -> bool :
    if os.path.exists( path ) : return True
    os.makedirs( path )
    return False

def check_file( path : str ) -> bool :
    if os.path.exists( path ) : return True
    check_path( os.path.dirname( path ) )
    with open( path , "w" ) : pass
    return False

def check_hash( file : str | bytes , sha1 : str ) :
    if isinstance( file , str ) :
        with open( file , "rb" ) as f : file = f.read()
    hash = hashlib.sha1( file )
    hash.update( file )
    return hash.hexdigest() == sha1

def get_filename( url : str ) -> str :
    return os.path.basename( urllib.parse.urlsplit( url ).path )

def get_path( data : str | dict ) -> str :
    if isinstance( data , dict ) :
        if "path" in data : return data[ "path" ]
        name = data[ "name" ]
    else :
        name = data
    path , name = name.split( ":" , 1 )
    path = path.split( "." )
    name , version = name.split( ":" , 1 )
    version = version.split( ":" )
    path += [ name , version[ 0 ] , "-".join( [ name , *version ] ) + ".jar" ]
    return "/".join( path )

def get_download( data : dict , name : str = "" ) -> list :
    if not name and "name" in data : name = data[ "name" ]
    download = [ "" , "" , 0 , None ]
    download[ 0 ] = data[ "url" ]
    download[ 1 ] = data[ "path" ] if "path" in data else get_path( name )
    if "size" in data : download[ 2 ] = data[ "size" ]
    if "sha1" in data : download[ 3 ] = data[ "sha1" ]
    return download
