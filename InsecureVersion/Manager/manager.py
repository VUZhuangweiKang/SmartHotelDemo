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

import boto3
import time
import datetime
from paho.mqtt.client import Client
from flask import Flask, request
from GlobalConstants import *


# The boto3 dynamoDB resource
dynamodb_resource = boto3.resource('dynamodb')
db_client = boto3.client(service_name='dynamodb')

mqtt_client = None
app = Flask(__name__)


def print_receipt(body):
    receipt = 'Customer Receipt\n' \
              'Room: %s\n' \
              'Item: %s\n' \
              'Size: %s\n' \
              'Price: $10' \
              'Ordered Time: %s' % (body['room'],
                                    body['foods'],
                                    body['size'],
                                    str(datetime.datetime.now()))
    print(receipt)
    return receipt


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        mqtt_client.connected_flag = True
    else:
        mqtt_client.connected_flag = False


def mqtt_responder():
    global mqtt_client
    Client.connected_flag = False
    mqtt_client = Client()
    mqtt_client.on_connect = on_connect
    mqtt_client.loop_start()
    mqtt_client.connect(host=MQTT_ADDR, port=MQTT_PRT)
    while not mqtt_client.connected_flag:  # wait in loop
        print("In wait loop")
        time.sleep(1)
    mqtt_client.loop_forever()
    mqtt_client.disconnect()


@app.route('/customer_order', methods=['POST'])
def handler():
    json_body = request.get_json()
    # use table
    table = dynamodb_resource.Table(DB_TABLE)
    # update order status
    json_body['order status'] = 'ordered'
    table.put_item(Item=json_body)

    time.sleep(0.3)

    receipt = print_receipt(json_body)

    # respond Lambda using MQTT
    mqtt_client.publish(topic='%s/%s' % (MANAGER_RSP_TOPIC, json_body['room']), payload=receipt)

    return 200, 'OK'


if __name__ == '__main__':
    mqtt_responder()
    app.run(host=MANAGER_ADDR, port=MANAGER_PRT, debug=True)
