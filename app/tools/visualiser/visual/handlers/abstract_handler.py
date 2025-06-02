from abc import ABC, abstractmethod

class HandlerABC(ABC):
    """
    A generic abstract base class for building or 
    transforming a collection of elements (nodes/edges). 
    Subclasses must implement `default_builder`.
    """

    def __init__(self, graph_builder,name):
        self._graph_builder = graph_builder
        self._builder = self.default_builder
        self._name = name

    @abstractmethod
    def default_builder(self, elements):
        """
        This is the fallback method that child 
        classes must implement. E.g., for color handlers, 
        it could be `standard` or `type`.
        """
        pass

    def build(self, elements, builder_type=None,**kwargs):
        """
        The main entry point. If `builder_type` is provided, look up the method
        matching that name. If found, set it as the active builder; otherwise
        raise an error.
        """
        if builder_type is not None:
            if hasattr(self, builder_type):
                builder_func = getattr(self, builder_type)
                self._builder = builder_func
            else:
                raise ValueError(f"Invalid builder type: {builder_type}")
        elements = self._remove_old_classes(elements)
        return self._builder(elements,**kwargs)

    def has_builder(self,builder):
        for item_name in dir(self):
            if item_name.startswith("_"):
                continue
            if builder == item_name:
                return True
        return False
    
    def get_builders(self):
        """
        Returns a list of all callable methods on this class that:
          1) don't start with '_'
          2) aren't blacklisted (like 'build', 'get_builders', 'default_builder')
        """
        blacklist = {"build", "get_builders", "default_builder","has_builder"}
        methods = []
        builder_dict = {"builder" : self.__class__.__name__,
                        "name" : self._name,
                        "default" : self.default_builder().__name__}
        for item_name in dir(self):
            if item_name.startswith("_"):
                continue
            if item_name in blacklist:
                continue
            val = getattr(self, item_name)
            if callable(val):
                methods.append(item_name)

        builder_dict["options"] = methods
        return builder_dict

    def _build_prefix(self):
        return self._name.lower().replace(" ","_")
    
    def _build_selector(self,suffix):
        suffix = suffix.replace(":","_")
        return f'{self._build_prefix()}_{suffix}'
    
    def _remove_old_classes(self,elements):
        # Can this be optimised?
        for e in elements:
            if "classes" not in e:
                e["classes"] = ""
            classes = e["classes"].split()
            new_class_v = ""
            for class_v in classes:
                if class_v.startswith(self._build_prefix()):
                    continue
                else:
                    new_class_v += f' {class_v}'
            e["classes"] = new_class_v
        return elements
    
    def _remove_old_selectors(self, stylesheet):
        prefix = self._build_prefix()
        return [selector for selector in stylesheet 
                if prefix not in selector["selector"]]

    
    def _is_node(self, element):
        return not ("source" in element["data"] and "target" in element["data"])

    def _is_edge(self, element):
        return ("source" in element["data"] and "target" in element["data"])
