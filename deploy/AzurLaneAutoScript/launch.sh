#!/bin/bash
ssh hgjazhgj@raspberrypi -o StrictHostKeyChecking=no "sudo docker run -v ~/hgjazhgj/FGO-py/FGO-py:/FGO-py --name fgo-py -e NO_COLOR=1 -i --rm hgjazhgj/fgo-py"
