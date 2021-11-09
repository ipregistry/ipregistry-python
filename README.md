[<img src="https://cdn.ipregistry.co/icons/icon-72x72.png" alt="Ipregistry" width="64"/>](https://ipregistry.co/) 
# Ipregistry Python Client Library

[![License](http://img.shields.io/:license-apache-blue.svg)](LICENSE)
[![Actions Status](https://github.com/ipregistry/ipregistry-python/workflows/Tests/badge.svg)](https://github.com/ipregistry/ipregistry-python/actions)
[![PyPI](https://img.shields.io/pypi/v/ipregistry)](https://pypi.org/project/ipregistry/)

This is the official Python client library for the [Ipregistry](https://ipregistry.co) IP geolocation and threat data API, 
allowing you to lookup your own IP address or specified ones. Responses return multiple data points including carrier, 
company, currency, location, timezone, threat information, and more.

Starting version 3 of the library, support for Python 2 has been dropped and the library requires Python 3.6+.

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
ipInfo = client.lookup("54.85.132.205")
print(ipInfo)
```

#### Batch IP Lookup

```python
from ipregistry import IpregistryClient

client = IpregistryClient("YOUR_API_KEY")
results = client.lookup(["54.85.132.205", "8.8.8.8", "2001:67c:2e8:22::c100:68b"])
for ipInfo in results:
    print(ipInfo)
```

#### Origin IP Lookup

```python
from ipregistry import IpregistryClient

client = IpregistryClient("YOUR_API_KEY")
ipInfo = client.lookup()
print(ipInfo)
```

More advanced examples are available in the [samples](https://github.com/ipregistry/ipregistry-python/tree/master/samples) 
folder.

### Caching

This Ipregistry client library has built-in support for in-memory caching. By default caching is disabled. 
Below are examples to enable and configure a caching strategy. Once enabled, default cache strategy is to memoize up to 
2048 lookups for at most 10min. You can change preferences as follows:

#### Enabling caching

Enable caching by passing an instance of `DefaultCache`:

```python
from ipregistry import DefaultCache, IpregistryClient

client = IpregistryClient("YOUR_API_KEY", cache=DefaultCache(maxsize=2048, ttl=600))
```

#### Disabling caching

Disable caching by passing an instance of `NoCache`:

```python
from ipregistry import IpregistryClient, NoCache

client = IpregistryClient("YOUR_API_KEY", cache=NoCache())
```

### Errors

All Ipregistry exceptions inherit `IpregistryError` class.

Main subtypes are `ApiError` and `ClientError`.

Errors of type _ApiError_ include a code field that maps to the one described in the [Ipregistry documentation](https://ipregistry.co/docs/errors).

### Filtering bots

You might want to prevent Ipregistry API requests for crawlers or bots browsing your pages.

A manner to proceed is to identify bots using the `User-Agent` header. 
To ease this process, the library includes a utility method:

```python
from ipregistry import UserAgent

isBot = UserAgent.isBot('YOUR_USER_AGENT_HEADER_VALUE_HERE')
```

## Other Libraries

There are official Ipregistry client libraries available for many languages including 
[Java](https://github.com/ipregistry/ipregistry-java), 
[Javascript](https://github.com/ipregistry/ipregistry-javascript), and more.

Are you looking for an official client with a programming language or framework we do not support yet? 
[let us know](mailto:support@ipregistry.co).
