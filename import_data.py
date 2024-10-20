import json


from models import DrawHistory, Person, Group


async def import_from_json(filename):
    with open(filename) as json_file:
        data = json.load(json_file)

    participants = data['participants']
    groups = data['groups']

    for group_name, group_data in groups.items():
        group = await Group.create(name=group_name)
        for p in group_data['members']:
            person_data = participants[p]
            person, _ = await Person.get_or_create(username=p, name=person_data['name'], phone_number=person_data['phone_number'])
            await group.members.add(person)

        for d in group_data['drawHistory']:
            giver = await Person.get(username=d['giver'])
            receiver = await Person.get(username=d['receiver'])
            await DrawHistory.create(group=group, giver=giver, receiver=receiver, year=d['year'], message_delivered=True)

    for person_username, person_data in participants.items():
        person, _ = await Person.get_or_create(username=person_username, name=person_data['name'], phone_number=person_data['phone_number'])

        if person_data['partner'] is not None:
            partner = await Person.get(username=person_data['partner'])

            person.partner = partner
            await person.save()

            partner.partner = person
            await partner.save()
