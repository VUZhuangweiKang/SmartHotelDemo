# Sample code for Marriott Lecture
# Vanderbilt University
# Author: Marriott Lecture Group
#
# This file is for Secure Version of Manager in the architecture, whose responsibility is receiving
# customer requests sent from Lambda Function.
#
#
#   The scenario is pizza ordering through Alexa Echo
#   Communication Manner:
#       1. MQTT(Lambda listens responses from Manager): tcp://*.*.*.*:1883
#       2. Flask(Manager listens requests from Lambda): https://*.*.*.*:6000
#   Communication Security Issue:
#       1. MQTT: using public MQTT server with username & password access control and TLS encrypted connection and AES
#               message encryption
#       2. Flask: using https instead, with http header encryption
#       3. Included message encryption
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
from MessageSecure import *
from FlaskSSLSecure import *

# The boto3 dynamoDB resource
dynamodb_resource = boto3.resource('dynamodb', region_name=REGION)

mqtt_client = None
order_status_flag = False
order_status = None
app = Flask(__name__)


def init_price_table():
    foods_price = [
        {
            'Foods': 'pizza',
            'Size': 'small',
            'Price': 10
        },
        {
            'Foods': 'burger',
            'Size': 'small',
            'Price': 20
        },
        {
            'Foods': 'sandwich',
            'Size': 'small',
            'Price': 30
        }
    ]
    price_table = dynamodb_resource.Table(PRICE_TABLE)
    for itemm in foods_price:
        price_table.put_item(Item=itemm)


def print_receipt(body):
    print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
    body.update({'Order Time': str(datetime.datetime.now())})
    print(body)
    print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
    return body


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        mqtt_client.connected_flag = True
    elif rc == 5:
        print('Connection Rejected')
        mqtt_client.connected_flag = False
    else:
        mqtt_client.connected_flag = False


def on_message(client, userdata, message):
    global order_info, order_status_flag
    order_info = decrypt(MESSAGE_DECRYPT_KEY, message.payload)
    order_status_flag = True
    # update order status in dynamodb
    table = dynamodb_resource.Table(DB_TABLE)
    table.put_item(Item=simplejson.loads(order_info))


def mqtt_handler():
    global mqtt_client
    Client.connected_flag = False
    mqtt_client = Client()

     # set mosquitto broker password and username
    mqtt_client.username_pw_set(username=USERNAME, password=PASSWORD)
    # set TLS cert for the client
    # mqtt_client.tls_set(ca_certs=TLS_CERT)
    
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    mqtt_client.loop_start()
    mqtt_client.connect(host=MQTT_ADDR, port=MQTT_PRT)
    while not mqtt_client.connected_flag:  # wait in loop
        print("In wait loop")
        time.sleep(1)
    mqtt_client.subscribe(topic='%s/+' % ORDER_STATUS)
    mqtt_client.loop_forever()
    mqtt_client.disconnect()


@app.route('/customer_order', methods=['POST'])
@require_appkey
def handler():
    global order_status_flag
    json_body = request.get_data()

    json_body = simplejson.loads(decrypt(key=MESSAGE_DECRYPT_KEY, data=json_body))

    # use table
    table = dynamodb_resource.Table(DB_TABLE)
    # update order status
    json_body['Order Status'] = 'Processing'

    price_table = dynamodb_resource.Table(PRICE_TABLE)

    json_body.update({
        'Price': price_table.scan(FilterExpression=Attr('Foods').eq(json_body['Foods']) & Attr('Size').eq(json_body['Size']))['Items'][0]['Price']
    })

    table.put_item(Item=json_body)

    # print customer receipt
    receipt = print_receipt(json_body)

    # respond Lambda using MQTT, payload is encrypted
    encrypted_payload = cipher(
        key=MESSAGE_DECRYPT_KEY, data=simplejson.dumps(receipt))
    mqtt_client.publish(topic='%s/%s' %
                        (FD_TOPIC, json_body['Room']), payload=encrypted_payload)
    while not order_status_flag:
        time.sleep(1)
    order_status_flag = False

    return order_status, 200


if __name__ == '__main__':
    init_price_table()
    mqtt_thr = Thread(target=mqtt_handler, daemon=True)
    mqtt_thr.start()
    app.run(host=MANAGER_ADDR, port=MANAGER_PRT, debug=True, ssl_context=context)
