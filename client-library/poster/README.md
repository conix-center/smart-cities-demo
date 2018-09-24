Client Libraries
===============

This folder will store python and go libraries for interacting with the 
smart cities demo.

They have two main functions
1) Abstract away the access control from the publishing process. They will
automatically register your sensor UUIDs with the central server guaranteeing
that your data is encrypted, can only be read by people with access (either that you
grant or that the central server grants), and that no one else will be
able to publish data on the same topics as you. Data is published to /uuid/\*.

2) Drive conformity to message type and field type. A large push is to
fit data into predefined categories so that everyone is speaking the same
naming schema. For now you have to choose from a list of predefined types (or add a type if you don't fit at all).
In the future we could imagine automatic translators that automatically make best effort matches
on a provided semantic name for a data stream or just purely based on observed data.
