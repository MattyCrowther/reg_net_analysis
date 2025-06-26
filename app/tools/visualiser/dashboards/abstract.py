import os
import dash
from dash import dcc
import dash_bootstrap_components as dbc
import dash_cytoscape as cyto
from dash import html
import dash_daq as daq
import dash_bio as dashbio
from dash import dash_table
from dash.dependencies import Input,State,Output

cyto.load_extra_layouts()

external_scripts = [
    {
        "src": "https://cdn.jsdelivr.net/npm/bootstrap@5.3.1/dist/js/bootstrap.bundle.min.js",
        "crossorigin": "anonymous"
    }
]

style_sheet = [
    {
        "rel": "stylesheet",
        "href": "https://cdn.jsdelivr.net/npm/bootstrap@5.3.1/dist/css/bootstrap.min.css",
        "crossorigin": "anonymous"
    }
]

assets =  os.path.join(os.path.dirname(os.path.realpath(__file__)),
                       "..",
                       "assets")

class AbstractDash:
    def __init__(self, visualiser, name=None, 
                 pathname=None, 
                 server=True, **kwargs):
        self.app = dash.Dash(name=name, server=server, 
                             url_base_pathname=pathname,
                             external_stylesheets=style_sheet, 
                             external_scripts=external_scripts, 
                             assets_folder=assets,
                             **kwargs)
        self.pathname = pathname
        self.visualiser= visualiser
        self.children = []
        self.parameters_calls = []
        self.callbacks = {}
        self.app.layout = html.Div()

    def run(self):
        self.app.run(debug=True)
        
    def build(self):
        for k, v in self.callbacks.items():
            if v["states"] == []:
                self.app.callback(v["outputs"], v["inputs"])(k)
            else:
                self.app.callback(v["outputs"], v["inputs"], v["states"])(k)

    def add_callback(self, function, inputs, outputs, states=None):
        def cast(i):
            if isinstance(i,(Input,Output,State)):
                i = [i]
            elif isinstance(i,dict):
                i = list(i.values())
            elif isinstance(i,list):
                pass
            else:
                i = list(i)
            return i
        if states is None:
            states = []
        self.callbacks[function] = {
            "inputs": cast(inputs), 
            "outputs": cast(outputs), 
            "states": cast(states)
        }

    def set_layout(self,layout):
        self.app.layout = layout
        
    def create_graph(self,graph_id,**kwargs):
        return cyto.Cytoscape(id=graph_id,**kwargs)

    def create_heading_1(self, identifier, children,  **kwargs):
        return [html.H1(id=identifier, children=children, **kwargs)]

    def create_heading_2(self, identifier, children,  **kwargs):
       return [html.H2(id=identifier, children=children, **kwargs)]

    def create_heading_3(self, identifier, children,  **kwargs):
       return [html.H3(id=identifier, children=children, **kwargs)]

    def create_heading_4(self, identifier, children,  **kwargs):
       return [html.H4(id=identifier, children=children, **kwargs)]

    def create_heading_5(self, identifier, children,  **kwargs):
       return [html.H5(id=identifier, children=children, **kwargs)]

    def create_heading_6(self, identifier, children,  **kwargs):
       return [html.H6(id=identifier, children=children, **kwargs)]

    def create_div(self, identifier, children,  **kwargs):
       return [html.Div(id=identifier, children=children, **kwargs)]

    def create_button(self, identifier, name=None, 
                      href=None,  **kwargs):
        if href is None:
            button = html.Button(name, id=identifier, **kwargs)
        else:
            button = html.A(html.Button(identifier), href="/" +
                            href, target="_blank", **kwargs)
    
        return [button]

    def create_input(self, identifier, value=None, 
                      **kwargs):
        if value is None:
            value = ""
        input_l = dcc.Input(id=identifier, value=value, **kwargs)
        return [input_l]

    def create_i(self, identifier,  **kwargs):
        input_l = html.I(id=identifier, **kwargs)
        return [input_l]

    def create_span(self, identifier, children, 
                     **kwargs):
        input_l = html.Span(id=identifier, children=children, **kwargs)
        return [input_l]

    def create_dropdown(self, identifier, options, 
                        value=None,  **kwargs):
        dropdown = dcc.Dropdown(
            id=identifier, options=options, value=value,**kwargs)
        return [dropdown]

    def create_radio_item(self, identifier, options, value=None, 
                           **kwargs):
        radio = dcc.RadioItems(
            id=identifier, options=options, value=value, **kwargs)
        return [radio]

    def create_checklist(self, identifier, name, options, 
                          **kwargs):
        checklist = dcc.Checklist(id=identifier, options=options, **kwargs)
        if name is not None:
            label = html.Label(name)
            return [label, checklist]
        else:
            return [checklist]

    def create_slider(self, identifier, min_val, max_val, 
                      default_val=None, step=None, 
                      marks=None,  **kwargs):
        if default_val is None:
            default_val = max_val/2
        if marks is None:
            marks = {}
            marks[min_val] = str(int(min_val))
            marks[max_val] = str(int(max_val))
        if step is None:
            step = max_val/4
        slider = dcc.Slider(id=identifier, min=min_val, max=max_val,
                            value=default_val, marks=marks, step=step, **kwargs)
        return [slider]

    def create_sidebar(self, id, name, content,  **kwagrs):
        children = [html.H2(name, className="display"), *content]
        sidebar = html.Div(id=id, children=children, **kwagrs)
        return [sidebar]

    def create_horizontal_row(self, add=False):
        return [html.Hr()]

    def add_table(self, identifier, children,  **kwargs):
        table = html.Table(id=identifier, children=children, **kwargs)
        return [table]

    def add_tr(self, identifier, children,  **kwargs):
        tr = html.Tr(id=identifier, children=children, **kwargs)
        return [tr]

    def add_th(self, identifier, children,  **kwargs):
        th = html.Th(id=identifier, children=children, **kwargs)
        return [th]

    def add_td(self, identifier, children,  **kwargs):
        th = html.Td(id=identifier, children=children, **kwargs)
        return [th]

    def create_line_break(self, number=1, add=False):
        return [html.Br()] * number

    def create_alert(self, identifier, text,  **kwargs):
        alert = dbc.Alert(id=identifier, children=text, **kwargs)
        return [alert]

    def create_toggle_switch(self, identifier, name, value=False, 
                              **kwargs):
        switch = daq.ToggleSwitch(
            id=identifier, label=name, value=value, **kwargs)
        return [switch]

    def create_color_picker(self, identifier, name,  **kwargs):
        picker = daq.ColorPicker(id=identifier, label=name, **kwargs)
        return [picker]

    def create_indicator(self, identifier, name, 
                         color="green",  **kwargs):
        indicator = daq.Indicator(
            id=identifier, label=name, color=color, **kwargs)
        return [indicator]

    def create_numeric_input(self, identifier, name, min_val, max_val, 
                             default_val=None,  **kwargs):
        if default_val is None:
            default_val = max_val/2

        label = html.Label(name)
        num_input = daq.NumericInput(
            id=identifier, min=min_val, max=max_val, 
            value=default_val, **kwargs)
        return [label, num_input]

    def create_file_upload(self, identifier, name, graph_parent_id, 
                            **kwargs):
        upload_box = dcc.Upload(id=identifier, children=html.Div(
            [dbc.Button(name, color="secondary", className="mr-1")]), 
            multiple=True, **kwargs)
        return [upload_box]

    def create_accordion(self, identifier, cards,  **kwargs):
        f_cards = []
        for index, (name, value) in enumerate(cards):
            id_index = identifier + str(index)
            c = html.Button(children=name, id="", 
            className="btn btn-link", type="button", **{
                      "data-toggle": "collapse", 
                      "data-target": f"#collapse{id_index}",
                      "aria-expanded": "false", 
                      "aria-controls": f"collapse{id_index}"})

            c = self.create_heading_5(name+"_h", c, className="mb-0")
            c = self.create_div(
                f"heading{id_index}", c, className="card-header")

            b = self.create_div(name+"_c_b", value, className="card-body")
            b = self.create_div(f'collapse{id_index}', b, **{"className": "collapse",
                                "aria-labelledby": f"heading{id_index}", 
                                "data-parent": f"#{identifier}"})
            card = self.create_div(name+"_c", c+b, className="card")
            f_cards += (card)

        acc = self.create_div(identifier, f_cards,
                              className="accordion", **kwargs)
        return acc

    def add_sequence_viewer(self, identifier, sequence,  
                            **kwargs):
        sequence_box = dashbio.SequenceViewer(
            id=identifier, sequence=sequence, **kwargs)
        return [sequence_box]

    def create_complex_table(self, identifier, columns, 
                             data=None,  **kwargs):
        table = dash_table.DataTable(
            id=identifier,
            columns=columns,
            data=data,
            filter_action="native",
            sort_action="native",
            sort_mode="multi",
            column_selectable="single",
            row_selectable="single",
            selected_columns=[],
            selected_rows=[],
            page_action="native",
            page_current=0,
            page_size=20,
            style_cell={'textAlign': 'left'},
            style_table={'overflowX': 'auto'})

        return [table]

    def create_hyperlink(self, identifier, href, add=False):
        a_tag = html.A(identifier, href=href)
        return [a_tag]

    def create_paragraph(self, text,  **kwargs):
        p_tag = html.P(text, **kwargs)
        return [p_tag]

    def create_detail(self, identifier, children,  **kwargs):
        detail_tag = html.Details(id=identifier, children=children, 
                                  **kwargs)
        return [detail_tag]

    def create_summary(self, identifier, text,  **kwargs):
        sum_tag = html.Summary(id=identifier, children=text, **kwargs)
        return [sum_tag]

    def create_modal(self, identifier, close_identifier, name, contents, 
                     submit_button=None,  **kwargs):
        modal_header = self.create_heading_3(name,name)
        modal_body = dbc.ModalBody(contents)
        if submit_button is not None:
            submit_button = [dbc.Button(
                "Submit", id=submit_button, className="ml-auto")]
        else:
            submit_button = []
        modal_footer = dbc.ModalFooter(
            submit_button + [dbc.Button("Close", id=close_identifier, 
                                        className="ml-auto")])
        modal = dbc.Modal(id=identifier, children=modal_header+[
                          modal_body, modal_footer], size="xl", **kwargs)

        return [modal]

    def create_modal_body(self, identifiers, contents, 
                           **kwargs):
        modal_body = dbc.ModalBody(contents, id=identifiers)
        return [modal_body]

    def create_question_mark(self, identifier,  **kwargs):
        q_mark = html.Abbr(id=identifier, children="\uFE56",
                           className="help-tip")
        return [q_mark]

    def create_legend(self,legend_dict):
        legend_body = []
        for name, legend_items in legend_dict.items():
            l_children = self.create_heading_5(name, name)
            for item_name, item_val in legend_items.items():
                style = {"background": item_val}
                l_children.append(
                    html.Li(children=[html.Span(style=style), 
                                      html.P(item_name)]))
            legend_body.append(
                html.Ul(children=l_children, className="legend-labels"))

        return  self.create_div(
            "legend_body", legend_body, className="legend-scale")

    def create_text_area(self, identifier,  **kwargs):
        ta = dcc.Textarea(id=identifier, style={
                          'width': '100%', 'height': 500}, **kwargs)

        return [ta]

    def create_card(self,children,card_body_id=None,
                    **kwargs):
        card = dbc.Card(dbc.CardBody(children,id=card_body_id),**kwargs)
        return [card]
    
    def create_collapse(self,children):
        collapsible_body = dbc.Collapse(
            children,
            id="banner-collapse",
            is_open=False
        )
        return [collapsible_body]
    
    def create_location(self,identifier):
        return [dcc.Location(id=identifier, refresh=False)]

    def create_unordered_list(self, items, className=None):
        list_items = [html.Li(str(i)) for i in items]
        return [html.Ul(list_items, className=className)]
    
    def create_list(self, identifier, items, className=None):
        list_items = [html.Li(str(i)) for i in items]
        ul = html.Ul(id=identifier, children=list_items, className=className)
        return [ul]
