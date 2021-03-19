import pandas as pd

import plotly.graph_objects as go

from data_fetching import cantons, select, conn, potential_canton
from util import adjust_figure, estimates

import dash_core_components as dcc
import dash_html_components as html


def convert_elem(elem):
    l = [[y.replace('(', '').replace(')', '').split() for y in x.split(',')] for x in
         elem.replace('MULTIPOLYGON Z ((', '').replace('))', '').split('),(')]
    return [[(float(cx) * 1000, float(cy) * 1000) for cx, cy, cz in y] for y in l]


maxp = potential_canton.max()


def get_color(v):
    c1 = 0, 0, 0
    c2 = 0, 200, 0
    return tuple(x1*(maxp - v)/maxp + x2*(v)/maxp for x1,x2 in zip(c1, c2))


def get_country_page():
    t2 = cantons
    fig = go.Figure()
    for name, shape in pd.read_sql(select(t2.c.name, t2.c.shape.ST_AsText()), conn).values:
        l = convert_elem(shape)
        potential = potential_canton[name]

        for polygon in l:
            c = 'rgb(%u, %u, %u)' % get_color(potential)
            fig.add_trace(
                go.Scatter(x=[x for x, y in polygon], y=[y for x, y in polygon], mode='lines',
                           line={'color': 'white'}, fill="toself", fillcolor=c, name=name + ' (%.1f TWh)' % (potential_canton[name]/1000),
                           hoveron='fills')
            )
    adjust_figure(fig)
    estimate_epfl = pd.read_sql("SELECT SUM(epv_kwh_a) FROM rooftop_pv_ch_annual_by_building", conn).values[0][0]/1000000000.0
    estimate_admin = potential_canton.sum()/1000.0
    return html.Div([estimates(estimate_admin, estimate_epfl, 'TWh'),
                     dcc.Graph(figure=fig, config={'displayModeBar': False})])
