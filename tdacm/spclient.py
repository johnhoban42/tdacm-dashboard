from typing import Any

import pandas as pd
import requests

from tdacm.constants import SP_API_PREFIX, SP_LOGIN
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

    def get_samples(self, start_date: DateLike) -> pd.DataFrame:
        """
        Get a time series of temperature, humidity, and pressure data

        :param start_date:
            Time series start date (UTC)
        :return:
            DataFrame with columns `time`, `temperature`, `humidity`, and `pressure`
        """
        start_dt = pd.Timestamp(start_date)
        samples = self._send_request(
            "samples",
            {
                "limit": 10000,
                "sensors": [self._sensor_id],
                "startTime": start_dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
            },
        )
        df_samples = pd.DataFrame(samples["sensors"][self._sensor_id])
        df_samples = df_samples.assign(
            time=pd.to_datetime(df_samples["observed"], utc=True)
        ).drop(columns=["gateways", "observed"])
        return df_samples
