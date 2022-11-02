
# Twilio Secret Santa

A python script that generates secret santa allocations given some restraints and sends the allocations to participants using [Twilio](https://www.twilio.com).

The conditions which this script had to meet for me and my friends needs were:

* The script should assign participants a receiver for their gift.
* Participants should be allowed to exclude other participants from being selected for them. Useful for couples or for preventing users from getting the same person they got last year.
* The allocations should be sent via an outside SMS service to each participant to prevent anyone from knowing the allocations. This is where Twilio comes in.




## Installation

Clone the project to your machine

```bash
git clone https://github.com/DanielKirkwood/twilio-secret-santa.git
cd twillio-secret-santa
```

Then install the dependencies listed in requirements.txt using pip

```bash
pip install -r requirements.txt
```

**NOTE: I highly recommend you create a virtual environment to install the dependencies to. For more information on creating virtual environments in python, check out the [docs](https://docs.python.org/3/tutorial/venv.html)** 


Create a `.env` file

```bash
touch .env
```

To run this project, you will need to add the following environment variables to your `.env` file:

`TWILIO_ACCOUNT_SID` - This can be found on Twilio by going to 'Account' -> 'API keys & tokens'.

`TWILIO_AUTH_TOKEN` - This can be found on Twilio by going to 'Account' -> 'API keys & tokens'.

`TWILIO_PHONE_NUMBER` - This is the phone number that the texts will be sent from.

`DEBUG` - Set to True if you do not want sms messages to be sent and instead the message bodies will be printed to terminal so that you can review them. In production, set to False so that the messages will be sent via Twilio.

You also need to create a `participants.py` file which will hold the details of your participants.

```bash
touch participants.py
```

Inside this file, create a dictionary called `participants` with the following format:

```python
participants = {
    'name1': {
        'phone_number': 'xxxxxxxxxxxxx',
        'excludes': ['name2'],
    },
    'name2': {
        'phone_number': 'xxxxxxxxxxxxx',
        'excludes': [],
    },
    'name3': {
        'phone_number': 'xxxxxxxxxxxxx',
        'excludes': ['name1'],
    },
    'name4': {
        'phone_number': 'xxxxxxxxxxxxx',
        'excludes': ['name2', 'name3'],
    },
}
```

Each key should be the name of the participant. The value should be another dictionary with two keys; `phone_number` and `excludes`. The phone number must be in [E.164 format](https://www.twilio.com/docs/glossary/what-e164) or the messages will not be sent correctly by Twilio. `Excludes` is a list that contains the names of the participants which cannot be seelcted for the participant. In the above example, `name1` cannot be given `name2`, `name2` can be given anyone, `name3` cannot be given `name1` and `name4` cannot be given `name2` or `name3`.


## Running the script

Provided that you have set-up your environment variables and the participants file, you can run the script by executing the `main.py` file:

```bash
python main.py
```

If you have set `DEBUG` to `False` then you will see 

```
Notifications sent to n people
```

Where n is the number of people that have been successfully sent their allocations.


If you have set `DEBUG` to `True` then you will first see a matplotlib figure of the bipartite created from your participants. You will then see the message bodies which would have been sent in the console:

```
------------------------------
body: name1, you are name3's Secret Santa this year. Remember to get them a gift!
Secret Santa assignment sent to name1 at xxxxxxxxxxxxx via SMS
------------------------------
------------------------------
body: name2, you are name4's Secret Santa this year. Remember to get them a gift!
Secret Santa assignment sent to name2 at xxxxxxxxxxxxx via SMS
------------------------------
------------------------------
body: name3, you are name2's Secret Santa this year. Remember to get them a gift!
Secret Santa assignment sent to name3 at xxxxxxxxxxxxx via SMS
------------------------------
------------------------------
body: name4, you are name1's Secret Santa this year. Remember to get them a gift!
Secret Santa assignment sent to name4 at xxxxxxxxxxxxx via SMS
------------------------------
Notifications sent to 0 people
```

In Debug mode, no messages are sent so this allows you to ensure eveything working correctly if you make any changes to the underlying code.
## License

[MIT](https://choosealicense.com/licenses/mit/)


## Authors

- [@DanielKirkwood](https://www.github.com/DanielKirkwood)

