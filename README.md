# Inbox Python bindings

Python bindings for Inbox, the next-generation email platform.

## Installation

This library is available on pypi. You can install it by running `pip install inbox-python`.

##Requirements

- requests 

## Examples

There's an example flask app in the `examples` directory. You can run the sample app to see how an authentication flow might be implemented. 

*Note: you will need to replace the APP_ID and APP_SECRET with your Inbox App ID and secret to use the sample app.*

## Usage

### App ID and Secret

Before you can interact with the Inbox API, you need to register for the Inbox Developer Program at [http://www.inboxapp.com/](http://www.inboxapp.com/). After you've created a developer account, you can create a new application to generate an App ID / Secret pair.

Generally, you should store your App ID and Secret into environment variables to avoid adding them to source control. That said, in the example project and code snippets below, the values are hardcoded for convenience.


### Authentication

The Inbox API uses server-side (three-legged) OAuth, and this library provides convenience methods to simplify the OAuth process.
Here's how it works:

1. You redirect the user to our login page, along with your App Id and Secret
2. Your user logs in
3. She is redirected to a callback URL of your own, along with an access code
4. You use this access code to get an authorization token to the API

For more information about authenticating with Inbox, visit the [Developer Documentation](https://www.inboxapp.com/docs/gettingstarted-hosted#authenticating).

In practice, the Inbox client simplifies this down to two steps.

**Step 1: Redirect the user to Inbox:**

```python
from flask import Flask, session, request, redirect, Response
from inbox import APIClient

@app.route('/')
def index():
    redirect_url = "http://0.0.0.0:8888/login_callback"
    client = APIClient(APP_ID, APP_SECRET)
    return redirect(client.authentication_url(redirect_uri))

```

**Step 2: Handle the Authentication Response:**

```python
@app.route('/login_callback')
def login_callback():
    if 'error' in request.args:
        return "Login error: {0}".format(request.args['error'])

    # Exchange the authorization code for an access token
    client = APIClient(APP_ID, APP_SECRET)
    code = request.args.get('code')
    session['access_token'] = client.auth_code_for_token(code)
```

### Fetching Namespaces

```python
inbox = APIClient(APP_ID, APP_SECRET, token)

# Get the first namespace
namespace = inbox.namespaces.first()

# Print out the email address and provider (Gmail, Exchange)
print namespace.email_address
print namespace.provider
```


### Fetching Threads

```python
# Fetch the first thread
thread = namespace.threads.first()

# Fetch a specific thread
thread = namespace.threads.find('ac123acd123ef123')

# List all threads tagged `inbox`
# (paginating 50 at a time until no more are returned.)
for thread in namespace.threads.items():
    print thread.subject

# List the 5 most recent unread threads
for thread in namespace.threads.where(tag='unread').items():
    print thread.subject

# List all threads with 'ben@inboxapp.com'
for thread in namespace.threads.where(any_email='ben@inboxapp.com').items():
    print thread.subject
```


### Working with Threads

```python
# List thread participants
for participant in thread.participants:
    print participant["email"]

# Mark as read
thread.mark_as_read()

# Archive
thread.archive()

# Unarchive
thread.unarchive()

# Add or remove arbitrary tags
tagsToAdd = ['inbox', 'cfa1233ef123acd12']
tagsToRemove = []
thread.update_tags(tagsToAd, tagsToRemove)

# List messages
for message in thread.messages.items():
    print message.subject
```


### Working with Files

```python
# List files
for file in namespace.files:
    print file.filename

# Create a new file - not yet implemented
```

### Working with Messages, Contacts, etc.

Each of the primary collections (contacts, messages, etc.) behave the same way as `threads`. For example, finding messages with a filter is similar to finding threads:

```python
messages = namespace.messages.where(to='ben@inboxapp.com`)
```

The `where` method accepts a hash of filters, as documented in the [Inbox Filters Documentation](https://www.inboxapp.com/docs/api#filters). 

### Creating and Sending Drafts

```python
# Create a new draft
draft = namespace.new_draft(
    {"to": [{"name": 'Ben Gotow', "email": 'ben@inboxapp.com'}],
     "subject": 'Sent by Ruby',
      "body": 'Hi there!<strong>This is HTML</strong>'
    })

# Modify attributes as necessary
draft.cc = [{:name => 'Michael', :email => 'mg@inboxapp.com'}]

# Add the file we uploaded as an attachment
draft.attach(file)

# Save the draft
draft = draft.save()

# Send the draft. This method returns immediately and queues the message
# with Inbox for delivery through the user's SMTP gateway.
draft.send()
```

## Open-Source Sync Engine

The [Inbox Sync Engine](http://github.com/inboxapp/inbox) is open-source, and you can also use the Ruby gem with the open-source API. Since the open-source API provides no authentication or security, connecting to it is simple. When you instantiate the Inbox object, provide nil for the App ID, App Secret, and API Token, and pass the fully-qualified address to your copy of the sync engine:

```python
from inbox import APIClient
inbox = APIClient(None, None, None, 'http://localhost:5555/')
```


## Contributing

We'd love your help making Inbox better. Join the Google Group for project updates and feature discussion. We also hang out in `##inbox` on [irc.freenode.net](http://irc.freenode.net), or you can email [help@inboxapp.com](mailto:help@inboxapp.com).

Please sign the Contributor License Agreement before submitting pull requests. (It's similar to other projects, like NodeJS or Meteor.)