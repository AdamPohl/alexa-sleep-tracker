from flask_ask import Ask, statement, question, context
from datetime import datetime
from random import randint
from flask import Flask
# import logging
import boto3

app = Flask(__name__)
ask = Ask(app, '/')
# logging.getLogger("flask_ask").setLevel(logging.DEBUG)

unit_type = ''
target = 0


def database():
	dynamodb = boto3.resource('dynamodb', region_name='eu-west-1')
	table = dynamodb.Table('SleepTrackerData')
	return table


def display_type():
	display = None

	if "Viewport" in context:
		display = context.Viewport.shape

	return display


@ask.launch
def welcome():
	display = display_type()
	msg = "Hell and welcome to sleep tracker, how can I help you today?"

	render_msg = question(msg)

	if display:
		render_msg = render_msg.display_render(
			template="BodyTemplate1",
			title="Sleep Tracker",
			backButton="VISIBLE",
			text={
				"primaryText": {
					"type": "RichText",
					"text": msg
				}
			}
		)

	return render_msg

@ask.intent("BedtimeIntent")
def bedtime_intent():
	table = database()
	display = display_type()

	item = {
		'userID': str(context.System.user.userId),
		'bedTime': str(datetime.now()).split('.')[0]
	}

	table.put_item(
		Item=item
	)

	options = [
		"have a good sleep.",
		"don't let the bed bugs bite.",
		"sweet dreams!",
		"may you count less than 10 sheep tonight.",
		"Sleep well, cause you will need your strength when you wake."
	]

	msg = "Thanks, {}".format(options[randint(0, 4)])

	render_msg = statement(msg)

	if display:
		render_msg = render_msg.display_render(
			template="BodyTemplate1",
			title="Sleep Tracker",
			backButton="VISIBLE",
			text={
				"primaryText": {
					"type": "RichText",
					"text": msg
				}
			}
		)

	return render_msg


@ask.intent("AwakeIntent")
def awake_intent():
	table = database()
	display = display_type()

	awake = datetime.now()

	try:
		response = table.get_item(
			Key={
				'userID': str(context.System.user.userId)
			}
		)

		bedtime = datetime.strptime(response['Item']['bedTime'], '%Y-%m-%d %H:%M:%S')

		time = str(awake - bedtime).split('.')[0].split(':')

		amount = "{} hours, {} minutes and {} seconds".format(time[0], time[1], time[2])

		table.update_item(
			Key={
				'userID': str(context.System.user.userId)
			},
			UpdateExpression='SET bedTime = :val1',
			ExpressionAttributeValues={
				':val1': "N/A",
			}
		)
	except Exception:
		return error('Response')

	options = [
		"Have a good day.",
		"Go forth and live your best life.",
		"Have a great day and try to do at least one thing that scares you.",
		"Good luck, I sense today will be a big day for you.",
		"May you achieve all that you set out to do today."
	]

	msg = "Thanks, you just slept for {}. {}".format(amount, options[randint(0, 4)])

	render_msg = statement(msg)

	if display:
		render_msg = render_msg.display_render(
			template="BodyTemplate1",
			title="Sleep Tracker",
			backButton="VISIBLE",
			text={
				"primaryText": {
					"type": "RichText",
					"text": msg
				}
			}
		)

	return render_msg


@ask.intent("AMAZON.HelpIntent")
def help_intent():
	display = display_type()
	msg = """Hi there, with this skill you can track your sleep, when you go to bed you let me know by saying something
	like this: I'm going to bed now, and when you wake up you say something like this: I just woke up, and I will tell
	you how long you slept for. What would you like to do?"""

	render_msg = question(msg)

	if display:
		render_msg = render_msg.display_render(
			template="BodyTemplate1",
			title="Sleep Tracker",
			backButton="VISIBLE",
			text={
				"primaryText": {
					"type": "RichText",
					"text": msg
				}
			}
		)

	return render_msg


@ask.intent("AMAZON.StopIntent")
def stop_intent():
	display = display_type()
	msg = 'Goodbye! Thanks for using Sleep Tracker.'
	render_msg = statement(msg)

	if display:
		render_msg = render_msg.display_render(
			template="BodyTemplate1",
			title="Sleep Tracker",
			backButton="VISIBLE",
			text={
				"primaryText": {
					"type": "RichText",
					"text": msg
				}
			}
		)

	return render_msg


@ask.intent("AMAZON.CancelIntent")
def cancel_intent():
	display = display_type()
	msg = 'Goodbye! Thanks for using Sleep Tracker.'
	render_msg = statement(msg)

	if display:
		render_msg = render_msg.display_render(
			template="BodyTemplate1",
			title="Sleep Tracker",
			backButton="VISIBLE",
			text={
				"primaryText": {
					"type": "RichText",
					"text": msg
				}
			}
		)

	return render_msg


def error(option):
	display = display_type()
	msg = ""

	if option == 'Response':
		msg = """Hi there, It seems as though you didn't tell me when you went to bed last night and I therefore
		can't tell you how long you slept for. If you did this by accident and you are in fact going to bed now,
		Please say I am going to bed now but if you are getting up now, then please tell me help to find out how to use
		this skill or stop to close this skill. What would you like to do?"""

	render_msg = question(msg)

	if display:
		render_msg = render_msg.display_render(
			template="BodyTemplate1",
			title="Sleep Tracker",
			backButton="VISIBLE",
			text={
				"primaryText": {
					"type": "RichText",
					"text": msg
				}
			}
		)

	return render_msg


if __name__ == '__main__':
	# app.run(debug=True)
	app.run()
