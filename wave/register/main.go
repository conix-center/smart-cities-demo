package main

import (
	"context"
	"encoding/base64"
	"encoding/json"
	"encoding/pem"
	"flag"
	"fmt"
	"github.com/BurntSushi/toml"
	mqtt "github.com/eclipse/paho.mqtt.golang"
	"github.com/immesys/wave/consts"
	"github.com/immesys/wave/eapi"
	"github.com/immesys/wave/eapi/pb"
	"github.com/pkg/errors"
	"google.golang.org/grpc"
	"io/ioutil"
	"log"
	"time"
)

var config = flag.String("config", "register.toml", "configuration file for registration server")

type RegisterMessage struct {
	Hash string `json:"hash"`
	UUID string `json:"uuid"`
}

type RegisterResponseMessage struct {
	Hash string
	UUID string
	Namespace string
	PSet string
}

type Config struct {
	// MQTT information
	MQTTBroker string
	MQTTUser   string
	MQTTPass   string
	// WAVe agent config
	WAVEAgent string
	// filename of WAVE entity who is giving permissions
	WAVEEntity string
	// base64 hash of namespace we are granting permissions for
	Namespace string
	Pset      string
	// registration URI
	RegistrationTopic string
	RegistrationResponseTopic string
}

type RegistrationServer struct {
	entity       *pb.Entity
	entitysecret []byte
	client       pb.WAVEClient
}

func (reg *RegistrationServer) readEntityFile(name string) (*pb.Entity, []byte, error) {
	content, err := ioutil.ReadFile(name)
	if err != nil {
		return nil, nil, errors.Wrapf(err, "Could not read WAVE entity file (%s)", name)
	}
	block, _ := pem.Decode(content)
	if block == nil || block.Type != eapi.PEM_ENTITY_SECRET {
		return nil, nil, errors.New("not an entity file")
	}
	resp, err := reg.client.Inspect(context.Background(), &pb.InspectParams{
		Content: block.Bytes,
	})
	if err != nil {
		return nil, nil, errors.Wrap(err, "Could not inspect entity")
	}
	if resp.Entity == nil {
		return nil, nil, errors.New("not an entity file")
	}

	return resp.Entity, block.Bytes, nil
}

func StartRegistrationServer(cfg *Config) error {
	// connect to WAVE agent
	conn, err := grpc.Dial(cfg.WAVEAgent, grpc.WithInsecure())
	if err != nil {
		return errors.Wrapf(err, "Could not connect to WAVE agent (%s)", cfg.WAVEAgent)
	}
	WAVEclient := pb.NewWAVEClient(conn)

	reg := &RegistrationServer{
		client: WAVEclient,
	}

	// read WAVE entity
	entity, secret, err := reg.readEntityFile(cfg.WAVEEntity)
	if err != nil {
		return errors.Wrap(err, "Could not load WAVE Entity")
	}
	reg.entity = entity
	reg.entitysecret = secret

	registrationNamespace, err := base64.URLEncoding.DecodeString(cfg.Namespace)
	if err != nil {
		return errors.Wrapf(err, "%s does not look like valid base64", cfg.Namespace)
	}
	pset, err := base64.URLEncoding.DecodeString(cfg.Pset)
	if err != nil {
		return errors.Wrapf(err, "%s does not look like valid base64", cfg.Pset)
	}

	// connect to MQTT broker
	opts := mqtt.NewClientOptions()
	opts = opts.SetCleanSession(false).
		AddBroker(cfg.MQTTBroker).
                SetClientID("Test").
		SetUsername(cfg.MQTTUser).
		SetPassword(cfg.MQTTPass).
		SetAutoReconnect(true)
	MQTTclient := mqtt.NewClient(opts)
	_connectstatus := MQTTclient.Connect()
	_connectstatus.Wait()
	if err := _connectstatus.Error(); err != nil {
		return errors.Wrapf(err, "Could not connect to MQTT broker (%s)", cfg.MQTTBroker)
	}

	// subscribe to registration topic
	MQTTclient.Subscribe(cfg.RegistrationTopic, 0, func(client mqtt.Client, msg mqtt.Message) {

                log.Println("got message")
		ctx, cancel := context.WithTimeout(context.Background(), time.Second*30)
		defer cancel()

		var registrationRequest RegisterMessage
		if err := json.Unmarshal(msg.Payload(), &registrationRequest); err != nil {
			log.Println("BAD REGISTRATION", err)
			return
		}
		log.Println("Got reg request", registrationRequest)

		subjectHash, err := base64.URLEncoding.DecodeString(registrationRequest.Hash)
		if err != nil {
			log.Println(errors.Wrapf(err, "%s does not look like valid base64", registrationRequest.Hash))
			return
		}

		resp, err := WAVEclient.Inspect(ctx, &pb.InspectParams{
			Content: reg.entitysecret,
		})
		log.Println(err)
		log.Println(resp)

		policy := pb.RTreePolicy{
			Namespace:    registrationNamespace,
			Indirections: uint32(3),
			Statements: []*pb.RTreePolicyStatement{
				&pb.RTreePolicyStatement{
					PermissionSet: pset,
					Permissions:   []string{"write", "read"},
					Resource:      fmt.Sprintf("%s/*", registrationRequest.UUID),
				},
			},
		}

		fmt.Println()
		log.Println("policy", policy)

		att, err := WAVEclient.CreateAttestation(ctx, &pb.CreateAttestationParams{
			Perspective: &pb.Perspective{
				EntitySecret: &pb.EntitySecret{
					DER: reg.entitysecret,
				},
			},
			BodyScheme:  eapi.BodySchemeWaveRef1,
			SubjectHash: subjectHash,
			Policy:      &pb.Policy{RTreePolicy: &policy},
			Publish:     true,
		})
		if err != nil {
			log.Println("bad attestation", err)
			return
		}
		if att.Error != nil {
			log.Println("bad attestation", att.Error)
			return
		}

		encrypt_policy := pb.RTreePolicy{
			Namespace:    registrationNamespace,
			Indirections: uint32(3),
			Statements: []*pb.RTreePolicyStatement{
				&pb.RTreePolicyStatement{
					PermissionSet: []byte(consts.WaveBuiltinPSETBytes),
					Permissions:   []string{consts.WaveBuiltinE2EE},
					Resource:      fmt.Sprintf("%s/*", registrationRequest.UUID),
					//Resource: "*",
				},
			},
		}

		encrypt_att, err := WAVEclient.CreateAttestation(ctx, &pb.CreateAttestationParams{
			Perspective: &pb.Perspective{
				EntitySecret: &pb.EntitySecret{
					DER: reg.entitysecret,
				},
			},
			BodyScheme:  eapi.BodySchemeWaveRef1,
			SubjectHash: subjectHash,
			Policy:      &pb.Policy{RTreePolicy: &encrypt_policy},
			Publish:     true,
		})
		if err != nil {
			log.Println("bad attestation", err)
			return
		}
		if encrypt_att.Error != nil {
			log.Println("bad attestation", encrypt_att.Error)
			return
		}

		// Form an MQTT response that gives the pset and namespace
		// for this registration server
		response := RegisterResponseMessage{registrationRequest.Hash, registrationRequest.UUID, cfg.Namespace, cfg.Pset}
		r, err := json.Marshal(response)
		if err != nil {
			log.Println("bad json marshaling")
			return
		}

		// Respond with the configured Namespace and PSET
		log.Println("Responding to request:")
		log.Println(string(r))
		MQTTclient.Publish(cfg.RegistrationResponseTopic, 0, false, string(r))

	})

	log.Println("Started!")
	log.Println(cfg)

	select {}

	return nil
}

func main() {
	var cfg Config
	if _, err := toml.DecodeFile(*config, &cfg); err != nil {
		log.Fatal(err)
	} else {
		log.Println(StartRegistrationServer(&cfg))
	}
}
