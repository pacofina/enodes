
from maya import cmds, mel

from ..node import Node

def __getitem__( self, key ):
    return key

class ChannelBox(object):

    def _channelBox( self ):
        return mel.eval('global string $gChannelBoxName; $temp=$gChannelBoxName;')	#fetch maya's main channelbox
    
    def get_selected_attrs( self ):
        return [Node(n)[a] for n, a in self._iter_selected_attrs()]

    def _iter_selected_attrs( self ):
        channelBox = self._channelBox()

        # Objects
        for n in cmds.channelBox( channelBox, q=True, mainObjectList=True ) or []:
            for attr in cmds.channelBox( channelBox, q=True, selectedMainAttributes=True ) or []:
                yield n, attr

		# Shape
        for n in cmds.channelBox( channelBox, q=True, shapeObjectList=True ) or []:
            for attr in cmds.channelBox( channelBox, q=True, selectedShapeAttributes=True ) or []:
                yield n, attr
		
		# History
        for n in cmds.channelBox( channelBox, q=True, historyObjectList=True ) or []:
            for attr in cmds.channelBox( channelBox, q=True, selectedHistoryAttributes=True ) or []:
                yield n, attr

		# Outputs
        for n in cmds.channelBox( channelBox, q=True, outputObjectList=True ) or []:
            for attr in cmds.channelBox( channelBox, q=True, selectedOutputAttributes=True ) or []:
                yield n, attr

_channelbox = ChannelBox()
get_selected_attrs = _channelbox.get_selected_attrs