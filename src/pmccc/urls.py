import urllib.parse
import re

__all__ = [ "urls" , "mirrors" , "url" ]

urls = {
    "version" : "https://launchermeta.mojang.com/mc/game/version_manifest_v2.json" ,
    "assets" : "https://piston-data.mojang.com/v1/objects" ,
}

mirrors = {
    "bmclapi" : {
        "launchermeta.mojang.com" : "https://bmclapi2.bangbang93.com" ,
        "piston-meta.mojang.com" : "https://bmclapi2.bangbang93.com" ,
        "piston-data.mojang.com/v1/objects" : "https://bmclapi2.bangbang93.com" ,
        "piston-data.mojang.com" : "https://bmclapi2.bangbang93.com/assets" ,
        "libraries.minecraft.net" : "https://bmclapi2.bangbang93.com/maven" ,
    }
}
mirrors[ "mcbbs" ] = { key : value.replace( "bmclapi2.bangbang93.com" , "download.mcbbs.net" ) for key , value in mirrors[ "bmclapi" ].items() }

class url :

    def __init__( self , urls : dict[ str , str ] = urls , mirrors : dict[ str , dict[ str , str ] ] = mirrors ) -> None :
        self.mirrors = mirrors
        self.urls = urls

    def __call__( self , url : str , mirrors : str = "" ) -> str :
        if mirrors is not None and mirrors in self.mirrors :
            parse = urllib.parse.urlsplit( url )
            for key in self.mirrors[ mirrors ].keys() :
                mirror = urllib.parse.urlsplit( self.mirrors[ mirrors ][ key ] ) if re.search( key , url ) else None
                if mirror is not None : return urllib.parse.urlunsplit( [ "https" , mirror.netloc , mirror.path + parse.path , "" , "" ] )
        return url

    @property
    def mirror( self ) -> list[ str ] :
        return list( self.mirrors.keys() )
