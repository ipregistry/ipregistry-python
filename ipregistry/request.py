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

from abc import ABC, abstractmethod
import json
import requests
import sys
import urllib.parse

from .__init__ import __version__
from .model import ApiError, ClientError, IpInfo


class IpregistryRequestHandler(ABC):
    def __init__(self, config):
        self._config = config

    @abstractmethod
    def batch_lookup_ips(self, ips, options):
        pass

    @abstractmethod
    def lookup_ip(self, ip, options):
        pass

    @abstractmethod
    def origin_lookup_ip(self, options):
        pass

    def _build_base_url(self, ip, options):
        result = self._config.base_url + "/" + ip + "?key=" + self._config.api_key

        for key, value in options.items():
            if isinstance(value, bool):
                value = 'true' if value is True else 'false'
            result += "&" + key + "=" + urllib.parse.quote(value)

        return result


class DefaultRequestHandler(IpregistryRequestHandler):
    def batch_lookup_ips(self, ips, options):
        try:
            r = requests.post(self._build_base_url('', options), data=json.dumps(ips), headers=self.__headers(), timeout=self._config.timeout)
            r.raise_for_status()
            return list(map(lambda data: LookupError(data) if 'code' in data else IpInfo(**data), r.json()['results']))
        except requests.HTTPError:
            raise ApiError(r.json())
        except Exception as e:
            raise ClientError(e)

    def lookup_ip(self, ip, options):
        try:
            r = requests.get(self._build_base_url(ip, options), headers=self.__headers(), timeout=self._config.timeout)
            r.raise_for_status()
            return IpInfo(**r.json())
        except requests.HTTPError:
            raise ApiError(r.json())
        except Exception as e:
            raise ClientError(e)

    def origin_lookup_ip(self, options):
        return self.lookup_ip('', options)

    @staticmethod
    def __headers():
        return {
            "content-type": "application/json",
            "user-agent": "Ipregistry/Python" + str(sys.version_info[0]) + "/" + __version__
        }
