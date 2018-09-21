import time
import client


# create berkeley namespace (only for managing permissions)
berkeley = client.Client("berkeley")

# create gabe client

def gabe_on_message(client, userdata, msg):
    print('GABE',msg.topic,msg.payload)
    print('-'*10)
gabe = client.Client("gabe", on_message=gabe_on_message)
# this doesn't fail (yet)
gabe.subscribe(berkeley.hash, 'a/b/c')

# grant gabe permission to read berkeley/a/b/c
berkeley.grant_read_to(gabe.hash, berkeley.hash, "a/b/c")

# gabe doesn't have permission to publish yet, so this should fail
try:
    gabe.publish(berkeley.hash, "a/b/c", "hello there")
except Exception as e:
    print("publish failed", e)

# grant publish permission
berkeley.grant_write_to(gabe.hash, berkeley.hash, "a/b/c")

# this should succeed now
try:
    gabe.publish(berkeley.hash, "a/b/c", "hello there")
except Exception as e:
    print("publish failed", e)

# create a new entity with no permissions
def other_on_message(client, userdata, msg):
    print('OTHER',msg.topic,msg.payload)
    print('-'*10)
other = client.Client("other", on_message=other_on_message)

# this successfully publishes, but other doesn't get it
gabe.publish(berkeley.hash, "a/b/c", "hello to other (no recv)")

# gabe delegates permission to other
gabe.grant_read_to(other.hash, berkeley.hash, "a/b/c") 

# this successfully publishes, AND other can get it
other.subscribe(berkeley.hash, "a/b/c")

gabe.publish(berkeley.hash, "a/b/c", "hello to other (you got this one)")
#other.publish(berkeleyhash, "a/b/c", "hey to gabe")

while True:
    time.sleep(10)
