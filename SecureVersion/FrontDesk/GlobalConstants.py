# ##############################
# Alexa related constants
SKILL = 'Customer Order'
HELP_TEXT = "Welcome to Marriott. You can ask me to order foods for you, we have pizza, buger and sandwich."

# ##############################
# AWS Lambda related constants
FD_TOPIC = 'CustomerOrder'
ORDER_STATUS = 'OrderStatus'

# ##############################
# Communication Layer Constants
# ############ MQTT ############
MQTT_ADDR = 'ec2-52-12-116-79.us-west-2.compute.amazonaws.com'
MQTT_PRT = 8883

USERNAME = 'zhuangwei'
PASSWORD = 'kzw123'

TLS_CERT = 'ca.crt'

# ######## Manager ############

MANAGER_ADDR = 'ec2-52-12-116-79.us-west-2.compute.amazonaws.com'
MANAGER_PRT = '5000'

MESSAGE_DECRYPT_KEY = 'kzw123'

# ##############################
# DynamoDB Constants
REGION = 'us-west-2'
END_POINT = 'dynamodb.us-west-2.amazonaws.com'
DB_TABLE = 'Customer_Order'
PRICE_TABLE = 'Foods_Price'
