from typing import Any

import requests

from tdacm.constants import SP_API_PREFIX, SP_LOGIN


class SensorPushClient:
    """
    Client for the SensorPush API.
    For more information, see https://www.sensorpush.com/gateway-cloud-api
    """

    def __init__(self):
        self._auth = None
        self._token = None
        self._init_auth()

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
        response = requests.post(url=url, data=data, headers=headers)
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
