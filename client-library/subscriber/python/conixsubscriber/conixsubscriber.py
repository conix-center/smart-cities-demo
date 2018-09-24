import sys, os
import wavemqtt
import time
from aenum import Enum, auto
import pint
import psycopg2
from psycopg2 import sql
import operator
import traceback

class ConixSubscriber:

    def __init__(self, client_id,
                domain_url = 'stream.conixdb.io', domain_username='conix', domain_password='stream', domain_port='8883',
                wave_uri='localhost:410',
                database_username='username',
                database_port='port',
                database_password='password',
                database_host='host',
                database_name='name'):

        #start up a conix client
        self.client = wavemqtt.Client(str(client_id),
            mosquitto_url=domain_url,
            mosquitto_pass=domain_password,
            mosquitto_user=domain_username,
            mosquitto_port=domain_port,
            mosquitto_tls = True,
            wave_uri=wave_uri,
            on_message=self.waveCallback)

        self.namespace = self.client.register(client_id)
        print(self.client.b64hash)
        print(self.namespace)

        #initialize a psycopg2 instance
        self.connection = psycopg2.connect(dbname=database_name,
                                            host=database_host,
                                            port=database_port,
                                            user=database_username,
                                            password=database_password)
    """
    Current only takes single equals to condition
    """
    def subscribe(self, channels, condition, callback):
        self.callback = callback

        # use psycopg2 to get a list of tables in the database
        cursor = self.connection.cursor()
        cursor.execute("""SELECT table_name FROM information_schema.tables
        WHERE table_schema = 'public'""")
        tables = [x[0] for x in cursor.fetchall()]
        tableDict = {}


        #remove uuid and timestamp from the list because those are standard
        channel_lower = [x.lower() for x in channels]
        if 'uuid' in channel_lower:
            channel_lower.remove('uuid')
        if 'timestamp' in channel_lower:
            channel_lower.remove('timestamp')

        wildcard = False
        if '*' in channel_lower:
            wildcard = True

        self.subscribed_channels = channel_lower
        # now query each one of those tables to see if the table contains a
        # channel that we care about
        tableList = []
        for table in tables:
            tableDict[table] = []
            cursor.execute("""select column_name from information_schema.columns where table_schema='public' AND table_name=%s""",(table,))
            columns = [x[0] for x in cursor.fetchall()]
            tableDict[table] = columns
            channel_set = set(channel_lower)
            column_set = set(columns)
            intersection = channel_set.intersection(column_set)
            if (len(intersection) > 0 or wildcard == True):
                tableList.append(table)

        tableUUID = {}
        uuids = []
        for table in tableList:
            s = '-'
            uuid = s.join(table.split('-')[:-1])
            uuids.append(uuid)
            if uuid in tableUUID:
                tableUUID[uuid].append(table)
            else:
                tableUUID[uuid] = []
                tableUUID[uuid].append(table)

        finalTableList = []
        if condition != '':
            #get column name in condition
            later_op = None
            split_char = None;
            if condition.find('=') > -1:
                split_char = '=';
                later_op = operator.eq > -1;
            elif condition.find('>'):
                split_char = '>';
                later_op = operator.gt;
            elif condition.find('<') > -1:
                split_char = '<';
                later_op = operator.lt;
            else:
                raise ValueError("condition must contain =,>,<")

            condition = condition.lower()
            condition = "".join(condition.split())
            condition_channel = condition.split(split_char)[0]
            condition_value = condition.split(split_char)[1]

            #look for all tables with the condition we care about
            tablesToCheck = []
            for key in tableDict:
                if condition_channel in tableDict[key]:
                    tablesToCheck.append(key)

            #check if the most recent entry into that table matches the
            #condition, if does add it to a good uuid list
            goodUUID = []
            for table in tablesToCheck:
                cursor.execute(sql.SQL("""select {} from {} ORDER BY timestamp DESC limit 1""").format(sql.Identifier(condition_channel), sql.Identifier(table)))
                result = [x[0] for x in cursor.fetchall()][0]
                if isinstance(result, str):
                    if later_op(result, condition_value):
                        #great this is a good uuid
                        goodUUID.append(s.join(table.split('-')[:-1]))
                elif isinstance(result, float):
                    try:
                        if later_op(result, float(condition_value)):
                            #great this is a good uuid
                            goodUUID.append(s.join(table.split('-')[:-1]))
                    except:
                        print('Error retyping condition')
                elif isinstance(result, int):
                    try:
                        if later_op(result, int(condition_value)):
                            #great this is a good uuid
                            goodUUID.append(s.join(table.split('-')[:-1]))
                    except:
                        print('Error retyping condition')

            #intersect the uuids and good UUID lists to produce a final list
            uuid_set = set(uuids)
            good_uuid_set = set(goodUUID)
            final_set = uuid_set.intersection(good_uuid_set)
            for uuid in final_set:
                finalTableList  = finalTableList + tableUUID[uuid]

        else:
            finalTableList = tableList

        # query all the tables in the final table list
        # make a dict with uuid as key and the info the user cares about
        # as the values
        self.subscribeData = {}
        for table in finalTableList:
            cursor.execute(sql.SQL("""select * from {} ORDER BY timestamp DESC limit 1""").format(sql.Identifier(table)))
            result = cursor.fetchall()[0]
            columns = [desc[0] for desc in cursor.description]
            if result[columns.index('uuid')] not in self.subscribeData:
                self.subscribeData[result[columns.index('uuid')]] = {}

            self.subscribeData[result[columns.index('uuid')]]['uuid'] = result[columns.index('uuid')]
            self.subscribeData[result[columns.index('uuid')]]['timestamp'] = result[columns.index('timestamp')].timestamp()*1000000
            for column in columns:
                if(wildcard == True and column != 'timestamp' and column != 'uuid'):
                    self.subscribeData[result[columns.index('uuid')]][column] = result[columns.index(column)]
                elif column in channel_lower:
                    self.subscribeData[result[columns.index('uuid')]][column] = result[columns.index(column)]

        #make the initial callbacks to the user with the starting data
        for key in self.subscribeData:
            self.callback(self.subscribeData[key])

        #now turn this list of final tables into a list of MQTT topics
        #and subscribe through wave.
        s = '-'
        for table in finalTableList:
            topic = s.join(table.split('-')[:-1])+'/'+ table.split('-')[-1]
            self.client.subscribe(self.namespace, topic)

    def waveCallback(self,client, userdata, msg):
        # on callback go into the dict, update the information that was sent
        # in this message, then callback to the user with the updated dict
        # for that uuid
        wildcard = False
        if '*' in self.subscribed_channels:
            wildcard = True

        try:
            for key in msg.payload:
                if key.lower() in self.subscribed_channels or wildcard == True:
                    self.subscribeData[msg.payload['uuid']][key.lower()] = msg.payload[key]

            self.callback(self.subscribeData[msg.payload['uuid']])
        except:
            traceback.print_exc()
