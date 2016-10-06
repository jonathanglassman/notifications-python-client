from __future__ import absolute_import

import math
import logging
import json

try:
    import urlparse
except ImportError:
    import urllib.parse as urlparse

from monotonic import monotonic
import requests

from notifications_python_client.errors import HTTPError, InvalidResponse
from notifications_python_client.authentication import create_jwt_token
from notifications_python_client.version import __version__

logger = logging.getLogger(__name__)


class BaseAPIClient(object):
    def __init__(self, base_url=None, service_id=None, api_key=None):
        """
        Initialise the client
        Error if either of base_url or secret missing
        :param base_url - base URL of GOV.UK Notify API:
        :param secret - application secret - used to sign the request:
        :return:
        """
        assert base_url, "Missing base url"
        assert service_id, "Missing service ID"
        assert api_key, "Missing API key"
        self.base_url = base_url
        self.service_id = service_id
        self.api_key = api_key

    def put(self, url, data):
        return self.request("PUT", url, data=data)

    def get(self, url, params=None):
        return self.request("GET", url, params=params)

    def post(self, url, data):
        return self.request("POST", url, data=data)

    def delete(self, url, data=None):
        return self.request("DELETE", url, data=data)

    def request(self, method, url, data=None, params=None):

        logger.debug("API request {} {}".format(method, url))

        payload = json.dumps(data)

        api_token = create_jwt_token(
            self.api_key,
            self.service_id
        )

        headers = {
            "Content-type": "application/json",
            "Authorization": "Bearer {}".format(api_token),
            "User-agent": "NOTIFY-API-PYTHON-CLIENT/{}".format(__version__),
        }

        url = urlparse.urljoin(self.base_url, url)

        start_time = monotonic()
        try:
            response = requests.request(
                method,
                url,
                headers=headers,
                data=payload,
                params=params
            )
            response.raise_for_status()
        except requests.RequestException as e:
            api_error = HTTPError.create(e)
            logger.error(
                "API {} request on {} failed with {} '{}'".format(
                    method,
                    url,
                    api_error.status_code,
                    api_error.message
                )
            )
            raise api_error
        finally:
            elapsed_time = monotonic() - start_time
            logger.debug("API {} request on {} finished in {}".format(method, url, elapsed_time))

        try:
            if response.status_code == 204:
                return
            return response.json()
        except ValueError:
            raise InvalidResponse(
                response,
                message="No JSON response object could be decoded"
            )

    @staticmethod
    def add_pagination(data):
        if 'page_size' not in data:
            raise ValueError('Cannot add pagination to unpaginated data {}'.format(data))

        # links contains URL hints /notifications?page=1
        total_pages = math.ceil(data['total'] / data['page_size'])
        if 'next' in data['links']:
            page_num = int(data['links']['next'].split('=')[-1]) - 1
        elif 'prev' in data['links']:
            page_num = int(data['links']['prev'].split('=')[-1]) + 1
        else:
            # not enough data to paginate
            page_num = total_pages = 1

        data['page_num'] = page_num
        data['total_pages'] = total_pages
        return data
