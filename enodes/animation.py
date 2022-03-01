
import maya.cmds as mc

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