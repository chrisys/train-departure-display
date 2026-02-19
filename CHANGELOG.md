# Changelog

## [0.7.0](https://github.com/chrisys/train-departure-display/compare/v0.6.2...v0.7.0) (2026-02-19)


### Features

* Add 'Welcome to -station name-' message when no services are running ([cdb9f1a](https://github.com/chrisys/train-departure-display/commit/cdb9f1a6d84e81e0f7627495f52b70cac3935a41))
* Add 'Welcome to -station name-' message when no services are running ([074acbd](https://github.com/chrisys/train-departure-display/commit/074acbd63a208cb76403a35920844d5127035fe6))
* Load real time data from Transport API ([193b2af](https://github.com/chrisys/train-departure-display/commit/193b2afc43ccf0baac8488feb8b3c262cc3239a6))
* Load real time data from Transport API ([117042a](https://github.com/chrisys/train-departure-display/commit/117042a34e15aa266dc8f8fcd145373d34916b93))
* Move config from env vars to a JSON config file ([0d19ab0](https://github.com/chrisys/train-departure-display/commit/0d19ab0733b8be5d16859934c3eb186e862b9b41))
* refresh data and redraw ([98a3861](https://github.com/chrisys/train-departure-display/commit/98a386164cc557caba2ecd8b7dc91e2546d3779d))
* Update README description text ([2c8b68d](https://github.com/chrisys/train-departure-display/commit/2c8b68d1f7150dc46db38de79d6f933fd583870a))
* Update README screenshot ([b38c230](https://github.com/chrisys/train-departure-display/commit/b38c230d340bfc40fce615c19f95277415a1bb53))


### Bug Fixes

* Add requirements to README, and update some copy ([e791de6](https://github.com/chrisys/train-departure-display/commit/e791de67b54a07991d965d671e99351eb8e9f660))
* Add requirements to README, and update some copy ([bb44fe2](https://github.com/chrisys/train-departure-display/commit/bb44fe20169f48ba0cd5a71dc0ed7e8c9421becd))
* Catches request errors to draw blank signage ([5a83a9c](https://github.com/chrisys/train-departure-display/commit/5a83a9cf68ee73630495520cf56d0183cef6c5af))
* Changes following on device testing ([28ee7f3](https://github.com/chrisys/train-departure-display/commit/28ee7f350b12794839ded989529dca4970833268))
* Correct asset for the OLED SPI pin configuration image ([03ed417](https://github.com/chrisys/train-departure-display/commit/03ed41797d60cdcc457b783d306b112dc95d9918))
* Issue which prevented the program from refreshing ([e398f43](https://github.com/chrisys/train-departure-display/commit/e398f43c189fcdb3d777e182d674fe687c66320c))
* Render correctly when only one service is available ([24af66a](https://github.com/chrisys/train-departure-display/commit/24af66ad83bb006d8b8c8d9b0fe9d1d59fd54b75))
* Render correctly when only one service is available ([0c73a24](https://github.com/chrisys/train-departure-display/commit/0c73a24bebda62fcd4d73441148a9b3fbb0049aa))
* Rendering issues ([370cd46](https://github.com/chrisys/train-departure-display/commit/370cd4669f5f9cd904b362af61e3be936893c355))
* Respect configured refresh time ([5d3ae12](https://github.com/chrisys/train-departure-display/commit/5d3ae12f6390c21691bb00d8c12b244dc2d4601c))
* Tweaks having tested on a real device ([6f50be7](https://github.com/chrisys/train-departure-display/commit/6f50be7f984f9a1b9e85f476bbe3c75c9b107a41))
* Update config.sample.json structure ([6f1c0fc](https://github.com/chrisys/train-departure-display/commit/6f1c0fc38e9f2ade962b6f930a9c71dfe30de5de))

From this point onwards the project was moved to use Release Please and conventional commits. The change log below is retained for historical purposes.

---

## v0.6.2
## (2025-08-08)

* Resolve dependency issue with RPi.GPIO and spidev [Chris Crocker-White]

## v0.6.1
## (2025-08-08)

* Update documentation fixes #136 [steco]
* Suppress "GPIO in use" error fixes #111 [steco]

## v0.6.0
## (2025-06-19)

* Migrate away from deprecated balenalib base images (and also reduce image size) fixes #138 [Chris Crocker-White]
* Add extra character to platform placeholder text to prevent overlapping text fixes #123 [Chris Crocker-White]
* Convert boolean values read from env vars into uppercase before comparison fixes #106 [Chris Crocker-White]
* Add version and date to startup fixes #75 [Chris Crocker-White]
* Remove reference to kits from README.md closes #94 [Chris Crocker-White]

## v0.5.5
## (2024-02-27)

* Fix regex for platform numbers above 10 [CalamityJames]

## v0.5.4
## (2023-07-26)

* Add alternate validation, allowing use of non-numeric platforms [CalamityJames]

## v0.5.3
## (2023-07-26)

* Load 10 rows by default, to get the most from the API call [CalamityJames]

## v0.5.2
## (2023-07-22)

* New feature: Debug screen support [CalamityJames]

## v0.5.1
## (2023-07-04)

* Readded `tzdata` to set timezone, fixes #36 again, sorry! [CalamityJames]

## v0.5.0
## (2023-06-29)

* Upgrade: Switch Python version and base OS: Python 3.11 on Alpine
* New feature: `showDepartureNumbers` option - Adds 1st / 2nd / 3rd prefix as per UK train departures
* New feature: `firstDepartureBold` option - toggle bold of first departure line as this is regional
* New feature: `targetFPS` option - configurable FPS regulator (zero to disable)
* Development UX: `fpsTime` option - Adjusts how frequently the Effecive FPS is displayed
* Development UX: `headless` option - Run using emulated serial port (Useful for optimisation checks)
* Development UX: Skip NRE attribution sleep in emulation mode
* Development UX: Simplify Dockerfile slightly in an attempt to be Balena-y
* Performance: Seconds now render every 0.1 second, rather than a hotspot (reduce CPU)
* Performance: All "in-loop" TTF font rendering is now cached (reduce CPU)
* Fix: screen1Platform/screen2Platform being required incorrectly on the env

## v0.4.0
## (2023-02-18)

* Fix: Catches request errors to draw blank signage [BeauAgst]
* New feature: Add individualStationDepartureTime option [BeauAgst]
* Fix: Correct some boolean config vars defaulting to true [Chris Crocker-White]

## v0.3.8
## (2023-01-26)

* Correctly handle when platform numbers set to null [Chris Crocker-White]

## v0.3.7
## (2023-01-20)

* Correct crash when destinationStation set to null [Chris Crocker-White]

## v0.3.6
## (2023-01-13)

* Remove usage of deprecated Pillow method [Chris Crocker-White]

## v0.3.5
## (2023-01-13)

* Update balena.yml template variables [Chris Crocker-White]

## v0.3.4
## (2022-05-31)

* Add assembly guide [Chris Crocker-White]

## v0.3.3
## (2022-05-30)

* Correct angle on desk mount lugs [Chris Crocker-White]

## v0.3.2
## (2022-05-16)

* Default to all-day operation fixes #72 [Chris Crocker-White]

## v0.3.1
## (2022-03-08)

* Adjust tolerances between case parts [Chris Crocker-White]

## v0.3.0
## (2021-12-09)

* Add modular case design [Chris Crocker-White]

## v0.2.0
## (2021-12-09)

* Enable dual display output [Lee Porte]

## v0.1.3
## (2021-12-09)

* Set Dockerfile to use raspberry-pi base image [Chris Crocker-White]

## v0.1.2
## (2021-12-08)

* Update timeOffset key [Lee Porte]

## v0.1.1
## (2021-10-29)

* Add screenBlankHours [Chris Crocker-White]

## v0.1.0
## (2021-10-29)

* Change to National Rail Enquiries API [Chris Crocker-White]

## v0.0.15
## (2021-08-02)

* Add `tzdata` to set timezone, fixes #36 [Chris Crocker-White]

## v0.0.14
## (2021-07-29)

* Reduce container size (~315MB to ~87MB) [Chris Crocker-White]

## v0.0.13
## (2021-07-12)

* Relocate update data log [Chris Crocker-White]

## v0.0.12
## (2021-07-12)

* Add logging, adjust framerate [Chris Crocker-White]

## v0.0.11
## (2021-07-09)

* Fix outOfHoursName config [Chris Crocker-White]

## v0.0.10
## (2021-07-08)

* Report API server errors fixes #29, fixes #32 [Chris Crocker-White]
* Reworked messy configuration setup [Chris Crocker-White]
* Added ability to filter by platform closes #7 [Chris Crocker-White]
* Reduce container size (~780MB to ~300MB) [Chris Crocker-White]

## v0.0.9
## (2021-05-20)

* Mark fleet as not joinable [Chris Crocker-White]

## v0.0.8
## (2021-04-01)

* docs: add query params to deploy link [Aaron Shaw]

## v0.0.7
## (2021-02-01)

* Update balena.yml [Chris Crocker-White]

## v0.0.6
## (2021-01-01)

* Add balena.yml and logo for hub [Chris Crocker-White]

## v0.0.5
## (2020-09-08)

* Add balena.yml with device and env var presets [Chris Crocker-White]

## v0.0.4
## (2020-09-08)

* Add DWB button for easier deployment [Chris Crocker-White]

## v0.0.3
## (2020-05-26)

* Unlock framerate [Chris Crocker-White]

## v0.0.2
## (2020-05-26)

* Add repo.yml [Chris Crocker-White]
* Improve local development [Chris Crocker-White]
* Remove piwheels - not currently building [Chris Crocker-White]
* Update readme to include destinationStation option [Chris Crocker-White]
* Added datasheet for similar display [Chris Crocker-White]
* Added connection diagram [Chris Crocker-White]
* Added 3D case STL files [Chris Crocker-White]
* Added +x to balena-run fixes #2 [Chris Crocker-White]
* Rotate display [Chris Crocker-White]
* Reduce image size further and reduce framerate to improve performance on Pi Zero [Chris Crocker-White]
* Update README with balena and hardware setup [Chris Crocker-White]
* Removed unused packages and simplified to reduce image size [Chris Crocker-White]
* Tidying plus bug fixes to handle empty values from the API [Chris Crocker-White]
* Handle data with no platform info [Chris Crocker-White]
* Visual formatting changes, addition of platform [Chris Crocker-White]
* Change layout to prevent font stretching and add line [Chris Crocker-White]
* Add Dockerfile and README for balenaCloud use [Chris Crocker-White]
