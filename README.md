
# enodes — Smarter Node Handling for Maya

**enodes** is a lightweight Python library for Autodesk Maya that makes working with nodes intuitive, clean, and fast.

If you've ever used [PyMEL](https://github.com/LumaPictures/pymel), you know the convenience it brings — but also the cost: PyMEL is notoriously slow, adding significant overhead on scene load and during complex operations. **enodes** gives you the same expressive, object-oriented workflow without sacrificing performance.

Under the hood, enodes is built directly on top of `maya.api.OpenMaya` (the Python API 2.0), giving you near-native speed while exposing a clean interface that feels as natural as `maya.cmds`. You get the best of both worlds: the readability of high-level commands and the performance of the low-level API — in a single, unified abstraction.

**Why enodes?**
- **Faster than PyMEL** — no expensive scene introspection on startup, direct `MObject` handling throughout.
- **Unified API** — seamlessly bridges `maya.cmds` convenience with `maya.api.OpenMaya` power.
- **Extensible** — register your own node classes for any Maya node type with a single call.
- **Pythonic** — attribute access, connections, and matrix operations all feel natural.

---

## Usage

### Import the base class
```python
from enodes import Node
```

### Get selected nodes using ls command
```python
selection = Node.ls( sl=True )
```

### Get a Node by name or dagpath
```python
# Returns a DagNode that represents a maya DagNode in a particular DagPath
node = Node("persp")
```

### Getting and setting attributes
```python
print( node.tx.value )
node.tx.value = node.ty.value = node.tz.value = 10

for attr in ["tx","ty","tz"]:
    node[attr].value = 10

node["r"].value = (10,10,10)
node.scale.value = (0.5,0.5,0.5)
```

### Getting the world matrix
```python
matrix = node.worldMatrix
node.worldMatrix = [0,0,0,1,0,0,1,0,0,1,0,0,1,0,0,0]
```

---

## Connections

```python
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

# iterating outputs of an attribute
for destination in node["tx"].outputs:
    print( destination )

# iterating inputs and outputs
for source, destination in node.outputs:
    print( source, destination )
```

---

## Custom Types

You can create your own class for a particular `typeName`.

```python
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
```

---

## License

See [LICENSE](LICENSE) for details.

