# WAVE 

See README/Tutorial at https://github.com/immesys/wave

---

The hash of the smart-cities-demo root entity is `GyAHBqhwQ9hEYEYArz0vUhHsUmMT6NC9TdoA2mhH5-DGoA==`

The hash of the permission set is `GyAa2eh0Ksh4eYdmHiAVuU7Hf2tyy06QbkrLke1ho0WS_Q==`

---

## Stuff to do

Create your entity:

```bash
$ wv mke -e '2y' -o myentity.ent --nopassphrase
wrote entity: myentity.ent
```

2. Inspect your entity file

```bash
$ wv inspect myentity.ent
= Entity
      Hash: GyDNAT7fMUUA_jw-Ochg07TLg1VmCBLNL-m0S1sl5hOyYw==
   Created: 2018-09-13 09:55:11 -0700 PDT
   Expires: 2020-09-12 09:55:11 -0700 PDT
  Validity:
   - Valid: true
   - Expired: false
   - Malformed: false
   - Revoked: false
   - Message:
```

3. Inspect the smart cities hash (remote hash). Pass your entity file as 'perspective'

```bash
$ wv resolve GyAHBqhwQ9hEYEYArz0vUhHsUmMT6NC9TdoA2mhH5-DGoA== --perspective myentity.ent
passphrase for entity secret:
Synchronized 1/2 entities
Synchronized 2/2 entities
Perspective graph sync complete
"GyAHBqhwQ9hEYEYArz0vUhHsUmMT6NC9TdoA2mhH5-DGoA==":
= Entity
  Location: default
      Hash: GyAHBqhwQ9hEYEYArz0vUhHsUmMT6NC9TdoA2mhH5-DGoA==
  Known as: < unknown >
   Created: 2018-09-13 09:52:40 -0700 PDT
   Expires: 2028-09-10 09:52:40 -0700 PDT
  Validity:
   - Valid: true
   - Expired: false
   - Malformed: false
   - Revoked: false
   - Message:
```

4. Check if you have access to the smart cities namespace (read, write permissions on `/*`)

```bash
$ wv rtprove --subject myentity.ent GyAa2eh0Ksh4eYdmHiAVuU7Hf2tyy06QbkrLke1ho0WS_Q==:read,write@GyAHBqhwQ9hEYEYArz0vUhHsUmMT6NC9TdoA2mhH5-DGoA==/*
passphrase for entity secret:
Synchronized 3/4 entities
Synchronized 4/4 entities
Perspective graph sync complete
error: (911: couldn't find a proof)
```

5. Grant access (replace the `--attester` with the path to your entity if you are granting permission to someone else; listed here is the command for smart cities to give YOU access).
Replace the `--subject` with the public hash of who you are granting to.

```bash
$ wv rtgrant -e 2y --attester smart-cities-demo-entity --indir 10 --subject GyDNAT7fMUUA_jw-Ochg07TLg1VmCBLNL-m0S1sl5hOyYw== GyAa2eh0Ksh4eYdmHiAVuU7Hf2tyy06QbkrLke1ho0WS_Q==:read,write@GyAHBqhwQ9hEYEYArz0vUhHsUmMT6NC9TdoA2mhH5-DGoA==/*
Synchronized 5/6 entities
Synchronized 6/6 entities
Perspective graph sync complete
wrote attestation: att_GyC7u4-AVZzvMLOeP_-nWq2amapROr5faV1BV8P34VbuQA==.pem
published attestation
```

6. Now re-check access

```bash
$ wv rtprove --subject myentity.ent GyAa2eh0Ksh4eYdmHiAVuU7Hf2tyy06QbkrLke1ho0WS_Q==:read,write@GyAHBqhwQ9hEYEYArz0vUhHsUmMT6NC9TdoA2mhH5-DGoA==/*
Synchronized 13/15 entities
Synchronized 14/15 entities
Synchronized 16/16 entities
Perspective graph sync complete
wrote proof: proof_2018-09-13T10:07:16-07:00.pem
```
