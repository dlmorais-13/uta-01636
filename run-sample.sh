#!/bin/bash

sudo rm -rf sample/outputs/

docker run --rm -ti \
    -v ./sample:/tmp \
    daycent \
    -s wooster_base
