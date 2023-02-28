from concurrent.futures import ThreadPoolExecutor
from typing import Any

import pandas as pd
import requests

from tdacm.constants import DATA_COLS, SP_API_PREFIX, SP_LOGIN
from tdacm.custom_types import DateLike


class SensorPushClient:
    """
    Client for the SensorPush API.
    For more information, see https://www.sensorpush.com/gateway-cloud-api
    """

    def __init__(self):
        self._auth = None
        self._token = None
        self._init_auth()
        self._sensor_id = self._get_sensor_id()
        self._sensor_name = self._get_sensor_name()

    def _send_request(self, endpoint: str, data: dict[str, Any]) -> dict[str, Any]:
        """
        Helper method to send a POST request to the SensorPush API

        :param endpoint:
            URL endpoint
        :param data:
            JSON data to send to the endpoint
        :return:
            JSON data returned from the endpoint as a dict
        """
        url = SP_API_PREFIX + endpoint
        headers = {"accept": "application/json", "Authorization": self._token}
        response = requests.post(url=url, json=data, headers=headers)
        if response.status_code != 200:
            # TODO - Add error handling for expired or bad auth
            pass
        return response.json()

    def _init_auth(self):
        """
        Initialize the authorization code and request tokens
        """
        self._auth = self._send_request("oauth/authorize", SP_LOGIN)["authorization"]
        self._get_access_token()

    def _get_access_token(self):
        """
        Get a fresh access token to use with all other API requests
        """
        self._token = self._send_request(
            "oauth/accesstoken", {"authorization": self._auth}
        )["accesstoken"]

    def _get_sensor_id(self) -> str:
        """
        Get the TDACM sensor ID. Assume that there is only one sensor
        """
        sensors = self._send_request("devices/sensors", {})
        return list(sensors.keys())[0]

    def _get_sensor_name(self) -> str:
        """
        Get the TDACM sensor name. Assume that there is only one sensor
        """
        sensors = self._send_request("devices/sensors", {})
        return list(sensors.values())[0]["name"]

    @property
    def sensor_name(self):
        """TDACM sensor name"""
        return self._sensor_name

    def _get_samples_helper(
        self, date_range: tuple[pd.Timestamp, pd.Timestamp]
    ) -> pd.DataFrame:
        """
        Helper method to fetch a one-day subset of sample data.
        """
        samples = self._send_request(
            "samples",
            {
                "limit": 2_000,
                "sensors": [self._sensor_id],
                "measures": ["temperature", "humidity", "barometric_pressure"],
                "startTime": date_range[0].strftime("%Y-%m-%dT%H:%M:%S+0000"),
                "stopTime": date_range[1].strftime("%Y-%m-%dT%H:%M:%S+0000"),
            },
        )
        # No data - return an empty DataFrame with the expected columns
        if not samples.get("sensors"):
            return pd.DataFrame(columns=DATA_COLS)
        # Data found - format and return to main thread
        df_samples = pd.DataFrame(samples["sensors"][self._sensor_id])
        df_samples = (
            df_samples.assign(time=pd.to_datetime(df_samples["observed"], utc=True))
            .sort_values("time")
            .reset_index()[DATA_COLS]
        )
        return df_samples

    def get_samples(self, start_date: DateLike) -> pd.DataFrame:
        """
        Get a time series of temperature, humidity, and pressure data

        :param start_date:
            Time series start date (UTC)
        :return:
            DataFrame with columns `time`, `temperature`, `humidity`, and `pressure`
        """
        start_dt = pd.Timestamp(start_date, tz="UTC")
        end_dt = pd.Timestamp.utcnow()
        # Sample request I/O time is proportional to the length of time requested
        # Run individual requests for each day concurrently to speed up I/O
        date_range = pd.date_range(start_dt, end_dt, freq="D")
        date_tuples = [(start, end) for start, end in zip(date_range, date_range[1:])]
        # Include "remainder" time period of the partial last day
        date_tuples.append((date_range[-1], end_dt))
        with ThreadPoolExecutor(10) as executor:
            responses = executor.map(self._get_samples_helper, date_tuples)
        df_samples = pd.concat(responses).sort_values("time")
        return df_samples
