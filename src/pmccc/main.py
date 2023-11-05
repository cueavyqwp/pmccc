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

    def get_lib( self , data : dict ) -> tuple[ list , list , list ] :
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
