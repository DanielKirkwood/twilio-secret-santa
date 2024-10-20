from datetime import datetime as dt
from models import DrawHistory, Group, Person


async def report_draw_results_for_group_and_year(group_name: str, year: int) -> list[str] | None:
    group = await Group.get(name=group_name)
    draw_results = await DrawHistory.filter(group=group, year=year).prefetch_related('giver', 'receiver')

    if not draw_results:
        return None

    print(f"Secret Santa Draw Report for Group '{group.name}' in {year}:\n")

    report = []

    for result in draw_results:
        line = f"{result.giver.name} gave a gift to {result.receiver.name}"
        report.append(line)
        print(line)

    return report


async def report_draw_history_for_person(person_username: str) -> list[str] | None:
    person = await Person.get(username=person_username)
    draw_results = await DrawHistory.filter(giver=person).prefetch_related('receiver', 'group')

    if not draw_results:
        print(f"No draw history found for {person.name}.")
        return None

    print(f"Secret Santa Draw History for {person.name}:\n")
    report = []

    for result in draw_results:
        line = f"In {result.year} ({result.group.name}), {
            person.name} gave a gift to {result.receiver.name}"
        report.append(line)
        print(line)

    return report


async def report_draw_history_for_group(group_name: str, start_year: int, end_year: int | None = None):
    group = await Group.get(name=group_name)
    if end_year is None:
        end_year = dt.now().year

    draw_results = await DrawHistory.filter(group_id=group.id, year__gte=start_year, year__lte=end_year).prefetch_related('giver', 'receiver')

    if not draw_results:
        print(f"No draw history found for Group '{
              group.name}' from {start_year} to {end_year}.")
        return None

    print(f"Secret Santa Draw History for Group '{
          group.name}' from {start_year} to {end_year}:\n")
    report = []

    for result in draw_results:
        line = f"In {result.year}, {
            result.giver.name} gave a gift to {result.receiver.name}"
        report.append(line)
        print(line)

    return report
