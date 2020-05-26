#!/bin/bash

if [[ ! -z "${departureStation}" ]]; then
  jq .journey.departureStation=\""${departureStation}"\" config.json | sponge config.json
fi

if [[ ! -z "${destinationStation}" ]]; then
  jq .journey.destinationStation=\""${destinationStation}"\" config.json | sponge config.json
fi

if [[ ! -z "${outOfHoursName}" ]]; then
  jq .journey.outOfHoursName=\""${outOfHoursName}"\" config.json | sponge config.json
fi

if [[ ! -z "${refreshTime}" ]]; then
  jq .refreshTime="${refreshTime}" config.json | sponge config.json
fi

if [[ ! -z "${transportApi_appId}" ]]; then
  jq .transportApi.appId=\""${transportApi_appId}"\" config.json | sponge config.json
fi

if [[ ! -z "${transportApi_apiKey}" ]]; then
  jq .transportApi.apiKey=\""${transportApi_apiKey}"\" config.json | sponge config.json
fi

if [[ ! -z "${transportApi_operatingHours}" ]]; then
  jq .transportApi.operatingHours=\""${transportApi_operatingHours}"\" config.json | sponge config.json
fi

python ./src/main.py
