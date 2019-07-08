# UK Train Departure Display 

A set of python scripts to display replica near real-time UK railway station departure data on SSD13xx style screens that uses the publicly available [Transport API](https://www.transportapi.com/).  

   * [Installation](#installation)
   * [Configuration](#configuration)

## Installation

To run this code, you will need Python 3.6+

To install the latest version of Python (3.7 at time of writing) on Raspbian, go [here](https://gist.github.com/SeppPenner/6a5a30ebc8f79936fa136c524417761d).

You will likely need to set up an alias so that when you type Python you get the latest installed version, a handy guide on how to do this on Raspbin is [here](https://linuxconfig.org/how-to-change-from-default-to-alternative-python-version-on-debian-linux).  If you used the above guide to install the latest Python your path to the executable will be /usr/local/bin/python3.x

>>### Raspbian Lite

>If you're using Raspbian Lite, you'll also need to install:
>- `libopenjp2-7`
>with:
>```bash
>$ sudo apt-get install libopenjp2-7
>```

Clone this repo

Install dependencies

```bash
$ pip3 install -r requirements.txt
```
If you installed Python using the above guide you will need to use pip3 instead of pip to install the requirements, if not or if your pip is aliased to python 3.6+ you can just use pip
```bash
$ pip install -r requirements.txt
```

## Configuration 
