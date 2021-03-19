import datetime as dt
import pandas as pd
import plotly.graph_objects as go

from data_fetching import get_roof_monthly, get_actual_monthly_production

efficiency = 0.2


def roof_bar_chart(df_uid, sb_uuid, year):
    s1 = get_roof_monthly(df_uid).set_index('monat')['mstrahlung_monat']*efficiency
    s2 = get_actual_monthly_production(year)
    fig = go.Figure()
    df = pd.DataFrame({'Actual': s2, 'Predicted': s1})
    df.index = [dt.date.strftime(dt.date(2020, x, 1), '%B') for x in df.index]
    s = df['Predicted']
    fig.add_trace(go.Scatter(x=s.index, y=s.values, mode='lines', name='Predicted'))
    s = df['Actual']
    fig.add_trace(go.Bar(x=s.index, y=s.values, name=s.name))

    fig.update_layout(margin=go.layout.Margin(l=0, r=0, b=0, t=0),
                      width=400,
                      height=400,
                      xaxis_title='Monthly production per m2 (in kWh)',
                      legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01))

    return fig
