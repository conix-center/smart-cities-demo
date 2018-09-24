Python Subscriber Client Library
=====================

Look at subscribe.py for an example. This provides a contextualized
query method for conix streams. Currently requires postgres access which
we are not giving out. This needs to be added in a future improvement.

To install:
```
#get the wave service running
sudo cp ../../wave/bin/waved /usr/local/bin/waved
sudo cp ../../wave/bin/wv /usr/local/bin/wv
sudo mkdir -p /etc/wave
sudo cp ../../conf/wave.toml /etc/wave/wave.toml
sudo chmod +x /usr/local/bin/waved
sudo chmod +x /usr/local/bin/wv
sudo cp ../../wave/systemd/waved.service /etc/systemd/system/.
sudo systemctl start waved
sudo systemctl enable waved

#install wave3
pip3 install git+https://github.com/immesys/pywave#egg=wave3

#install the conixsubscriber package
pip3 install conixsubscriber
```

To use:
```
import conixsubscriber

subscriber = conixposter.ConixSubscriber("SomeUniqueString"...database_details)

def callback(data_on_update):
    print(data_on_update)

subscriber.subscribe(['data','temperature'],'someFilter > 2', callback)
```
