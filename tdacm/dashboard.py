import dash_bootstrap_components as dbc
import plotly.express as px
from dash import dcc, html, Dash, Input, Output

from tdacm.spclient import SensorPushClient

_SP_CLIENT = SensorPushClient()

PLOT_STYLE = dict(
    xaxis_title="",
    yaxis_title="",
    title_x=0.5,
    margin={"l": 20, "r": 20, "t": 50, "b": 10},
    paper_bgcolor="#2A2A2A",
    plot_bgcolor="#4A4A4A",
    xaxis_gridcolor="#505050",
    yaxis_gridcolor="#505050",
    font={"family": "Helvetica", "color": "#CADBE3"},
)

app = Dash(__name__)
app.layout = html.Div(
    [
        dcc.Interval(id="dashboard-interval", interval=60 * 1000),
        dbc.Row(dcc.Graph(id="dashboard-fig-temperature")),
        dbc.Row(dcc.Graph(id="dashboard-fig-humidity")),
        dbc.Row(dcc.Graph(id="dashboard-fig-pressure")),
    ]
)


@app.callback(
    Output("dashboard-fig-temperature", "figure"),
    Output("dashboard-fig-humidity", "figure"),
    Output("dashboard-fig-pressure", "figure"),
    Input("dashboard-interval", "n_intervals"),
)
def update_samples(n_intervals):
    """
    Automatically the sample graphs at a regular interval
    """
    df_samples = _SP_CLIENT.get_samples("2023-02-27")

    fig_temperature = px.line(
        df_samples,
        "time",
        "temperature",
        title="<b>TEMPERATURE</b>",
        color_discrete_sequence=["#9EDDE7"],
    )
    fig_temperature.update_layout(PLOT_STYLE)
    fig_temperature.update_yaxes(ticksuffix="°F")

    fig_humidity = px.line(
        df_samples,
        "time",
        "humidity",
        title="<b>HUMIDITY</b>",
        color_discrete_sequence=["#9EDDE7"],
    )
    fig_humidity.update_layout(PLOT_STYLE)
    fig_humidity.update_yaxes(ticksuffix="%")

    fig_pressure = px.line(
        df_samples,
        "time",
        "barometric_pressure",
        title="<b>BAROMETRIC PRESSURE</b>",
        color_discrete_sequence=["#9EDDE7"],
    )
    fig_pressure.update_layout(PLOT_STYLE)
    fig_pressure.update_yaxes(ticksuffix="mb")

    return fig_temperature, fig_humidity, fig_pressure
