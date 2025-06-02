class LayoutHandler:
    def __init__(self):
        self._builder = self.default_builder()

    def default_builder(self):
        return self.Cose()
    
    def build(self,builder_type=None):
        if builder_type is not None:
            if hasattr(self, builder_type):
                layout_class = getattr(self, builder_type)
                self._builder = layout_class()
            else:
                raise ValueError(f"Invalid layout name: {builder_type}")
        return self._builder.build()
    
    def has_builder(self,builder):
        for item_name in dir(self):
            val = getattr(self, item_name)
            if isinstance(val, type) and issubclass(val, self.Layout):
                if builder == item_name:
                    return True
        return False
    
    def get_builders(self):
        """
        Return all possible layout classes. This replaces get_layouts().
        """
        methods = []
        builder_dict = {"builder" : self.__class__.__name__,
                        "name" : "Layout",
                        "default" : self.default_builder().__class__.__name__}
        for item_name in dir(self):
            val = getattr(self, item_name)
            if (isinstance(val, type) and 
                issubclass(val, self.Layout) 
                and val != self.Layout):
                methods.append(item_name)

        builder_dict["options"] = methods
        return builder_dict

    class Layout:
        def __init__(self):
            self._settings = {}
            self._params = {}
            self._init_settings()

        def build(self,layout):
            self.params.update(layout)
            return self.params
        
        @property
        def settings(self):
            return self._settings
        
        @property
        def params(self):
            return self._params

        def add_param(self,key,value):
            self._params[key] = value
        
        def _init_settings(self):
            self._settings = {
                "fit": bool, 
                "padding": int,
                "animate": bool, 
                "animationDuration": int,
                "nodeDimensionsIncludeLabels": bool}
        
    class No(Layout):
        def __init__(self):
            super().__init__()
            
        def build(self):
            return super().build({"name" : "preset"}) 
            
        def _init_settings(self):
            super()._init_settings()

    class Concentric(Layout):
        def __init__(self):
            super().__init__()

        def build(self):
            return super().build({"name" : "concentric",
                                  "minNodeSpacing" : 80}) 

        def _init_settings(self):
            super()._init_settings()
            self._settings.update({
                "startAngle": float, 
                "sweep": int, 
                "clockwise": bool, 
                "equidistant": bool, 
                "minNodeSpacing": int, 
                "avoidOverlap": bool})

    class BreadthFirst(Layout):
        def __init__(self):
            super().__init__()
            

        def build(self):
            return super().build({"name" : "breadthfirst"}) 

        def _init_settings(self):
            super()._init_settings()
            self._settings.update({  
                "circle": bool, 
                "grid": bool, 
                "spacingFactor": float, 
                "avoidOverlap": bool, 
                "roots": str, 
                "maximal": bool})

    class Cose(Layout):
        def __init__(self):
            super().__init__()

        def build(self):
            return super().build({"name" : "cose"})

        def _init_settings(self):
            super()._init_settings()
            self._settings.update({
                "idealEdgeLength": int,
                "nodeOverlap": int,
                "refresh": int,
                "randomize": bool,
                "componentSpacing": int,
                "nodeRepulsion": int,
                "edgeElasticity": int,
                "nestingFactor": int,
                "gravity": int,
                "numIter": int,
                "initialTemp": int,
                "coolingFactor": float,
                "minTemp": float})
    
    class Cola(Layout):
        def __init__(self):
            super().__init__()

        def build(self):
            return super().build({"name" : "cola"})

        def _init_settings(self):
            super()._init_settings()
            self._settings.update({
                "refresh": int, 
                "maxSimulationTime": int, 
                "randomize": bool, 
                "avoidOverlap": bool, 
                "handleDisconnected": bool, 
                "convergenceThreshold": float, 
                "nodeSpacing": int,
                "edgeLength": int, 
                "edgeSymDiffLength": int, 
                "edgeJaccardLength": int})

    class Euler(Layout):
        def __init__(self):
            super().__init__()

        def build(self):
            return super().build({"name" : "euler"})

        def _init_settings(self):
            super()._init_settings()
            self._settings.update({
                "springLength": int,
                "springCoeff": float,
                "mass": int,
                "gravity": int,
                "pull": float,
                "theta": float,
                "dragCoeff": float,
                "movementThreshold": int,
                "timeStep": int,
                "refresh": int,
                "maxIterations": int,
                "maxSimulationTime": int,
                "randomize": bool})

    class Spread(Layout):
        def __init__(self):
            super().__init__()

        def build(self):
            return super().build({"name" : "spread"}) 

        def _init_settings(self):
            super()._init_settings()
            self._settings.update({
                "minDist": int, 
                "expandingFactor": float, 
                "maxExpandIterations": int, 
                "randomize": bool})

    class Dagre(Layout):
        def __init__(self):
            super().__init__()

        def build(self):
            return super().build({"name" : "dagre"}) 

        def _init_settings(self):
            super()._init_settings()
            self._settings.update({
                "nodeSep": int, 
                "edgeSep": int, 
                "rankSep": int, 
                "rankDir": ["LR","TB"],
                "ranker": ["network-simplex","tight-tree","longest-path"], 
                "minLen": int, 
                "edgeWeight": int, 
                "spacingFactor": float})

    class Klay(Layout):
        def __init__(self):
            super().__init__()

        def build(self):
            return super().build({"name" : "klay"}) 

        def _init_settings(self):
            super()._init_settings()


    class Grid(Layout):
        def __init__(self):
            super().__init__()

        def build(self):
            return super().build({"name" : "grid"})

        def _init_settings(self):
            super()._init_settings()
            self._settings.update({
                "avoidOverlap": bool, 
                "avoidOverlapPadding": int, 
                "condense": bool, 
                "rows": int, 
                "cols": int})

    class Circle(Layout):
        def __init__(self):
            super().__init__()

        def build(self):
            return super().build({"name" : "circle"}) 

        def _init_settings(self):
            super()._init_settings()
            self._settings.update({
                "avoidOverlap": bool, 
                "radius": float, 
                "startAngle": float, 
                "sweep": int, 
                "clockwise": bool})

    class Random(Layout):
        def __init__(self):
            super().__init__()

        def build(self):
            return super().build({"name" : "random"}) 

        def _init_settings(self):
            super()._init_settings()


    class CoseBilkent(Layout):
        def __init__(self):
            super().__init__()

        def build(self):
            return super().build({"name" : "cose-bilkent"}) 

        def _init_settings(self):
            super()._init_settings()
        