"""
    Secret Santa!

    Given a dictionary of people, their phone numbers and other people to exclude this script will
    facilitate the selection and notification process for secret santa.

    Twillio is used to send each participant the name of the person they have this year.

    A bipartite graph is created to map each participant to the people that they can have
    this year for secret santa.
"""

import matplotlib.pyplot as plt
import networkx as nx
from dotenv import dotenv_values
from networkx.algorithms import bipartite
from twilio.base.exceptions import TwilioRestException
from twilio.rest import Client

from participants import participants

# load twilio details
env = dotenv_values(".env")
client = Client(env['TWILIO_ACCOUNT_SID'], env['TWILIO_AUTH_TOKEN'])

# Use a global variable so it's available to helper functions
PARTICIPANTS = participants

def create_assignments():
    """created the assignments from PARTICIPANTS
    """
    people = list(PARTICIPANTS)

    graph = create_graph(people)

    matching = bipartite.maximum_matching(graph)
    assignments = dict((k,f'{v[:-1]}') for k,v in matching.items() if '2' not in k)

    return assignments

def create_graph(people):
    """ creates a bipartite graph
    """

    graph = nx.Graph()

    # add the nodes
    graph.add_nodes_from(people, bipartite=0)
    graph.add_nodes_from([f'{x}2' for x in people], bipartite=1)

    # add edges from each person in zone 0 to zone 1
    # excluding themselves and anyone in their exclude list.
    for person in people:
        excludes = PARTICIPANTS[person]['excludes']
        excludes.append(person)

        edges = [(person, f'{x}2') for x in people if x not in excludes]

        graph.add_edges_from(edges)

    # prints graph for visualisation in debug mode
    if env['DEBUG'] == 'True':
        plt.figure()
        nx.draw_networkx(graph, pos = nx.drawing.layout.bipartite_layout(graph, people))
        plt.show()

    return graph

def send_assignments(assignments):
    """
        sends the assignments via twillio

        if DEBUG env variable set to True, then the messages are instead printed
    """

    successful_notification_counter = 0
    for gift_sender, gift_recipient in assignments.items():
        body = f"{gift_sender}, you are {gift_recipient}'s Secret Santa this year. Remember to get them a gift!"

        if env['DEBUG'] == 'True':
            print('-' * 30)
            print(f'body: {body}')
            print(f'Secret Santa assignment sent to {gift_sender} at {PARTICIPANTS[gift_sender]["phone_number"]} via SMS')
            print('-' * 30)
        elif env['DEBUG'] == 'False':
            try:
                client.messages.create(
                     body=body,
                     from_=env['TWILIO_PHONE_NUMBER'],
                     to=PARTICIPANTS[gift_sender]['phone_number']
                 )
                successful_notification_counter += 1

            except TwilioRestException as error:
                print(error)
                print(f'There may have been a problem sending the notification to {gift_sender} at {PARTICIPANTS[gift_sender]["phone_number"]}')
                continue

    print(f'Notifications sent to {successful_notification_counter} people')


if __name__ == "__main__":
    assignments_dict = create_assignments()
    send_assignments(assignments_dict)
