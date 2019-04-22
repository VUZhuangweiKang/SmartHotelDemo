# Sample code for Marriott Lecture
# Vanderbilt University
# Author: Marriott Lecture Group
#
# This file is for Manager in the architecture, whose responsibility is receiving
# customer requests sent from Lambda Function.
#
#
#   The scenario is pizza ordering through Alexa Echo
#   Communication Manner:
#       1. MQTT(Lambda listens responses from Manager): tcp://*.*.*.*:1883
#       2. Flask(Manager listens requests from Lambda): https://*.*.*.*:5000
#   Communication Security Issue:
#       1. MQTT: using public MQTT server
#       2. Flask: using http instead of https, no http header encryption
#       3. No message encryption
#
#

import time
import simplejson
from paho.mqtt.client import Client
from GlobalConstants import *
from MessageSecure import *


Client.connected_flag = False
mqtt_client = Client()


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        mqtt_client.connected_flag = True
    elif rc == 5:
        print('Connection refused.')
        mqtt_client.connected_flag = False
    else:
        mqtt_client.connected_flag = False


def on_message(client, userdata, message):
    info = decrypt(MESSAGE_DECRYPT_KEY, simplejson.loads(message.payload))
    print('Customer Order:')
    info['Order Status'] = 'Confirmed'
    print(info)
    client.publish(topic='%s/%s' % (ORDER_STATUS,
                                    info['Room']), payload=cipher(MESSAGE_DECRYPT_KEY, simplejson.dumps(info)))


mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

# set mosquitto broker password and username
mqtt_client.username_pw_set(username=USERNAME, password=PASSWORD)
# set TLS cert for the client
# mqtt_client.tls_set(ca_certs=TLS_CERT)

mqtt_client.loop_start()
mqtt_client.connect(host=MQTT_ADDR, port=MQTT_PRT)
while not mqtt_client.connected_flag:  # wait in loop
    print("In wait loop")
    time.sleep(1)
mqtt_client.subscribe(topic='%s/+' % FD_TOPIC)
mqtt_client.loop_forever()
mqtt_client.disconnect()
