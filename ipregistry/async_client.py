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
import asyncio
import json

from .cache import IpregistryCache, NoCache
from .core import (MAX_BATCH_SIZE, IpregistryConfig, _build_cache_key, _is_number,
                   _merge_batch_responses)
from .json import AutonomousSystem, IpInfo
from .model import (ApiResponse, ApiResponseCredits, ApiResponseThrottling,
                    ClientError, LookupError, RequesterAutonomousSystem,
                    RequesterIpInfo, RequesterUserAgent, UserAgent)
from .request import (DefaultRequestHandler, IpregistryRequestHandler, _backoff_interval,
                      _build_headers, _is_retryable_status, _raise_api_error, _retry_delay)

try:
    import httpx
except ImportError:
    httpx = None


class AsyncDefaultRequestHandler(IpregistryRequestHandler):
    """Asynchronous request handler backed by httpx.

    Requires the httpx package, available through the 'async' extra:
    pip install ipregistry[async]
    """

    def __init__(self, config, client=None):
        if httpx is None:
            raise ImportError(
                "The asynchronous client requires the httpx package. "
                "Install it with: pip install ipregistry[async]"
            )
        super().__init__(config)
        self._owns_client = client is None
        self._client = httpx.AsyncClient(timeout=self.__build_timeout(config.timeout)) \
            if client is None else client

    async def aclose(self):
        if self._owns_client:
            await self._client.aclose()

    async def batch_lookup_asns(self, asns, options):
        response = await self._request_with_retry(
            'POST',
            self._build_base_url('', options),
            data=json.dumps(["AS" + str(asn) for asn in asns])
        )
        try:
            results = response.json().get('results', [])
            parsed_results = [
                LookupError(data) if 'code' in data else AutonomousSystem(**data)
                for data in results
            ]
            return DefaultRequestHandler.build_api_response(response, parsed_results)
        except Exception as e:
            raise ClientError(e)

    async def batch_lookup_ips(self, ips, options):
        response = await self._request_with_retry(
            'POST',
            self._build_base_url('', options),
            data=json.dumps(ips)
        )
        try:
            results = response.json().get('results', [])
            parsed_results = [
                LookupError(data) if 'code' in data else IpInfo(**data)
                for data in results
            ]
            return DefaultRequestHandler.build_api_response(response, parsed_results)
        except Exception as e:
            raise ClientError(e)

    async def batch_parse_user_agents(self, user_agents, options):
        response = await self._request_with_retry(
            'POST',
            self._build_base_url('user_agent', options),
            data=json.dumps(user_agents)
        )
        try:
            results = response.json().get('results', [])
            parsed_results = [
                LookupError(data) if 'code' in data else UserAgent(**data)
                for data in results
            ]
            return DefaultRequestHandler.build_api_response(response, parsed_results)
        except Exception as e:
            raise ClientError(e)

    async def lookup_asn(self, asn, options):
        response = await self._request_with_retry('GET', self._build_base_url(asn, options))
        try:
            json_response = response.json()
            return DefaultRequestHandler.build_api_response(
                response,
                RequesterAutonomousSystem(**json_response) if asn == 'AS'
                else AutonomousSystem(**json_response)
            )
        except Exception as e:
            raise ClientError(e)

    async def lookup_ip(self, ip, options):
        response = await self._request_with_retry('GET', self._build_base_url(ip, options))
        try:
            json_response = response.json()
            return DefaultRequestHandler.build_api_response(
                response,
                RequesterIpInfo(**json_response) if ip == ''
                else IpInfo(**json_response)
            )
        except Exception as e:
            raise ClientError(e)

    async def origin_lookup_ip(self, options):
        return await self.lookup_ip('', options)

    async def origin_parse_user_agent(self, options):
        response = await self._request_with_retry('GET', self._build_base_url('user_agent', options))
        try:
            json_response = response.json()
            return DefaultRequestHandler.build_api_response(
                response,
                RequesterUserAgent(**json_response)
            )
        except Exception as e:
            raise ClientError(e)

    async def _request_with_retry(self, method, url, data=None):
        """Perform an HTTP request, retrying transient network errors and,
        depending on the configuration, 5xx and 429 responses with exponential
        backoff (honoring the Retry-After header for 429 responses)."""
        max_attempts = max(1, self._config.retry_max_attempts)
        attempt = 0

        while True:
            attempt += 1
            try:
                response = await self._client.request(
                    method,
                    url,
                    content=data,
                    headers=_build_headers(self._config)
                )
            except httpx.HTTPError as e:
                if attempt < max_attempts:
                    await asyncio.sleep(_backoff_interval(self._config, attempt))
                    continue
                raise ClientError(e)

            if response.status_code >= 400:
                if attempt < max_attempts and _is_retryable_status(self._config, response.status_code):
                    await asyncio.sleep(_retry_delay(self._config, response, attempt))
                    continue
                _raise_api_error(response)

            return response

    @staticmethod
    def __build_timeout(timeout):
        if isinstance(timeout, tuple):
            connect, read = timeout
            return httpx.Timeout(read, connect=connect)
        return timeout


class AsyncIpregistryClient:
    """Asynchronous counterpart of IpregistryClient with the same feature set:
    caching, batch chunking, retries and origin lookups."""

    def __init__(self, key_or_config, **kwargs):
        self._config = key_or_config if isinstance(key_or_config, IpregistryConfig) else IpregistryConfig(key_or_config)
        self._cache = kwargs["cache"] if "cache" in kwargs else NoCache()
        self._requestHandler = kwargs["requestHandler"] if "requestHandler" in kwargs \
            else AsyncDefaultRequestHandler(self._config, client=kwargs.get("client"))
        self._max_batch_size = min(int(kwargs.get("max_batch_size", MAX_BATCH_SIZE)), MAX_BATCH_SIZE)
        self._batch_concurrency = max(int(kwargs.get("batch_concurrency", 4)), 1)

        if self._max_batch_size < 1:
            raise ValueError("max_batch_size must be at least 1")
        if not isinstance(self._cache, IpregistryCache):
            raise ValueError("Given cache instance is not of type IpregistryCache")
        if not isinstance(self._requestHandler, IpregistryRequestHandler):
            raise ValueError("Given request handler instance is not of type IpregistryRequestHandler")

    async def aclose(self):
        await self._requestHandler.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.aclose()

    async def batch_lookup_asns(self, ips, **options):
        return await self.batch_request(ips, self._requestHandler.batch_lookup_asns, **options)

    async def batch_lookup_ips(self, ips, **options):
        return await self.batch_request(ips, self._requestHandler.batch_lookup_ips, **options)

    async def batch_parse_user_agents(self, user_agents, **options):
        return await self.batch_request(user_agents, self._requestHandler.batch_parse_user_agents, **options)

    async def batch_request(self, items, request_handler_func, **options):
        sparse_cache = [None] * len(items)
        cache_misses = []

        for i in range(len(items)):
            item = items[i]
            cache_key = _build_cache_key(item, options)
            cache_value = self._cache.get(cache_key)
            if cache_value is None:
                cache_misses.append(item)
            else:
                sparse_cache[i] = cache_value

        result = [None] * len(items)
        if len(cache_misses) > 0:
            response = await self.__batch_request_chunked(cache_misses, request_handler_func, options)
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
                    self._cache.put(_build_cache_key(items[j], options), fresh_item_info[k])
                result[j] = fresh_item_info[k]
                k += 1
            else:
                result[j] = cached_item_info
            j += 1

        response.data = result

        return response

    async def __batch_request_chunked(self, items, request_handler_func, options):
        """Split a batch into chunks of at most max_batch_size items and issue
        them concurrently, preserving input order in the merged response."""
        if len(items) <= self._max_batch_size:
            return await request_handler_func(items, options)

        chunks = [items[i:i + self._max_batch_size] for i in range(0, len(items), self._max_batch_size)]
        semaphore = asyncio.Semaphore(self._batch_concurrency)

        async def run_chunk(chunk):
            async with semaphore:
                return await request_handler_func(chunk, options)

        responses = await asyncio.gather(*[run_chunk(chunk) for chunk in chunks])

        return _merge_batch_responses(responses)

    async def lookup_asn(self, asn, **options):
        return await self.__lookup_asn(asn, options)

    async def lookup_ip(self, ip, **options):
        if isinstance(ip, str):
            return await self.__lookup_ip(ip, options)
        else:
            raise ValueError("Invalid value for 'ip' parameter: {!r}".format(ip))

    async def origin_lookup_asn(self, **options):
        return await self._requestHandler.lookup_asn('AS', options)

    async def origin_lookup_ip(self, **options):
        return await self._requestHandler.origin_lookup_ip(options)

    async def origin_parse_user_agent(self, **options):
        return await self._requestHandler.origin_parse_user_agent(options)

    async def parse_user_agent(self, user_agent, **options):
        response = await self.batch_parse_user_agents([user_agent], **options)
        response.data = response.data[0]
        return response

    async def __lookup_asn(self, asn, options):
        return await self.__lookup(
            'AS' + str(asn) if _is_number(asn) else 'AS',
            options, self._requestHandler.lookup_asn,
            AutonomousSystem)

    async def __lookup_ip(self, ip, options):
        return await self.__lookup(ip, options, self._requestHandler.lookup_ip, IpInfo)

    async def __lookup(self, key, options, lookup_func, response_type):
        cache_key = _build_cache_key(key, options)
        cache_value = self._cache.get(cache_key)

        if cache_value is None:
            response = await lookup_func(key, options)
            if isinstance(response.data, response_type):
                self._cache.put(cache_key, response.data)
            return response

        return ApiResponse(
            ApiResponseCredits(),
            cache_value,
            ApiResponseThrottling()
        )
