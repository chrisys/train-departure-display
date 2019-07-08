# UK Train Departure Display 

A set of python scripts to display replica near real-time UK railway station departure data on SSD13xx style screens that uses the publicly available [Transport API](https://www.transportapi.com/).  

   * [Requirements](#requirements)
   * [Installation](#installation)
   * [Configuration](#configuration)

## Requirements

To run this code, you will need Python 3.6+, to install the latest version of Python (3.7 at time of writing) on Raspbian, go [here](https://gist.github.com/SeppPenner/6a5a30ebc8f79936fa136c524417761d).

You will likely need to setup an alias so that when you type Python you get the latest installed version, a handy guide on how to do this on Raspbin is [here](https://linuxconfig.org/how-to-change-from-default-to-alternative-python-version-on-debian-linux).  If you used the above guide to install the latest Python your path to the executable will be /usr/local/bin/python3.x

### Raspbian

If you're using Raspbian Lite, you'll also need to install:

- `libopenjp2-7`

with:

```bash
$ sudo apt-get install libopenjp2-7
```
