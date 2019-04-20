# Sample code for Marriott Lecture
# Vanderbilt University
# Author: Marriott Lecture Group
#
#
# Codes in this file should be placed in a AWS Lambda function
# to handle incoming requests from AVS and return a response.
# Before returning a response, the handler should relay request
# information to Manager and store data into DynamoDB.
#
#
#   The scenario is pizza ordering through Alexa Echo
#   Communication Manner:
#       1. MQTT(Lambda listens responses from Manager): tcp://*.*.*.*:1883
#       2. Flask(Manager listens requests from Lambda): https://*.*.*.*:6000
#   Communication Security Issue:
#       1. MQTT: using public MQTT server
#       2. Flask: using http instead of https, with http header encryption
#       3. Include message encryption
#   Alexa handler is implemented using handler classes involved by the Alexa skill kit SDK(ask-sdk).
#
#
#   Expect Echo output: "Your pizza has been ordered, and please check
#   your email to see your receipt."
#
#

import boto3
import json
import requests
from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.utils import is_request_type, is_intent_name
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model import Response
from ask_sdk_model.ui import SimpleCard
from GlobalConstants import *
from MessageSecure import *


# Customer order processing logic
class CustomerOrderIntentHandler(AbstractRequestHandler):
    def parse_request(self, handler_input):
        """
        :param handler_input:
        :return: a request dict {intent_name: intent_value}
        """
        slots = handler_input.request_envelope.request.intent.slots
        request_dict = {}
        for slot in slots.values():
            request_dict.update({slot.name: slot.value})
        return request_dict

    def can_handle(self, handler_input):
        return is_intent_name("CustomerOrder")(handler_input)

    def handle(self, handler_input):
        # get slots values
        request_dict = parse_request(handler_input)
        # add order status (key, value) pair
        request_dict.update({'order status': 'pending'})

        # DynamoDB client
        client = boto3.resource('dynamodb')
        # get customer order table
        table = client.Table(DB_TABLE)

        # store data into DynamoDB
        table.put_item(item=request_dict)

        # send request to Manager using Flask
        encrypt_msg = cipher(key=MESSAGE_DECRYPT_KEY,
                             data=json.dumps(request_dict))

        response = requests.post(url='http://%s:%s/customer_order' %
                                 (MANAGER_ADDR, MANAGER_PRT), data=encrypt_msg)

        speech_text = response.text

        # set simple card for this request
        handler_input.response_builder.speak(speech_text).set_card(
            SimpleCard(SKILL, speech_text)).set_should_end_session(True)
        return handler_input.response_builder.response


# This function shows how to configure a handler to be invoked
# when the skill receives a LaunchRequest.
class LaunchRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        speech_text = HELP_TEXT

        # create a speech card for the request, which can be viewed from Alexa App
        handler_input.response_builder.speak(speech_text).set_card(
            SimpleCard(SKILL, speech_text)).set_should_end_session(False)
        return handler_input.response_builder.response


# Alexa built-in intent AMAZON.HelpIntent
class HelpIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        speech_text = HELP_TEXT

        handler_input.response_builder.speak(speech_text).ask(speech_text).set_card(
            SimpleCard(SKILL, speech_text))
        return handler_input.response_builder.response


class SessionEndedRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        return handler_input.response_builder.response


class CancelAndStopIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("AMAZON.CancelIntent")(handler_input) or is_intent_name("AMAZON.StopIntent")(handler_input)

    def handle(self, handler_input):
        speech_text = "Goodbye!"

        handler_input.response_builder.speak(speech_text).set_card(
            SimpleCard(SKILL, speech_text))
        return handler_input.response_builder.response


class AllExceptionHandler(AbstractExceptionHandler):
    def can_handle(self, handler_input, exception):
        return True

    def handle(self, handler_input, exception):
        print(exception)

        speech = "Sorry, I didn't get it. Can you please say it again!!"
        handler_input.response_builder.speak(speech).ask(speech)
        return handler_input.response_builder.response


sb = SkillBuilder()
sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(CustomerOrderIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelAndStopIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_exception_handler(AllExceptionHandler())

handler = sb.lambda_handler()
