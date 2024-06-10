"""
    Copyright 2019 Ipregistry (https://ipregistry.co).

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

       https://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
"""

import abc
import json
import requests
import six
import sys

from six.moves.urllib.parse import quote

from .__init__ import __version__
from .model import ApiError, ClientError, IpInfo


@six.add_metaclass(abc.ABCMeta)
class IpregistryRequestHandler:
    def __init__(self, config):
        self._config = config

    @abc.abstractmethod
    def batch_lookup(self, ips, options):
        pass

    @abc.abstractmethod
    def origin_lookup(self, options):
        pass

    @abc.abstractmethod
    def single_lookup(self, ip, options):
        pass

    def _build_base_url(self, ip, options):
        result = self._config.base_url + "/" + ip + "?key=" + self._config.api_key

        for key, value in options.items():
            if isinstance(value, bool):
                value = 'true' if value is True else 'false'
            result += "&" + key + "=" + quote(value)

        return result


class DefaultRequestHandler(IpregistryRequestHandler):
    def batch_lookup(self, ips, options):
        try:
            r = requests.post(self._build_base_url('', options), data=json.dumps(ips), headers=self._headers(), timeout=self._config.timeout)
            r.raise_for_status()
            return list(map(lambda data: LookupError(data) if 'code' in data else IpInfo(**data), r.json()['results']))
        except requests.HTTPError:
            raise ApiError(r.json())
        except Exception as e:
            raise ClientError(e)

    def origin_lookup(self, options):
        return self.single_lookup('', options)

    def single_lookup(self, ip, options):
        try:
            r = requests.get(self._build_base_url(ip, options), headers=self._headers(), timeout=self._config.timeout)
            r.raise_for_status()
            return IpInfo(**r.json())
        except requests.HTTPError:
            raise ApiError(r.json())
        except Exception as e:
            raise ClientError(e)

    def _headers(self):
        return {
            "content-type": "application/json",
            "user-agent": "Ipregistry/Python" + str(sys.version_info[0]) + "/" + __version__
        }
