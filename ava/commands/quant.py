import click
from ava.services.quant import Quantitative


class Context:
    def __init__(self, ticker):
        self.ticker = ticker
        self.compute = Quantitative()


@click.group()
@click.option('--ticker', type=str, default='AAPL', help="Yahoo Finance ticker")
@click.pass_context
def cli(ctx, ticker):
    """Quantitative Analysis"""
    ctx.obj = Context(ticker)


@cli.command()
@click.pass_context
def alpha(ctx):
    """Alpha from Fama French 4-Factor Model"""
    click.echo(ctx.obj.ticker)


@cli.command()
@click.pass_context
def beta(ctx):
    """Beta from Fama French 4-Factor Model"""
    click.echo(ctx.obj.ticker)
