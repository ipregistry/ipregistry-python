# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Changed
- Decrease the default cache period to 10min from 24h. 
This is to better handle use cases that require fresh [security data](https://ipregistry.co/docs/proxy-tor-threat-detection#content). 
Indeed, such data is updated multiple times each hour. 
You can still configure the cache period to a higher value:
https://github.com/ipregistry/ipregistry-python#caching

## [1.0.0] - 2019-07-28

- First public release.

[Unreleased]: https://github.com/ipregistry/ipregistry-javascript/compare/1.0.0...HEAD
[1.0.0]: https://github.com/ipregistry/ipregistry-javascript/releases/tag/1.0.0
