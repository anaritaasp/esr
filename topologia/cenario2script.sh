#!/bin/bash
server=$1
bootstrapper=$2
ssh core@$server 'cd /home/core/Desktop/esr/src; python3 oNode.py' $bootstrapper