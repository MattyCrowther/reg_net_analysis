from dash import ctx
from dash.exceptions import PreventUpdate
from flask import session

from app.tools.visualiser.dashboards.abstract import AbstractDash
from app.tools.visualiser.visual.net_vis_explore_visual import NetVisExploreVisual
from app.tools.visualiser.dashboards.explore.callbacks import DashBoardCallbacks

graph_name = "graph"
graph_container_name = "graph_container"

class ExploreDashboard(AbstractDash):
    def __init__(self, storage, name=None, server=True):
        super().__init__(NetVisExploreVisual(storage), 
                         name=name, server=server,
                         pathname="/explore/")
        self._build_app()
    
    def _build_app(self):
        cbs = DashBoardCallbacks(self, graph_name)
        style = self.visualiser.get_style()
        figure = self.create_graph(
            graph_name,
            elements=[],
            layout={"name" : "cose"},
            stylesheet=style,
            className="cytoscape-graph",
            style={"width":"100%","height":"100%"}
        )
        legend_dict = self._generate_legend_data(style)
        legend = self.create_legend(legend_dict)
        legend = self.create_div(cbs.update_legend.outputs.graph_legend,
                                 legend,className="graph-legend")

        depth_input = self.create_input(cbs.graph_update.inputs.depth)
        node_detils = self.create_div(cbs.graph_update.outputs.node_data_output,[])
        right_side = self.create_div("right_side",depth_input+ legend + node_detils)
        graph_container = self.create_div(
            graph_container_name,
            figure,
            className="graph-container"
        )
        location_id = "url"
        location = self.create_location(location_id)

        cbs.new_callback("load_graph",self.load_graph,
                         {location_id: "href"},
                         {graph_container_name:"children"})
        
        main_content = self.create_div(
            "main-container",location+graph_container+right_side,
            className="container-fluid main-container"
        )

        [self.add_callback(*callback.to_struct()) for _, callback in cbs]
        self.set_layout(main_content)
        self.build()

    def load_graph(self,_):
        node_id = session.get("node_id",None)
        if node_id is None:
            node_id = "http://www.nv_ontology.org/42366ea1-8807-464b-ba4f-b74110f732f1"
            #raise PreventUpdate()
        self._node_id = node_id
        layout,elements = self.visualiser.build(node_id)
            
        figure = self.create_graph(
            graph_name,
            elements=elements,
            layout=layout,
            stylesheet=self.visualiser.get_style(),
            className="cytoscape-graph",
            style={"width":"100%","height":"100%"}
        )
        return [figure]
    
    def update_legend(self,stylehseet):
        triggered_id = ctx.triggered_id
        if triggered_id is None:
            raise PreventUpdate
        legend_dict = self._generate_legend_data(stylehseet)
        return [self.create_legend(legend_dict)]
    
    def graph_update(self,node_data,depth,*args):
        '''
        Callback for graph visual change includes 
        view,layout and any other visual based change.
        '''
        triggered_id = ctx.triggered_id
        if triggered_id is None:
            raise PreventUpdate
        
        if node_data is not None and triggered_id == graph_name:
            node_id = node_data["id"]
            ve = args[-1]

            if not self.visualiser.is_expanded(node_id):
                node_data, ve = self.visualiser.expand_node(node_id, ve)
                node_id = self._get_name(node_data.id)
                node_type = self._get_name(node_data.type)

                card_body = []
                card_body += self.create_heading_5("nd_heading", node_id, className="card-title")
                card_body += self.create_heading_6("nd_type", f"Type: {node_type}", className="text-muted")
                card_body += self.create_horizontal_row()

                for k, v in node_data.properties.items():
                    key = self._get_name(k)
                    card_body += self.create_paragraph(f"{key}:", className="fw-bold mb-0")

                    if isinstance(v, list):
                        # Abstracted list rendering
                        card_body += self.create_list(f"list_{key}", v, 
                                                      className="ms-3 text-secondary")
                    else:
                        card_body += self.create_paragraph(str(v), 
                                                           className="mb-2 ms-3 text-secondary")

                card_body += self.create_horizontal_row()

                card_style = {
                    "className": "shadow p-4 mb-4 bg-white rounded border"
                }

                card = self.create_card(
                    card_body,
                    id="node_details_card",
                    card_body_id="node_details_card_body",
                    **card_style
                )

                return card, ve, self.visualiser.get_style()

            else:
                node_id = node_data["id"]
                ve = args[-1]
                ve = self.visualiser.compress_node(node_id,ve)
                return [],ve,self.visualiser.get_style()
        elif triggered_id == graph_name:
            raise PreventUpdate()
        elif triggered_id == "depth":
            self.visualiser.set_depth(depth)
            _,elements = self.visualiser.build(self._node_id)
            return [],elements,self.visualiser.get_style()
        else:
            elements = args[-1]
            values = args[:-1]

            builder_value = [v for v in values if triggered_id in v]
            assert(len(builder_value) == 1)
            builder_value = builder_value[0].split()[1]
            ve = self.visualiser.get_visual_element(elements,
                                                    handler_name=triggered_id,
                                                    builder_type=builder_value)
            
            return [],ve,self.visualiser.get_style()
        
    def _generate_legend_data(self,stylesheet):
        legend_dict = {"Node Colour" : {},
                       "Edge Colour" : {}}
        for selector in stylesheet:
            if "node_colour" in selector["selector"]:
                name = selector["selector"].replace(".node_colour_","")
                legend_dict["Node Colour"][name] = selector["style"]["background-color"]
            elif "edge_colour" in selector["selector"]:
                name = selector["selector"].replace(".edge_colour_","")
                legend_dict["Edge Colour"][name] = selector["style"]["line-color"]
            
        return legend_dict
    

    def _get_name(self,uri):
        return uri.split("/")[-1]