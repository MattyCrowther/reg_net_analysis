from dash import ctx
from dash.exceptions import PreventUpdate

from app.tools.visualiser.dashboards.abstract import AbstractDash
from app.tools.visualiser.visual.net_vis_view_visual import NetVisViewVisual
from app.tools.visualiser.dashboards.full.callbacks import DashBoardCallbacks

graph_name = "graph"
graph_container_name = "graph_container"

class ViewDashboard(AbstractDash):
    def __init__(self, storage, name=None, server=True):
        super().__init__(NetVisViewVisual(storage), name=name, server=server,
                         pathname="/dashboard/")
        self._build_app()
    
    def _build_app(self):
        cbs = DashBoardCallbacks(self, graph_name)

        # called once to build the initial network and visual features 
        # (utility opposed to calling each function individually)
        layout,elements = self.visualiser.build()
        style = self.visualiser.get_style()
        figure = self.create_graph(
            graph_name,
            elements=elements,
            layout=layout,
            stylesheet=style,
            className="cytoscape-graph",
            style={"width":"100%","height":"100%"}
        )

        legend_dict = self._generate_legend_data(style)
        legend = self.create_legend(legend_dict)
        legend = self.create_div(cbs.update_legend.outputs.graph_legend,
                                 legend,className="graph-legend")

        graph_options,cbs = self._create_graph_options(cbs)
        misc_options = self._create_misc_options(cbs)
        node_detils = self.create_div(cbs.graph_update.outputs.node_data_output,[])
        right_side = self.create_div("right_side",legend+node_detils)
        graph_container = self.create_div(
            graph_container_name,
            figure,
            className="graph-container"
        )

        main_content = self.create_div(
            "main-container",
            graph_options+graph_container+right_side+misc_options,
            className="container-fluid main-container"
        )

        [self.add_callback(*callback.to_struct()) for _, callback in cbs]
        self.set_layout(main_content)
        self.build()

    def view_update(self,view):
        triggered_id = ctx.triggered_id
        if triggered_id is None:
            raise PreventUpdate
        builder_value = view.split()[1]
        layout,elements = self.visualiser.build(view_builder=builder_value)
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

    def graph_update(self,node_data,*args):
        '''
        Callback for graph visual change includes 
        view,layout and any other visual based change.
        '''
        triggered_id = ctx.triggered_id
        if triggered_id is None:
            raise PreventUpdate
        
        if triggered_id == graph_name:
            raise PreventUpdate
        else:
            elements = args[-1]
            values = args[:-1]

            builder_value = [v for v in values 
                             if triggered_id in v]
            assert(len(builder_value) == 1)
            builder_value = builder_value[0].split()[1]
            ve = self.visualiser.get_visual_element(elements,
                                                    handler_name=triggered_id,
                                                    builder_type=builder_value)
            
            return [],ve,self.visualiser.get_style()
        
    def layout_update(self,layout_name):
        triggered_id = ctx.triggered_id
        if triggered_id is None:
            raise PreventUpdate
        layout_name = layout_name.split()[-1]
        return [self.visualiser.get_layout(layout_name)]
    
    def export_graph_img(self, get_jpg_clicks, get_png_clicks, get_svg_clicks):
        action = 'store'
        input_id = None
        if ctx.triggered:
            input_id = ctx.triggered[0]["prop_id"].split(".")[0]
            if input_id != "tabs":
                action = "download"
        else:
            raise PreventUpdate
        return [{'type': input_id, 'action': action}]
    
    def _create_graph_options(self,callback_manager):
        """
        Creates a collapsible sidebar with a subtle arrow toggle.
        """
        def _new_options(option_groups):
            radios = []
            cb_inputs = {}
            if not isinstance(option_groups,list):
                option_groups = [option_groups]
            for options in option_groups:
                builder = options["builder"]
                builder_name = options["name"]
                builder_options = options["options"]
                default_name = options["default"]
                radio_options = []
                for option in builder_options:
                    radio_options.append({"label" : f'  {option.capitalize().replace("_"," ").replace("viewbuilder","")}',
                                        "value" : f'{builder} {option}'})
                value = f'{builder} {default_name}'
                radio_option = (self.create_heading_5(f'{builder_name}_heading',builder_name) +
                                self.create_radio_item(builder,
                                                    radio_options,
                                                    value=value) + 
                                self.create_horizontal_row())
                radio_option = self.create_div(f'{builder_name}_div',
                                            radio_option)
                radios += radio_option
                cb_inputs[builder] = "value"
            return radios,cb_inputs
        
        toggle_button = {"className":"sidebar-toggle-button",
                        "data-bs-toggle": "offcanvas",
                        "data-bs-target": "#sidebar",
                        "aria-controls": "sidebar"}
        
        toggle_button = self.create_button("sidebar-toggle-btn",
                                           ">",**toggle_button)
        

        manual_button = self.create_div("tenp", [], className="manual-tip col")
        command_buttons = self.create_div("tenp1", manual_button)
        
        all_radio_buttons = []
        # --View--
        view_options = self.visualiser.get_view_options()
        radios,cb_inputs = _new_options(view_options)
        cb_outputs = {graph_container_name:"children"}
        all_radio_buttons += radios
        callback_manager.new_callback("view_change",
                                      self.view_update,
                                      cb_inputs,
                                      cb_outputs)

        # --Layouts--
        
        layout_options = self.visualiser.get_layout_options()
        radios,cb_inputs = _new_options(layout_options)
        cb_outputs = {graph_name:"layout"}
        all_radio_buttons += radios
        callback_manager.new_callback("layout_change",
                                      self.layout_update,
                                      cb_inputs,
                                      cb_outputs)

        # --Visual Elements--
        visual_options = self.visualiser.get_visual_options()
        radios,cb_inputs = _new_options(visual_options)
        # potential issue here with overwriting attrs in cbs (graph_legend 
        # and elements part of same callback with same key.)
        all_radio_buttons += radios
        callback_manager.update_callback("graph_update",
                                         inputs=cb_inputs)

        header = self.create_heading_3("sidebar_title","Graph Options",
                                       className="offcanvas-title")
        close_button = {"className":"btn-close",
                        "data-bs-dismiss": "offcanvas",
                        "aria-label": "Close"}
        close_button = self.create_button("close_siderbar","", 
                                          **close_button)
        sidebar_header = self.create_div("sidebar_header",
                                         header+close_button,
                                         className="offcanvas-header")
        sidebar_body = self.create_div("sidebar_body",command_buttons+all_radio_buttons,
                                       className="offcanvas-body")
        
        # Sidebar Content (Bootstrap Offcanvas)
        sidebar = {"className":"offcanvas offcanvas-start",
                   "tabIndex": "-1",
                   "aria-labelledby": "sidebar-toggle-btn"}
        sidebar = self.create_div("sidebar",sidebar_header+sidebar_body,**sidebar)

        return self.create_div("sidebar_content",toggle_button+sidebar),callback_manager

    def _create_misc_options(self,cbs):
        """
        Creates a collapsible sidebar with a subtle arrow toggle.
        """
        toggle_button = {"className":"misc-sidebar-toggle-button",
                        "data-bs-toggle": "offcanvas",
                        "data-bs-target": "#misc-sidebar",
                        "aria-controls": "misc-sidebar"}
        
        toggle_button = self.create_button("misc-sidebar-toggle-btn",
                                           "<",**toggle_button)
        
        header = self.create_heading_3("misc_sidebar_title","Misc Options",
                                       className="offcanvas-title")
        close_button = {"className":"btn-close",
                        "data-bs-dismiss": "offcanvas",
                        "aria-label": "Close"}
        close_button = self.create_button("close_misc_sidebar","", 
                                          **close_button)
        sidebar_header = self.create_div("misc_sidebar_header",
                                         header+close_button,
                                         className="offcanvas-header")
        
        export = self.create_heading_5("export_graph_heading", "Export Graph")

        # Wrap buttons in a div with flexbox for spacing
        export += self.create_div("export_buttons",
            self.create_button(cbs.download.inputs.png, "PNG", 
                               className="btn btn-secondary mb-2") +
            self.create_button(cbs.download.inputs.jpg, "JPG", 
                               className="btn btn-secondary mb-2") +
            self.create_button(cbs.download.inputs.svg, "SVG", 
                               className="btn btn-secondary"),
            className="d-flex flex-column align-items-start gap-1"
        )

        export += self.create_horizontal_row()
        export_div = self.create_div("export_options",export)
        sidebar_body = self.create_div("misc_sidebar_body",export_div,
                                       className="offcanvas-body")
        
        # Sidebar Content (Bootstrap Offcanvas)
        sidebar = {"className":"offcanvas offcanvas-end",
                   "tabIndex": "-1",
                   "aria-labelledby": "misc-sidebar-toggle-btn"}
        sidebar = self.create_div("misc-sidebar",sidebar_header+sidebar_body,**sidebar)

        return self.create_div("misc_sidebar",toggle_button+sidebar)
    
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
