import json
import os
import math
import dateutil.parser
import datetime
import time
import logging
import boto3
import requests

def get_slots(intent_request):
    return intent_request['currentIntent']['slots']

def close(session_attributes, fulfillment_state, message):
    response = {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Close',
            'fulfillmentState': fulfillment_state,
            'message': message
        }
    }
   
    return response

def dispatch(intent_request):
    #logger.debug('dispatch userId={}, intentName={}'.format(intent_request['userId'], intent_request['currentIntent']['name']))
    intent_name = intent_request['currentIntent']['name']
    return search_intent(intent_request)

    raise Exception('Intent with name ' + intent_name + ' not supported')

def search_intent(labels):

    
    url = 'https://search-photosindex-nhstcgewxc644dwhjtcaqel3zi.us-west-2.es.amazonaws.com/photos/_doc/_search?q='
    
    resp = []
    print(labels)
    for label in labels:
        if (label is not None) and label != '':
            url2 = url+label
            resp.append(requests.get(url2,headers={"Content-Type": "application/json"},auth=('admin', 'Admin@123')).json())
    print ("response: ")
    print(resp)
    output = []
    for r in resp:
        if 'hits' in r:
             for val in r['hits']['hits']:
                if 'objectkey' in val['_source']:
                    key = val['_source']['objectkey']
                    if key not in output:
                        output.append(key)
    print(output)

    return output
   
def lambda_handler(event, context):
    # TODO implement
    os.environ['TZ'] = 'America/New_York'
    time.tzset()
    print(event)
    client = boto3.client('lex-runtime')
    #logger.debug("In lambda")
    response_lex = client.post_text(
    botName='PhotoBot',
    botAlias="TestBot",
    userId="abhi1289",
    inputText= event["search_query"])
    print(response_lex)
    if 'slots' in response_lex:
        keys = [response_lex['slots'].get('KeyOne')]
        if(response_lex['slots'].get('KeyTwo')!=None):
            keys.append(response_lex['slots'].get('KeyTwo'))
        print(keys)
        pictures = search_intent(keys) #get images keys from elastic search labels
        response = {
            "statusCode": 200,
            "headers": { 'Access-Control-Allow-Headers' : 'Content-Type',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
},
            "body": json.dumps(pictures),
            "isBase64Encoded": False
        }
    else:
        response = {
            "statusCode": 200,
            "headers": {"Access-Control-Allow-Origin":"*","Content-Type":"application/json"},
            "body": [],
            "isBase64Encoded": False}
    return response