#!/bin/bash

set -ex

# copy wave binary and systemd unit file
sudo cp wave/bin/waved /usr/local/bin/waved
sudo cp wave/bin/wv /usr/local/bin/wv
sudo mkdir -p /etc/wave
sudo cp conf/wave.toml /etc/wave/wave.toml
sudo chmod +x /usr/local/bin/waved
sudo chmod +x /usr/local/bin/wv
sudo cp wave/systemd/waved.service /etc/systemd/system/.
sudo systemctl start waved
sudo systemctl enable waved

# install python dependencies
sudo apt update -y
sudo apt install -y python3-venv
python3 -m venv venv
. venv/bin/activate
rm -rf pywave
git clone https://github.com/immesys/pywave
pip3 install -e pywave 
pip3 install wheel paho-mqtt

# run example
cd wave/mqtt-client/python/examples
python example.py
