# -*- coding: utf-8 -*-
import logging
import ask_sdk_core.utils as ask_utils

# These imports are needed to communicate with the HTTP API
import requests
import json

# Needed to build a Custom skill
from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_core.utils import get_user_id
from ask_sdk_core.utils import get_device_id

# Contains definitions for creating a response with spoken text etc.
from ask_sdk_model import Response

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# This constant is points to the API URL without trailing the trailing slash
WEBSERVER_URL = lambda: 'https://d9144d3592a4.ngrok.io'



# This function is used to set the Do not Disturb to 'busy'
class SetBusyIntentHandler(AbstractRequestHandler):
    
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("SetBusyIntent")(handler_input)

    def handle(self, handler_input):
        
        # data is the JSON document which is sent to the API
        # it contains the alexaUserID and deviceID, as well as
        # a '1' which sets the busy to 'true'
        data = {
            "alexaUserID": get_user_id(handler_input), 
            "deviceID": get_device_id(handler_input),
            "status": "1"
        }
        
        # the JSON data is sent to the /alexa/changeStatus URL and the response is saved
        response = requests.post(WEBSERVER_URL() + '/alexa/changeStatus', json=data)
        
        # We evaluate the HTTP status code of the response. 200 means 'OK'
        if response.status_code == 200:
            speak_output = "Ich setze deinen Status nun auf beschäftigt."
        else:
            speak_output = "Die Antwort vom Server war ungültig."
        
        # We tell the Alexa device to tell the user the contents of 'speak_output'
        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )


# This function is called when the user wants to indicate that
# he is available again / not busy anymore
class SetAvailableIntentHandler(AbstractRequestHandler):
    
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("SetAvailableIntent")(handler_input)

    def handle(self, handler_input):
        
        # Equivalent to the data JSON document within SetBusyIntentHandler()
        # but this time 'status' is set to '0' indicating 'busy' is 'false'
        data = {
            "alexaUserID": get_user_id(handler_input), 
            "deviceID": get_device_id(handler_input),
            "status": "0"
        }
        
        # the JSON data is sent to the /alexa/changeStatus URL and the response is saved
        response = requests.post(WEBSERVER_URL() + '/alexa/changeStatus', json=data)
        
        # We evaluate the HTTP status code of the response. 200 means 'OK'
        if response.status_code == 200:
            speak_output = "Ich setze deinen Status nun auf verfügbar."
        else:
            speak_output = "Die Antwort vom Server war ungültig."

        # We tell the Alexa device to tell the user the contents of 'speak_output'
        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )


# This function is used to query the API for the current
# status of the user. I. E. whether or not he is busy.
class GetStatusIntentHandler(AbstractRequestHandler):
    
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("GetStatusIntent")(handler_input)

    def handle(self, handler_input):
        
        data = {
            "alexaUserID": get_user_id(handler_input), 
            "deviceID": get_device_id(handler_input)
        }
        
        # The data JSON document previously defined is sent to
        # /alexa/status this time, indicating that this is a query
        response = requests.post(WEBSERVER_URL() + '/alexa/status', json=data)
        
        if response.status_code == 200:
            response_data = json.loads(response.content.decode('utf-8'))
            
            # If the HTTP status code is 200 (OK) we will have received a json
            # document containing the current status. 1 equals 'busy', 0 available
            if response_data["status"] == 1:
                speak_output = "Aktuell scheinst du beschäftigt zu sein."
            elif response_data["status"] == 0:
                speak_output = "Aktuell scheinst du nicht beschäftigt zu sein."
            else:
                speak_output = "Es gibt ein Problem mit dem Server" # this should not happen
        else:
            speak_output = "Die Antwort vom Server war ungültig." # in case the Server didn't respond with 200

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )


# This function is used to get a 6-digit code from the API
# to allow the user to link the Alexa device on the website
class GetLinkingCodeIntentHandler(AbstractRequestHandler):
    
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("GetLinkingCodeIntent")(handler_input)

    def handle(self, handler_input):
        
        # The usual JSON document containing user id and device id
        data = {
            "alexaUserID": get_user_id(handler_input), 
            "deviceID": get_device_id(handler_input)
        }
        
        # The URL we send the JSON to is /alexa/register
        response = requests.post(WEBSERVER_URL() + '/alexa/register', json=data) 
        
        # The HTTP status code is checked
        # If it is okay, we extract the JSON content from the response and
        # make Alexa tell it the user
        if response.status_code == 200:
            response_data = json.loads(response.content.decode('utf-8'))
            speak_output = "Hier ist dein Code: " + response_data['alexaPin']
        # If for example the Alexa device is already registered, Alexa
        # will inform the user about the failure while retreiving a code.
        else:
            speak_output = "Die Antwort vom Server war ungültig."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )


# This function is called whenever a user launches the custom
# skill but does not immediately declare his intent.
class LaunchRequestHandler(AbstractRequestHandler):
    
    def can_handle(self, handler_input):
        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        speak_output = "Hallo, was kann ich für dich tun?"

        return (
            handler_input.response_builder
                .speak(speak_output)
                # ask() makes sure the user can answer with his intent and does not have have to relaunch the skill keeping the session open.
                .ask(speak_output) 
                .response
        )


# This function is called if a user asks the skill for help
# i. E. if he does not know what his options are.
class HelpIntentHandler(AbstractRequestHandler):
    
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        speak_output = "Du kannst deinen Status auf beschäftigt oder verfügbar setzen. Du kannst ihn auch abfragen. Wenn du dein Gerät verbinden moechtest kann ich dir einen code generieren"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


# This function is used if the skill is launched and waits for an intent (either through
# Launch- or HelpIntent) but the user wants to cancel the conversation.
class CancelOrStopIntentHandler(AbstractRequestHandler):
    
    def can_handle(self, handler_input):
        return (ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
                ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        speak_output = "Tschüss!"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )

# This function is called whenever the user launches the custom skill
# but the Alexa service is not able to map his utterance to an intent.
class FallbackIntentHandler(AbstractRequestHandler):
    
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("AMAZON.FallbackIntent")(handler_input)

    def handle(self, handler_input):
        logger.info("In FallbackIntentHandler")
        speech = "Hmm, ich weiss nicht so genau was ich mit dieser Aufforderung anfangen soll."
        reprompt = "Versuche einen anderen Befehl"

        return handler_input.response_builder.speak(speech).ask(reprompt).response


# This function is called whenever a conversation between user
# and the custom skill is terminated (for cleanup purposes etc.).
class SessionEndedRequestHandler(AbstractRequestHandler):
    
    def can_handle(self, handler_input):
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        return handler_input.response_builder.response


class IntentReflectorHandler(AbstractRequestHandler):
    """The intent reflector is used for interaction model testing and debugging.
    It will simply repeat the intent the user said. You can create custom handlers
    for your intents by defining them above, then also adding them to the request
    handler chain below.
    """
    def can_handle(self, handler_input):
        return ask_utils.is_request_type("IntentRequest")(handler_input)

    def handle(self, handler_input):
        intent_name = ask_utils.get_intent_name(handler_input)
        speak_output = "You just triggered " + intent_name + "."

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )

# This function is called if an exception happened in one of the handlers
# above (for example if a JSON parse failed). The error will be stored to
# CloudWatch Logfiles to be inspected by the developer.
class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Generic error handling to capture any syntax or routing errors. If you receive an error
    stating the request handler chain is not found, you have not implemented a handler for
    the intent being invoked or included it in the skill builder below.
    """
    def can_handle(self, handler_input, exception):
        return True

    def handle(self, handler_input, exception):
        logger.error(exception, exc_info=True)

        speak_output = "Mist, da ist ein Fehler passiert."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


# Down below we define the different kinds of handlers 
# we need to provide for our skill to work properly.
sb = SkillBuilder()

# These are our self-defined intents
sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(SetBusyIntentHandler())
sb.add_request_handler(GetStatusIntentHandler())
sb.add_request_handler(SetAvailableIntentHandler())
sb.add_request_handler(GetLinkingCodeIntentHandler())

# These are default intents required for Custom Skills
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(FallbackIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(IntentReflectorHandler())

sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()