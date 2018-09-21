import wavemqtt

# config information
SMARTCITIES_NAMESPACE = 'GyAHBqhwQ9hEYEYArz0vUhHsUmMT6NC9TdoA2mhH5-DGoA=='

# also serves as subscribe topic
a_uuid = "8607a83a-b7a2-11e8-8755-0cc47a0f7eea"

### PUBLISHER
def sensor():
    i = 0
    while True:
        i = i+1
        yield i

a = wavemqtt.Client("a")
print("entity is",a.b64hash)
a_sensor = sensor()
a.register(a_uuid)


# "out of band" a grants to b
# TODO: replace this with the b64 hash you get for the 'b' entity upon running 'subscriber.py', then uncomment this
# b_entity = "GyDIik10v8Qbh9queY86HESpqLNWBy6d2lGL_Tq6NQDwDw=="
# a.grant_read_to(b_entity, client.smart_cities_namespace, a_uuid+'/*')

# sense'n'send
import threading
import time
def sense_and_send():
    while True:
        time.sleep(2)
        a.publish(SMARTCITIES_NAMESPACE, a_uuid, {'uuid': a_uuid, 'count': next(a_sensor)})
t = threading.Thread(target=sense_and_send)
t.start()
