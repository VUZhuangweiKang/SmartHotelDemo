# Insecure Version of Marriott Lecture Example Application
# Vanderbilt University
# Author: Marriott Lecture Group
#
# This file is for the Dining in the architecture, whose responsibility is verifying customer order
# relayed from the FrontDesk by updating entries in DynamoDB.
#
#   The scenario is pizza ordering through Alexa Echo
#   Communication Manner:
#       1. MQTT(Communication between the FrontDesk and the Dining): tcp://*.*.*.*:1883
#
#

import time
import simplejson
from paho.mqtt.client import Client
from GlobalConstants import *


Client.connected_flag = False
mqtt_client = Client()


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        mqtt_client.connected_flag = True
    else:
        mqtt_client.connected_flag = False


def on_message(client, userdata, message):
    info = simplejson.loads(message.payload)
    print('Customer Order:')
    info['Order Status'] = 'Confirmed'
    print(info)
    client.publish(topic='%s/%s' % (ORDER_STATUS,
                                    info['Room']), payload=simplejson.dumps(info))


mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.loop_start()
mqtt_client.connect(host=MQTT_ADDR, port=MQTT_PRT)
while not mqtt_client.connected_flag:  # wait in loop
    print("In wait loop")
    time.sleep(1)
mqtt_client.subscribe(topic='%s/+' % FD_TOPIC)
mqtt_client.loop_forever()
mqtt_client.disconnect()
