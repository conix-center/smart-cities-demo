#!/usr/bin/env python3

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'conixsubscriber'))
import conixsubscriber

#import the postgres config file
postgresParser.read('postgres.ini')
postgresConf = postgresParser['DEFAULT']

subscriber = conixsbuscriber.ConixSubscriber("subscribe", 
                                            database_username = postgresConf['username'],
                                            database_port = postgresConf['port'],
                                            database_name = postgresConf['database'],
                                            database_password = postgresConf['password'],
                                            database_host = postgresConf['host'])

def callback():
    pass

subscriber.subscribe(['Temperature'],'uuid=8608a83a-b7a2-11e8-8755-0cc47a0f7777', callback)
