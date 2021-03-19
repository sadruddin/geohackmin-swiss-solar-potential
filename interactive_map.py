import functools
import glob
import logging

from skimage import io

import plotly.express as px
import plotly.graph_objects as go


@functools.cache
def get_maptile(x, y):
    logging.info('Fetching map tile %u %u' % (x, y))
    mapfile = glob.glob('data/swissimage/*%u-%u*.tif' % (x, y))[0]
    maptile = io.imread(mapfile)
    return maptile


def interactive_map(x, y, dx, dy, roofs, panels, sb_uuid=None):
    width = 750

    x1 = x + dx / 10000
    y1 = y + dy / 10000
    x2 = x1 + width/10000
    y2 = y1 + width/10000

    df = roofs

    maxy = df['shape'].apply(lambda x: max(max(z[1] for z in y) for y in x)).max()
    miny = df['shape'].apply(lambda x: min(min(z[1] for z in y) for y in x)).min()

    maxx = df['shape'].apply(lambda x: max(max(z[0] for z in y) for y in x)).max()
    minx = df['shape'].apply(lambda x: min(min(z[0] for z in y) for y in x)).min()

    efficiency = 0.17

    maptile = get_maptile(x, y)
    img = maptile[(10000 - dy - width):(10000 - dy), dx:dx + width, :]
    fig = px.imshow(img)

    for index, row in df.iterrows():
        for polygon in row['shape']:
            c = 'rgba(0, 0, 255, 0.2)'
            if sb_uuid == row['sb_uuid']:
                c = 'rgba(255, 255, 0, 0.5)'
            fig.add_trace(
                go.Scatter(x=[x * 10 for x, y in polygon], y=[width - y * 10 for x, y in polygon], mode='lines',
                           name=str(row['df_uid']), line={'color': c}, fill="toself", fillcolor=c,
                           text=[row['sb_uuid']] * len(polygon),
                           hoveron='points+fills')
            )
    for i, cluster in enumerate(panels):
        def check_point(x, y):
            return x >= dx and x <= (dx + width) and y >= dy and y <= (dy + width)

        cluster = [((x - int(x/1000)*1000)*10, (y - int(y/1000)*1000)*10) for x, y in cluster]
        visible = [x for x in cluster if check_point(*x)]
        if visible:
            surface = len(cluster) / 100  # in square meters
            fig.add_trace(
                go.Scatter(x=[x - dx for x, y in visible], y=[width - (y - dy) for x, y in visible], mode='markers',
                           name='~ %u m2' % (surface))
            )

    xaxis = {
        'range': [0, width],
        'showgrid': False,  # thin lines in the background
        'zeroline': False,  # thick line at x=0
        'visible': False,  # numbers below
    }
    yaxis = {
        'range': [width, 0],
        'showgrid': False,  # thin lines in the background
        'zeroline': False,  # thick line at x=0
        'visible': False,  # numbers below
    }

    fig.update_layout(template="plotly_white", height=width, width=width, showlegend=False, xaxis=xaxis, yaxis=yaxis,
                      margin=go.layout.Margin(
                          l=0,  # left margin
                          r=0,  # right margin
                          b=0,  # bottom margin
                          t=0,  # top margin
                      ))
    return fig