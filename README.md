Smart Cities Demonstrator
=========================

The smart cities demonstrator is presenting a vision for a unified CONIX framework
for sensor data streaming, storage, diagnostics and access control. 

## Key ideas

### Administrative Domain 
The collection of sensors, gateways, servers, broker(s), database(s) and access permissions controlled by one entity.


### System Bus 
A Pub/Sub broker. Currently we are using mosquitto and it is located at stream.conxidb.io.

### Data Ingester
Takes everything on the system bus and logs it.

### Timescale database 
Stores a per-sensor table and exposes a global view of all sensors

### Gateway shim library 
Common language libraries that registers sensors and properly posts their data on the system bus.

### Authentication plugins 
Works with mosquitto to update the access control lists based on current permissions/sensor data.
We are working on making this work with [WAVE](https://github.com/immesys/wave/) right now, but could
also imagine other auth styles.

### External interface
The API to interacting with the administrative domain. Probably just raw database and mqtt for now.


### App submission(not for CONIX y1) 
A runtime for applications that allows for more optimal scheduling/resource management.

[Roughly sketched architecture](https://github.com/conix-center/smart-cities-demo/raw/master/media/arch.pdf)
    
