import pandas as pd

import plotly.graph_objects as go

from data_fetching import municipalities, cantons, select, conn, potential_muni

from util import adjust_figure, estimates

import dash_core_components as dcc
import dash_html_components as html


def convert_elem(elem):
    l = [[y.replace('(', '').replace(')', '').split() for y in x.split(',')] for x in
         elem.replace('MULTIPOLYGON Z ((', '').replace('))', '').split('),(')]
    return [[(float(cx) * 1000, float(cy) * 1000) for cx, cy, cz in y] for y in l]


def get_canton_page(canton='Schwyz'):
    t1 = municipalities
    t2 = cantons
    munis = pd.read_sql(select(t1.c.name, t1.c.shape.ST_AsText()).where(t2.c.shape.ST_Contains(t1.c.shape)).where(
        t2.c.name == canton), conn)

    potential = potential_muni[canton]
    maxp = potential.max()

    def get_color(v):
        c1 = 0, 0, 0
        c2 = 0, 200, 0
        return tuple(x1 * (maxp - v) / maxp + x2 * (v) / maxp for x1, x2 in zip(c1, c2))

    fig = go.Figure()
    for name, shape in munis.values:
        l = convert_elem(shape)
        for polygon in l:
            c = 'rgb(%u, %u, %u)' % get_color(potential[name])
            fig.add_trace(
                go.Scatter(x=[x for x, y in polygon], y=[y for x, y in polygon], mode='lines',
                           line={'color': 'lightgrey'}, fill="toself", fillcolor=c, name=name + ' (%.1f GWh)' % (potential[name]),
                           hoveron='fills')
            )
    adjust_figure(fig)
    estimate_epfl = pd.read_sql("SELECT SUM(epfl_potential) FROM buildings WHERE canton = '%s'" % canton, conn).values[0][0]/1000000.0
    estimate_admin = potential.sum()
    return html.Div([
            estimates(estimate_admin, estimate_epfl, 'GWh'),
            dcc.Graph(figure=fig, config={'displayModeBar': False})
        ])
