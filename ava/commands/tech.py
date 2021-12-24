import click
from ava.services.tech import Technical


@click.command()
@click.option('--ticker', type=str, default='AAPL', help="Yahoo Finance ticker")
def cli(ticker):
    """Technical Analysis"""
    tech = Technical(ticker)
    click.echo(tech.status())

