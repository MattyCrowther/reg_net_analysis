from app.tools.visualiser.visual.handlers.color_producer import ColorPicker
from app.tools.visualiser.visual.handlers.abstract_color import EdgeColorHandler
from app.tools.visualiser.visual.handlers.abstract_color import NodeColorHandler



color_picker = ColorPicker()

class NetVisNodeColorHandler(NodeColorHandler):
    def __init__(self,builder):
        super().__init__(builder)

    # I also wonder if we could add node outline colours?

    '''
    {
        'selector': 'node',
        'style': {
            'border-width': 3,
            'border-color': 'black',
            'border-style': 'dashed'
        }
    }

    '''
    
class NetVisEdgeColorHandler(EdgeColorHandler):
    def __init__(self,builder):
        super().__init__(builder)
