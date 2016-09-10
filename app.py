from flask import Flask, Response
app = Flask(__name__

VALIDATION_TOKEN = ''


@app.route('/webhook')
def webhook():
    if request.method == 'GET':
        return handle_get(request)
    elif request.method == 'POST':
        return handle_post(request)
    else:
        # Bad request
        pass
    return 'Hello, World!'


def handle_get(request):
    mode = request.args.get('hub.mode')
    verify_token = request.args.get('hub.verify_token')

    response = Response(request.args.get('hub.challenge'), 200)
    if verify_token != VALIDATION_TOKEN:
        response = Response('', 403)

    return response


def handle_post(request):
    data = request.form

    if 'page' == data['object']:
        for page_entry in data['entry']:
            page_id = page_entry['id']
            timestamp = page_entry['time']

            for messaging_event in page_entry['messaging']:
                if messaging_event.get('optin'):
                    # Handle optin
                    pass
                elif messaging_event.get('message'):
                    # Handle message
                    pass
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
