#!/bin/bash
if [ ! -f config.json ]; then
  cp config.sample.json config.json
  jq .journey.departureStation=\""${departureStation}"\" config.json | sponge config.json
  jq .journey.outOfHoursName=\""${outOfHoursName}"\" config.json | sponge config.json
  jq .refreshTime="${refreshTime}" config.json | sponge config.json
  jq .transportApi.appId=\""${transportApi_appId}"\" config.json | sponge config.json
  jq .transportApi.apiKey=\""${transportApi_apiKey}"\" config.json | sponge config.json
  jq .transportApi.operatingHours=\""${transportApi_operatingHours}"\" config.json | sponge config.json
fi

./run.sh
