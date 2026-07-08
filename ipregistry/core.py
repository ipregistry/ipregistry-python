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
from concurrent.futures import ThreadPoolExecutor

from .cache import IpregistryCache, NoCache
from .json import AutonomousSystem, IpInfo
from .model import LookupError, ApiResponse, ApiResponseCredits, ApiResponseThrottling
from .request import DefaultRequestHandler, IpregistryRequestHandler

MAX_BATCH_SIZE = 1024


class IpregistryClient:
    def __init__(self, key_or_config, **kwargs):
        self._config = key_or_config if isinstance(key_or_config, IpregistryConfig) else IpregistryConfig(key_or_config)
        self._cache = kwargs["cache"] if "cache" in kwargs else NoCache()
        self._requestHandler = kwargs["requestHandler"] if "requestHandler" in kwargs \
            else DefaultRequestHandler(self._config, session=kwargs.get("session"))
        self._max_batch_size = min(int(kwargs.get("max_batch_size", MAX_BATCH_SIZE)), MAX_BATCH_SIZE)
        self._batch_concurrency = max(int(kwargs.get("batch_concurrency", 4)), 1)

        if self._max_batch_size < 1:
            raise ValueError("max_batch_size must be at least 1")
        if not isinstance(self._cache, IpregistryCache):
            raise ValueError("Given cache instance is not of type IpregistryCache")
        if not isinstance(self._requestHandler, IpregistryRequestHandler):
            raise ValueError("Given request handler instance is not of type IpregistryRequestHandler")

    def close(self):
        self._requestHandler.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def batch_lookup_asns(self, ips, **options):
        return self.batch_request(ips, self._requestHandler.batch_lookup_asns, **options)

    def batch_lookup_ips(self, ips, **options):
        return self.batch_request(ips, self._requestHandler.batch_lookup_ips, **options)

    def batch_parse_user_agents(self, user_agents, **options):
        return self.batch_request(user_agents, self._requestHandler.batch_parse_user_agents, **options)

    def batch_request(self, items, request_handler_func, **options):
        sparse_cache = [None] * len(items)
        cache_misses = []

        for i in range(len(items)):
            item = items[i]
            cache_key = self.__build_cache_key(item, options)
            cache_value = self._cache.get(cache_key)
            if cache_value is None:
                cache_misses.append(item)
            else:
                sparse_cache[i] = cache_value

        result = [None] * len(items)
        if len(cache_misses) > 0:
            response = self.__batch_request_chunked(cache_misses, request_handler_func, options)
        else:
            response = ApiResponse(
                ApiResponseCredits(),
                [],
                ApiResponseThrottling()
            )

        fresh_item_info = response.data
        j = 0
        k = 0

        for cached_item_info in sparse_cache:
            if cached_item_info is None:
                if not isinstance(fresh_item_info[k], LookupError):
                    self._cache.put(self.__build_cache_key(items[j], options), fresh_item_info[k])
                result[j] = fresh_item_info[k]
                k += 1
            else:
                result[j] = cached_item_info
            j += 1

        response.data = result

        return response

    def __batch_request_chunked(self, items, request_handler_func, options):
        """Split a batch into chunks of at most max_batch_size items and issue
        them concurrently, preserving input order in the merged response."""
        if len(items) <= self._max_batch_size:
            return request_handler_func(items, options)

        chunks = [items[i:i + self._max_batch_size] for i in range(0, len(items), self._max_batch_size)]

        if self._batch_concurrency > 1:
            with ThreadPoolExecutor(max_workers=self._batch_concurrency) as executor:
                responses = list(executor.map(lambda chunk: request_handler_func(chunk, options), chunks))
        else:
            responses = [request_handler_func(chunk, options) for chunk in chunks]

        data = []
        credits_consumed = 0
        credits_remaining = None
        throttling = None
        for response in responses:
            data.extend(response.data)
            if response.credits.consumed is not None:
                credits_consumed += response.credits.consumed
            if response.credits.remaining is not None:
                credits_remaining = response.credits.remaining \
                    if credits_remaining is None else min(credits_remaining, response.credits.remaining)
            if response.throttling is not None:
                throttling = response.throttling

        return ApiResponse(
            ApiResponseCredits(credits_consumed, credits_remaining),
            data,
            throttling if throttling is not None else ApiResponseThrottling()
        )

    def lookup_asn(self, asn, **options):
        return self.__lookup_asn(asn, options)

    def lookup_ip(self, ip, **options):
        if isinstance(ip, str):
            return self.__lookup_ip(ip, options)
        else:
            raise ValueError("Invalid value for 'ip' parameter: {!r}".format(ip))

    def origin_lookup_asn(self, **options):
        return self._requestHandler.lookup_asn('AS', options)

    def origin_lookup_ip(self, **options):
        return self._requestHandler.origin_lookup_ip(options)

    def origin_parse_user_agent(self, **options):
        return self._requestHandler.origin_parse_user_agent(options)

    def __lookup_asn(self, asn, options):
        return self.__lookup(
            'AS' + str(asn) if IpregistryClient.__is_number(asn) else 'AS',
            options, self._requestHandler.lookup_asn,
            AutonomousSystem)

    def __lookup_ip(self, ip, options):
        return self.__lookup(ip, options, self._requestHandler.lookup_ip, IpInfo)

    def __lookup(self, key, options, lookup_func, response_type):
        cache_key = self.__build_cache_key(key, options)
        cache_value = self._cache.get(cache_key)

        if cache_value is None:
            response = lookup_func(key, options)
            if isinstance(response.data, response_type):
                self._cache.put(cache_key, response.data)
            return response

        return ApiResponse(
            ApiResponseCredits(),
            cache_value,
            ApiResponseThrottling()
        )

    def parse_user_agent(self, user_agent, **options):
        response = self.batch_parse_user_agents([user_agent], **options)
        response.data = response.data[0]
        return response

    @staticmethod
    def __build_cache_key(key, options):
        result = key

        for key, value in sorted(options.items()):
            if isinstance(value, bool):
                value = 'true' if value is True else 'false'
            result += ';' + key + '=' + str(value)

        return result

    @staticmethod
    def __is_api_error(data):
        return 'code' in data

    @staticmethod
    def __is_number(value):
        try:
            int(str(value))
            return True
        except ValueError:
            return False


class IpregistryConfig:
    def __init__(self, key, base_url="https://api.ipregistry.co", timeout=15,
                 retry_max_attempts=3, retry_interval=1,
                 retry_on_server_error=True, retry_on_too_many_requests=False,
                 user_agent=None):
        """
        Initialize the IpregistryConfig instance.

        Parameters:
        key (str): The API key for accessing the Ipregistry service.
        base_url (str): The base URL for the Ipregistry API. Defaults to "https://api.ipregistry.co".
                        There also exists a European Union (EU) base URL "https://eu.api.ipregistry.co"
                        that can be used to ensure requests are handled by nodes hosted in the EU only.
        timeout (int | float | tuple): The timeout duration (in seconds) for API requests.
                        Defaults to 15 seconds. A (connect, read) tuple is also accepted.
        retry_max_attempts (int): The maximum number of attempts per request, including the
                        initial one. Defaults to 3.
        retry_interval (int | float): The base delay (in seconds) between retries; the actual
                        delay grows exponentially with each attempt. Defaults to 1 second.
        retry_on_server_error (bool): Whether to retry requests failing with a 5xx status.
                        Defaults to True. Transient network errors are always retried.
        retry_on_too_many_requests (bool): Whether to retry requests failing with a 429 status,
                        honoring the Retry-After response header. Defaults to False.
        user_agent (str): A custom value for the User-Agent header sent with each request.
                        Defaults to a library-specific value.
        """
        self.api_key = key
        self.base_url = base_url
        self.timeout = timeout
        self.retry_max_attempts = retry_max_attempts
        self.retry_interval = retry_interval
        self.retry_on_server_error = retry_on_server_error
        self.retry_on_too_many_requests = retry_on_too_many_requests
        self.user_agent = user_agent

    def with_eu_base_url(self):
        self.base_url = 'https://eu.api.ipregistry.co'
        return self

    def __str__(self):
        """
        Return a string representation of the IpregistryConfig instance.

        Returns:
        str: A string containing the API key, base URL, timeout and retry settings.
        """
        return ("api_key={}, base_url={}, timeout={}, retry_max_attempts={}, retry_interval={}, "
                "retry_on_server_error={}, retry_on_too_many_requests={}").format(
            self.api_key, self.base_url, self.timeout, self.retry_max_attempts,
            self.retry_interval, self.retry_on_server_error, self.retry_on_too_many_requests)
