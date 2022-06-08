from maya import cmds
from ..node import Node

class ObjectSetNode(Node):

    def __init__( self, *args, **kwargs ):
        super( ObjectSetNode, self ).__init__( *args, **kwargs )
        self._members = ObjectSetMemberCollection( self )

    @property
    def members( self ):
        return self._members

class ObjectSetMemberCollection(object):

    def __init__( self, node ):
        self._setNode = node

    def __contains__( self, value ):
        return cmds.sets( str(value), im=str(self._setNode) )

    def __iter__( self ):
        for n in Node.ls( cmds.sets( str(self._setNode), q=True )):
            yield n

    def add( self, *members ):
        cmds.sets( members, addElement=str(self._setNode) )

    