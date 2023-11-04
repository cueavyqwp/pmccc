from . import network
from . import func

__all__ = [ "main" ]

class main :

    @property
    def ossplit( self ) -> str :
        return ";" if self.os[ 0 ] == "windows" else ":"

    @property
    def oslibsuffx( self ) -> str :
        return str( { "windows" : "dll" , "linux" : "so" , "osx" : "dylib" }.get( self.os[ 0 ] ) )

    def __init__( self , path : str = "./minecraft" ) -> None :
        self.os = [ func.osname , func.osarch , func.osversion ]
        self.path = path

    def get_lib( self , data ) :
        """
        test
        """
        downloads , libraries , natives = [] , [] , []
        add = lambda value : downloads.append( [ value[ "url" ] , value[ "path" ] , value[ "size" ] , value[ "sha1" ] ] )
        for value in [ value for value in data if func.check_rules( value , *self.os ) ] :
            if "natives" in value :
                v = value[ "downloads" ][ "classifiers" ][ value[ "natives" ][ self.os[ 0 ] ] ]
                natives.append( v[ "path" ] )
                add( v )
            v = value[ "downloads" ][ "artifact" ]
            libraries.append( v[ "path" ] )
            add( v )
        return downloads , libraries , natives
