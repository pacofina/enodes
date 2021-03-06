from .ui   import channelbox
from .node import Node, ReferenceNode, NodeList, NodeAttribute, Namespace, registerCustomType

Node.getSelectedAttrs = channelbox.get_selected_attrs

from .nodes.objectSet import ObjectSetNode
registerCustomType( 'objectSet', ObjectSetNode )