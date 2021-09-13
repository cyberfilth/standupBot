import slack
import os
from pathlib import Path
from dotenv import load_dotenv
# Flask is only used for testing locally
from flask import Flask
from slackeventsapi import SlackEventAdapter
# File containing users
from userlist import usualSuspects

# Message counter, increments after each answer
global msgCounter
msgCounter = 1

# File contains environment variables
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

# Local server for testing
app = Flask(__name__)

# Output channel used for testing
testChannel = ''

# Redirect all Events to this URL
slack_event_adapter = SlackEventAdapter(
    os.environ['SIGNING_SECRET_'], '/slack/events', app)

# Canned questions
intro = '\n:alarm_clock: It\'s time for the *daily standup*.\nPlease share what you\'ve been working on.\n\n'
question1 = 'What will you do today?'
question2 = 'Anything blocking your progress?'
question3 = 'Anything you would like the team to know?'
outro = 'Awesome! Have a great day  :thumbsup:'

# Slack token
client = slack.WebClient(token=os.environ['SLACK_TOKEN_'])
# Bot ID, to stop it talking to itself
BOT_ID = client.api_call("auth.test")['user_id']

# Event endpoint that catches responses
@slack_event_adapter.on('message')
def message(payload):
    event = payload.get('event', {})
    channel_id = event.get('channel')
    user_id = event.get('user')
    answer = event.get('text')

    # Check the event wasn't triggered by the bot
    if BOT_ID != user_id:

        # for respondentID, loop through dictionary until user_id matches Username        
        for k in range(2):
            print('getting id')
            if user_id == usualSuspects[k]['userName']:
                thisID = usualSuspects[k]['id']
 

        if usualSuspects[thisID]['msgCounter'] == 1:
            client.chat_postMessage(channel=channel_id, text=question2)
            usualSuspects[thisID]['answer1'] = answer
            usualSuspects[thisID]['msgCounter'] = 2

        elif usualSuspects[thisID]['msgCounter'] == 2:
            client.chat_postMessage(channel=channel_id, text=question3)
            usualSuspects[thisID]['answer2'] = answer
            usualSuspects[thisID]['msgCounter'] = 3

        elif usualSuspects[thisID]['msgCounter'] == 3:
            client.chat_postMessage(channel=channel_id, text=outro)
            usualSuspects[thisID]['answer3'] = answer
            # Increment the counter once more to break the loop
            usualSuspects[thisID]['msgCounter'] = 4


            # Get display name
            r = client.users_info(user=user_id)
            dispName = r['user']['profile']['display_name']

             # Post the results
            if usualSuspects[thisID]['answer2'].lower() and usualSuspects[thisID]['answer3'].lower() !='no':
                client.chat_postMessage(channel=testChannel, text=':robot_face: *' + dispName + '* posted an update for *Daily Standup*\n' + '*' + question1 + '*' + '\n>' + usualSuspects[thisID]['answer1'] + '\n' + '*' + question2 +'*' + '\n>' + usualSuspects[thisID]['answer2'] + '\n' + '*' + question3 + '*' + '\n>' + usualSuspects[thisID]['answer3'] + '\n\n---')
            elif usualSuspects[thisID]['answer2'].lower() != 'no' and usualSuspects[thisID]['answer3'].lower() == 'no':
                client.chat_postMessage(channel=testChannel, text=':robot_face: *' + dispName + '* posted an update for *Daily Standup*\n' + '*' + question1 + '*' + '\n>' + usualSuspects[thisID]['answer1'] + '\n' + '*' + question2 +'*' + '\n>' + usualSuspects[thisID]['answer2'] + '\n\n---')
            else:
                client.chat_postMessage(channel=testChannel, text=':robot_face: *' + dispName + '* posted an update for *Daily Standup*\n' + '*' + question1 + '*' + '\n>' + usualSuspects[thisID]['answer1'] + '\n\n---')

        else:
            return

# Reset each msgCounter at program start
for x in range(2):
    usualSuspects[x]['msgCounter'] == 1
    client.chat_postMessage(channel=usualSuspects[x]['userName'], text=intro + question1)


if __name__ == "__main__":
    app.run(debug=True)
