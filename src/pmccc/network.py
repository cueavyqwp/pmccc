import urllib.parse
import requests
import re

__all__ = [ "urls" , "mirrors" , "url" , "download" ]

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
        if mirrors in self.mirrors :
            parse = urllib.parse.urlsplit( url )
            for key in self.mirrors[ mirrors ].keys() :
                mirror = urllib.parse.urlsplit( self.mirrors[ mirrors ][ key ] ) if re.search( key , url ) else None
                if mirror is not None : return urllib.parse.urlunsplit( [ "https" , mirror.netloc , mirror.path + parse.path , "" , "" ] )
        return url

    @property
    def mirror_list( self ) -> list[ str ] :
        return list( self.mirrors.keys() )

class download( url ) :

    def __init__( self ) :
        self.header = { "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64)" }
        self.mirror = ""
        self.proxy = {}
        super().__init__()

    def __call__( self , url : str , file : str ) -> None :
        url = super().__call__( url , self.mirror )
        response = requests.get( url , headers = self.header , proxies = self.proxy , stream = True )
