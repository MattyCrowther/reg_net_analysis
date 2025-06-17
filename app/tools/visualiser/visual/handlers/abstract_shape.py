from app.tools.visualiser.visual.handlers.abstract_handler import HandlerABC

class NodeShapeHandler(HandlerABC):
    def __init__(self, graph_builder):
        super().__init__(graph_builder,"Node Shape")
        self.shapes = [
            "ellipse", "square", "triangle", "rectangle",
            "diamond", "hexagon", "octagon", "vee",
            "parallelogram", "roundrect", "ellipse",
        ]
        self._builder = self.default_builder()

    def default_builder(self):
        return self.circle
    
    def adaptive(self,elements):
        no_type_key = "no_type"
        cur_view = self._graph_builder.view
        shape_map = {}
        counter = 0
        for element in elements:
            # Its an edge
            if not self._is_node(element):
                continue
            node = cur_view.get_node(element["data"]["id"])
            node_type = self._get_name(node.type)
            if node_type is None:
                node_type = no_type_key
            else:
                node_type = node_type

            if node_type not in shape_map:
                shape = self.shapes[counter]
                shape_map[node_type] = shape
                counter += 1
            else:
                shape = shape_map[node_type]
            element["classes"] += f" {shape}"
        return elements
        
    def circle(self,elements):
        return self._set_all(elements,"ellipse")
        
    def square(self,elements):
        return self._set_all(elements,"square")
        
    def triangle(self,elements):
        return self._set_all(elements,"triangle")
        
    def rectangle(self,elements):
        return self._set_all(elements,"rectangle")
        
    def diamond(self,elements):
        return self._set_all(elements,"diamond")
        
    def hexagon(self,elements):
        return self._set_all(elements,"hexagon")
        
    def octagon(self,elements):
        return self._set_all(elements,"octagon")
        
    def vee(self,elements):
        return self._set_all(elements,"vee")
            
    def _set_all(self, elements, s_type):
        for element in elements:
            if not self._is_node(element):
                continue
            classes_list = element["classes"].split()
            classes_list = [cls for cls in classes_list if 
                            cls not in self.shapes]
            if s_type not in classes_list:
                classes_list.append(s_type)
            element["classes"] = " ".join(classes_list)
        return elements


    
class EdgeShapeHandler(HandlerABC):
    def __init__(self, graph_builder):
        super().__init__(graph_builder,"Edge Shape")
        self._builder = self.haystack
        self.shapes = ["straight",
                    "bezier",
                    "taxi",
                    "unbundled_bezier",
                    "loop",
                    "haystack",
                    "octagon",
                    "segments"]
        self._builder = self.default_builder()
       
    def default_builder(self):
        return self.haystack
    
    def haystack(self,elements):
        return self._set_all(elements,"haystack")
    
    def segments(self,elements):
        return self._set_all(elements,"segments")
    
    def straight(self,elements):
        return self._set_all(elements,"straight")
    
    def bezier(self,elements):
        return self._set_all(elements,"bezier")
    
    def taxi(self,elements):
        return self._set_all(elements,"taxi")
    
    def unbundled_bezier(self,elements):
        return self._set_all(elements,"unbundled-bezier")
    
    def loop(self,elements):
        return self._set_all(elements,"loop")
    
    def _set_all(self, elements, s_type):
        for element in elements:
            if not self._is_edge(element):
                continue
            classes_list = element["classes"].split()
            classes_list = [cls for cls in classes_list if 
                            cls not in self.shapes]
            if s_type not in classes_list:
                classes_list.append(s_type)
            element["classes"] = " ".join(classes_list)
        return elements
    
    def _is_edge(self,element):
        if "source" in element["data"] and "target" in element["data"]:
            return True
        return False