import os
import json
import logging
from smarty.app import verify_address_freeform

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    # TODO implement
    logger.info('Testing logging by printing messages to cloudwatch logs')
    print(f'event is {event}, context is {context}')
    message = 'Address: {}'.format(event['street'])
    print(message)
    address = event['street']
    #json_region = os.environ['AWS_REGION']
    content = verify_address_freeform(address)
    print(f'content is {content}')

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": {
            "content": content
        }
    }

def error_handler(event, context):
    event_details = json.dumps(error=str(event)), 500
    raise Exception('Error Occured. Event: '+event_details)