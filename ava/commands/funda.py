import click
from ava.services.funda import Fundamental


class Context:
    def __init__(self, ticker):
        self.ticker = ticker
        self.compute = Fundamental()


@click.group()
@click.option('--ticker', type=str, default='AAPL', help="Yahoo Finance ticker")
@click.pass_context
def cli(ctx, ticker):
    """Fundamental Analysis"""
    ctx.obj = Context(ticker)


@cli.command()
@click.pass_context
def revenue(ctx):
    """Revenue Trend"""
    click.echo(ctx.obj.ticker)


@cli.command()
@click.pass_context
def profit(ctx):
    """Profit Trend"""
    click.echo(ctx.obj.ticker)


@cli.command()
@click.pass_context
def cash(ctx):
    """Free Cash Flow Trend"""
    click.echo(ctx.obj.ticker)
