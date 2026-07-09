# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [5.0.1] - 2026-07-09
### Fixed
- Fix batch lookups with a `fields` selection: the API applies the filter to the whole batch
  response body, so each field is now prefixed with `results.` on batch endpoints. Previously
  the filter stripped the `results` array itself and the lookup crashed with an `IndexError`.
- Raise a descriptive `ClientError` when a batch response contains fewer results than requested
  items, instead of crashing with an `IndexError`.

## [5.0.0] - 2026-07-07
### Added
- Add an asyncio-based `AsyncIpregistryClient` with the same feature set, available with the `async`
  extra: `pip install ipregistry[async]`.
- Add configurable retries through `IpregistryConfig`: `retry_max_attempts`, `retry_interval`,
  `retry_on_server_error` and `retry_on_too_many_requests` (honoring the `Retry-After` header).
  Transient network errors are now retried too.
- Add a typed `ErrorCode` enum exposed as `ApiError.error_code`.
- Add `IpregistryLookupError` as the primary name for per-entry batch lookup errors; the previous
  `LookupError` name, which shadows the Python builtin, remains available as an alias.
- Ship a `py.typed` marker so type checkers use the library's annotations.
- Add automatic splitting of batch lookups larger than the API limit of 1024 items into concurrent
  chunks, tunable with the `max_batch_size` and `batch_concurrency` client options.
- Add `close()` and context manager support to `IpregistryClient`, plus an optional `session`
  option to provide a custom `requests.Session`.
- Add a `user_agent` configuration option to customize the User-Agent header.
- Add a release workflow publishing to PyPI through trusted publishing, a ruff lint workflow, and
  a weekly scheduled workflow running tests against the live API.
### Changed
- Require Python 3.10+.
- Migrate the project metadata to the standard PEP 621 format and switch project management
  from Poetry to [uv](https://docs.astral.sh/uv/).
- Update all dependencies to their latest versions and remove the dependency on tenacity.
- Reuse pooled HTTP connections through a `requests.Session` instead of opening a new connection
  per request.
- Align the default request timeout with other Ipregistry client libraries: 15 seconds instead of 5.
- Origin lookups are no longer cached: cached requester data would be stale or wrong when the
  network context changes.
- Cache keys are now deterministic regardless of the order lookup options are given in.
- Remove the redundant retry on `origin_lookup_ip` that could triple retry attempts.
- Detect the Yahoo Slurp crawler in `UserAgents.is_bot`.
### Fixed
- Fix nested model fields (`Connection`, `CurrencyFormat`, `UserAgent` device/engine/os, `RequesterIpInfo` user_agent)
  raising a validation error when excluded from a response using the `fields` parameter.
- Fix `str(ApiError)` returning a tuple representation instead of the error message.
- Raise `ClientError` instead of leaking a `JSONDecodeError` when an error response has a non-JSON body.
- Raise `ValueError` instead of `TypeError` when `lookup_ip` is called with a non-string input.
- Support boolean and numeric option values when building request URLs and cache keys.
- Reject float inputs when detecting ASN values in `lookup_asn`.

## [4.0.0] - 2024-06-14
### Changed
- Require Python 3.8+.
- Add new functions for retrieving Autonomous System data: `batch_lookup_asns`, `lookup_asn`, `origin_lookup_asn`.
- Add new functions for user-agent header value parsing: `batch_parse_user_agents`, `parse_user_agent`. 
- API key is passed as header value and no longer as query parameter.
- Client library method are now wrapped in a new _ApiResponse_ object that includes a mean to retrieve metadata 
  about _credits_ and _throttling_ in addition to _data_.
- Introduce data model for responses to enable field value access using dot notation and ensure code autocompletion functionality.
- Rename all function and variable names to adhere to snake_case convention.
- Replace the function named `lookup` by 3 new functions: `batch_lookup_ips`, `lookup_ip` and `origin_lookup_ip`.
- Rename _IpregistryConfig_ option `apiUrl` to `baseUrl`.
- Rename _UserAgent_ utility class to _UserAgents.

## [3.2.0] - 2021-11-09
### Changed
- Dependencies are now managed with [Poetry](https://python-poetry.org).
### Fixed
- Fix setup.py import assumes deps already installed ([#37](https://github.com/ipregistry/ipregistry-python/issues/37)).

## [3.1.0] - 2021-10-26
### Changed
- Dependencies update

## [3.0.0] - 2021-04-09
### Changed
- Drop Python 2 support.
- Rename _DefaultCache_ to _InMemoryCache_.

## [2.0.1] - 2020-09-25
### Fixed
- Fix packaging with version 2.0.0 deployed on pypi.

## [2.0.0] - 2020-07-05
### Changed
- Disable caching by default since people are often confused by this default setting. You can enable caching by following what is explained in the README.
- Increase maximum timeout to 15s from 3s.

## [1.1.0] - 2019-10-27
### Changed
- Decrease the default cache period to 10min from 24h. 
This is to better handle use cases that require fresh [security data](https://ipregistry.co/docs/proxy-tor-threat-detection#content). 
Indeed, such data is updated multiple times each hour. 
You can still configure the cache period to a higher value:
https://github.com/ipregistry/ipregistry-python#caching

## [1.0.0] - 2019-07-28
- First public release.

[Unreleased]: https://github.com/ipregistry/ipregistry-python/compare/5.0.1...HEAD
[5.0.1]: https://github.com/ipregistry/ipregistry-python/compare/5.0.0...5.0.1
[5.0.0]: https://github.com/ipregistry/ipregistry-python/compare/4.0.0...5.0.0
[4.0.0]: https://github.com/ipregistry/ipregistry-python/compare/3.2.0...4.0.0
[3.2.0]: https://github.com/ipregistry/ipregistry-python/compare/3.1.0...3.2.0
[3.1.0]: https://github.com/ipregistry/ipregistry-python/compare/3.0.0...3.1.0
[3.0.0]: https://github.com/ipregistry/ipregistry-python/compare/2.0.1...3.0.0
[2.0.1]: https://github.com/ipregistry/ipregistry-python/compare/2.0.0...2.0.1
[2.0.0]: https://github.com/ipregistry/ipregistry-python/compare/1.1.0...2.0.0
[1.1.0]: https://github.com/ipregistry/ipregistry-python/compare/1.0.0...1.1.0
[1.0.0]: https://github.com/ipregistry/ipregistry-python/releases/tag/1.0.0
