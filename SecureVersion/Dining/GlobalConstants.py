# ##############################
# Alexa related constants
SKILL = 'Customer Order'
HELP_TEXT = "Welcome to Marriott. You can ask me to order foods for you, we have pizza, burger and sandwich."

# ##############################
# AWS Lambda related constants
FD_TOPIC = 'CustomerOrder'
ORDER_STATUS = 'OrderStatus'

# ##############################
# Communication Layer Constants
# ############ MQTT ############
MQTT_ADDR = '54.71.236.142'
MQTT_PRT = 8883

USERNAME = 'zhuangwei'
PASSWORD = 'kzw123'

TLS_CERT = 'ca.crt'

# ######## Manager ############

MANAGER_ADDR = '54.71.236.142'
MANAGER_PRT = '5000'

MESSAGE_DECRYPT_KEY = '123456789'

# ##############################
# DynamoDB Constants
REGION = 'us-west-2'
END_POINT = 'dynamodb.us-west-2.amazonaws.com'
DB_TABLE = 'Customer_Order'
PRICE_TABLE = 'Foods_Price'
