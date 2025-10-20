import re
from datetime import datetime as dt
from tortoise.models import Model
from tortoise import fields

from mixins import TimestampMixin
from validate import UKMobileNumberValidator


class Person(TimestampMixin, Model):
    username = fields.CharField(max_length=256, primary_key=True)
    name = fields.CharField(max_length=256)
    phone_number = fields.CharField(
        max_length=15,
        unique=True,
        validators=[UKMobileNumberValidator()]
    )
    partner = fields.ForeignKeyField(
        "models.Person", related_name="partner_of", null=True, on_delete=fields.SET_NULL)

    async def save(self, *args, **kwargs):
        # If the username is not set, generate it from the person's name
        if not self.username:
            self.username = self.generate_username(self.name)
        await super().save(*args, **kwargs)

    def __str__(self):
        return f"Person(username={self.username}, name={self.name}, phone={self.phone_number})"

    def __lt__(self, other):
        """Compare two Person objects based on their usernames (alphabetically)."""
        if not isinstance(other, Person):
            return NotImplemented
        return self.username < other.username

    class Meta:
        table = "persons"

    @staticmethod
    def generate_username(name):
        """Generate a username by lowercasing and removing spaces, punctuation, and hyphens."""
        username = name.lower()
        username = re.sub(r'[\s\W_]+', '', username)
        return username


class Group(TimestampMixin, Model):
    id = fields.IntField(primary_key=True)
    name = fields.CharField(max_length=256)
    members: fields.ManyToManyRelation[Person] = fields.ManyToManyField(
        "models.Person", related_name="groups")

    def __str__(self):
        return f"Group(id={self.id}, name={self.name})"

    class Meta:
        table = "group"


class DrawHistory(TimestampMixin, Model):
    id = fields.IntField(primary_key=True)
    group: fields.ForeignKeyRelation[Group] = fields.ForeignKeyField(
        "models.Group", related_name="draws", on_delete=fields.CASCADE)
    giver: fields.ForeignKeyRelation[Person] = fields.ForeignKeyField(
        "models.Person", related_name="gifts_given", on_delete=fields.CASCADE)
    receiver: fields.ForeignKeyRelation[Person] = fields.ForeignKeyField(
        "models.Person", related_name="gifts_received", on_delete=fields.CASCADE)
    year = fields.IntField(default=dt.now().year)
    message_delivered = fields.BooleanField()

    def __str__(self):
        return f"DrawHistory(giver={self.giver.name}, receiver={self.receiver.name}, group={self.group.name}, year={self.year}, message_delivered={self.message_delivered})"
