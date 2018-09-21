# Registration service

Subscribes to some URI (e.g. `GyAHBqhwQ9hEYEYArz0vUhHsUmMT6NC9TdoA2mhH5-DGoA==/register` for CONIX) and listens for requests.

A request is of the form

```json
{
    "hash": "GyBSjxk46TBzOwFi-hHCh5waVIj8EaGDJwCXV5uBZ3vo5A==",
    "uuid": "8b98d56e-b778-11e8-8755-0cc47a0f7eea",
}
```

`hash` is the public key hash of a WAVE entity. `uuid` is a UUID for a sensor or other reporting device. Receiving this registration, the service gives the WAVE entity permission to publish as the sensor with that UUID.

*The specifics here depend on how we define the URI structure*

Concretely, this means that the WAVE entity has publish/write permission on the URI `GyAHBqhwQ9hEYEYArz0vUhHsUmMT6NC9TdoA2mhH5-DGoA==/8b98d56e-b778-11e8-8755-0cc47a0f7eea/*`.
