#!/bin/bash

docker run --rm -ti \
    -v ./sample:/tmp \
    daycent \
    -s wooster_base
