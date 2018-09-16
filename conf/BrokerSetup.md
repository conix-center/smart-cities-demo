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

Start the data ingester as a service

Start the registration server as a service
