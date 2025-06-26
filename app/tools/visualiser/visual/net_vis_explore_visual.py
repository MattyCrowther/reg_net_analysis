import dash_cytoscape as cyto
cyto.load_extra_layouts()
from app.tools.visualiser.builder.net_vis_explorer_builder import NetVisExplorerBuilder
from app.tools.visualiser.visual.abstract import ViewVisual
from app.tools.visualiser.visual.handlers.net_vis.layout import NetVisLayoutHandler
from app.tools.visualiser.visual.handlers.net_vis.label import NetVisNodeLabelHandler
from app.tools.visualiser.visual.handlers.net_vis.label import NetVisEdgeLabelHandler
from app.tools.visualiser.visual.handlers.net_vis.color import NetVisNodeColorHandler
from app.tools.visualiser.visual.handlers.net_vis.color import NetVisEdgeColorHandler
from app.tools.visualiser.visual.handlers.net_vis.size import NetVisSizeHandler
from app.tools.visualiser.visual.handlers.net_vis.shape import NetVisNodeShapeHandler
from app.tools.visualiser.visual.handlers.net_vis.shape import NetVisEdgeShapeHandler

class NetVisExploreVisual(ViewVisual):
    def __init__(self,storage):
        builder = NetVisExplorerBuilder(storage)
        super().__init__(builder,
                         layout_handler=NetVisLayoutHandler(),
                         node_label_handler=NetVisNodeLabelHandler(builder),
                         edge_label_handler=NetVisEdgeLabelHandler(builder),
                         node_colour_handler=NetVisNodeColorHandler(builder),
                         edge_colour_handler=NetVisEdgeColorHandler(builder),
                         size_handler=NetVisSizeHandler(builder),
                         node_shape_handler=NetVisNodeShapeHandler(builder),
                         edge_shape_handler=NetVisEdgeShapeHandler(builder))
        
    
    def build(self,node_id):
        self._builder.initialise_view(node_id)
        return super().build()
    
    def set_depth(self,depth):
        self._builder.set_depth(depth)
        
    def is_expanded(self,node_id):
        return self._builder.is_expanded(node_id)
    
    def expand_node(self,node_id,elements):
        node_data,new_nodes = self._builder.expand_node(node_id)
        if len(new_nodes) > 1:
            elements = self.get_view_elements() 
            elements = self.get_visual_element(elements)
        return node_data,elements
    

    def compress_node(self, node_id, elements):
        removed_elements = self._builder.compress_node(node_id)
        removed_ids = [s.id for s in removed_elements]
        final_elements = []
        for e in elements:
            if e["data"]["id"] in removed_ids:
                continue
            if "source" in e["data"] and node_id == e["data"]["source"]:
                continue
            final_elements.append(e) 
        return final_elements