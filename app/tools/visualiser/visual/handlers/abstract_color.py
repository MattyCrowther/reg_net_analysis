from app.tools.visualiser.visual.handlers.color_producer import ColorPicker
from app.tools.visualiser.visual.handlers.abstract_handler import HandlerABC
color_picker = ColorPicker()

class NodeColorHandler(HandlerABC):
    def __init__(self, graph_builder):
        super().__init__(graph_builder,"Node Colour")
        self._builder = self.default_builder()

    def default_builder(self):
        return self.type

    def standard(self, elements,stylesheet=None):
        stylesheet = self._remove_old_selectors(stylesheet)
        standard_key = self._build_selector("standard")
        new_style = {"background-color": color_picker[0]}
        stylesheet = self._add_to_stylesheet(stylesheet, standard_key, new_style)
        for element in elements:
            if not self._is_node(element):
                continue
            element["classes"] += f' {standard_key}'
        return (elements, stylesheet)

    def type(self, elements,stylesheet=None):
        stylesheet = self._remove_old_selectors(stylesheet)
        no_type_key = self._build_selector("no_type")
        cur_view = self._graph_builder.view
        new_colour_index = 0
        colour_map = {}
        for element in elements:
            if not self._is_node(element):
                continue
            node = cur_view.get_node(element["data"]["id"])
            node_type = self._get_name(node.type)
            if node_type is not None:
                selector = self._build_selector(node_type)
            else:
                selector = no_type_key
            
            if selector not in colour_map:
                colour_map[selector] = color_picker[new_colour_index]
                new_colour_index += 1
                new_style = {"background-color": colour_map[selector]}
                stylesheet = self._add_to_stylesheet(stylesheet, selector, new_style)
            element["classes"] += f' {selector}'
        return (elements, stylesheet)


    def _add_to_stylesheet(self,stylesheet, selector, new_style):
        new_style = {"selector": f".{selector}", "style": new_style}
        for index, style in enumerate(list(stylesheet)):
            style_parts = style["selector"].split(" ")
            if selector in style_parts:
                stylesheet[index].update(new_style)
                break
        else:
            stylesheet.append(new_style)
        return stylesheet

class EdgeColorHandler(HandlerABC):
    def __init__(self, graph_builder):
        super().__init__(graph_builder,"Edge Colour")
        self._builder = self.default_builder()

    def default_builder(self):
        return self.type
    
    def standard(self, elements,stylesheet=None):
        stylesheet = self._remove_old_selectors(stylesheet)
        standard_key = self._build_selector("standard")
        new_style = {"line-color": color_picker[0],
                     "mid-target-arrow-color" : color_picker[0]}
        stylesheet = self._add_to_stylesheet(stylesheet,
                                            standard_key,
                                            new_style)
        for element in elements:
            # Its an node
            if not self._is_edge(element):
                continue
            element["classes"] += f" {standard_key}"
        return (elements, stylesheet)
    
    def type(self,elements,stylesheet=None):
        stylesheet = self._remove_old_selectors(stylesheet)
        no_type_key = self._build_selector("no_type")
        cur_view = self._graph_builder.view
        new_colour_index = 0
        colour_map = {}
        for element in elements:
            if not self._is_edge(element):
                continue
            source = element["data"]["source"]
            target = element["data"]["target"]
            edge_type = cur_view.get_edge_type(source,target)
            
            if edge_type is None:
                selector = no_type_key
            else:
                edge_type = self._get_name(edge_type)
                edge_type = edge_type
                selector = self._build_selector(edge_type)
            if selector not in colour_map:
                colour_map[selector] = color_picker[new_colour_index]
                new_colour_index += 1
                new_style = {"line-color": colour_map[selector],
                             "mid-target-arrow-color" : colour_map[selector]}
                stylesheet = self._add_to_stylesheet(stylesheet,
                                                    selector,
                                                    new_style)
            element["classes"] += f" {selector}"
        return elements,stylesheet
    
    def _add_to_stylesheet(self,stylesheet,selector,new_style):
        new_style = {"selector": f".{selector}",
                        "style": new_style}
        for index,style in enumerate(list(stylesheet)):
            if not selector in style["selector"]:
                continue
            stylesheet[index].update(new_style)
            break
        else:
            stylesheet.append(new_style)
        return stylesheet