from dash import dcc, html, Dash, Input, Output
import dash_bootstrap_components as dbc
from tdacm.spclient import SensorPushClient
import plotly.express as px

_SP_CLIENT = SensorPushClient()

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

    fig_temperature = px.line(df_samples, "time", "temperature", title="TEMPERATURE")
    fig_temperature.update_layout(xaxis_title="", yaxis_title="")
    fig_temperature.update_yaxes(ticksuffix="°F")

    fig_humidity = px.line(df_samples, "time", "humidity", title="HUMIDITY")
    fig_humidity.update_layout(xaxis_title="", yaxis_title="")
    fig_humidity.update_yaxes(ticksuffix="%")

    fig_pressure = px.line(df_samples, "time", "barometric_pressure", title="BAROMETRIC_PRESSURE")
    fig_pressure.update_layout(xaxis_title="", yaxis_title="")
    fig_pressure.update_yaxes(ticksuffix=" mb")

    return fig_temperature, fig_humidity, fig_pressure


if __name__ == "__main__":
    app.run_server(debug=True)
