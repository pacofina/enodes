"""
Libreria por Paco Fina - Diciembre 2012
pacofina@gmail.com
"""

import re
import maya.cmds         as mc
import maya.api.OpenMaya as om

class Node(object):

	@staticmethod
	def ls( *args, **kwArgs ):
		ls = mc.ls( *args, **kwArgs )
			
		return NodeList( ls )

	@staticmethod
	def one( *args, **kvArgs ):
		ls = Node.ls( *args, **kvArgs )

		if len(ls) > 1:
			raise Exception( "More than one node was found." )
		
		try:
			return ls[0]
		except IndexError:
			raise Exception( "No node was found." )

	@staticmethod
	def create( type, **args ):
		return Node( mc.createNode( type, **args ), False )

	@staticmethod
	def getSelectedAttrs():
		
		import maya.mel as mel
		channelBox = mel.eval('global string $gChannelBoxName; $temp=$gChannelBoxName;')	#fetch maya's main channelbox
		
		sel = []
		
		# Objects
		for n in NodeList( mc.channelBox( channelBox, q=True, mainObjectList=True ) ):
			attrs = mc.channelBox( channelBox, q=True, selectedMainAttributes=True )
			
			if attrs:
				for attr in attrs:
					sel.append( n[attr] )

		# Shape
		for n in NodeList( mc.channelBox( channelBox, q=True, shapeObjectList=True ) ):
			attrs = mc.channelBox( channelBox, q=True, selectedShapeAttributes=True )
			
			if attrs:
				for attr in attrs:
					sel.append( n[attr] )
		
		# History
		for n in NodeList( mc.channelBox( channelBox, q=True, historyObjectList=True ) ):
			attrs = mc.channelBox( channelBox, q=True, selectedHistoryAttributes=True )
			
			if attrs:
				for attr in attrs:
					sel.append( n[attr] )

		# Outputs
		for n in NodeList( mc.channelBox( channelBox, q=True, outputObjectList=True ) ):
			attrs = mc.channelBox( channelBox, q=True, selectedOutputAttributes=True )
			
			for attr in attrs:
				sel.append( n[attr] )

		return sel

	@staticmethod
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

	@staticmethod
	def _fromMSelectionList( mSelectionList, index ):

		n, d = Node._getNodeAndPath( mSelectionList, index )
		return Node( None, mFnDependencyNode=n, mDagPath=d )
			
	@staticmethod
	def _getNodeAndPath( mSelectionlist, index ):
		
		try:
			mFnDependencyNode = om.MFnDependencyNode( mSelectionlist.getDependNode( index ) )
			mDagPath          = mSelectionlist.getDagPath( index )
		except TypeError:
			mDagPath          = None
			pass # Object is not a DagPath

		return mFnDependencyNode, mDagPath
	
	def __init__( self, name, mFnDependencyNode=None, mDagPath=None ):

		if name:
			try:
				sel = om.MSelectionList()
				sel.add( name )

				mFnDependencyNode, mDagPath = Node._getNodeAndPath( sel, 0 )
			except RuntimeError:
				raise ValueError( "Node '%s' doesn't exists." % name )

		self._MFnDependencyNode = mFnDependencyNode
		self._MDagPath          = mDagPath

		self._attributes = None
		self._animation  = None
		
	def __str__( self ):
		
		if self._MDagPath:
			return self._MDagPath.partialPathName()
		else:
			return self.name
	
	def __repr__(self):
		return str(self)

	def __getitem__( self, attribute ):
		return self.attributes[ attribute ]
	
	def __eq__( self, other ):
		return str(self) == str(other)

	def __ne__( self, other ):
		return not self.__eq__( other )

	def __hash__( self ):
		return self._MFnDependencyNode.userNode().__hash__()
	
	@property
	def isDagNode( self ):
		return bool(self._MDagPath)

	@property
	def name( self ):
		return self._MFnDependencyNode.name()

	@name.setter
	def name( self, value ):
		
		try:
			ns = value[ :value.rindex(':') ]
		except ValueError:
			ns = None
		
		if ns and not Namespace.exists( ns ):
			raise ValueError( "Namespace '"+ ns +"' doesn't exist." )
		
		with Namespace( ":" ):
			mc.rename( str(self), value, ignoreShape=True )

	def rename( self, value ):
		mc.rename( str(self), value )

	@property
	def nameWithoutNamespace( self ):
		return Node.splitName( self.name )[2]
	
	@nameWithoutNamespace.setter
	def nameWithoutNamespace( self, value ):
		
		if ':' in value or '|' in value:
			raise ValueError( "Invalid node name '%s'." % value )

		self.name = str(self.namespace) +":"+ value
			
	@property
	def namespace( self ):
		return Namespace.fromNodeName( self.name )

	@namespace.setter
	def namespace( self, value ):
		value.add( self )

	@property
	def type( self ):
		return mc.nodeType( str(self) )

	@property
	def locked( self ):
		return mc.lockNode( str(self), q=True )[0]
	
	@locked.setter
	def locked( self, value ):
		mc.lockNode( str(self), lock=value )

	@property
	def root( self ):
		parent = self.parent

		if parent:
			return parent.root
		else:
			return self
	
	@property
	def parent( self ):
		p = mc.listRelatives( str(self), parent=True, path=True )

		if p:
			return Node( p[0], False )
		else:
			return None
			
	@parent.setter
	def parent( self, value ):
		self._parent( value, world=not bool(value) )

	def addInstanceTo( self, value=None ):
		self._parent( value, world=not bool(value), add=True )

	def removeInstance( self ):
		self._parent( None, rm=True )

	def _parent( self, value, **args ):

		nodes = [str(self),str(value)] if value else [str(self)]
		
		try:
			isShape  = self.isShape or self.type == "unknownDag"
			relative = args.pop( "relative", isShape )
			mc.parent( *nodes, shape=isShape, relative=relative, **args )
		except RuntimeError as e:
			#raise RuntimeError( "Can't parent '%s' to '%s'." % (self,value) )
			#raise RuntimeError( "Can't parent '%s' to world." % self )
			raise e			

	@property
	def worldMatrix( self ):
		return mc.xform( str(self), q=True, matrix=True, worldSpace=True )
	
	@worldMatrix.setter
	def worldMatrix( self, value ):
		mc.xform( str(self), matrix=value, worldSpace=True )
	
	@property
	def childNodes( self ):
		return self.children

	@property
	def children( self ):
		return NodeList( mc.listRelatives( str(self), path=True ) )

	@property
	def attrs( self ):
		return self.attributes
	
	@property
	def attributes( self ):
		if self._attributes == None:
			self._attributes = NodeAttributeCollection( self )

		return self._attributes

	@property
	def animation( self ):
		if self._animation == None:
			self._animation = Animation( [self.name] )

		return self._animation

	@property
	def connections( self ):
		return NodeConnectionList( self )

	@property
	def outputs( self ):
		return NodeConnectionList( self, source=False )

	@property
	def inputs( self ):
		return NodeConnectionList( self, destination=False )

	def getInputs( self, **args ):
		return NodeList( [str(self)] ).getInputs( **args )

	def getOutputs( self, **args ):
		return NodeList( [str(self)] ).getOutputs( **args )

	@property
	def isShape( self ):
		return mc.objectType( str(self), isAType="shape")

	@property
	def shapes( self ):
		
		return NodeList( mc.listRelatives( str(self), shapes=True, ni=True, path=True ) )
	
	# Returns an iterator
	def getShapes( self, recursive=False ):
		
		if recursive:
			childs = mc.listRelatives( str(self), type="transform" )

			# Children Shapes
			if childs:
				for child in childs:
					for shape in Node( child, False ).getShapes( True ):
						yield shape

		# Shapes
		for shape in self.shapes:
			yield shape
	
	def delete( self ):
		mc.delete( str(self) )
		
	def createInstance( self, **kwArgs ):
	
		return Node( mc.instance( str(self), **kwArgs )[0], False )
	
	def createIntermediateObject( this ):
		iop = Node( mc.duplicate( str(this) )[0] )
		io  = iop.shapes[0]
		mc.parent( str(io), str(this.parent), s=True, add=True )
		mc.delete( str(iop) )
		io["io"].value = True

		return io
	
	@property
	def isReferenced( this ):
		return mc.referenceQuery( str(this), isNodeReferenced=True )

	@property
	def referenceNode( this ):
		try:
			return Node( mc.referenceQuery( str(this), referenceNode=True ) )
		except:
			return None

	def referenceFile( self ):
		return self.getReferenceFile( widthoutCopyNumber=True )

	def getReferenceFile( self, withoutCopyNumber=False ):
		return mc.referenceQuery( str(self), filename=True, withoutCopyNumber=withoutCopyNumber )

	def isLoaded( self ):
		return mc.referenceQuery( str(self), isLoaded=True )

	def loadReference( self ):
		mc.file( self.getReferenceFile(), loadReference=str(self) )

	def unloadReference( self ):
		referenceFile = mc.referenceQuery( str(self), filename=True )
		mc.file( self.getReferenceFile(), unloadReference=True )

	def removeReference( self, removeRemainingNodes=False ):
		mc.file( self.getReferenceFile(), removeReference=True, force=removeRemainingNodes )

	@property
	def referenceNamespace( self ):
		return mc.referenceQuery( str(self), namespace=True )

	@referenceNamespace.setter
	def referenceNamespace( self, value ):
		# Avoid to assign the same value because maya will add a number at the end.
		if value.lstrip(":") != self.referenceNamespace.lstrip(":"):
			mc.file( self.getReferenceFile(), e=True, namespace=value )
		

class NodeAttribute(object):

	@staticmethod
	def fromName( name ):
		p = name.index('.')
		return NodeAttribute( Node( name[ :p ] ), name[ p+1: ] )
	
	def __init__( self, node, attribute ):
		self._node      = node
		self._attribute = attribute

	def __str__( self ):
		return str(self._node) +"."+ self._attribute

	def __repr__(self):
		return str(self)

	def __getitem__( self, index ):
		if isinstance( index, int ):
			return self._getByIndex( index )
		else:
			return NodeAttribute( self._node, self._attribute +"."+ index )

	def _getByIndex( self, index ):
		return NodeAttribute( self._node, self._attribute +"[%d]" % index )

	def __iter__( self ):
		indexes = mc.getAttr( str(self), multiIndices=True )
		
		if indexes:
			for index in indexes:
				yield self._getByIndex( index )
			
	def __eq__( self, other ):
		return str(self) == str(other)

	def __ne__( self, other ):
		return not self.__eq__( other )
	
	def __cmp__( self, other ):
		return str(self) == str(other)
	
	def __hash__( self ):
		return str(self).__hash__()

	def __len__( self ):
		return self.length
	
	@property
	def node( self ):
		return self._node

	@property
	def name( self ):
		return self._attribute

	@name.setter
	def name( self, value ):
		mc.renameAttr( str(self), value )

	@property
	def shortName( self ):
		return mc.attributeQuery( self._attribute, node=str(self._node), shortName=True )
	
	@property
	def index( self ):
		try:
			n = self._attribute
			return int(n[ n.rindex('[')+1:-1 ])
		except:
			raise TypeError( "Attribute is not inxeded." )

	@property
	def niceName( self ):
		return mc.attributeName( str(self), nice=True )
	
	@niceName.setter
	def niceName( self, value ):
		mc.addAttr( str(self), e=True, nn=value )
	
	@property
	def alias( this ):
		return mc.aliasAttr( str(this), q=True )

	@alias.setter
	def alias( this, value ):
		return mc.aliasAttr( value, str(this) )

	@property
	def type( self ):
		return mc.getAttr( str(self), type=True )

	@property
	def length( self ):
		return mc.getAttr( str(self), size=True )

	@length.setter
	def length( self, value ):
		return mc.setAttr( str(self), size=value )

	@property
	def value( self ):
		type  = self.type
		value = mc.getAttr( str(self) )

		if type == "float3" or type == "double3":
			return value[0]
		elif type == "componentList":
			raise Exception()
		else:
			return value
	
	@value.setter
	def value( self, value ):
		type = self.type
		
		if type == "float3" or type == "double3":
			mc.setAttr( str(self), value[0], value[1], value[2] )
		elif type == "matrix" or type == "string":
			mc.setAttr( str(self), value, type=type )
		else:
			mc.setAttr( str(self), value )

	@property
	def locked( self ):
		return mc.getAttr( str(self), lock=True )

	@locked.setter
	def locked( self, value ):
		mc.setAttr( str(self), lock=value )
	
	@property
	def hidden( self ):
		return not self.keyable and not mc.getAttr( str(self), channelBox=True )
	
	@hidden.setter
	def hidden( self, value ):
		mc.setAttr( str(self), channelBox=not value )
	
	@property
	def keyable( self ):
		return mc.getAttr( str(self), keyable=True )
	
	@keyable.setter
	def keyable( self, value ):
		mc.setAttr( str(self), keyable=value )

	@property
	def minValue( self ):
		if mc.attributeQuery( self._attribute, node=str(self._node), minExists=True ):
			return mc.attributeQuery( self._attribute, node=str(self._node), minimum=True )[0]
		else:
			return None
	
	@minValue.setter
	def minValue( self, value ):
		raise NotImplemented()

	@property
	def maxValue( self ):
		if mc.attributeQuery( self._attribute, node=str(self._node), maxExists=True ):
			return mc.attributeQuery( self._attribute, node=str(self._node), maximum=True )[0]
		else:
			return None

	@maxValue.setter
	def maxValue( self, value ):
		raise NotImplemented()

	@property
	def children( self ):
		raise NotImplemented()

	@property
	def input( self ):
		conn = mc.connectionInfo( str(self), sourceFromDestination=True )
		
		if conn:
			return NodeAttribute( Node( conn[ :conn.index('.') ], False ), conn[ conn.index('.') + 1: ] )
		else:
			return None

	@input.setter
	def input( self, value ):
		if value:
			mc.connectAttr( str(value), str(self) )
		else:
			self.disconnect()
	
	@property
	def inputConnection( self ):
		return self.input

	@inputConnection.setter
	def inputConnection( self, value ):
		self.input = value
	
	@property
	def outputs( self ):
		return NodeAttributeList( mc.connectionInfo( str(self), destinationFromSource=True ) )
	
	def connect( self, source, **args ):
		mc.connectAttr( str(source), str(self), **args )
	
	def connectTo( self, destination, **args ):
		mc.connectAttr( str(self), str(destination), **args )

	def disconnect( self ):
		destination = str(self)
		source      = mc.connectionInfo( destination, sourceFromDestination=True )
		
		if destination:
			mc.disconnectAttr( source, destination )

	def isConnected( self ):
		raise NotImplemented()
		
	def setKey( self, time=None ):
	
		if time != None:
			mc.setKeyframe( str(self._node), at=self._attribute, time=time )
		else:	
			mc.setKeyframe( str(self._node), at=self._attribute )
		
	@property
	def hasKeys( self ):
	
		return mc.keyframe( str(self), q=True, keyframeCount=True ) > 0
	
	@property
	def hasAnimatedConstantValue( self ):
		attr = str(self)
		tKey = mc.keyframe( attr, query=True )
		
		if not tKey or len(tKey) == 1:
			return True
		
		r     = True
		value = mc.keyframe( attr, time=(tKey[0],tKey[0]), q=True, eval=True )
		
		for t in KeyframeList._drange( tKey[1], tKey[-1], 1.0 ):
			if value != mc.keyframe( attr, time=(t,t), q=True, eval=True ):
				r = False
				break
				
		return r

	def delete( this ):
		mc.deleteAttr( str(this) )

	def findByAlias( this, alias ):
		
		for attr in this:
			if attr.alias == alias:
				return attr

		return None

class NodeConnectionList(object):
	
	def __init__( self, node, source=True, destination=True, **args ):
		self._node = node
		self._args = args
		self._args.update( source=source, destination=destination )
		
		self._mode = 0 if source and destination else 1 if source else 2

	def __getitem__( self, value ):

		if isinstance( value, int ):
			s, d = list(self._iterPlugs())[value]
			NodeAttribute.fromName( s ), NodeAttribute.fromName( d )
		else:
			return NodeConnectionList( self._node, type=value )
	
	def __iter__( self ):
		for s, d in self._iterPlugs():
			yield NodeAttribute.fromName( s ), NodeAttribute.fromName( d )

	def __bool__( self ):
		return next( (True for n in self._iterPlugs()), False )
	
	def _iterPlugs( self ):
		conns = mc.listConnections( str(self._node), plugs=True, connections=True, **self._args ) or []
		
		if self._mode == 1:
			z = zip( conns[1::2], conns[0::2] )
		elif self._mode == 2:
			z = zip( conns[0::2], conns[1::2] )
		else:
			raise NotImplementedError( "Can't list sources and destinations in the same list." )

		return z
	
	@property
	def nodes( self ):
		if self._args:
			conns = mc.listConnections( str(self._node), **self._args )
		else:
			conns = mc.listConnections( str(self._node) )
		
		out = []

		if conns:
			for conn in conns:
				if not conn in out:
					out.append( conn )
					yield Node( conn, False )

class NodeList(object):
	
	def __init__( self, innerList ):
		
		if innerList:
			self._innerList = innerList
		else:
			self._innerList = []
		
		self._MSelectionList = om.MSelectionList()
		
		for n in self._innerList:
			try:
				self._MSelectionList.add( n )
			except:
				raise Exception( "Object '%s' doesn't exists" % n )
		
		self._animation = None
		
	def __iter__( self ):
		
		length = self._MSelectionList.length()

		for index in range( 0, length ):
			yield self[ index ]
	
	def __str__( self ):
		
		return str( self._innerList )
	
	def __repr__( self ):
		
		return str(self)
		
	def __len__( self ):
		return len(self._innerList)
	
	def __getitem__( self, index ):
		
		if isinstance( index, int ):
			return Node._fromMSelectionList( self._MSelectionList, index )
		else:
			raise ValueError( "Int expected." )
	
	def __nonzero__( self ):
		
		return bool(self._innerList)

	def getInputs( this, type=None ):

		return this.getConnections( inputs=True, outputs=False, type=type )

	def getOutputs( this, type=None ):

		return this.getConnections( inputs=False, outputs=True, type=type )

	def getConnections( this, inputs=True, outputs=True, type=None, attrs=False ):

		if type:
			list = mc.listConnections( this._innerList, source=inputs, destination=outputs, type=type )
		else:
			list = mc.listConnections( this._innerList, source=inputs, destination=outputs )
		
		if list:
			ls = []

			for n in list:
				if not n in ls:
					ls.append( n );
		
			return NodeList( ls )
		else:
			return NodeList( [] )
	
	def delete( this ):

		mc.delete( this._innerList )

	@property
	def first( this ):
		if len(this) > 0:
			return this[ 0 ]
		else:
			return None

	@property
	def nodeNames( this ):
		return this._innerList;

	@property
	def animation( this ):
		if not this._animation:
			this._animation = Animation( this._innerList )

		return this._animation
		
	def setAttr( self, attrName, value ):
		
		for n in self:
			n[ attrName ] = value

class NodeAttributeList(object):
	
	def __init__( self, nameList ):
		self._list = nameList

	def __iter__( self ):
		for n in self._list:
			yield NodeAttribute.fromName( n )

	def __nonzero__( self ):
		return bool( self._list )
			
	def __getitem__( self, index ):
		return NodeAttribute.fromName( self._list[index] )

class NodeAttributeCollection(object):

	def __init__( self, node ):
		self._node = node

	def __getitem__( self, attribute ):

		if not self.contains( attribute ):
			raise KeyError( "Node '%s' has not attribute '%s'." % (self._node, attribute) )

		return NodeAttribute( self._node, attribute )

	def __getattr__( self, attribute ):

		return self[ attribute ]
		
	def __iter__( self ):

		for n in mc.listAttr( str(self._node) ):
			if not '.' in n:
				yield NodeAttribute( self._node, n )

	def contains( self, attribute ):

		return mc.attributeQuery( attribute, node=str(self._node), ex=True )

	def remove( self, attribute ):

		try:
			mc.deleteAttr( str(self._node), at=attribute )
		except:
			raise KeyError( "Node '%s' has not attribute '%s'." % (self._node, attribute) )
	
	def add( self, name, type=None, **args ):
		
		if type:
			args["at"] = type
		
		mc.addAttr( str(self._node), ln=name, **args )
		return NodeAttribute( self._node, name )

	def addRotate( self, name ):
		n = str(self._node)
		
		mc.addAttr( n, shortName=name, attributeType='double3' )
		mc.addAttr( n, shortName=name +'X', attributeType='doubleAngle', parent=name, keyable=True )
		mc.addAttr( n, shortName=name +'Y', attributeType='doubleAngle', parent=name, keyable=True )
		mc.addAttr( n, shortName=name +'Z', attributeType='doubleAngle', parent=name, keyable=True )
		
		return NodeAttribute( self._node, name )

class Animation(object):
	
	def __init__( this, source ):
		this._source = source

	@property
	def start( this ):
		range = this.range
		if range:
			return range[0]
		else:
			return None

	@start.setter
	def start( this, value ):
		range = this.range
		if range and range[0] < range[1]:
			if value > range[1]:
				raise Exception( "Value must be lower or equal than end." )
			
			this.range = (value,range[1])
		else:
			raise Exception( "No animation or single frame." )

	@property
	def end( this ):
		range = this.range
		if range:
			return range[1]
		else:
			return None

	@end.setter
	def end( this, value ):
		range = this.range
		if range and range[0] < range[1]:
			if value < range[0]:
				raise Exception( "Value must be greater or equal than start." )
			
			this.range = (range[0],value)
		else:
			raise Exception( "No animation or single frame." )
		
	@property
	def length( this ):
		range = this.range

		if range:
			return range[1] - range[0] + 1
		else:
			return None
	
	@length.setter
	def length( this, value ):
		range = this.range
		
		if range and range[0] < range[1]:
			this.range = (range[0], range[0] + value - 1)
		else:
			raise Exception( "No animation or a single key." )

	@property
	def range( this ):
		keys = mc.keyframe( this._source, q=True, timeChange=True )

		if keys:
			keys.sort()
			return keys[0], keys[-1]
		else:
			return None
	
	@range.setter
	def range( this, value ):
		mc.scaleKey( this._source, iub=False, newStartTime=value[0], newEndTime=value[1] )

class KeyframeList(object):
	
	def __init__( this, attribute ):
		this._attribute = attribute
		
	@property
	def hasConstantValue( this ):
		
		tKey = mc.keyframe( str(this._attribute), query=True )
		
		if not tKey or len(tKey) == 1:
			return True
		
		r     = True
		value = mc.keyframe( str(this._attribute), time=(tKey[0],tKey[0]), q=True, eval=True )
		
		for t in KeyframeList._drange( tKey[1], tKey[-1], 1.0 ):
			if value != mc.keyframe( str(this._attribute), time=(t,t), q=True, eval=True ):
				r = False
				break
				
		return r
	
	@staticmethod
	def _drange( start, stop, step ):
		r = start
		while r < stop:
			yield r
			r += step

class Namespace(object):

	_root = None

	@staticmethod
	def fromNodeName( nodeName ):

		dag, ns, name = Node.splitName( nodeName )
		
		if ns:
			return Namespace( ":"+ ns )
		else:
			if not Namespace._root:
				Namespace._root = Namespace( ":" )

			return Namespace._root
	
	@staticmethod
	def getCurrent():
		ns = mc.namespaceInfo( currentNamespace=True, absoluteName=True )
	
		if mc.namespace( q=True, isRootNamespace=True ):
			if not Namespace._root:
				Namespace._root = Namespace( ns )
			return Namespace._root
		else:
			return Namespace( ns )
	
	@staticmethod
	def ensure( namespace ):
		if Namespace.exists( namespace ):
			return Namespace( namespace )
		else:
			return Namespace.create( namespace )
	
	@staticmethod
	def exists( namespace ):
		
		if namespace[0] != ":":
			return mc.namespace( exists=":"+ namespace )
		else:
			return mc.namespace( exists=namespace )

	@staticmethod
	def getUnique( baseName ):

		match = re.search( "\d+$", baseName )

		if match:
			i        = int(match.group(0))
			name     = baseName
			baseName = baseName[ :-len(match.group(0)) ]
		else:
			i        = 0
			name     = baseName
		
		while mc.namespace( exists=name ):
			i   += 1
			name = baseName + str(i)
		
		return name

	@staticmethod
	def createUnique( baseName ):
	
		i    = 0
		name = baseName
		
		while mc.namespace( exists=name ):
			i    = i + 1
			name = baseName + str(i)
		
		return Namespace.create( name )
	
	@staticmethod
	def create( name ):
	
		return Namespace( mc.namespace( addNamespace=name, absoluteName=True ) )
	
	def __init__( self, path ):

		if not Namespace.exists( path ):
			raise Exception( "Namespace '%s' does not exists." % path )

		self._path = path

	def __str__( self ):
		return self._path
	
	def __repr__( self ):
		return self._path

	def __eq__( self, other ):
		return str(self) == str(other)

	def __ne__( self, other ):
		return str(self) != str(other)

	def __getitem__( this, key ):
		
		ls = this.ls( query=key, recursive=False )

		if not ls:
			raise KeyError();

		return ls[0]
	
	def __enter__( self ):
		self._prevNs = Namespace.getCurrent()
		self._set()
		
		return self
	
	def __exit__( self, exc_type, exc_value, traceback ):
		self._prevNs._set()
		self._prevNs = None

	@property
	def relativeName( self ):
		p = self._path.rfind(':')

		if p != -1:
			return self._path[ p: ]
		else:
			return ":"
	
	@property
	def parent( this ):
		
		if this._path != ":":
			path = this._path[ :this._path.rindex(':') ]
			
			if path != "":
				return Namespace( path )
			else:
				if not Namespace._root:
					Namespace._root = Namespace( ":" )

				return Namespace._root
		else:
			return None
	
	@property
	def children( this ):
		
		children = mc.namespaceInfo( this._path, listOnlyNamespaces=True )
		
		if children:
			return NamespaceList( children )
		else:
			return NamespaceList( [] )
		
	def remove( this, removeChildren=False ):
	
		if removeChildren:
			mc.namespace( removeNamespace=this._path, deleteNamespaceContent=True )
		else:
			mc.namespace( removeNamespace=this._path )
	
	def _set( self ):
		
		mc.namespace( setNamespace=self._path )
		
	def ls( self, query="*", recursive=False, **args ):

		return NodeList( self.lsNames( query=query, recursive=recursive, **args ) )
		
	def lsNames( self, query="*", recursive=False, **args ):
	
		names  = mc.ls( self._path +":"+ query, **args )
		
		if recursive:
			for child in self.children:
				names += child.lsNames( query=query, recursive=recursive, **args )
			
		return names

class NamespaceList(object):

	def __init__( this, list ):

		this._list = list;

	def __iter__( this ):

		for ns in this._list:
			yield Namespace( ns )

	def __len__( this ):

		return len(this._list)

class Scene(object):

	@staticmethod
	def ensurePlugin( plugin ):

		if not mc.pluginInfo( plugin, q=True, loaded=True ):
			mc.loadPlugin( plugin )