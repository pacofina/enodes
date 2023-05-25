
Easer way to work with nodes in maya
=========================

### Import the base class
```from enodes import Node```

### Get selected nodes using ls command
```selection = Node.ls( sl=True )```

### Get a Node by name or dagpath
```
# Returns a DagNode that reperesets a maya DagNode in a particular DagPath
node = Node("persp")
```

### Getting and setting attributes
```
print( node["tx"].value )
node["tx"].value = node["ty"].value = 10
node["r"].value = (10,10,10)
```

### Getting the world matrix
```
matrix = node.worldMatrix
node.worldMatrix = [0,0,0,1,0,0,1,0,0,1,0,0,1,0,0,0]
```

CONNECTIONS
-----------------
```
# get the input of an attribute
input = node["v"].input # return node

# you can connect an attribute by assigning its input. 
node["tx"].input = Node("time1")["output"]
# or
node["tx"].input = "time1.output"

# force to create a connection
node["tx"].connect( "time1.output", force=True )
# or
Node("time1")["output"].connectTo( node["tx"], force=True )

# disconnecting the attribute
node["tx"].input = None
# or
node["tx"].disconnect()

# itarating outputs of an attribute
for destination in node["tx"].outputs:
    print( destination )

# iterating inputs and outputs
for source, destination in node.outputs:
    print( source, destination )
```

CUSTOM TYPES
-----------------
You can create your own class for a particular typeName.

```
from enodes import Node, registerCustomType

class ObjectSetNode(Node):

  @property
  def members( self ):
    """Returns the members of the set"""
    return Node.ls( cmds.sets( str(self), q=True ) )

# register your custom type
registerCustomType( 'objectSet', ObjectSetNode )

# create a new node
obj_set = Node.create( 'objectSet' )
print( type(obj_set) )
print( obj_set.members )

