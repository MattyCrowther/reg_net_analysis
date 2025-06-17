import os
import json

from app.tools.visualiser.visual.handlers.abstract_layout import LayoutHandler
from app.tools.visualiser.visual.handlers.abstract_label import NodeLabelHandler
from app.tools.visualiser.visual.handlers.abstract_label import EdgeLabelHandler
from app.tools.visualiser.visual.handlers.abstract_color import NodeColorHandler
from app.tools.visualiser.visual.handlers.abstract_color import EdgeColorHandler
from app.tools.visualiser.visual.handlers.net_vis.size import SizeHandler
from app.tools.visualiser.visual.handlers.net_vis.shape import NodeShapeHandler
from app.tools.visualiser.visual.handlers.net_vis.shape import EdgeShapeHandler

default_stylesheet_fn = os.path.join(os.path.dirname(
    os.path.realpath(__file__)), "default_stylesheet.txt")

class Visual:
    def __init__(self,builder,
                 layout_handler=None,
                 node_label_handler=None,
                 edge_label_handler=None,
                 node_colour_handler=None,
                 edge_colour_handler=None,
                 size_handler=None,
                 node_shape_handler=None,
                 edge_shape_handler=None):

        self._builder = builder
        
        if layout_handler is None:
            self._layout_handler = LayoutHandler()
        else:
            self._layout_handler = layout_handler
        
        if node_label_handler is None:
            self._node_label_handler = NodeLabelHandler(self._builder)
        else:
            self._node_label_handler = node_label_handler
        if edge_label_handler is None:
            self._edge_label_handler = EdgeLabelHandler(self._builder)
        else:
            self._edge_label_handler = edge_label_handler


        if node_colour_handler is None:
            self._node_colour_handler = NodeColorHandler(self._builder)
        else:
            self._node_colour_handler = node_colour_handler
        if edge_colour_handler is None:
            self._edge_colour_handler = EdgeColorHandler(self._builder)
        else:
            self._edge_colour_handler = edge_colour_handler

        if node_shape_handler is None:
            self._node_shape_handler = NodeShapeHandler(self._builder)
        else:
            self._node_shape_handler = node_shape_handler
        if edge_shape_handler is None:
            self._edge_shape_handler = EdgeShapeHandler(self._builder)
        else:
            self._edge_shape_handler = edge_shape_handler
        
        if size_handler is None:
            self._size_handler = SizeHandler(self._builder)
        else:
            self._size_handler = size_handler

        self._handlers = [
                        self._node_label_handler,
                        self._edge_label_handler,
                        self._node_colour_handler,
                        self._edge_colour_handler,
                        self._size_handler,
                        self._node_shape_handler,
                        self._edge_shape_handler,]

        self._stylesheet = self._build_default_stylesheet()

    # -- View --
    def get_view_options(self):
        return self._builder.get_builder_options()
    
    def set_view(self,view_builder=None):
        return self._builder.set_view(view_builder=view_builder)
    
    def get_view_elements(self,sub_view=None):
        return self._builder.get_view_elements(sub_view=sub_view)
    
    # -- Layout --
    def get_layout_options(self):
        return self._layout_handler.get_builders()
    
    def get_layout(self,layout_type=None):
        return self._layout_handler.build(builder_type=layout_type)
    
    # -- visual elements -- 
    def get_visual_options(self):
        return [h.get_builders() for h in self._handlers]
    
    def get_style(self):
        return self._stylesheet

    def update_style(self,selector,key,value):
        for style in self._stylesheet:
            if style["selector"] == selector:
                style["style"][key] = value
                
    def get_visual_element(self,elements,handler_name=None,builder_type=None):
        style = self._stylesheet
        def _dispatch(handler,elements,builder_type=None):
            nonlocal style
            try:
                n_ss = handler.build(elements,builder_type=builder_type)
                return n_ss
            except TypeError:
                elements,style = handler.build(elements,
                                            builder_type=builder_type,
                                            stylesheet=style)
                return elements,style
                        
        for handler in self._handlers:
            if handler_name is None:
                rv = _dispatch(handler,elements)
                if len(rv) == 2:
                    elements,style = rv
                else:
                    elements = rv
            elif handler.__class__.__name__ == handler_name:
                rv = _dispatch(handler,elements,
                                           builder_type=builder_type)
                if len(rv) == 2:
                    elements,style = rv
                else:
                    elements = rv
                break
            
        if style is not None:
            self._stylesheet = style
        return elements
            
    def build(self,view_builder=None):
        self.set_view(view_builder=view_builder)
        elements = self.get_view_elements()
        layout = self.get_layout()
        elements = self.add_node_labels(elements)
        elements = self.add_edge_labels(elements)
        elements = self.add_node_colour(elements)
        elements = self.add_edge_colour(elements)
        elements = self.add_node_size(elements)
        elements = self.add_node_shape(elements)
        elements = self.add_edge_shape(elements)
        return layout,elements
        

    def add_node_labels(self,elements,label_type=None):
        return self._node_label_handler.build(elements,
                                              builder_type=label_type)
    
    def add_edge_labels(self,elements,label_type=None):
        return self._edge_label_handler.build(elements,
                                              builder_type=label_type)
    
    def add_node_colour(self,elements,colour_type=None):
        elements,style = self._node_colour_handler.build(elements,
                                                        stylesheet=self._stylesheet,
                                                        builder_type=colour_type)
        self._stylesheet = style
        return elements
    
    def add_edge_colour(self,elements,colour_type=None):
        elements,style = self._edge_colour_handler.build(elements,
                                                        stylesheet=self._stylesheet,
                                                        builder_type=colour_type)
        self._stylesheet = style
        return elements
    
    def add_node_size(self,elements,size_type=None):
        return self._size_handler.build(elements,
                                        builder_type=size_type)
    
    def add_node_shape(self,elements,shape_type=None):
        return self._node_shape_handler.build(elements,
                                              builder_type=shape_type)
    
    def add_edge_shape(self,elements,shape_type=None):
        return self._edge_shape_handler.build(elements,
                                              builder_type=shape_type)
    
    def _build_default_stylesheet(self):
        with open(default_stylesheet_fn) as json_file:
            stylesheet = json.load(json_file)
        # Pre-add as there is a finite number.
        for shape in self._node_shape_handler.shapes:
            stylesheet.append({
                'selector': '.' + shape,
                'style': {'shape': shape}})
        for shape in self._edge_shape_handler.shapes:
            stylesheet.append({
                'selector': '.' + shape,
                'style': {'curve-style': shape}})
        return stylesheet