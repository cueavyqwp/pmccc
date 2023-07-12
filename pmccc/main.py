"""
main
"""

from .errors import *
from . import func

import subprocess
import zipfile
import json
import sys
import os

class libs :
    """
    libs
    """

    def __init__( self , cp_lib : list[ dict ] , natives_lib : list[ dict ] ) -> None :
        self.libs = [ i[ "path" ] for i in cp_lib ]
        self.natives = [ i[ "path" ] for i in natives_lib ]


class player :
    """
    player
    """

    def __init__( self , name : str , uuid : str = None ) -> None :
        self.online = False
        if uuid == None :
            self.uuid = "a0a1a2a3a4a5a6a7fb1b2b3b4b5b6b7f"
        self.token = self.uuid
        self.name = name

class main :
    """
    pmccc
    """

    def __init__( self , path : str = ".minecraft" , name : str = "" , version : str = "" ) -> None :
        """
        init
        """
        path = os.path.abspath( path )
        self.path = {
            "libraries" : os.path.join( path , "libraries" ) ,
            "versions" : os.path.join( path , "versions" ) ,
            "assets" : os.path.join( path , "assets" ) ,
            "root" : path
        }
        self.java_use = {
            8 : [ "1.8" ] ,
            16 : [ "16" , "17" ] ,
            17 : [ "17" , "18" , "19" ] ,
        }
        for path in self.path.values() :
            func.mkdir( path )
        os_type = sys.platform
        self.cp_split = ":"
        if os_type == "win32" :
            self.os = "windows"
            self.cp_split = ";"
        elif os_type == "linux" :
            self.os = "linux"
        else :
            self.os = "osx"
        self.use_url = "minecraft"
        self.urls = func.url_dict
        self.version = version
        self.name = name
        self.javas = {}

    def url_replace( self , url : str ) -> str :
        """
        url replace
        """
        if self.use_url == "minecraft" :
            return url
        else :
            return func.url_replace( url , self.urls[ self.use_url ] , self.urls )

    def get_manifest( self ) -> dict :
        """
        get manifest
        """
        return func.json_get( self.url_replace( self.urls[ "minecraft" ][ "manifest" ] ) , os.path.join( self.path[ "versions" ] , "manifest.json" ) )

    def java_get( self ) -> list :
        """
        get_javas
        """
        self.javas = {}
        for i in os.environ[ "PATH" ].split( self.cp_split ) :
            if "bin" in i and os.path.exists( i ) :
                for file in os.listdir( i ) :
                    if file in [ "javaw.exe" , "javaw" ] :
                        for l in subprocess.check_output( [ os.path.join( i , "java" ) , "-version" ] , stderr = subprocess.STDOUT ).decode().split( "\"" ) :
                            for s in l :
                                if s not in [ str( n ) for n in range( 10 ) ] + [ "." , "_" , "-" ] :
                                    break
                            else :
                                self.javas[ l ] = i
        if not len( self.javas.items() ) :
            raise func.JavaNotFindError()
        return self.javas

    def java( self , version : str ) -> str :
        path = os.path.join( self.path[ "versions" ] , version , version + ".json" )
        with open( path , "rb" ) as file :
            json_data = json.load( file )
        java_version = json_data[ "javaVersion" ][ "majorVersion" ]
        javas = self.java_use[ java_version ]
        ret = []
        for key , value in self.javas.items() :
            for i in javas :
                if i in key :
                    ret.append( value )
        if not len( ret ) :
            raise JavaNotFindError( javas )
        return ret

    def install_version( self , mc_version : str , version : str , manifest : dict = None , jar_type : str = "client" ) -> None :
        """
        install version
        """
        name = version
        if not os.path.isabs( name ) :
            path = os.path.join( self.path[ "versions" ] , name )
        else :
            path = name
            name = os.path.split( path )[ -1 ]
        if manifest == None :
            manifest = self.get_manifest()
        for i in manifest[ "versions" ] :
            if i[ "id" ] == mc_version :
                json_url = self.url_replace( i[ "url" ] )
                json_hash = i[ "sha1" ]
                break
        else :
            raise KeyError( f"version not find { mc_version }" )
        json_data = func.json_get( json_url , os.path.join( path , name + ".json" ) , json_hash )
        if jar_type == "client" :
            jar_path = os.path.join( path , name + ".jar" )
        else :
            jar_path = os.path.join( path , f" { name }-{ jar_type }.jar" )
        jar_url = self.url_replace( json_data[ "downloads" ][ jar_type ][ "url" ] )
        jar_hash = json_data[ "downloads" ][ jar_type ][ "sha1" ]
        func.file_get( jar_url , jar_path , jar_hash )

    def install_assets( self , version : str ) -> None :
        """
        install assets
        """
        name = version
        path = self.path[ "assets" ]
        with open( os.path.join( self.path[ "versions" ] , name , name + ".json" ) , "r" , encoding = "utf-8" ) as file :
            json_data = json.load( file )
        assets_path = os.path.join( path , "indexes" , json_data[ "assets" ] + ".json" )
        assets_url = json_data[ "assetIndex" ][ "url" ]
        assets_hash = json_data[ "assetIndex" ][ "sha1" ]
        assets_data = func.json_get( assets_url , assets_path , assets_hash )
        files = []
        for i in assets_data[ "objects" ].values() :
            sha1 = i[ "hash" ]
            files.append( {
                "url" : f"""{ self.url_replace( self.urls[ "minecraft" ][ "assets" ] ) }/{ sha1[ :2 ] }/{ sha1 }""" ,
                "path" : os.path.join( path , "objects" , sha1[ :2 ] , sha1 ) ,
                "sha1" : sha1
                } )
        func.files_get( files )

    def install_libraries( self , version : str ) -> libs :
        """
        install libraries
        """
        name = version
        path = self.path[ "libraries" ]
        with open( os.path.join( self.path[ "versions" ] , name , name + ".json" ) , "r" , encoding = "utf-8" ) as file :
            json_data = json.load( file )
        natives_lib = []
        cp_lib = []
        files = []
        for i in json_data[ "libraries" ] :
            use = True
            if "rules" in i :
                use = False
                for r in i["rules"] :
                    if "os" in r :
                        if self.os not in r[ "os" ].values() :
                            continue
                    use = func.use_dict[ r[ "action" ] ]
            if not use :
                continue
            if "classifiers" in i[ "downloads" ] :
                if self.os in i[ "natives" ] and i[ "natives" ][ self.os ] in i[ "downloads" ][ "classifiers" ] :
                    natives_lib.append( i[ "downloads" ][ "classifiers" ][ i[ "natives" ][ self.os ] ] )
                    natives_lib[ -1 ][ "path" ] = os.path.join( path , natives_lib[ -1 ][ "path" ] )
            else :
                cp_lib.append( i[ "downloads" ][ "artifact" ] )
                cp_lib[ -1 ][ "path" ] = os.path.join( path , cp_lib[ -1 ][ "path" ] )
        for i in natives_lib + cp_lib :
            files.append( {
                "url" : self.url_replace( i[ "url" ] ) ,
                "path" : os.path.join( path , i[ "path" ] ) ,
                "sha1" : i[ "sha1" ]
                } )
        func.files_get( files )
        return libs( cp_lib , natives_lib )

    def unzip_natives( self , lib : libs , version : str ) -> None :
        """
        unzip natives
        """
        name = version
        path = os.path.join( self.path[ "versions" ] , name , f"{ name }-natives" )
        func.mkdir( path )
        for i in lib.natives :
            with zipfile.ZipFile( i ) as file :
                file.extractall( path )

    def get( self , player : player , version : str ) :
        """
        get
        """
        lib = self.install_libraries( version )
        self.install_assets( version )
        self.unzip_natives( lib , version )
        return self.args( lib , player , version )

    def run( self , player : player , version : str , java : str = None ) :
        """
        run
        """
        if java == None :
            self.java_get()
            java = os.path.join( self.java( version )[ 0 ] , "java" )
        args = self.get( player , version )
        os.system( f"{ java } {args}" )

    def args( self , lib : libs , player : player , version : str ) :
        """
        args
        """
        lib_str = ""
        args = ""
        for i in lib.libs :
            lib_str += i + self.cp_split
        path = os.path.join( self.path[ "versions" ] , version )
        natives = os.path.join( path , f"{ version }-natives" )
        with open( os.path.join( path , version + ".json" ) , "rb" ) as file :
            json_data = json.load( file )
        main_class = json_data[ "mainClass" ]
        lib_str = f"""\"{ lib_str }{ os.path.join( path , version + ".jar" ) }\" { main_class }"""

        l = [
            f"-XX:+UseG1GC" ,
            "-XX:-UseAdaptiveSizePolicy" ,
            "-XX:-OmitStackTraceInFastThrow" ,
            "-Dfml.ignoreInvalidMinecraftCertificates=True" ,
            "-Dfml.ignorePatchDiscrepancies=True" ,
            "-Dlog4j2.formatMsgNoLookups=true"
        ]
        if "arguments" in json_data :
            l += [
                "-Dos.name=\"Windows 10\"" ,
                "-Dos.version=10.0"
            ]
            for i in json_data["arguments"]["jvm"] :
                if isinstance( i , str ) :
                    i = "".join( i.split() )
                    l.append(i)
            for i in json_data["arguments"]["game"] :
                    if isinstance( i , str ) :
                        l.append(i)
        else :
            l += [
                "-Djava.library.path=${natives_directory}" ,
                "-cp ${classpath}"
            ]
            for i in json_data["minecraftArguments"].split() :
                l.append(i)
        for i in l :
            args += i + " "

        return args.replace("${auth_player_name}" , "Dev" ) \
        .replace("${version_name}" , version ) \
        .replace("${game_directory}" , f"\"{ path }\"" ) \
        .replace("${assets_root}" , f"""\"{ self.path[ "assets" ] }\"""" ) \
        .replace("${game_assets}" , f"""\"{ self.path[ "assets" ] }\"""" ) \
        .replace("${assets_index_name}" , json_data["assets"] ) \
        .replace("${auth_uuid}" , player.uuid ) \
        .replace("${auth_access_token}" , player.token ) \
        .replace("${user_type}" , "msa" ) \
        .replace("${version_type}" , self.name ) \
        .replace("${natives_directory}" , f"\"{ natives }\"" ) \
        .replace("${launcher_name}" , self.name ) \
        .replace("${launcher_version}" , self.version ) \
        .replace("${classpath}" , lib_str ) \
        .replace("${library_directory}" , f"""\"{ self.path[ "libraries" ] }\"""" ) \
        .replace("${classpath_separator}" , ";" ) \
        .replace("${user_properties}" , "{}" )
