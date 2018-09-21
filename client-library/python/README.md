Python Client Library
=====================

Look at publisher.py for an example. This standardizes units and sensor types
before putting them on the conix broker. It also automates the use of wave.

To install:
```
#get the wave service running
sudo cp ../../wave/systemd/waved.service /etc/systemd/system/.
sudo cp ../../wave/bin/waved /usr/local/bin/.
sudo cp ../../wave/bin/wv /usr/local/bin/.
sudo systemctl enable waved
sudo systemctl start waved

#install wave3
pip3 install git://github.com/immesys/pywave#egg=wave3

#install the conixposter package
pip3 install conixposter
```

To use:
```
import conixposter

poster = conixposter.ConixPoster("Some Unique ID")

poster.post(sensor_uuid, conixposter.ConixPoster.SensorTypes.Temperature_Sensor, value, 'degC')
```
