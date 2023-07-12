"""
pmccc
"""

import pmccc
import os

main = "home"
guis = {}

class gui :
    def __init__( self , key : str , func ) :
        self.func = func
        guis[ key ] = self
    def __call__( self ) :
        return self.func()

def cls() -> None :
    if os.name == "nt" :
        os.system( "cls" )
    else :
        os.system( "clear" )

def home() :
    print( """[0] get versions
[1] instll versions
[2] run version
[3] exit""")
    def _( num : str ) :
        global main
        if num :
            n = num[ 0 ]
            if n in guis.keys() and n.isalnum() :
                main = n
    return _
gui( "home" , home )
gui( "3" , exit )

root = pmccc.main( ".\.minecraft" , "Demo" , "0.01" )
player = pmccc.player( "Dev" )

while 1 :
    cls()
    f = guis[ main ]()
    n = None
    try :
        n = input( ">" )
    except :
        main = "3"
    f( n )
