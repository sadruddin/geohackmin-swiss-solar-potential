import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import plotly.graph_objects as go

from data_fetching import get_roofs, get_detected_solar_panels, get_building_potential

from country_page import get_country_page
from canton_page import get_canton_page
from municipality_page import get_municipality_page

from util import estimates

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)

# the style arguments for the sidebar. We use position:fixed and a fixed width
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}

# the styles for the main content position it to the right of the sidebar and
# add some padding.
CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

sidebar = html.Div(
    [
        html.H2("S2P2", className="display-4"),
        html.Hr(),
        html.P(
            "Everything about solar power in Switzerland", className="lead"
        ),
        dbc.Nav(
            [
                dbc.NavLink("Switzerland", href="/", active="exact"),
                dbc.NavLink("Canton", href="/canton", active="exact"),
                dbc.NavLink("Municipality", href="/municipality", active="exact"),
                dbc.NavLink("Building", href="/building", active="exact"),
            ],
            vertical=True,
            pills=True,
        ),
    ],
    style=SIDEBAR_STYLE,
)

content = html.Div(id="page-content", style=CONTENT_STYLE)

app.layout = html.Div([dcc.Location(id="url"), sidebar, content])



@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    global sb_uuid
    if pathname == "/":
        sb_uuid = None
        return get_country_page()
    elif pathname == "/canton":
        sb_uuid = None
        return get_canton_page()
    elif pathname == "/municipality":
        #from specific_roof import get_specific_roof
        sb_uuid = None
        return get_municipality_page()
    elif pathname == "/building":
        #from specific_roof import get_specific_roof
        return get_specific_roof()
    # If the user tries to reach a different page, return a 404 message
    return dbc.Jumbotron(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ]
    )

def get_specific_roof():
    table = html.Div([
        dbc.Row([
            dbc.Col(html.Div([
                                dbc.InputGroup(
                                    [
                                        dbc.InputGroupAddon("Y", addon_type="prepend"),
                                        dbc.Input(id='y-slider', type='number', min=0, max=9500, step=500, value=2000),
                                        dbc.InputGroupAddon("X", addon_type="prepend"),
                                        dbc.Input(id='x-slider', type='number', min=0, max=9500, step=500, value=8000),
                                    ],
                                    className="mb-3",
                                ),
                dbc.Checklist(
                    options=[
                        {"label": "Show detected solar arrays", "value": "show_panels"},
                    ],
                    value=[],
                    id="map-config",
                    switch=True,
                )

            ]
                    ), md=8),
            dbc.Col(dbc.RadioItems(
            options=[{'label': x, 'value': x} for x in range(2015, 2021)],
            value=2020,
            labelStyle={'display': 'idasnline-block'},
            inline=True,
            id='year-choice'
    )
)

        ]),
        dbc.Row([
            dbc.Col(
                dcc.Graph(id='map', config={
        'displayModeBar': False
    }), md=8
            ),
            dbc.Col(
                html.Div([html.Div(id='roof-estimates'), html.Br(), dcc.Graph(id='barchart', config={
        'displayModeBar': False
    })]), md=4
            ),
        ]),
    ])
    return table

x, y = 2697, 1205

# Define callback to update graph
@app.callback(
    Output('map', 'figure'),
    [Input("x-slider", "value"), Input("y-slider", "value"), Input("map-config", "value"), Input('roof-estimates', 'children')]
)
def update_figure(dx, dy, conf, children):
    global mapping_roof
    global mapping_building
    global x,y

    from interactive_map import interactive_map
    global sb_uuid
    x1 = x + dx/10000
    y1 = y + dy/10000
    x2 = x1 + 0.1
    y2 = y1 + 0.1
    roofs = get_roofs(x1, y1, x2, y2)
    panels = get_detected_solar_panels(rectangle=(x1, y1, x2, y2)) if 'show_panels' in conf else []
    mapping_roof = {(i + 1): x['df_uid'] for i, (_, x) in enumerate(roofs.iterrows())}
    mapping_building = {(i + 1): x['sb_uuid'] for i, (_, x) in enumerate(roofs.iterrows())}
    return interactive_map(x, y, dx=dx, dy=dy, roofs=roofs, panels=panels, sb_uuid=sb_uuid)

df_uid = None
sb_uuid = None
mapping_roof = {}
mapping_building = {}

@app.callback(
    Output('roof-estimates', 'children'),
    [Input("map", "clickData")]
)
def update_label(data):
    global df_uid
    global sb_uuid

    if data is not None:
        n = data['points'][0]['curveNumber']
        df_uid = mapping_roof[n] if n > 0 else None
        sb_uuid = mapping_building[n] if n > 0 else None

    if sb_uuid is not None:
        s = get_building_potential(sb_uuid)
        v1 = s['gstrahlung']*0.17*0.8/1000.0
        try:
            v2 = s['epfl_potential']/1000.0
        except:
            v2 = None
        return [estimates(v1, v2, 'MWh')]
    else:
        return []


@app.callback(
    Output('barchart', 'figure'),
    [Input("map", "clickData"), Input("year-choice", "value")]
)
def update_label(data, year):
    from roof_bar_chart import roof_bar_chart

    global df_uid
    global sb_uuid

    if data is not None:
        n = data['points'][0]['curveNumber']
        df_uid = mapping_roof[n] if n > 0 else None
        sb_uuid = mapping_building[n] if n > 0 else None

    if df_uid is not None:
        fig = roof_bar_chart(df_uid, sb_uuid, year)
    else:
        fig = go.Figure()
        ax = {'showgrid': False, 'zeroline': False, 'visible': False}
        fig.update_layout(showlegend=False, xaxis=ax, yaxis=ax,
                          paper_bgcolor='rgba(0,0,0,0)',
                          plot_bgcolor='rgba(0,0,0,0)')

    return fig

if __name__ == "__main__":
    app.run_server(debug=True, host='0.0.0.0', port=8050)