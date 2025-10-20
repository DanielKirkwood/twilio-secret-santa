import random
from constraint import NotInSetConstraint, Problem, AllDifferentConstraint
from datetime import datetime as dt

from history import exclusion_list_from_history
from models import DrawHistory, Group, Person


async def solve_secret_santa_csp_for_group(
    group_id: int,
) -> dict[Person, Person] | None:
    problem = Problem()

    group = await Group.get(id=group_id).prefetch_related("members__partner")
    members = group.members

    # Add variables: Each person must be assigned to one other person (not themselves)
    for person in members:
        all_except_me = [p for p in members if p.username != person.username]
        problem.addVariable(person, all_except_me)

    # Add the AllDifferent constraint: everyone must be assigned to a unique person
    problem.addConstraint(AllDifferentConstraint())

    # Add exclusion constraints
    for person in members:
        # Adding the constraint for each person's exclusion list
        current_year = dt.now().year
        previous_receivers = await exclusion_list_from_history(
            person.username, group.id, current_year - 2
        )

        if len(previous_receivers) > 0:
            problem.addConstraint(NotInSetConstraint(previous_receivers), [person])

        partner = person.partner
        if partner is not None:
            problem.addConstraint(
                lambda p, partner_val=partner: p != partner_val, [person]
            )

    # Solve the problem
    solutions = problem.getSolutions()

    if not solutions:
        return None

    solution = random.choice(solutions)

    return solution
