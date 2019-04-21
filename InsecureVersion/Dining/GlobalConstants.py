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
MQTT_ADDR = 'ec2-54-188-117-8.us-west-2.compute.amazonaws.com'
MQTT_PRT = 1883

MANAGER_ADDR = 'ec2-54-188-117-8.us-west-2.compute.amazonaws.com'
MANAGER_PRT = '5000'

# ##############################
# DynamoDB Constants
REGION = 'us-west-2'
END_POINT = 'dynamodb.us-west-2.amazonaws.com'
DB_TABLE = 'Customer_Order'
PRICE_TABLE = 'Foods_Price'
