from app.tools.visualiser.visual.handlers.abstract_shape import NodeShapeHandler
from app.tools.visualiser.visual.handlers.abstract_shape import EdgeShapeHandler

class NetVisNodeShapeHandler(NodeShapeHandler):
    def __init__(self,builder):
        super().__init__(builder)
        
class NetVisEdgeShapeHandler(EdgeShapeHandler):
    def __init__(self,builder):
        super().__init__(builder)