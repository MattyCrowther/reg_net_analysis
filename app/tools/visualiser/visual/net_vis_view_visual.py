import dash_cytoscape as cyto
cyto.load_extra_layouts()
from app.tools.visualiser.builder.net_vis_view_builder import NetVisViewBuilder
from app.tools.visualiser.visual.abstract import ViewVisual
from app.tools.visualiser.visual.handlers.net_vis.layout import NetVisLayoutHandler
from app.tools.visualiser.visual.handlers.net_vis.label import NetVisNodeLabelHandler
from app.tools.visualiser.visual.handlers.net_vis.label import NetVisEdgeLabelHandler
from app.tools.visualiser.visual.handlers.net_vis.color import NetVisNodeColorHandler
from app.tools.visualiser.visual.handlers.net_vis.color import NetVisEdgeColorHandler
from app.tools.visualiser.visual.handlers.net_vis.size import NetVisSizeHandler
from app.tools.visualiser.visual.handlers.net_vis.shape import NetVisNodeShapeHandler
from app.tools.visualiser.visual.handlers.net_vis.shape import NetVisEdgeShapeHandler

class NetVisViewVisual(ViewVisual):
    def __init__(self,storage):
        builder = NetVisViewBuilder(storage)
        super().__init__(builder,
                         layout_handler=NetVisLayoutHandler(),
                         node_label_handler=NetVisNodeLabelHandler(builder),
                         edge_label_handler=NetVisEdgeLabelHandler(builder),
                         node_colour_handler=NetVisNodeColorHandler(builder),
                         edge_colour_handler=NetVisEdgeColorHandler(builder),
                         size_handler=NetVisSizeHandler(builder),
                         node_shape_handler=NetVisNodeShapeHandler(builder),
                         edge_shape_handler=NetVisEdgeShapeHandler(builder))
        
    def get_view_options(self):
        return self._builder.get_builder_options()
    
    def set_view(self,view_builder=None):
        return self._builder.set_view(view_builder=view_builder)
        
    def build(self,view_builder=None):
        self.set_view(view_builder=view_builder)
        return super().build()