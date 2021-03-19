import pandas as pd

import dash_html_components as html
import dash_table

from data_fetching import get_detected_solar_panels


def get_municipality_page(municipality='Illgau'):
    clusters = get_detected_solar_panels(municipality=municipality)
    df = [{'surface': len(x)/100, 'X': '%.4f' % (min(y[0] for y in x)/1000.0), 'Y': '%.4f' % (min(y[1] for y in x)/1000.0)} for x in clusters]
    df = pd.DataFrame(df)
    if not len(df):
        return f'No solar panels detected in {municipality}'

    df = pd.DataFrame(df).sort_values(['surface'], ascending=False)

    labels = {'surface': 'Surface (m2)'}
    c = dash_table.DataTable(
        id='municipality-table',
        columns=[{"name": labels.get(x, x), "id": x} for x in df.columns],
        data=df.to_dict('records'),
    )
    return html.Div([html.H3(f'{municipality} - List of detected solar panels'), c])
