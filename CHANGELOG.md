# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.4.1]

### Changed

- Fixed loki installation error in Makefile

## [0.4.0]

### Added

- Unit testing added with 100% coverage and check to IM
- Docstrings were added to the code in all methods/modules/packages to IM
- Introduced type hints checks with mypi, but still requires code refactoring
- Added automatic formatting using black and sorting python imports using isort
  to IM
- Added setup.py and moved code to im subfolder

### Changed

- CHANGELOG format changed to use keepachangelog.com format
- Internet Monitor (IM) code refactored, but maintained the same functionality

## [0.3.0]

### Added

- Added upload speed calculation
- Added labels to the Dockerfile
- Added make support to facilitate build/run
- Added support for Pipenv and python 3
- Added more widgets into the dashboard

### Changed

- Jobs now starts almost immediately after the program starts
- Alerthook disabled until we can finish its integration with alertmanager
- Fixed metrics names and values

## [0.2.0]

### Added

- Added alertmanager, node-exporter and a webhook to receive alerts
- Added a CHANGELOG.md file

### Changed

- Upgrade of grafana to 7.2 version

## [0.1.0]

### Added

- Initial code base for internet monitor
- Grafana, prometheus, loki for logs and cAdvisor are integrated
