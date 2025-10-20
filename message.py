
from dotenv import dotenv_values
from twilio.base.exceptions import TwilioRestException
from twilio.rest import Client

from models import Person

env = dotenv_values(".env")
client = Client(username=env['TWILIO_ACCOUNT_SID'],
                password=env['TWILIO_AUTH_TOKEN'], account_sid=env['TWILIO_ACCOUNT_SID'])


def send_assignment(giver: Person, receiver: Person) -> bool:
    body = f"Hello {giver.name}, you are {receiver.name}'s Secret Santa this year. Remember to get them a gift!"

    try:
        client.messages.create(
            body=body,
            from_=env['TWILIO_PHONE_NUMBER'],
            to=giver.phone_number
        )
        return True

    except TwilioRestException as e:
        print(e)
        return False
