#!/usr/bin/env python
#
# This demo app shows how to use the Nylas client to authenticate against
# the Nylas API and how to fetch emails from an authenticated account.
#
# NOTE: This app does NOT use SSL. Before deploying this code to a
# server environment, you should ENABLE SSL to avoid exposing your API
# access token in plaintext.
#
# To run this demo app:
# 1. Save this file to your computer as `server.py`
#
# 2. In the Nylas Developer Portal, create a new application. Replace the
#    APP_ID and APP_SECRET variables below with the App ID and App
#    Secret of your application.
#    https://nylas.com/
#
# 3. In the Nylas Developer Portal, edit your application and add the
#    callback URL: http://localhost:8888/login_callback
#
# 4. On the command line, `cd` to the folder where you saved the file
#
# 5. On the command line, run `python ./server.py`
#    - You may need to install Python: https://www.python.org/download/
#    - You may need to install dependencies using pip:
#      (http://pip.readthedocs.org/en/latest/installing.html)
#      pip install nylas flask requests
#    - Note: You may want to set up a virtualenv to isolate these
#      dependencies from other packages on your system. Otherwise, you
#      will need to sudo pip install, to install them globally.
#      http://docs.python-guide.org/en/latest/dev/virtualenvs/
#
# 6. In the browser, visit http://localhost:8888/
#

import time
from flask import Flask, url_for, session, request, redirect, Response

from nylas import APIClient

APP_ID = 'YOUR_APP_ID'
APP_SECRET = 'YOUR_APP_SECRET'

app = Flask(__name__)
app.debug = True
app.secret_key = 'secret'

assert APP_ID != 'YOUR_APP_ID' or APP_SECRET != 'YOUR_APP_SECRET',\
    "You should change the value of APP_ID and APP_SECRET"


@app.route('/')
def index():
    # If we have an access_token, we may interact with the Nylas Server
    if 'access_token' in session:
        client = APIClient(APP_ID, APP_SECRET, session['access_token'])
        message = None
        while not message:
            try:
                # Get the latest message from namespace zero.
                message = client.messages.first()
                if not message:  # A new account takes a little time to sync
                    print "No messages yet. Checking again in 2 seconds."
                    time.sleep(2)
            except Exception as e:
                print(e.message)
                return Response("<html>An error occurred.</html>")
        # Format the output
        text = "<html><h1>Here's a message from your inbox:</h1><b>From:</b> "
        for sender in message["from"]:
            text += "{} &lt;{}&gt;".format(sender['name'], sender['email'])
        text += "<br /><b>Subject:</b> " + message.subject
        text += "<br /><b>Body:</b> " + message.body
        text += "</html>"

        # Return result to the client
        return Response(text)
    else:
        # We don't have an access token, so we're going to use OAuth to
        # authenticate the user

        # Ask flask to generate the url corresponding to the login_callback
        # route. This is similar to using reverse() in django.
        redirect_uri = url_for('.login_callback', _external=True)

        client = APIClient(APP_ID, APP_SECRET)
        return redirect(client.authentication_url(redirect_uri))


@app.route('/login_callback')
def login_callback():
    if 'error' in request.args:
        return "Login error: {0}".format(request.args['error'])

    # Exchange the authorization code for an access token
    client = APIClient(APP_ID, APP_SECRET)
    code = request.args.get('code')
    session['access_token'] = client.token_for_code(code)
    return index()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8888)
