import dash_bootstrap_components as dbc
import dash_html_components as html


def adjust_figure(fig):
    ax = {'showgrid': False, 'zeroline': False, 'visible': False}
    fig.update_layout(width=1000, height=800, showlegend=False, xaxis=ax, yaxis=ax,
                      paper_bgcolor='rgba(0,0,0,0)',
                      plot_bgcolor='rgba(0,0,0,0)')
    fig.update_yaxes(scaleanchor="x", scaleratio=1)


def estimates(v1, v2, unit):
    return html.Div([
        dbc.Button(
            ["Annual potential (admin.ch)", dbc.Badge("%.1f %s" % (v1, unit), color="light", className="ml-1")],
            color="primary",
        ),
        html.Label(' - '),
        dbc.Button(
            ["Annual potential (EPFL)", dbc.Badge("%.1f %s" % (v2, unit) if v2 is not None else 'N/A', color="light", className="ml-1")],
            color="secondary",
        )
    ])
