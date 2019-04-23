# Insecure Version of Marriott Lecture Example Application
# Vanderbilt University
# Author: Marriott Lecture Group
#
# This file is for FrontDesk in the architecture, whose responsibility is receiving
# customer requests sent from Lambda Function, generating order receipt, and notify Dining.
#
#
#   The scenario is pizza ordering through Alexa Echo
#   Communication Manner:
#       1. MQTT(Communication between FrontDesk and Dining): tcp://*.*.*.*:1883
#       2. Flask(Communication between Lambda and FrontDesk): http://*.*.*.*:5000
#

import boto3
from boto3.dynamodb.conditions import Key, Attr
import time
import simplejson
import datetime
from threading import Thread
from paho.mqtt.client import Client
from flask import Flask, request
from GlobalConstants import *


# The boto3 dynamoDB resource
dynamodb_resource = boto3.resource('dynamodb', region_name=REGION)

mqtt_client = None
order_status_flag = False
order_info = None
app = Flask(__name__)


def init_price_table():
    foods_price = [
        {
            'Foods': 'pizza',
            'Price': {
                'small': 10,
                'medium': 20,
                'large': 30
            }
        },
        {
            'Foods': 'burger',
            'Price': {
                'small': 5,
                'medium': 10,
                'large': 15
            }
        },
        {
            'Foods': 'sanwich',
            'Price': {
                'small': 7,
                'medium': 9,
                'large': 13
            }
        }
    ]
    price_table = dynamodb_resource.Table(PRICE_TABLE)
    for item in foods_price:
        price_table.put_item(Item=item)

# Print Cutomer Receipt
def print_receipt(body):
    print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
    print(body)
    print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
    return body

# MQTT connect callback function
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        mqtt_client.connected_flag = True
    else:
        mqtt_client.connected_flag = False


# MQTT callback function when receive messge
def on_message(client, userdata, message):
    global order_info, order_status_flag
    order_status_flag = True
    order_info = message.payload
    # update order status in dynamodb
    table = dynamodb_resource.Table(DB_TABLE)
    table.put_item(Item=simplejson.loads(order_info))


def mqtt_handler():
    global mqtt_client
    Client.connected_flag = False
    mqtt_client = Client()
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    mqtt_client.loop_start()
    mqtt_client.connect(host=MQTT_ADDR, port=MQTT_PRT)
    while not mqtt_client.connected_flag:  # wait in loop
        print("In wait loop")
        time.sleep(1)

    # subscribe all rooms, using MQTT single layer wildcard
    mqtt_client.subscribe(topic='%s/+' % ORDER_STATUS)
    mqtt_client.loop_forever()
    mqtt_client.disconnect()


# Define REST function
@app.route('/customer_order', methods=['POST'])
def handler():
    global order_status_flag
    json_body = request.get_json()
    
    # use table
    table = dynamodb_resource.Table(DB_TABLE)
    # update order status
    json_body['Order_Status'] = 'Processing'

    price_table = dynamodb_resource.Table(PRICE_TABLE)

    price = price_table.query(KeyConditionExpression=Key('Foods').eq(json_body['Foods']))['Items'][0]['Price'][json_body['Size']]

    json_body.update({
        'Price': price
    })

    table.update_item(
        Key={
            'Order Time': json_body['Order Time'],
            'Room': json_body['Room']
        },
        UpdateExpression="set Order_Status = :os, Price = :p",
        ExpressionAttributeValues={
            ':os': 'Processing',
            ':p': price
        },
        ReturnValues="UPDATED_NEW"
    )

    # print customer receipt
    receipt = print_receipt(json_body)

    # publish order information to Dining
    mqtt_client.publish(topic='%s/%s' % (FD_TOPIC,
                                         json_body['Room']), payload=simplejson.dumps(receipt))
    
    # wait until received response from Dining
    while not order_status_flag:
        time.sleep(1)
    order_status_flag = False

    return order_info, 200


if __name__ == '__main__':
    init_price_table()
    mqtt_thr = Thread(target=mqtt_handler, daemon=True)
    mqtt_thr.start()
    app.run(host=MANAGER_ADDR, port=MANAGER_PRT, debug=True)
