import click
from datetime import datetime as dt
from dotenv import dotenv_values
from tortoise import Tortoise, run_async

from models import DrawHistory, Person, Group

env = dotenv_values(".env")


async def schema_exists():
    """Check if the database schema already exists."""
    # Fetch the list of tables in the current database
    tables = Tortoise.describe_models()
    return bool(tables)


async def init(db_url: str) -> None:
    await Tortoise.init(
        db_url=f'sqlite://{db_url}',
        modules={'models': ['models']}
    )
    await Tortoise.generate_schemas(safe=True)


@click.group()
@click.option('--db', default='db.sqlite3', help='The SQLite database to use (default is in-memory).')
@click.pass_context
def cli(ctx, db):
    ctx.ensure_object(dict)
    ctx.obj['db_url'] = db


@click.command()
@click.pass_context
def generate_schemas(ctx):
    async def generate():
        from tortoise import Tortoise
        await init(ctx.obj['db_url'])
        await Tortoise.generate_schemas()

    run_async(generate())


@cli.command()
@click.argument('name')
@click.pass_context
def add_group(ctx, name):
    """Add a new group."""
    async def _add_group():
        await init(ctx.obj['db_url'])
        group = await Group.create(name=name)
        click.echo(f"Group '{group.name}' created with ID {group.id}")

    run_async(_add_group())


@cli.command()
@click.argument('name')
@click.argument('phone')
@click.pass_context
def add_person(ctx, name, phone):
    """Add a new person."""
    async def _add_person():
        await init(ctx.obj['db_url'])
        person = await Person.create(name=name, phone_number=phone)
        click.echo(f"Person '{person.name}' created with username {
                   person.username}")

    run_async(_add_person())


@cli.command()
@click.argument('person_id', type=int)
@click.argument('group_id', type=int)
@click.pass_context
def add_person_to_group(ctx, person_id, group_id):
    """Add a person to a group."""
    async def _add_person_to_group():
        await init(ctx.obj['db_url'])
        person = await Person.get(id=person_id)
        group = await Group.get(id=group_id)
        await group.members.add(person)
        click.echo(f"Added '{person.name}' to group '{group.name}'")

    run_async(_add_person_to_group())


@cli.command()
@click.argument('person_id', type=int)
@click.argument('partner_id', type=int)
@click.pass_context
def set_relationship(ctx, person_id, partner_id):
    """Sets a person's relationship status."""
    async def _set_relationship():
        await init(ctx.obj['db_url'])
        person = await Person.get(id=person_id)
        partner = await Person.get(id=partner_id)

        # Set the relationship
        person.partner = partner
        await person.save()

        partner.partner = person
        await partner.save()

        click.echo(f"Set {person.name} and {partner.name} as partners.")

    run_async(_set_relationship())


@cli.command()
@click.argument('person_id', type=int)
@click.pass_context
def clear_relationship(ctx, person_id):
    """Clear a person's relationship status."""
    async def _clear_relationship():
        await init(ctx.obj['db_url'])
        person = await Person.get(id=person_id)

        if person.partner:
            partner = await Person.get(id=person.partner)
            person.partner = None
            await person.save()
            partner.partner = None
            await partner.save()
            click.echo(f"Cleared relationship between {
                       person.name} and {partner.name}.")
        else:
            click.echo(f"{person.name} does not have a partner.")

    run_async(_clear_relationship())


@cli.command()
@click.argument('group_id', type=int)
@click.option('--debug', is_flag=True)
@click.pass_context
def run_draw(ctx, group_id, debug):
    """Run the Secret Santa draw for a group."""
    async def _run_draw():
        from message import send_assignment
        from match import solve_secret_santa_csp_for_group
        await init(ctx.obj['db_url'])

        solution = await solve_secret_santa_csp_for_group(group_id)

        if solution is None:
            click.echo(f"No valid solution found for Group ID: {
                       group_id}", err=True)
            return

        for giver, receiver in solution.items():
            if debug is True:
                click.echo(f"{giver.name} is assigned to give a gift to {
                    receiver.name}")
            else:
                sent = send_assignment(giver, receiver)
                if sent is False:
                    click.echo(f'failed to deliver message to {
                               giver.name}', err=True)

                await DrawHistory.create(
                    giver=giver,
                    receiver=receiver,
                    group_id=group_id,
                    message_delivered=sent
                )

    run_async(_run_draw())


@cli.command()
@click.argument('group_name', type=str)
@click.argument('year', type=int)
@click.option('--export', type=click.Choice(['csv', 'json']), default=None, help="Export format")
@click.pass_context
def report_group_draw(ctx, group_name, year, export):
    """Generate and optionally export the draw report for a group and year."""
    async def _report_group_draw():
        from export import export_report_to_csv, export_report_to_json
        from report import report_draw_results_for_group_and_year

        await init(ctx.obj['db_url'])
        report = await report_draw_results_for_group_and_year(group_name, year)

        if not report:
            click.echo(f"No draw results found for Group '{
                       group_name}' in {year}.", err=True)
            return

        if export == 'csv':
            export_report_to_csv(report, f"group_{group_name}_{
                                 year}_secret_santa.csv")
        elif export == 'json':
            export_report_to_json(report, f"group_{group_name}_{
                                  year}_secret_santa.json")

    run_async(_report_group_draw())


@cli.command()
@click.argument('person_username', type=str)
@click.pass_context
def report_person_history(ctx, person_username):
    """Generate a report of a person's draw history."""
    async def _report_person_history():
        from report import report_draw_history_for_person
        await init(ctx.obj['db_url'])
        await report_draw_history_for_person(person_username)

    run_async(_report_person_history())


@cli.command()
@click.argument('group_name', type=str)
@click.argument('start_year', type=int)
@click.option('--end_year', type=int, default=dt.now().year, help="End year of the report")
@click.pass_context
def report_group_history(ctx, group_name, start_year, end_year):
    """Generate a report of a group's draw history over multiple years."""
    async def _report_group_history():
        from report import report_draw_history_for_group
        await init(ctx.obj['db_url'])
        await report_draw_history_for_group(group_name, start_year, end_year)

    run_async(_report_group_history())


@cli.command()
@click.pass_context
def clear_db(ctx):
    """Clear the database by dropping all tables."""
    async def _clear_db():
        # Use the database URL passed via the context
        await init(ctx.obj['db_url'])

        # Ask for confirmation before clearing the database
        confirmed = click.confirm(f"Are you sure you want to clear the database '{
                                  ctx.obj['db_url']}'?")
        if not confirmed:
            click.echo("Database clear operation canceled.")
            return

        click.echo("Clearing the database...")

        # Drop all tables in the database
        await Tortoise._drop_databases()

        click.echo("Database cleared successfully.")

    run_async(_clear_db())


@cli.command()
@click.argument('filename', type=str)
@click.pass_context
def import_data(ctx, filename):
    async def _import_data(filename: str):
        import import_data

        await init(ctx.obj['db_url'])
        click.echo(f'importing data from {filename}')

        await import_data.import_from_json(filename)

        click.echo("data imported")

    run_async(_import_data(filename))


if __name__ == "__main__":
    cli()
