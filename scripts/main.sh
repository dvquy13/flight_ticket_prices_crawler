#!/bin/bash

# Start docker
docker_ps_scrapinghub="$(docker ps | grep scrapinghub)"
docker_ps_scrapinghub_len=${#docker_ps_scrapinghub}
if [ $docker_ps_scrapinghub_len -eq 0 ]
then
    echo "Starting scrapinghub/splash docker..."
    docker run -d -p 8050:8050 scrapinghub/splash
    echo "scrapinghub/splash docker running..."
else
    echo "scrapinghub/splash docker already running!"
fi

# Scrapy crawling
scrapy crawl traveloka

# Report via Slack channel
python3 report.py

# Stop docker
docker_scrapinghub_id="$(docker ps | grep scrapinghub/splash | awk '{print $1;}')"
docker stop "$docker_scrapinghub_id"
echo "Stopped scrapinghub/splash docker container"