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
#   Communication Manner(Lambda Function to Manager):
#       1. MQTT: tcp://*.*.*.*:5000
#       2. Flask: https://*.*.*.*:6000
#   Communication Security Issue:
#       1. MQTT: using public MQTT server
#       2. Flask: using http instead of https, no http header encryption
#       3. No message encryption
#   Alexa handler is implemented using handler classes involved by the Alexa skill kit SDK(ask-sdk).
#
#
#   Expect Echo output: "Your pizza has been ordered, and please check
#   your email to see your receipt."
#
#

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.utils import is_request_type, is_intent_name
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model import Response
from ask_sdk_model.ui import SimpleCard


help_text = ""
skill = 'Customer Order'


# Customer order processing logic
class CustomerOrderIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("CustomerOrder")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speech_text = ""

        handler_input.response_builder.speak(speech_text).set_card(
            SimpleCard(skill, speech_text)).set_should_end_session(
            True)
        return handler_input.response_builder.response


# This function shows how to configure a handler to be invoked 
# when the skill receives a LaunchRequest. 
class LaunchRequestHandler(AbstractRequestHandler):
     def can_handle(self, handler_input):
         # type: (HandlerInput) -> bool
         return is_request_type("LaunchRequest")(handler_input)

     def handle(self, handler_input):
         # type: (HandlerInput) -> Response
         speech_text = help_text

        # create a speech card for the request, which can be viewed from Alexa App
         handler_input.response_builder.speak(speech_text).set_card(
            SimpleCard(skill, speech_text)).set_should_end_session(
            False)
         return handler_input.response_builder.response


# Alexa built-in intent AMAZON.HelpIntent
class HelpIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speech_text = help_text

        handler_input.response_builder.speak(speech_text).ask(speech_text).set_card(
            SimpleCard(skill, speech_text))
        return handler_input.response_builder.response


class SessionEndedRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        # any cleanup logic goes here

        return handler_input.response_builder.response


class CancelAndStopIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("AMAZON.CancelIntent")(handler_input) or is_intent_name("AMAZON.StopIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speech_text = "Goodbye!"

        handler_input.response_builder.speak(speech_text).set_card(
            SimpleCard(skill, speech_text))
        return handler_input.response_builder.response


class AllExceptionHandler(AbstractExceptionHandler):
    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        # Log the exception in CloudWatch Logs
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