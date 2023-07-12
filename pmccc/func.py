"""
func
"""

from .errors import *
import urllib.parse
import threading
import requests
import hashlib
import json
import os

url_dict = {
    "minecraft" : {
            "manifest" : "https://piston-meta.mojang.com/mc/game/version_manifest_v2.json" ,
            "version" : "https://piston-meta.mojang.com" ,
            "data" : "https://piston-data.mojang.com" ,
            "assets" : "https://resources.download.minecraft.net" ,
            "libraries" : "https://libraries.minecraft.net" ,
            "forge" : "https://files.minecraftforge.net/maven" ,
            "fabric-meta" : "https://meta.fabricmc.net" ,
            "fabric" : "https://maven.fabricmc.net"
    } ,
    "bmclapi" : {
            "manifest" : "bmclapi2.bangbang93.com" ,
            "version" : "bmclapi2.bangbang93.com" ,
            "data" : "bmclapi2.bangbang93.com" ,
            "assets" : "bmclapi2.bangbang93.com/assets" ,
            "libraries" : "bmclapi2.bangbang93.com/maven" ,
            "forge" : "bmclapi2.bangbang93.com/maven" ,
            "fabric-meta" : "bmclapi2.bangbang93.com/fabric-meta" ,
            "fabric" : "bmclapi2.bangbang93.com/maven"
    } ,
    "mcbbs" : {
            "manifest" : "download.mcbbs.net" ,
            "version" : "download.mcbbs.net" ,
            "data" : "download.mcbbs.net" ,
            "assets" : "download.mcbbs.net/assets" ,
            "libraries" : "download.mcbbs.net/maven" ,
            "forge" : "download.mcbbs.net/maven" ,
            "fabric-meta" : "download.mcbbs.net/fabric-meta" ,
            "fabric" : "download.mcbbs.net/maven"
    }
}

def hash( data : str ) -> str :
    hash = hashlib.sha1()
    hash.update( data )
    return hash.hexdigest().lower()

def file_hash( path : str ) -> str :
    """
    get file hash
    """
    with open( path , "rb" ) as file :
        return hash( file.read() )

def the_hash( path : str , sha1 : str ) -> bool :
    return file_hash( path ) == sha1.lower()

def mkdir( path : str ) -> bool :
    """
    if directory not exist create it
    """
    if not os.path.exists( path ) :
        try :
            os.makedirs( path )
            return True
        except :
            pass
    return False

def url_replace( url : str , urls : dict , url_dict : dict = url_dict ) :
    """
    url replace
    """
    url_split = urllib.parse.urlsplit( url )
    ret = url_split.netloc
    for key , value in url_dict[ "minecraft" ].items() :
        ret = ret.replace( urllib.parse.urlsplit( value ).netloc , urls[ key ] )
    return urllib.parse.urlunsplit( [ "https" , ret , url_split.path , "" , "" ] )

def file_get( url : str , path : str , sha1 : str = None ) -> bytes :
    """
    file get
    """
    if os.path.exists( path ) :
        with open( path , "rb" ) as file :
            content = file.read()
        if hash( content ) == sha1 :
            return content
    mkdir( os.path.split( path )[ 0 ] )
    data = requests.get( url , headers = { "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 Edg/116.0.0.0" } )
    if data.status_code != 200 :
        raise StatusError( data.status_code , url )
    content = data.content
    if ( sha1 != None ) and ( not hash( content ) == sha1 ) :
        raise HashError( hash( content ) , sha1 )
    with open( path , "wb" ) as file :
        file.write( content )
    return content

def json_get( url : str , path : str , sha1 : str = None ) -> dict :
    """
    json get
    """
    return json.loads( file_get( url , path , sha1 ) )

def files_get( files : list[ dict ] ) -> None :
    thread = []
    for i in files :
        url = i [ "url" ]
        path = i[ "path" ]
        sha1 = None
        if "sha1" in i :
            sha1 = i[ "sha1" ]
        thread.append( threading.Thread( target = file_get , args = [ url , path , sha1 ] ) )
        thread[ -1 ].start()
        thread[ -1 ].join()
