import tempfile
import zipfile
import shutil
import os

from . import network
from . import func

__all__ = [ "main" ]

class main :

    @property
    def ossplit( self ) -> str :
        return ";" if self.os[ 0 ] == "windows" else ":"

    @property
    def oslibsuffx( self ) -> str :
        return str( { "windows" : ".dll" , "linux" : ".so" , "osx" : ".dylib" }.get( self.os[ 0 ] ) )

    def __init__( self ) -> None :
        self.os = [ func.osname , func.osarch , func.osversion ]

    def unzip_natives( self , natives : list , path : str , oslibsuffx : str | None = None ) -> None :
        path = os.path.normpath( path )
        if oslibsuffx is None : oslibsuffx = self.oslibsuffx
        if os.path.exists( path ) : shutil.rmtree( path )
        os.mkdir( path )
        [ zipfile.ZipFile( file , "r" ).extractall( path ) for file in natives ]
        for file in os.listdir( path ) :
            file = os.path.join( path , file )
            if os.path.isdir( file ) : shutil.rmtree( file )
            elif os.path.splitext( file )[ -1 ] != oslibsuffx : os.remove( file )

    def get_java( self ) -> list :
        javas = []
        path = os.environ[ "path" ].split( self.ossplit )
        if "JAVA_HOME" in os.environ : path.append( os.environ[ "JAVAHOME" ] )
        for path in { s for s in path if os.path.exists( s ) and os.path.isdir( s ) } :
            if not any( ( l := os.path.splitext( p ) )[ 0 ] == "javaw" for p in os.listdir( path ) ) : continue
            data = func.get_java( os.path.normpath( os.path.join( path , "".join( l ) ) ) )
            if data : javas.append( data )
        return javas

    def get_lib( self , data : dict ) -> tuple[ list , list , list ] :
        if "libraries" in data : data = data[ "libraries" ]
        downloads , libraries , natives = [] , [] , []
        add = lambda value , name = "" : downloads.append( func.get_download( value , name ) )
        for value in [ value for value in data if func.check_rules( value , *self.os ) ] :
            if "natives" in value :
                v = value[ "downloads" ][ "classifiers" ][ value[ "natives" ][ self.os[ 0 ] ] ]
                natives.append( func.get_path( v ) )
                add( v )
            if "downloads" in value :
                v , name = value[ "downloads" ][ "artifact" ] , value[ "name" ]
            else :
                v , name = value , ""
            libraries.append( func.get_path( v ) )
            add( v , name )
        return downloads , libraries , natives

    def get_args( self , data : dict ) -> tuple[ list , list ] :
        if "arguments" in data : data = data[ "arguments" ]
        javaargs , gameargs = [] , [ value for value in data[ "game" ] if isinstance( value , str ) ]
        for value in data[ "jvm" ] :
            if isinstance( value , str ) : javaargs.append( value )
            elif func.check_rules( value , *self.os ) : javaargs += func.tolist( value[ "value" ] )
        return javaargs , gameargs
