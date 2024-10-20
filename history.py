from models import DrawHistory, Group, Person


async def exclusion_list_from_history(username: str, group_id: int, from_year: int) -> list[Person]:

    group = await Group.get(id=group_id).prefetch_related("members")
    member = await group.members.filter(username=username).first()

    if member is None:
        raise RuntimeError(f"no member with username={
                           username} in group={group_id}")

    history = await DrawHistory.filter(
        group_id=group_id,
        giver=member,
        year__gte=from_year
    ).all().prefetch_related('receiver')

    return [draw.receiver for draw in history]
