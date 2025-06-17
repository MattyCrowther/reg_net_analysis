import os

import dash_cytoscape as cyto
cyto.load_extra_layouts()
from app.tools.visualiser.builder.net_vis_builder import NetVisBuilder
from app.tools.visualiser.visual.abstract import Visual
from app.tools.visualiser.visual.handlers.net_vis.layout import NetVisLayoutHandler
from app.tools.visualiser.visual.handlers.net_vis.label import NetVisNodeLabelHandler
from app.tools.visualiser.visual.handlers.net_vis.label import NetVisEdgeLabelHandler
from app.tools.visualiser.visual.handlers.net_vis.color import NetVisNodeColorHandler
from app.tools.visualiser.visual.handlers.net_vis.color import NetVisEdgeColorHandler
from app.tools.visualiser.visual.handlers.net_vis.size import NetVisSizeHandler
from app.tools.visualiser.visual.handlers.net_vis.shape import NetVisNodeShapeHandler
from app.tools.visualiser.visual.handlers.net_vis.shape import NetVisEdgeShapeHandler

default_stylesheet_fn = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                     "default_stylesheet.txt")
 
class NetVisVisual(Visual):
    def __init__(self,storage):
        builder = NetVisBuilder(storage)
        super().__init__(builder,
                         layout_handler=NetVisLayoutHandler(),
                         node_label_handler=NetVisNodeLabelHandler(builder),
                         edge_label_handler=NetVisEdgeLabelHandler(builder),
                         node_colour_handler=NetVisNodeColorHandler(builder),
                         edge_colour_handler=NetVisEdgeColorHandler(builder),
                         size_handler=NetVisSizeHandler(builder),
                         node_shape_handler=NetVisNodeShapeHandler(builder),
                         edge_shape_handler=NetVisEdgeShapeHandler(builder))