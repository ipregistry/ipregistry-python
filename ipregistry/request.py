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

import abc, six
import requests
import sys
import urllib

from __init__ import __version__
from model import ApiError, ClientError, IpInfo

@six.add_metaclass(abc.ABCMeta)
class IpregistryRequestHandler:
    def __init__(self, config):
        self._config = config

    @abc.abstractmethod
    def batchLookup(self, ips, **kwargs):
        pass

    @abc.abstractmethod
    def originLookup(self, **kwargs):
        pass

    @abc.abstractmethod
    def singleLookup(self, ip, *options):
        pass

    def _buildApiUrl(self, ip, **kwargs):
        result = self._config.apiUrl + "/" + ip + "?key=" + self._config.apiKey

        for key, value in kwargs.items():
            result += "&" + key + "=" + urllib.quote(value)

        return result

class DefaultRequestHandler(IpregistryRequestHandler):
    def batchLookup(self, ips, **kwargs):
        pass

    def originLookup(self, **kwargs):
        return self.singleLookup('')

    def singleLookup(self, ip, *options):
        try:
            r = requests.get(self._buildApiUrl(ip), headers=self._headers(), timeout=self._config.timeout)
            r.raise_for_status()
            return IpInfo(r.json())
        except requests.HTTPError:
            raise ApiError(r.json())
        except Exception as e:
            raise ClientError(e)

    def _headers(self):
        return {
            "content-type": "application/json",
            "user-agent": "Ipregistry/Python" + str(sys.version_info[0]) + "/" + __version__
        }
