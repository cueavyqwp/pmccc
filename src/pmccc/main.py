from . import network
from . import func

__all__ = [ "main" ]

class main :

    def __init__( self , path : str = "./minecraft" ) -> None :
        self.path = path
