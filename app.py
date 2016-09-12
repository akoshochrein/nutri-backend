import base64
import json
import os
import requests
import sys
import urllib

from apiclient.discovery import build
from flask import Flask, Response, request

app = Flask(__name__)

VALIDATION_TOKEN = os.environ.get('FB_VALDIATION_TOKEN') or 'test'
MESSENGER_PAGE_ACCESS_TOKEN = os.environ.get('MESSENGER_PAGE_ACCESS_TOKEN')
GOOGLE_VISION_API_KEY = os.environ.get('GOOGLE_VISION_API_KEY')

gvision = build('vision', 'v1', developerKey=GOOGLE_VISION_API_KEY)


@app.route('/healthcheck')
def healthcheck():
    return Response('OK', 200)


@app.route('/webhook', methods=['POST', 'GET'])
def webhook():
    if request.method == 'GET':
        return handle_get(request)
    elif request.method == 'POST':
        return handle_post(request)


def handle_get(request):
    mode = request.args.get('hub.mode')
    verify_token = request.args.get('hub.verify_token')

    response = Response(request.args.get('hub.challenge'), 200)
    if verify_token != VALIDATION_TOKEN:
        response = Response('', 403)

    return response


def handle_post(request):
    data = request.json

    if 'page' == data['object']:
        for page_entry in data['entry']:
            page_id = page_entry['id']
            timestamp = page_entry['time']

            for messaging_event in page_entry['messaging']:
                if messaging_event.get('optin'):
                    # Handle optin
                    pass
                elif messaging_event.get('message'):
                    message = messaging_event.get('message')
                    text = message.get('text', '')
                    attachments = message.get('attachments', [])

                    if attachments and attachments[0]['type'] == 'image':
                        opener = urllib.urlopen(attachments[0]['payload']['url'])
                        image_content = base64.b64encode(opener.read())
                        request = gvision.images().annotate(body={
                            'requests': [{
                                'image': {
                                    'content': image_content
                                },
                                'features': [{
                                    'type': 'LABEL_DETECTION',
                                    'maxResults': 4
                                }]
                            }]
                        })
                        api_response = request.execute()

                        text = attachments[0]['payload']['url']
                        if api_response.get('responses'):
                            descriptions = [annotation['description'] for annotation in api_response['responses'][0]['labelAnnotations']]

                            # text = 'I think you cannot eat that. Maybe show it to me from a different angle.'
                            # if 'food' not in descriptions:
                            text = ', '.join(descriptions)

                    respond(messaging_event['sender']['id'], text)
                elif messaging_event.get('delivery'):
                    # Handle message delivery
                    pass
                elif messaging_event.get('postback'):
                    # Handle postback
                    pass
                elif messaging_event.get('read'):
                    # Handle read
                    pass
                elif messaging_event.get('account_linking'):
                    # Handle account linking
                    pass
                else:
                    # Unknown message
                    pass

    return Response('', 200)


def respond(recipient_id, text):
    print recipient_id, text
    requests.post('https://graph.facebook.com/v2.6/me/messages?access_token={access_token}'.format(
        access_token=MESSENGER_PAGE_ACCESS_TOKEN
    ), data=json.dumps({
        'recipient': {
            'id': recipient_id,
        },
        'message': {
            'text': text,
            'metadata': 'DEVELOPER_DEFINED_METADATA'
        }
    }), headers={
        'content-type': 'application/json'
    })
