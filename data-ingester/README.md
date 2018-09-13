Data Ingester
=============

This folder contains:
1) An automated table creator, view creator, data appender and column adder for a timescale database
2) A service which consumes data from from the system bus and posts it to
timescale. The goal is to store everything it sees. It will create tables for new
sensor channels, append them to the (materialized?) view of the sensor, and updated the
(materialized) global view off all sensors. Then data gets stored in these channels. New metadata
columns will be automatically appended to channel tables and just set to NULL if not provided.
