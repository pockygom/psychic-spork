# -*- coding: utf-8 -*-
# Alert/Info Bot v0.0
# Probably better to implement using a class
# John Song
# May 31 2017

from slackclient import SlackClient
import sys
import os
import info
from datetime import datetime, timedelta
from time import sleep

# Slack Token for app
token = os.environ.get('SLACK_TOKEN')
sc = SlackClient(token)

# Slack Token for bot
bot_token = os.environ.get('SLACK_BOT_TOKEN')
sc_bot = SlackClient(bot_token)

# Connect to RTM
while True:
	print('Connecting...')
	if sc_bot.rtm_connect():
		print('Connected!')
		break

msg_interval = 60 # Seconds

# Function for sendng message/attachments
def send_msg(message, attachment, chan, now):
	# Send message to Slack
	if not isinstance(message,str):
		message = 'Error: Message not a string'
	if not attachment:
		sc.api_call('chat.postMessage', asuser=True, channel=chan, text=message)
	else:
		sc.api_call('chat.postMessage', asuser=True, channel=chan, text=message, attachments=attachment)
	print('Sending message...')

	# Record the time that the message was sent
	send_time = datetime.now()
	send_time = send_time - timedelta(microseconds=now.microsecond)

	# Wait until message interval passes (prevent spam)
	time_into_minute = (send_time - now).seconds
	if time_into_minute < msg_interval: # Wait until next second
		wait_time = msg_interval - time_into_minute
		print('Waiting for ' + str(wait_time) + ' seconds until next command.')
		sleep(wait_time)
	return(send_time)

# Some initializers
event_list = []

while True:
	# Current time (MM/DD/YYYY HH:mm)
	now = datetime.now()
	now = now - timedelta(seconds=now.second,
		microseconds=now.microsecond)

	# Event alerts
	if event_list:
		alert_list, event_list = info.event_alerts(event_list, now)
		if alert_list:
			msg, att = info.compose_event_message(alert_list, now)
			send_time = send_msg(msg, att, info.chan, now)
			print('Alert sent at %s' % str(send_time))

	# Parse channel messages
	rcvd_call = ['-1']
	rcvd = sc_bot.rtm_read()

	for call in rcvd:
		if call['type'] == 'message':
			rcvd_call = call['text'].split()
			command = rcvd_call[0]
			command_tags = rcvd_call[1:]

			# List of commands
			if command == '!parse':
				print('Parsing list of upcoming events with the following tags: %s.' % command_tags)
				event_calender, event_list = info.event_parse(command_tags, now)
				parse_msg = 'Parsing complete. Includes events with the following tags: %s.' % command_tags
				_, att = info.compose_event_message(event_list, now)
				_ = send_msg(parse_msg, att, info.chan, now)
				event_calender, event_list = info.update_event_list(event_calender, command_tags, now)

			elif command == '!events':
				print('Sending upcoming event list.')
				msg, att = info.compose_event_message(event_list, now)
				_ = send_msg(msg, att, info.chan, now)

			elif command == '!alert':
				print('Sending log of recent latency alerts.')
				send_msg(msg, att, alert.chan, now)

	# Kill command
	if rcvd_call == 'Kill Alert Bot!':
		print('Killed')
		break
