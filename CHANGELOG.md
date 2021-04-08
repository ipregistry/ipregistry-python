# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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

[Unreleased]: https://github.com/ipregistry/ipregistry-javascript/compare/3.0.0...HEAD
[3.0.0]: https://github.com/ipregistry/ipregistry-javascript/releases/tag/2.0.1...3.0.0
[2.0.1]: https://github.com/ipregistry/ipregistry-javascript/releases/tag/2.0.0...2.0.1
[2.0.0]: https://github.com/ipregistry/ipregistry-javascript/releases/tag/1.1.0...2.0.0
[1.1.0]: https://github.com/ipregistry/ipregistry-javascript/releases/tag/1.0.0...1.1.0
[1.0.0]: https://github.com/ipregistry/ipregistry-javascript/releases/tag/1.0.0
