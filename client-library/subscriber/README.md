CONIX Subscriber
===============

The subscriber interface is how you consume data from the conix system.

At a high level the idea is to make it easy to find the data you care about and
use/perform computation on that data.

Specifically a subscriber will subscribe to set a set of sensors that
fall under some conditions (which could be sensor IDs or other some other
sensor data stream)

The subscriber then gets callbacks for these sensors when they update and
are still within the conditions.

Eventually we hope that this will also be a mechanism for finding both
sensors and actuators relative to the context an application cares about.
