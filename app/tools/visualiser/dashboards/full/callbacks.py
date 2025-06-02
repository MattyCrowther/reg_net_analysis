from app.tools.visualiser.dashboards.utility.callback_structs import Callbacks
from app.tools.visualiser.dashboards.utility.callback_structs import Callback

static_callbacks = {}


class DashBoardCallbacks(Callbacks):
    def __init__(self, dashboard, graph_id):
        callbacks = self._generate_callbacks(dashboard, graph_id)
        super().__init__(**callbacks)
        self._graph_id = graph_id

    def _generate_callbacks(self, dashboard, graph_id):
        return {
            "update_legend": Callback(
                dashboard.update_legend,
                inputs={graph_id: "stylesheet"},
                outputs={"graph_legend": "children"},
            ),
            "download": Callback(
                dashboard.export_graph_img,
                inputs={"png": "n_clicks", "jpg": "n_clicks", "svg": "n_clicks"},
                outputs={graph_id: "generateImage"},
            ),
            "graph_update": Callback(
                dashboard.graph_update,
                inputs = {graph_id: 'tapNodeData'},
                outputs = {'node_data_output': 'children',
                           graph_id:["elements","stylesheet"]},
                states={graph_id:"elements"}
            )
        }