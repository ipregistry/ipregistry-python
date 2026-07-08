[<img src="https://cdn.ipregistry.co/icons/favicon-96x96.png" alt="Ipregistry" width="64"/>](https://ipregistry.co/) 
# Ipregistry Python Client Library

[![License](http://img.shields.io/:license-apache-blue.svg)](LICENSE)
[![Actions Status](https://github.com/ipregistry/ipregistry-python/workflows/Tests/badge.svg)](https://github.com/ipregistry/ipregistry-python/actions)
[![PyPI](https://img.shields.io/pypi/v/ipregistry)](https://pypi.org/project/ipregistry/)

This is the official Python client library for the [Ipregistry](https://ipregistry.co) IP geolocation and threat data API, 
allowing you to lookup your own IP address or specified ones. Responses return multiple data points including carrier, 
company, currency, location, timezone, threat information, and more.

Starting version 3 of the library, support for Python 2 has been dropped. Version 5 and above require Python 3.10+.

## Getting Started

You'll need an Ipregistry API key, which you can get along with 100,000 free lookups by signing up for a free account at [https://ipregistry.co](https://ipregistry.co).

### Installation

```
pip install ipregistry
```

### Quick Start

#### Single IP Lookup

```python
from ipregistry import IpregistryClient

client = IpregistryClient("YOUR_API_KEY")
response = client.lookup_ip("54.85.132.205")

# Printing whole response
print(response)

# Retrieving a specific field
country_code = response.data.location.country.code

# Getting number of credits consumed or remaining
credits_consumed = response.credits.consumed
credits_remaining = response.credits.remaining
```

#### Single ASN Lookup

```python
from ipregistry import IpregistryClient

client = IpregistryClient("YOUR_API_KEY")
response = client.lookup_asn(42)
print(response.credits.consumed)
print(response.data.prefixes)
print(response.data.relationships)
```

#### Batch IP Lookup

```python
from ipregistry import IpregistryClient

client = IpregistryClient("YOUR_API_KEY")
response = client.batch_lookup_ips(["54.85.132.205", "8.8.8.8", "2001:67c:2e8:22::c100:68b"])
for ip_info in response.data:
    print(ip_info)
```

#### Origin IP Lookup

```python
from ipregistry import IpregistryClient

client = IpregistryClient("YOUR_API_KEY")
response = client.origin_lookup_ip()
print(response.data)
```

#### User-Agent Parsing

```python
from ipregistry import IpregistryClient

client = IpregistryClient("YOUR_API_KEY")
response = client.parse_user_agent('Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36')
print(response.data)
```

#### Asynchronous Client

An asyncio-based client with the same feature set is available when the library is installed
with the `async` extra (`pip install ipregistry[async]`):

```python
from ipregistry import AsyncIpregistryClient

async def main():
    async with AsyncIpregistryClient("YOUR_API_KEY") as client:
        response = await client.lookup_ip("54.85.132.205")
        print(response.data.location.country.code)
```

More advanced examples are available in the [samples](https://github.com/ipregistry/ipregistry-python/tree/master/samples) 
folder.

### Configuration

Timeouts, retries and the User-Agent header are configurable through `IpregistryConfig`:

```python
from ipregistry import IpregistryClient, IpregistryConfig

config = IpregistryConfig(
    "YOUR_API_KEY",
    timeout=15,                        # seconds; a (connect, read) tuple is also accepted
    retry_max_attempts=3,              # attempts per request, including the initial one
    retry_interval=1,                  # base delay in seconds, doubled on each retry
    retry_on_server_error=True,        # retry 5xx responses
    retry_on_too_many_requests=False,  # retry 429 responses, honoring Retry-After
    user_agent=None                    # custom User-Agent header value
)
client = IpregistryClient(config)
```

Transient network errors are always retried up to `retry_max_attempts`.

The client reuses pooled HTTP connections through a `requests.Session`. You may pass your own
session with `IpregistryClient("YOUR_API_KEY", session=my_session)` for proxy or TLS control,
and release resources with `client.close()` or by using the client as a context manager.

Batch lookups larger than the API limit of 1024 items are automatically split into concurrent
chunks. Tune this with `IpregistryClient("YOUR_API_KEY", max_batch_size=1024, batch_concurrency=4)`.

### Caching

This Ipregistry client library has built-in support for in-memory caching. By default caching is disabled. 
Below are examples to enable and configure a caching strategy. Once enabled, default cache strategy is to memoize up to 
2048 lookups for at most 10min. You can change preferences as follows:

#### Enabling caching

Enable caching by passing an instance of `InMemoryCache`:

```python
from ipregistry import InMemoryCache, IpregistryClient

client = IpregistryClient("YOUR_API_KEY", cache=InMemoryCache(maxsize=2048, ttl=600))
```

#### Disabling caching

Disable caching by passing an instance of `NoCache`:

```python
from ipregistry import IpregistryClient, NoCache

client = IpregistryClient("YOUR_API_KEY", cache=NoCache())
```

### European Union Base URL

Using the EU base URL, your requests are handled by the closest cluster of nodes in the European Union:

```python
from ipregistry import IpregistryClient, NoCache

client = IpregistryClient(IpregistryConfig("YOUR_API_KEY").with_eu_base_url())
```

### Errors

All Ipregistry exceptions inherit `IpregistryError` class.

Main subtypes are `ApiError` and `ClientError`.

Errors of type _ApiError_ include a `code` field that maps to the one described in the [Ipregistry documentation](https://ipregistry.co/docs/errors), along with a typed `error_code` enum value (`ErrorCode`) that is `None` for unrecognized codes.

### Filtering bots

You might want to prevent Ipregistry API requests for crawlers or bots browsing your pages.

A manner to proceed is to identify bots using the `User-Agent` header. 
To ease this process, the library includes a utility method:

```python
from ipregistry import UserAgents

is_bot = UserAgents.is_bot('YOUR_USER_AGENT_HEADER_VALUE_HERE')
```

## Other Libraries

There are official Ipregistry client libraries available for many languages including 
[Java](https://github.com/ipregistry/ipregistry-java), 
[Javascript](https://github.com/ipregistry/ipregistry-javascript), and more.

Are you looking for an official client with a programming language or framework we do not support yet? 
[let us know](mailto:support@ipregistry.co).
