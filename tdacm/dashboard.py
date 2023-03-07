from functools import partial

import dash
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from dash import dcc, html, Input, Output, State
from dash_extensions.enrich import DashProxy, MultiplexerTransform
from pandas.tseries.offsets import Minute, Hour, Day

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

TIME_BUTTONS = [f"dashboard-btn-{x}" for x in ("30m", "24h", "7d")]

app = DashProxy(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    transforms=[MultiplexerTransform()],
)
app.title = "TDACM Dashboard"
app.layout = html.Div(
    [
        dbc.Navbar(
            dbc.Container(
                [
                    dbc.Col(dbc.NavbarBrand("TDACM DASHBOARD"), width=7),
                    dbc.Col(html.I("Loading...", id="dashboard-timestamp"), width=3),
                    dbc.Col(
                        [
                            # Start the app in 30M mode (30M button disabled)
                            dbc.Button(
                                "30M",
                                id="dashboard-btn-30m",
                                class_name="navbar-button",
                                disabled=True,
                            ),
                            dbc.Button(
                                "24H",
                                id="dashboard-btn-24h",
                                class_name="navbar-button",
                            ),
                            dbc.Button(
                                "7D",
                                id="dashboard-btn-7d",
                                class_name="navbar-button",
                            ),
                        ]
                    ),
                ]
            ),
            dark=True,
        ),
        dcc.Interval(id="dashboard-interval", interval=60 * 1000),
        dbc.Row(
            dbc.Spinner(
                dcc.Graph(id="dashboard-fig-temperature"), color="info", type="grow"
            )
        ),
        dbc.Row(
            dbc.Spinner(
                dcc.Graph(id="dashboard-fig-humidity"), color="info", type="grow"
            )
        ),
        dbc.Row(
            dbc.Spinner(
                dcc.Graph(id="dashboard-fig-pressure"), color="info", type="grow"
            )
        ),
    ]
)


def update_button_state(n_clicks):
    """
    Disable a time-range button when clicked and enable all others
    """
    if not n_clicks:
        return dash.no_update
    trigger_id = dash.callback_context.triggered_id
    return [btn_id == trigger_id for btn_id in TIME_BUTTONS]


for btn in TIME_BUTTONS:
    app.callback(
        [Output(btn_id, "disabled") for btn_id in TIME_BUTTONS],
        Input(btn, "n_clicks"),
    )(partial(update_button_state))


@app.callback(
    Output("dashboard-fig-temperature", "figure"),
    Output("dashboard-fig-humidity", "figure"),
    Output("dashboard-fig-pressure", "figure"),
    Output("dashboard-timestamp", "children"),
    Input("dashboard-interval", "n_intervals"),
    Input("dashboard-btn-30m", "disabled"),
    State("dashboard-btn-24h", "disabled"),
    State("dashboard-btn-7d", "disabled"),
)
def update_samples(n_intervals, active_30m, active_24h, active_7d):
    """
    Automatically the sample graphs at a regular interval

    Sample time series range depends on which time button is clicked/activated

    Can be triggered by the interval component, or by the 30M button changing
    state, which occurs when any of the three time buttons are clicked
    """
    now = pd.Timestamp.now()
    if active_30m:
        start_dt = now - Minute(30)
    elif active_24h:
        start_dt = now - Hour(24)
    elif active_7d:
        start_dt = now - Day(7)
    # App start trigger - 30M
    else:
        start_dt = now - Minute(30)

    # Get samples and draw figures
    df_samples = _SP_CLIENT.get_samples(start_dt)

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

    # Get last update timestamp
    ts = df_samples.tail(1).time.squeeze()
    label = f"Last Updated: {ts:%b %m, %Y %#I:%M:%S %p}"

    return fig_temperature, fig_humidity, fig_pressure, label
