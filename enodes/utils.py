from maya import cmds
from maya.api.OpenMaya import MSelectionList

def iter_MObjectAndMDagPath( *names ):

    sel = MSelectionList()
	
    for name in names:
        try:
            sel.add( name )
        except RuntimeError:
            raise ValueError( "Node '%s' doesn't exists." % name )
        
        mObject = sel.getDependNode(0)
        try:
            mDagPath = sel.getDagPath(0)

            yield mObject, mDagPath
        except TypeError:
            # Object is not a DagPath
            yield mObject, None

        sel.remove(0)

def iter_MPlugs( *plugs_names ):

    sel = MSelectionList()
	
    for plug in plugs_names:
        try:
            sel.add( plug )
        except RuntimeError:
            raise ValueError( "Plug '%s' doesn't exists." % plug )
        
        yield sel.getPlug(0)

        sel.remove(0)

def splitName( name ):

    dag = name.rfind('|')
    
    if dag == -1:
        n = name.rfind(':')

        if n == -1:
            return None, None, name[ n + 1: ]
        else:
            return None, name[ :n ], name[ n + 1: ]
    else:	
        n = name.rfind( ':', dag )
        
        if n == -1:
            return name[ :dag ], None, name[ dag + 1: ]
        else:
            return name[ :dag ], name[ dag + 1:n ], name[ n + 1: ]

class UndoChunk:
    def __init__(self, undo_on_exit=True, chunk_name=None  ):
        self._undo_on_exit = undo_on_exit
        self._chunk_name = chunk_name
        self._undo_state = None

    def __enter__(self):
        self._undo_state = cmds.undoInfo(q=True,state=True)
        cmds.undoInfo(state=True)
        cmds.undoInfo( openChunk=True, chunkName=self._chunk_name )
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        is_empty = cmds.undoInfo(q=True,undoQueueEmpty=True)
        
        cmds.undoInfo( closeChunk=True )

        if not is_empty and self._undo_on_exit:
            cmds.undo()
            
        cmds.undoInfo(state=self._undo_state)