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

import json

class JsonPayload:
    def __init__(self, json):
        self._json = json

    def __getattr__(self, attr):
        return self._json[attr]

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return json.dumps(self._json, indent=4)

class IpInfo(JsonPayload):
    pass

class IpregistryError(Exception):
    pass

class ApiError(JsonPayload, IpregistryError):
    pass

class ClientError(IpregistryError):
   pass

class LookupError(JsonPayload, IpregistryError):
    pass
