import click
from tdacm.dashboard import app


@click.command()
@click.option("--debug", is_flag=True, help="Run dashboard in debug mode.")
def dashboard(debug):
    app.run_server(debug=debug)


@click.group()
def cli():
    pass


cli.add_command(dashboard)

if __name__ == "__main__":
    cli()
