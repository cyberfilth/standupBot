import slack
import os
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask, request, Response
from slackeventsapi import SlackEventAdapter

# Message counter, increments after each answer
global msgCounter
msgCounter = 1

# File contains environment variables
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

# Local server for testing
app = Flask(__name__)

# Channel used for testing
testChannel = ' '
# Username used for testing
testUser = ' '

# Redirect all Events to this URL
slack_event_adapter = SlackEventAdapter(
    os.environ['SIGNING_SECRET_'], '/slack/events', app)

# Canned questions
intro = ':alarm_clock: It\'s time for the *daily standup*.\nPlease share what you\'ve been working on.\n\n'
question1 = 'What will you do today?'
question2 = 'Anything blocking your progress?'
question3 = 'Anything you would like the team to know?'
outro = 'Awesome! Have a great day  :thumbsup:'
# Store the responses in these variables
global ans1
global ans2
global ans3


client = slack.WebClient(token=os.environ['SLACK_TOKEN_'])
BOT_ID = client.api_call("auth.test")['user_id']

# Post the welcome message
client.chat_postMessage(channel=testChannel, text=intro + question1)

# Event endpoint
@slack_event_adapter.on('message')
def message(payload):
    event = payload.get('event', {})
    channel_id = event.get('channel')
    user_id = event.get('user')
    answer = event.get('text')

    if BOT_ID != user_id:
        global msgCounter
        if msgCounter == 1:
            client.chat_postMessage(channel=channel_id, text=question2)
            global ans1
            ans1 = answer
            msgCounter += 1 
        elif msgCounter == 2:
            client.chat_postMessage(channel=channel_id, text=question3)
            global ans2
            ans2 = answer
            msgCounter += 1
        elif msgCounter == 3:
            client.chat_postMessage(channel=channel_id, text=outro)
            global ans3
            ans3 = answer
            # Post the results
            client.chat_postMessage(channel=testUser, text=ans1 + '\n' + ans2 + '\n' + ans3 )
            # Increment the counter once more to break the loop
            msgCounter += 1
        else:
            return

        

if __name__ == "__main__":
    app.run(debug=True)