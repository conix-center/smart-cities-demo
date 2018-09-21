import client

# config information
SMARTCITIES_NAMESPACE = 'GyAHBqhwQ9hEYEYArz0vUhHsUmMT6NC9TdoA2mhH5-DGoA=='

# also serves as subscribe topic
a_uuid = "8607a83a-b7a2-11e8-8755-0cc47a0f7eea"

### SUBSCRIBER
def b_cb(client, ud, msg):
    print('b got', msg.topic, msg.payload)
b = client.Client("b", on_message=b_cb)
print("entity is", b.b64hash)

b.subscribe(SMARTCITIES_NAMESPACE, a_uuid)

# block and wait for data
import time
while True:
    time.sleep(1)
