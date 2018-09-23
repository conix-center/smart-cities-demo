import sys, os
import wavemqtt
import time
from aenum import Enum, auto
import pint
import psycopg2

class ConixSubscriber:

    def __init__(self, client_id, 
                domain_url = 'stream.conixdb.io', domain_username='conix', domain_password='stream', domain_port='8883', 
                wave_uri='localhost:410',
                database_username='username',
                database_port='port',
                database_password='password',
                database_hoster='host'
                database_name='name'):

        #start up a conix client
        self.client = wavemqtt.Client(str(client_id),
            mosquitto_url=domain_url,
            mosquitto_pass=domain_password,
            mosquitto_user=domain_username,
            mosquitto_port=domain_port,
            mosquitto_tls = True,
            wave_uri=wave_uri)

        #initialize a psycopg2 instance
        self.connection = psycopg2.connect(dbname=database_name, 
                                            host=database_host, 
                                            port=database_port, 
                                            user=database_username, 
                                            password=database_password)
    """
    Current only takes single equals to condition
    """
    def subscribe(channels, condition, callback):
        self.callback = callback
        
        # use psycopg2 to get a list of tables in the database
        cursor = self.connection.cursor()
        cursor.execute("""SELECT table_name FROM information_schema.tables
        WHERE table_schema = 'public'""")
        tables = cursor.fetchall()
        tableDict = {}

        #remove uuid and timestamp from the list because those are standard
        channel_lower = [x.lower() for x in channels]
        channel_lower.remove('uuid')
        channel_lower.remove('timestamp')

        # now query each one of those tables to see if the table contains a
        # channel that we care about
        tableList = []
        for table in tables:
            tableDict[table] = [] 
            cursor.execute("select column_name from information_schema.columns where table_schema='public' AND table_name=%s",table)
            columns = cursor.fetchall()
            tableDict[table] = columns
            channel_set = set(channel_lower)
            column_set = set(columns)
            intersection = channel_set.intersection(column_set)
            if (len(intersection) > 0):
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
            condition_channel = condition.split('=')[0]
            condition_value = condition.split('=')[1]
            
            #look for all tables with the condition we care about
            tablesToCheck = []
            for key in tableDict:
                if condition_channel in tableDict[key]:
                    tablesToCheck.append(key)

            #check if the most recent entry into that table matches the
            #condition, if does add it to a good uuid list
            goodUUID = []
            for table in tablesToCheck:
                cursor.execute(sql.SQL("select %s from {} ORDER BY timestamp DESC limit 1").format(sql.Identifier(table)), condition_channel)
                result = cursor.fetch()
                if condition_value == result:
                    #great this is a good uuid
                    goodUUID.append(s.join(table.split('-')[:-1]))
            
            #intersect the uuids and good UUID lists to produce a final list
            uuid_set = set(uuids)
            good_uuid_set = set(goodUUID)
            final_set = uuid_set.intersection(good_uuid_set)
            for uuid in final_set:
                finalTableList  = finalTableList + tableUUID[uuid] 

        else:
            finalTableList = tableList
        
        print(finalTableList)
