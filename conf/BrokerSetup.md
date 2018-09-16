Broker Setup
============

These are all the steps I'm taking to set up an administrative domain on stream.conixdb.io

## Setup an MQTT Broker

The new feature allowing localhost to not have password protection but
access control remote host is worth it. Clone, build and install mosquitto 1.5.1.

This required linking the three binaries into /usr/bin, copying the shared
library into the right location, setting up /etc/mosquitto and starting
mosquitto as a service in systemd. You can find these instructions
in the mosquitto install readmes.

## Clone the repo and setup wave permissions

Clone the smart-cities-demo repository

Create a root wave entity

Create a data ingester wave entity, and grant it root read permissions.

Create a registration wave entity, and grant it root read,write permissions.

## Startup necessary services

Start the data ingester as a service. This requires placing the systemd file
in the systemd services, enabling and starting the service.

Start the registration server as a service. This requires install go. Make sure
to use the apt package golang-1.10-go because this registration script will no
work on 1.6, the version downloaded by golang-go. You will also need to 
symbolic link from /usr/lib/go-1.10/bin to /usr/bin for go to be on your path.

Then copy the systemd file into your services folder, enable and start it. It expects
the smart-cities-demo repo to be at the root of the home directory of the ubuntu user for now.
