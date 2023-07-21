# Configuration

Sign up for the [National Rail Enquiries OpenLDBWS API](http://realtime.nationalrail.co.uk/OpenLDBWSRegistration), which will generate an token for you to use as the API key.

Only the API key is required to make the project run, everything else is optional but of course it may make sense for you to at least choose your preferred your station.

These environment variables are specified using the [balenaCloud dashboard](https://www.balena.io/docs/learn/manage/serv-vars/), allowing you to set up mutiple signs in one fleet for different stations.


| Key                              | Example Value
|----------------------------------|----------
|`apiKey` **(REQUIRED)** | `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx` (OpenLDBWS API key)
|`TZ`  | `Europe/London` ([timezone](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones))
|`departureStation`  | `PAD` ([station code](https://www.nationalrail.co.uk/stations_destinations/48541.aspx))
|`destinationStation`  | `HWV` ([station code](https://www.nationalrail.co.uk/stations_destinations/48541.aspx)) [optional] Filters trains shown to only those that call at this station
|`timeOffset`  | `5` [optional] (Time offset, in minutes, for the departure board. Can be used to see into the future (positive value) or past (negative value). Set 5 if you live 5 min from the station and want to hide departures that are too soon to catch)
|`refreshTime` | `120` (seconds between data refresh)
|`screenRotation` | `2` (rotates the output of the OLED)
|`operatingHours` | `8-22` (hours during which the data will refresh at the interval above - leave blank to run all day)
|`screenBlankHours` | `1-6` (hours during which the screen will be blank and data will not refresh - leave blank to never blank)
| `outOfHoursName` | `London Paddington` (name shown when current time is outside the `operatingHours`)
| `dualScreen` | `True` (if you are using two displays)
| `screen1Platform` | `1` (sets the platform you want to have displayed on the first or single-screen display)
| `screen2Platform` | `2` (sets the platform you want to have displayed on the second display)
| `individualStationDepartureTime` | `False` (Displays the estimated or scheduled time of the service at each leg of a journey)
| `fpsTime` | `4` (adjusts how often the effective FPS is displayed)
| `headless` | `True` (outputs to noop serial device rather than serial port; useful for running on a development machine)
| `showDepartureNumbers` | `True` (adds 1st / 2nd / 3rd as per UK train departures)
| `firstDepartureBold` | `False` (makes the first departure use either the bold or normal font)
| `targetFPS` | `20` (Frame rate regulator FPS target; 0 disables the regulator, which will increase FPS on constrained CPU, but will run the CPU hot at 100%.)
| `debug` | `False` (Display debugging information; `True` shows the debug info permanently, any integer `>1` will show instead of the splash screen for that number of seconds)

If using two screens the following line needs to be added into /boot/config.txt which is achieved by using the 'Define DT overlays' option within the Device configuration screen on balenaCloud: `spi1-3cs`

![](images/overlays.png)

