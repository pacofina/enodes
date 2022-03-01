from .ui   import channelbox
from .node import Node, NodeList, NodeAttribute, Namespace

reload( channelbox )

Node.getSelectedAttrs = channelbox.get_selected_attrs