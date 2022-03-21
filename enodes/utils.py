from maya.api.OpenMaya import MSelectionList

def iter_MObjectAndMDagPath( *names ):

    sel = MSelectionList()
	
    for index, name in enumerate( names ):
        try:
            sel.add( name )
        except RuntimeError:
            raise ValueError( "Node '%s' doesn't exists." % name )
        
        mObject = sel.getDependNode( index )
        try:
            mDagPath = sel.getDagPath( index )

            yield mObject, mDagPath
        except TypeError:
            # Object is not a DagPath
            yield mObject, None
            pass

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