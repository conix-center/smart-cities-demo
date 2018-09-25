import paho.mqtt.client as mqtt
import time
import wave3
import json
import pickle
import base64
import grpc
import threading

#use this pset
pset = bytes("GyAa2eh0Ksh4eYdmHiAVuU7Hf2tyy06QbkrLke1ho0WS_Q==", "utf8")


"""
**NOTE**: WAVE is pretty general; below I describe a particular application/interpretation of its features towards the pub/sub task

Permissions:

An entity constitutes a namespace, designated by the public key hash of that entity. This entity is the "root" authority
for all URIs starting with that hash. For example, if Alice's public key hash was "ABC", then Alice would be the root authority
for all URIs matching "ABC/#" (using mosquitto parlance for the URIs).

Alice can delegate the permission to "read/subscribe" or "write/publish" on URI patterns to other entities, identified by their
own public key hashes. A specific entity can read/write on a URI if there is a path of delegation from Alice to that entity where
all of the delegations are valid and non-expired. Each delegation consists of a URI pattern, a set of permissions, an expiry, and a
source/destination. WAVE defines, constructs, authenticates and validates these chains of delegations for you.

A "URI" is composed of a namespace hash followed by a '/'-delimited resource path.
Because all entities have a public hash, every entity can serve as the root authority of its own "namespace". Any entity can grant
a permission on a resource on a namespace to another entity. This permission is only considered valid if there is a sequence of these
grants that is rooted at the entity whose hash is the namespace these permissions are granted on.
"""

class Client:
    """
    A client has a WAVE ENTITY (identified by entity_name). This gets published to WAVE storage so others
    can refer to it by the public key (retrieved using Client.hash()). This entity is placed into a pickle
    file in the current directory in a file called entity-<Client.entity_name> (e.g. "entity-gabe").

    Parameters:
    - entity_name: a local alias for a public/private key pair comprising a WAVE entity
    - wave_uri: the GRPC endpoint of the local waved agent. Shouldn't need to be changed
    - mosquitto_url, mosquitto_user, mosquitto_pass: MQTT broker information
    - on_message: paho.mqtt style callback (def callback(client, userdata, meta): ...)
    """
    def __init__(self, entity_name="gabe", wave_uri="localhost:410", mosquitto_url="", mosquitto_pass="", mosquitto_user="", mosquitto_port=1883, mosquitto_tls=True, mosquitto_capath=None, on_message=None):
        # connect to WAVE agent
        self.agent = wave3.WAVEStub(grpc.insecure_channel(wave_uri))

        # set up entity and store keys
        self.entity_name = entity_name
        self.entity, newlycreated = self.createOrLoadEntity(entity_name)
        self.entityPublicDER = self.entity.PublicDER
        self.entitySecretDER = self.entity.SecretDER
        self.perspective =  wave3.Perspective(
            entitySecret=wave3.EntitySecret(DER=self.entity.SecretDER))
        # publish this so others can refer to it
        if newlycreated:
            self.agent.PublishEntity(
                wave3.PublishEntityParams(DER=self.entity.PublicDER))

        # create mqtt client
        self.topic_list = []
        self.client = mqtt.Client(client_id=entity_name, clean_session=True)
        self._connected = False
        self._pending = []
        self._call_on_message = on_message
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_message = self.on_message
        self.client.username_pw_set(mosquitto_user, mosquitto_pass)
        if mosquitto_tls is True and mosquitto_capath is None:
            self.client.tls_set()
        elif mosquitto_tls is True:
            self.client.tls_set(mosquitto_capath)
        self.client.connect(mosquitto_url, int(mosquitto_port), 60)
        self.client.loop_start()

        #we should store our proofs in memory to save time
        self.publish_proofs = {}
        self.decrypt_proofs = {}

    @property
    def hash(self):
        """
        Return the hash of the client's entity
        """
        return self.entity.hash

    @property
    def b64hash(self):
        """
        Return the base64, url-safe encoding of the hash of the client's entity
        """
        return str(b64encode(self.hash), 'utf8')

    def createOrLoadEntity(self, name):
        """
        Check if we have already created an entity (maybe we reset the notebook kernel)
        and load it. Otherwise create a new entity and persist it to disk
        """
        try:
            f = open("entity-"+name, "rb")
            entf = pickle.load(f)
            f.close()
            ent = wave3.CreateEntityResponse(PublicDER=entf["pub"], SecretDER=entf["sec"], hash=entf["hash"])
            #print("file", ent.hash)
            return ent, False
        except (IOError, FileNotFoundError) as e:
            ent = self.agent.CreateEntity(wave3.CreateEntityParams())
            if ent.error.code != 0:
                raise Exception(repr(ent.error))
            entf = {"pub":ent.PublicDER, "sec":ent.SecretDER, "hash":ent.hash}
            f = open("entity-"+name, "wb")
            pickle.dump(entf, f)
            f.close()
            resp = self.agent.PublishEntity(wave3.PublishEntityParams(DER=ent.PublicDER))
            #print("creat", resp.hash)
            if resp.error.code != 0:
                raise Exception(resp.error.message)
            return ent, True

    def _grant_permission_to(self, entityhash, namespace, uripattern, permissions):
        """
        hashes: entityhash, namespace
        uripattern: string
        permissions is a list of permissions
        """
        namespace = self.parsehash(namespace)
        entityhash = self.parsehash(entityhash)

        # grants the permission to access the uri
        resp = self.agent.CreateAttestation(wave3.CreateAttestationParams(
            perspective=self.perspective,
            subjectHash=entityhash,
            publish=True,
            policy=wave3.Policy(rTreePolicy=wave3.RTreePolicy(
                namespace=namespace,
                indirections=5,
                statements=[
                    wave3.RTreePolicyStatement(
                        permissionSet=pset,
                        permissions=permissions,
                        resource=uripattern,
                    )
                ]
            ))
        ))
        if resp.error.code != 0:
            raise Exception(resp.error.message)

        # grant permission to decrypt/encrypt
        resp = self.agent.CreateAttestation(wave3.CreateAttestationParams(
            perspective=self.perspective,
            subjectHash=entityhash,
            publish=True,
            policy=wave3.Policy(rTreePolicy=wave3.RTreePolicy(
                namespace=namespace,
                indirections=5,
                statements=[
                    wave3.RTreePolicyStatement(
                        permissionSet=wave3.WaveBuiltinPSET,
                        permissions=[wave3.WaveBuiltinE2EE],
                        resource=uripattern,
                    )
                ]
            ))
        ))
        if resp.error.code != 0:
            raise Exception(resp.error.message)

    def register(self, uuidstring):
        """
        Registers this entity as being able to publish on the smart_cities_namespace/<uuidstring>; requires the external
        service to be running.

        Also subscribes to the registration response and sets the namespace
        and pset for the registering entity
        """
        # Subscribe to this topic
        self.client.subscribe('register/response')

        # Wait for a response event or a timeout
        self.registerEvent = threading.Event()

        self.client.publish('register', payload=json.dumps({
            'hash': str(b64encode(self.hash), 'utf8'),
            'uuid': uuidstring,
        })).wait_for_publish()

        if not self.registerEvent.wait(timeout=10):
            print("ERROR: Registration response timed out!")
            raise TimeoutError("Registration response timed out")
        else:
            return self.registerResponseNamespace


    def sync(self):
        """
        Call this to make sure you are up to date with the permissions graph.
        The client library should do this automatically, but its here in case its needed
        """
        resp =self.agent.ResyncPerspectiveGraph(wave3.ResyncPerspectiveGraphParams(perspective=self.perspective))
        if resp.error.code != 0:
            raise Exception(resp.error.message)

        resp = self.agent.WaitForSyncComplete(wave3.SyncParams(perspective=self.perspective))
        for r in resp:
            pass
        return

    def parsehash(self, b64hash):
        if isinstance(b64hash, bytes):
            return b64hash
        else:
            return b64decode(b64hash)

    def grant_read_to(self, target_entity_hash, namespace, uripattern):
        """
        Creates a delegation from this client to target_entity_hash. The delegation
        attests that this client has given the ability to read/subscribe to the topic 'uripattern'
        on the given namespace. The namespace is the hash of an entity; this entity is considered
        the root authority of the namespace.
        REMEMBER TO USE * INSTEAD OF # FOR WILDCARD. + IS ALSO SUPPORTED
        """
        self._grant_permission_to(target_entity_hash, namespace, uripattern, ["read"])

    def grant_write_to(self, target_entity_hash, namespace, uripattern):
        """
        Creates a delegation from this client to target_entity_hash. The delegation
        attests that this client has given the ability to write/publish to the topic 'uripattern'
        on the given namespace. The namespace is the hash of an entity; this entity is considered
        the root authority of the namespace.
        REMEMBER TO USE * INSTEAD OF # FOR WILDCARD. + IS ALSO SUPPORTED
        """
        self._grant_permission_to(target_entity_hash, namespace, uripattern, ["write"])

    def grant_all_to(self, target_entity_hash, namespace, uripattern):
        """
        Grants both read and write permissions
        """
        self._grant_permission_to(target_entity_hash, namespace, uripattern, ["read", "write"])

    def subscribe(self, namespace, topic):
        """
        Subscribes to the topic on the given namespace; fires the callback you registered in the index
        """
        self.sync()
        namespace = self.parsehash(namespace)
        while not self._connected:
            time.sleep(1)
        self.topic_list.append(form_topic(namespace,topic))
        print(self.entity_name, 'subscribing to',form_topic(namespace, topic))
        self.client.subscribe(form_topic(namespace, topic))

    def publish(self, namespace, topic, payload):
        """
        Publish the payload (any JSON-serializable object) to the topic on the given namespace
        """
        namespace = self.parsehash(namespace)
        publish_proof = None
        if topic not in self.publish_proofs:
            # build the proof for publishing on the topic
            publish_proof = self.agent.BuildRTreeProof(wave3.BuildRTreeProofParams(
                perspective = self.perspective,
                namespace=namespace,
                resyncFirst=True,
                statements=[
                    wave3.RTreePolicyStatement(
                        permissionSet=pset,
                        permissions=["write"],
                        resource=topic,
                    )
                ]
            ))
            if publish_proof.error.code != 0:
                raise Exception(publish_proof.error)

            self.publish_proofs[topic] = publish_proof
        else:
            publish_proof = self.publish_proofs[topic]

        #build the proof for decrypting messages on the topic
        decrypt_proof = None
        if topic not in self.decrypt_proofs:
            decrypt_proof = self.agent.BuildRTreeProof(wave3.BuildRTreeProofParams(
                perspective = self.perspective,
                namespace=namespace,
                resyncFirst=True,
                statements=[
                    wave3.RTreePolicyStatement(
                        permissionSet=wave3.WaveBuiltinPSET,
                        permissions=[wave3.WaveBuiltinE2EE],
                        resource=topic,
                    )
                ]
            ))
            if decrypt_proof.error.code != 0:
                raise Exception(decrypt_proof.error)

            self.decrypt_proofs[topic] = decrypt_proof
        else:
            decrypt_proof = self.decrypt_proofs[topic]

        # encrypt payload
        msg = bytes(json.dumps(payload), 'utf8')
        resp = self.agent.EncryptMessage(wave3.EncryptMessageParams(
            perspective=self.perspective,
            namespace=namespace,
            content=msg,
            resource=topic
        ))
        if resp.error.code != 0:
            raise Exception(resp.error)

        # pack message
        #b64 = str(bbase64.ase64.b64encode(publish_proof.proofDER), "utf8")
        b64 = base64.b64encode(publish_proof.proofDER)
        packed_payload = bytes("%08d" % (len(b64)), "utf8") + b64 + resp.ciphertext

        print(self.entity_name, "publishing on", form_topic(namespace, topic))
        res = self.client.publish(form_topic(namespace, topic), payload=packed_payload, qos=1)
        #res = self.client.publish(form_topic(namespace, topic), payload="hello")
        #I don't think we should wait for publish
        #res.wait_for_publish()

    def on_connect(self, client, userdata, flags, rc):
        """MQTT callback"""
        print('connected!')
        self._connected = True
        for topic in self.topic_list:
            print(self.entity_name, 'subscribing to', topic)
            self.client.subscribe(topic)

    def on_disconnect(self, client, userdata, flags, rc):
        """MQTT callback"""
        print('lost connection!')
        self._connected = False

    def on_message(self, client, userdata, msg):
        """MQTT callback for handling messages. Decodes/unpacks"""
        if msg.topic == 'register/response':
            resp = json.loads(msg.payload.decode('utf8'))
            if(resp['Hash'] == self.b64hash):
                self.registerResponseNamespace = resp['Namespace']
                self.registerEvent.set()

        else:
            self.sync()
            msg.payload = self.handle_msg(msg)
            if msg.payload:
                self._call_on_message(client, userdata, msg)

    def handle_msg(self, msg):
        """
        Verify that the published message was authorized, then decrypt it
        """
        namespace, topic = parse_topic(msg.topic)

        proof, payload = unpack_payload(msg.payload)

        resp = self.agent.VerifyProof(wave3.VerifyProofParams(
            proofDER=proof,
            requiredRTreePolicy=wave3.RTreePolicy(
                namespace=namespace,
                statements=[wave3.RTreePolicyStatement(
                    permissionSet=pset,
                    permissions=["write"],
                    resource=topic,
                )]
            )
        ))
        if resp.error.code != 0:
            print(resp.error)
            return None
            #raise Exception(resp.error)

        decrypt_msg = self.agent.DecryptMessage(wave3.DecryptMessageParams(
            perspective=self.perspective,
            ciphertext=payload,
        ))
        return json.loads(decrypt_msg.content.decode('ascii'))

### Utility functions

def unpack_payload(payload):
    if len(payload) < 100:
        return b"", ""
    proof_len=int(payload[:8])
    proof = payload[8:proof_len+8]
    bproof = base64.b64decode(proof)
    real_payload = payload[proof_len+8:]
    return bproof, real_payload

def form_topic(namespace, topic):
    return str(b64encode(namespace), 'utf8') + '/' + topic

def parse_topic(topic):
    parts = topic.split('/')
    namespace, topic = parts[0], '/'.join(parts[1:])
    namespace = b64decode(namespace)
    return namespace, topic

def b64encode(e):
    return base64.b64encode(e, altchars=bytes('-_', 'utf8'))
def b64decode(e):
    return base64.b64decode(e, altchars=bytes('-_', 'utf8'))
