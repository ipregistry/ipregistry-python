# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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

[Unreleased]: https://github.com/ipregistry/ipregistry-javascript/compare/4.0.0...HEAD
[4.0.0]: https://github.com/ipregistry/ipregistry-javascript/releases/tag/3.2.0...4.0.0s
[3.2.0]: https://github.com/ipregistry/ipregistry-javascript/releases/tag/3.1.0...3.2.0
[3.1.0]: https://github.com/ipregistry/ipregistry-javascript/releases/tag/3.0.0...3.1.0
[3.0.0]: https://github.com/ipregistry/ipregistry-javascript/releases/tag/2.0.1...3.0.0
[2.0.1]: https://github.com/ipregistry/ipregistry-javascript/releases/tag/2.0.0...2.0.1
[2.0.0]: https://github.com/ipregistry/ipregistry-javascript/releases/tag/1.1.0...2.0.0
[1.1.0]: https://github.com/ipregistry/ipregistry-javascript/releases/tag/1.0.0...1.1.0
[1.0.0]: https://github.com/ipregistry/ipregistry-javascript/releases/tag/1.0.0
