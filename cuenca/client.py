import os
from typing import Any, ClassVar, Dict, Optional

from requests import Response, Session

from .resources import Transferencia
from .resources.base import Resource
from .version import API_VERSION, CLIENT_VERSION

API_URL = 'https://api.cuenca.com'
SANDBOX_URL = 'https://sandbox.cuenca.com'


class Client:

    base_url: str
    api_key: str
    api_secret: str
    headers = Dict[str, str]
    session = Session
    webhook_secret: str

    # resources
    transferencias: ClassVar = Transferencia

    def __init__(
        self,
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
        webhook_secret: Optional[str] = None,
        api_version: str = API_VERSION,
        sandbox: bool = False,
    ):
        self.headers = {
            'X-Cuenca-Api-Version': api_version,
            'User-Agent': f'cuenca-python/{CLIENT_VERSION}',
        }
        self.session = Session()
        self.api_key = api_key or os.environ['CUENCA_API_KEY']
        self.api_secret = api_secret or os.environ['CUENCA_API_SECRET']
        self.webhook_secret = (
            webhook_secret or os.environ['CUENCA_WEBHOOK_SECRET']
        )
        if sandbox:
            self.base_url = SANDBOX_URL
        else:
            self.base_url = API_URL
        Resource._client = self

    def get(self, endpoint: str, **kwargs: Any) -> Dict[str, Any]:
        return self.request('get', endpoint, **kwargs)

    def post(
        self, endpoint: str, data: Dict[str, Any], **kwargs: Any
    ) -> Dict[str, Any]:
        return self.request('post', endpoint, data, **kwargs)

    def request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]],
        **kwargs,
    ) -> Dict[str, Any]:
        url = self.base_url + endpoint
        response = self.session.request(
            method,
            url,
            auth=(self.api_key, self.api_secret),
            headers=self.headers,
            json=data or {},
            **kwargs,
        )
        self._check_response(response)
        return response.json()

    def _check_response(self, response: Response):
        if response.ok:
            return
        response.raise_for_status()
